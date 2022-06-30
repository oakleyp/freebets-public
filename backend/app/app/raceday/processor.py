import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.lib.clients.live_abstract import AbstractLiveRacingClient

from app.lib_private.clients.live_racing import LiveRacingClient
from app.lib.crawlers.live_racing import (
    LiveRacingCrawler,
    LiveRacingCrawlerException,
)
from app.lib.schemas.live_racing import StarterDetails, TrackWithRaceDetails
from app.ml.predictor.race_predictor import RacePredictor
from app.models.bet import Bet
from app.models.race import Race
from app.models.race_entry import RaceEntry
from app.raceday.bet_strategy.bet_strategies import (
    BetResult,
    BetTypeImpl,
    MultiBetResult,
)
from app.raceday.bet_strategy.bet_tagger import BetTagger
from app.raceday.bet_strategy.generator import BetGen
from app.raceday.race_canonical import (
    LiveRaceEntryCanonical,
    LiveTrackBasicCanonical,
)

logger = logging.getLogger(__name__)


class RaceWatcher(BaseModel):
    race_id: int
    post_time: datetime
    next_check_time: datetime
    last_checked_time: Optional[datetime]

    def __repr__(self):
        """String repr of RaceWatcher."""
        return "<RaceWatcher(race_id=%s, post_time=%s, next_check_time=%s)>" % (
            self.race_id,
            self.post_time,
            self.next_check_time,
        )


class TimeContext(BaseModel):
    now: datetime
    lookahead_start: datetime
    lookahead_end: datetime
    refresh_interval: timedelta

    def __repr__(self):
        """String repr of TimeContext."""
        return (
            "<TimeContext(now=%s, lookahead_start=%s, lookahead_end=%s, refresh_interval=%s)>"
            % (
                self.now,
                self.lookahead_start,
                self.lookahead_end,
                self.refresh_interval,
            )
        )


class NextCheckGen(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_next_check_time(
        self, watcher: RaceWatcher, time_context: TimeContext,
    ) -> Optional[datetime]:
        raise NotImplementedError(
            f"get_next_check_time() not implemented for {self.__class__.__name__}"
        )


class DefaultNextCheckGen(NextCheckGen):
    def get_next_check_time(
        self, watcher: RaceWatcher, time_context: TimeContext
    ) -> Optional[datetime]:
        if watcher.post_time <= time_context.lookahead_start:
            # Time has passed, don't check
            return None

        if watcher.last_checked_time is None:
            return time_context.now

        # If nct would be outside of lookahead range, return the lookahed_end as nct
        if (
            watcher.post_time - time_context.refresh_interval
            > time_context.lookahead_end
        ):
            return time_context.lookahead_end
        # Otherwise, nct should be the refresh_interval + current time
        else:
            return time_context.now + time_context.refresh_interval


class RaceDayProcessorException(Exception):
    pass


class FailedRaceListIngestException(RaceDayProcessorException):
    pass


class FailedRaceEntryIngestException(RaceDayProcessorException):
    pass


class RaceDayProcessor:
    def __init__(
        self,
        db: Session,
        *,
        enabled_bet_types: List[BetTypeImpl] = [],  # TODO
        enabled_track_codes: List[str] = [],
        lookahead_base: timedelta = timedelta(days=0),
        lookahead_limit: timedelta = timedelta(days=1),
        race_refresh_interval: timedelta = timedelta(days=0, minutes=10),
        next_check_gen: NextCheckGen = DefaultNextCheckGen(),
        max_sleep_secs: float = 60 * 10,
        max_bets_per_race: int = 1000,
        resilient: bool = True,
    ) -> None:
        self.db: Session = db
        self.enabled_bet_types: List[BetTypeImpl] = enabled_bet_types
        self.lookahead_base: timedelta = lookahead_base
        self.lookahead_limit: timedelta = lookahead_limit
        self.race_refresh_interval: timedelta = race_refresh_interval
        self.next_check_gen: NextCheckGen = next_check_gen
        self.max_sleep_secs: float = max_sleep_secs
        self.enabled_track_codes: List[str] = enabled_track_codes
        self.max_bets_per_race: int = max_bets_per_race
        self.resilient: bool = resilient

        self.watching_races: Dict[int, RaceWatcher] = {}

        self.live_race_client: AbstractLiveRacingClient = LiveRacingClient()
        self.live_race_crawler = LiveRacingCrawler(self.live_race_client)
        self.bet_tagger = BetTagger(self.db)

        self.race_predictor = RacePredictor()

    def blocking_start(self) -> None:
        """Starts processing races for the configured time context.
           Blocks the current thread.
        """
        logger.debug(
            f"Starting RaceDayProcessor for "
            f"{self.lookahead_base} -> {self.lookahead_limit}"
        )

        time_context = self._active_time_context()
        self._clean_db(time_context)

        while True:
            try:
                time_context = self._active_time_context()
                next_nct = self.process_once(time_context)
            except RaceDayProcessorException as e:
                logger.exception(
                    "process_once() encountered an error (%s).", e, stack_info=True
                )
                self._log_and_sleep(self.max_sleep_secs)
                continue

            if not next_nct:
                logger.info(
                    "No upcoming nct within configured time context.",
                    self.max_sleep_secs,
                )
                self._log_and_sleep(self.max_sleep_secs)

            # Sleep for either the max_sleep time or the soonest nct,
            # whichever is smallest
            sleep_time = min(self.max_sleep_secs, next_nct)

            if sleep_time < 0:
                logger.error(
                    "Something went wrong - sleep_time is negative (%d)", sleep_time
                )
                sleep_time = self.max_sleep_secs

            self._log_and_sleep(sleep_time)

    def process_once(self, time_context: TimeContext) -> Optional[float]:
        """
            Run a single cycle of the race ingest and bet generation process.
            Returns the number of seconds until the soonest next_check_time,
            if there is a valid one.
        """

        logger.debug(
            f"Pulling races for range "
            f"{time_context.lookahead_start.isoformat()} -> "
            f"{time_context.lookahead_end.isoformat()}"
        )

        try:
            self._ingest_races_shallow(time_context)
        except LiveRacingCrawlerException:
            raise FailedRaceListIngestException

        self._remove_expired_watchers(time_context)
        upcoming_races = self._get_races_in_time_context(time_context)
        races_to_refresh = self._get_races_to_refresh(upcoming_races, time_context)

        logger.debug(f"{len(races_to_refresh)} races to refresh...")

        for race in upcoming_races:
            logger.debug("Refreshing race entries for %s", race)

            try:
                self._ingest_race_entries(race)
            except LiveRacingCrawlerException:
                logger.exception(
                    "Failed to ingest race entries for %s", race, stack_info=True
                )
                if not self.resilient:
                    raise FailedRaceEntryIngestException

                self._del_watcher(race)

                continue

            self._update_watcher(race, time_context)

            logger.debug("Regenerating predictions for race %s", race)
            self._refresh_race_predictions(race)

            logger.debug("Regenerating bets for race %s", race)
            self._refresh_race_bets(race)

        min_nct = self._get_min_watcher_nct()
        sleep_til_nct = (min_nct - time_context.now).total_seconds()

        return sleep_til_nct

    def _ingest_races_shallow(self, time_context: TimeContext) -> None:
        """Ingest all races (without entries) for the given time."""
        tracks: List[
            TrackWithRaceDetails
        ] = self.live_race_crawler.get_all_track_races_shallow(
            target_date=time_context.now.date()
        )
        races_canon: List[Race] = []

        for track in tracks:
            races_canon.extend(LiveTrackBasicCanonical(track).convert())

        for race in races_canon:
            existing_race = (
                self.db.query(Race)
                .filter(
                    Race.track_code == race.track_code,
                    Race.race_date == race.race_date,
                    Race.country == race.country,
                    Race.race_number == race.race_number,
                )
                .first()
            )

            existing_race_watcher = None

            # If the race already exists in the db, reassign existing entries
            # to the updated race model and overwrite the existing data
            if existing_race:
                if existing_race.id in self.watching_races:
                    existing_race_watcher = self.watching_races[existing_race.id]
                    del self.watching_races[existing_race.id]

                existing_entries = existing_race.entries

                for existing_entry in existing_entries:
                    existing_entry.race_id = race.id

                race.entries = existing_entries
                existing_race.entries = []

                self.db.delete(existing_race)
                self.db.commit()

            if self._should_watch_race(race, time_context):
                self.db.add(race)
                self.db.flush()

                if existing_race_watcher:
                    self.watching_races[race.id] = existing_race_watcher
                    self.watching_races[race.id].post_time = race.post_time
                    self.watching_races[race.id].race_id = race.id
                else:
                    self._add_watcher(race, time_context)

        self.db.commit()

    def _remove_expired_watchers(self, time_context: TimeContext) -> None:
        """
            Remove all watchers from watching_races where
            the next_check_time is None.
        """
        for (id, watcher) in self.watching_races.copy().items():
            nct = self.next_check_gen.get_next_check_time(watcher, time_context)

            if nct is None:
                del self.watching_races[id]

    def _get_races_in_time_context(self, time_context: TimeContext) -> List[Race]:
        """Get all races in the active time context."""
        return (
            self.db.query(Race)
            .filter(
                Race.post_time >= time_context.lookahead_start,
                Race.post_time < time_context.lookahead_end,
            )
            .all()
        )

    def _get_races_to_refresh(
        self, upcoming_races: List[Race], time_context: TimeContext
    ) -> List[Race]:
        """
            Get races that are due for a refresh and
            update their corresponding RaceWatchers.
        """
        races_to_refresh: List[Race] = []

        for race in upcoming_races:
            if race.id in self.watching_races:
                watcher = self.watching_races[race.id]

                if watcher.next_check_time <= time_context.now:
                    races_to_refresh.append(race)

        return races_to_refresh

    def _refresh_race_bets(self, race: Race) -> None:
        """Regenerate bets for the given race."""
        existing_race_bets = (
            self.db.query(Bet).filter(Bet.race.has(Race.id == race.id)).all()
        )

        for bet in existing_race_bets:
            self.db.delete(bet)

        bet_gen = BetGen(race=race)
        bets = bet_gen.all_bets()

        logger.debug("Generated %d bets for race %s", len(bets), race)

        for (i, bet) in enumerate(bets):
            if i >= self.max_bets_per_race:
                logger.debug(
                    "Reached max_bets_per_race (%d); breaking", self.max_bets_per_race
                )
                break

            bet_res: Union[BetResult, MultiBetResult] = bet.result()
            bet_db = bet_res.to_bet_db()

            self.bet_tagger.assign_tags(bet_db)

            self.db.add(bet_db)

        logger.debug("Saving generated bets")

        self.db.commit()

    def _active_time_context(self) -> TimeContext:
        """Create a TimeContext based on the current time and configured lookahead."""
        now = datetime.now(timezone.utc)

        return TimeContext(
            now=now,
            lookahead_start=now + self.lookahead_base,
            lookahead_end=now + self.lookahead_limit,
            refresh_interval=self.race_refresh_interval,
        )

    def _refresh_race_predictions(self, race: Race) -> None:
        result = self.race_predictor.calc_probs(race)

        for entry in race.entries:
            if entry.id in result.entries_probs:
                entry.predicted_odds = 1 / result.entries_probs[entry.id].win_proba
                self.db.add(entry)
            else:
                logger.debug(
                    "Failed getting odds for entry %s somehow - %s",
                    entry,
                    result.json(),
                )

        self.db.commit()

    def _get_min_watcher_nct(self) -> datetime:
        """Get the soonest next_check_time from watching_races."""
        ncts = [v.next_check_time for (k, v) in self.watching_races.items()]

        if len(ncts) < 1:
            max_dt = datetime.max
            return max_dt.astimezone(tz=timezone.utc)

        return min(ncts)

    def _add_watcher(self, race: Race, time_context: TimeContext) -> None:
        """Creates a new RaceWatcher for the given race, using the given time_context
           as the basis for the next_check_time.
        """
        watcher = RaceWatcher(
            race_id=race.id,
            post_time=race.post_time,
            next_check_time=time_context.now,
            last_checked_time=None,
        )

        nct = self.next_check_gen.get_next_check_time(watcher, time_context)

        if nct is None:
            logger.debug("Skipping add watcher - nct is None for race %s", race)
            return None

        watcher.next_check_time = nct
        self.watching_races[race.id] = watcher

    def _del_watcher(self, race) -> None:
        if race.id in self.watching_races:
            del self.watching_races[race.id]

    def _update_watcher(self, race: Race, time_context: TimeContext) -> None:
        watcher = self.watching_races[race.id]

        if watcher is None:
            logger.error("Called update watcher when none exists for race %s", race)
            return None

        watcher.last_checked_time = time_context.now

        nct = self.next_check_gen.get_next_check_time(watcher, time_context)

        if nct is None:
            del self.watching_races[race.id]
            return None

        watcher.next_check_time = nct
        self.watching_races[race.id] = watcher

    def _ingest_race_entries(self, race: Race) -> None:
        """Refresh the list of entries for the given race."""
        race_entries: List[StarterDetails] = self.live_race_crawler.get_race_entries(
            race.track_code, race.race_number, race.race_type
        )
        entries_canon: List[RaceEntry] = [
            LiveRaceEntryCanonical(entry).convert() for entry in race_entries
        ]

        race.entries = []
        self.db.commit()

        race.entries = entries_canon
        self.db.commit()

    def _should_watch_race(self, race: Race, time_context: TimeContext) -> bool:
        """Determine whether the given race should be tracked based
           on the current config.
        """
        if race.status != "Open":
            return False

        if self.enabled_track_codes and len(self.enabled_track_codes) > 0:
            if race.track_code not in self.enabled_track_codes:
                return False

        if not (
            race.post_time >= time_context.lookahead_start
            and race.post_time < time_context.lookahead_end
        ):
            return False

        return True

    def _clean_db(self, time_context: TimeContext) -> None:
        """Delete all race, entries, and bets within the current time context."""

        all_races: List[Race] = self.db.query(Race).filter(
            Race.post_time >= time_context.lookahead_start,
            Race.post_time < time_context.lookahead_end,
        ).all()

        logger.debug(
            "Cleaning up %d races found in active time context", len(all_races)
        )

        for race in all_races:
            self.db.delete(race)

        self.db.commit()

    def _log_and_sleep(self, sleep_time: float) -> None:
        """Log the time to be slept, then sleep."""
        logger.info("Sleeping %d seconds.", sleep_time)
        sleep(sleep_time)
