import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from sqlalchemy.orm import Session, make_transient

from app.core.config import settings
from app.lib.clients.demo_live_racing_client import DemoLiveRacingClient
from app.lib.clients.live_abstract import AbstractLiveRacingClient
from app.lib.crawlers.live_racing import LiveRacingCrawler, LiveRacingCrawlerException
from app.lib.schemas.live_racing import (
    RacePoolTotals,
    StarterDetails,
    TrackWithRaceDetails,
)
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
from app.raceday.processor_logger import RaceDayProcessorLogger
from app.raceday.processor_result import ProcessOnceResult
from app.raceday.race_canonical import LiveRaceEntryCanonical, LiveTrackBasicCanonical

logger = logging.getLogger(__name__)


class RaceWatcher(BaseModel):
    race_id: int
    race_md5: str
    post_time: datetime
    next_check_time: datetime

    def __repr__(self):
        """String repr of RaceWatcher."""
        return "<RaceWatcher(race_id=%s, post_time=%s, next_check_time=%s)>" % (
            self.race_id,
            self.post_time,
            self.next_check_time,
        )

    @classmethod
    def from_race(cls, race: Race, nct: datetime) -> "RaceWatcher":
        return cls(
            race_id=race.id,
            race_md5=race.md5_hash().hexdigest(),
            post_time=race.post_time,
            next_check_time=nct,
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

        # If nct would be outside of lookahead range, return the lookahed_end as nct
        if (
            watcher.post_time - time_context.refresh_interval
            > time_context.lookahead_end
        ):
            return time_context.lookahead_end
        # If within 5 minutes, refresh every 1 minute
        elif watcher.post_time - (time_context.now + time_context.refresh_interval) <= timedelta(minutes=5):
            return time_context.now + timedelta(minutes=1)
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
        max_sleep_secs: float = float(settings.MAX_SLEEP_TIME_SECS),
        max_bets_per_race: int = 1000,
        resilient: bool = True,
        live_racing_client: AbstractLiveRacingClient = DemoLiveRacingClient(),
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

        # Map of race md5 -> RaceWatcher
        self.watching_races: Dict[str, RaceWatcher] = {}

        self.live_race_client: AbstractLiveRacingClient = live_racing_client
        self.live_race_crawler = LiveRacingCrawler(self.live_race_client)
        self.bet_tagger = BetTagger(self.db)
        self.proc_logger = RaceDayProcessorLogger(self.db)

        self.race_predictor = RacePredictor()

    def blocking_start(self) -> None:
        """Starts processing races for the configured time context.
           Blocks the current thread.
        """
        logger.debug(
            f"Starting RaceDayProcessor for "
            f"{self.lookahead_base} -> {self.lookahead_limit}"
        )

        while True:
            time_context = self._active_time_context()

            try:
                proc_result = self.process_once(time_context)
            except RaceDayProcessorException as e:
                logger.exception(
                    "process_once() encountered an error (%s).", e, stack_info=True
                )
                self._log_complete(
                    time_context,
                    [],
                    [],
                    datetime.now(timezone.utc) + timedelta(seconds=self.max_sleep_secs),
                    False,
                )
                self._log_and_sleep(self.max_sleep_secs)
                continue

            # Sleep for either the max_sleep time or the soonest nct,
            # whichever is smallest
            sleep_time = min(self.max_sleep_secs, proc_result.next_check_secs)

            if sleep_time < 0:
                logger.error(
                    "Something went wrong - sleep_time is negative (%d)", sleep_time
                )
                sleep_time = self.max_sleep_secs

            self._log_complete(
                time_context,
                proc_result.races,
                proc_result.bets,
                datetime.now(timezone.utc) + timedelta(seconds=sleep_time),
                True,
            )
            self._log_and_sleep(sleep_time)

    def process_once(self, time_context: TimeContext) -> ProcessOnceResult:
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

        result_bets: List[Bet] = []
        result_races: List[Race] = []
        result_ncs: float = 0

        try:
            self._ingest_races_shallow(time_context)
        except LiveRacingCrawlerException:
            raise FailedRaceListIngestException

        self._remove_expired_watchers(time_context)
        upcoming_races = self._get_races_in_time_context(time_context)
        races_to_refresh = self._get_races_to_refresh(upcoming_races, time_context)

        logger.info(f"{len(races_to_refresh)} races to refresh...")

        for race in races_to_refresh:
            logger.debug("Refreshing race entries for %s", race)

            try:
                self._ingest_race_entries(race)
            except LiveRacingCrawlerException:
                logger.exception(
                    "Failed to ingest race entries for %s", race, stack_info=True
                )

                self._del_watcher(race)

                if not self.resilient:
                    raise FailedRaceEntryIngestException

                continue

            use_pool_totals = False

            try:
                if race.current_race:
                    logger.debug("Refreshing pool totals for %s", race)
                    self._ingest_race_pool_totals(race)
                    use_pool_totals = True
            except LiveRacingCrawlerException:
                logger.exception(
                    "Failed to ingest race pool totals for %s", race, stack_info=True
                )

            result_races.append(race)

            self._update_watcher(race, time_context)

            logger.debug("Regenerating predictions for race %s", race)
            self._refresh_race_predictions(race)

            logger.debug("Regenerating bets for race %s", race)
            created_bets = self._refresh_race_bets(
                race, use_pool_totals=use_pool_totals
            )
            result_bets.extend(created_bets)

        min_nct = self._get_min_watcher_nct()
        result_ncs = (min_nct - time_context.now).total_seconds()

        return ProcessOnceResult(
            next_check_secs=result_ncs, races=result_races, bets=result_bets
        )

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
            new_race_hash = race.md5_hash().hexdigest()

            # If this proc should not watch the race, do nothing.
            # This is in consideration of the fact that multiple rdprocs
            # could be running on different time ranges, they shouldn't
            # interfere with eachother's races (other than shallow updates).
            if not self._should_watch_race(race, time_context):
                self._del_watcher(race)
                continue

            maybe_existing_race = (
                self.db.query(Race).filter(Race.race_md5_hex == new_race_hash).first()
            )

            if not maybe_existing_race:
                self.db.add(race)
                self.db.commit()

                self._add_watcher(race, time_context)

                continue

            existing_race: Race = maybe_existing_race

            # If the race already exists in the db, do a shallow update w/
            # the new data.
            existing_race.update_shallow(race)
            self.db.commit()

            self._update_watcher(existing_race, time_context, refresh_nct=False)

    def _remove_expired_watchers(self, time_context: TimeContext) -> None:
        """
            Remove all watchers from watching_races where
            the next_check_time() is outside the time_context.
        """
        for (hash, watcher) in self.watching_races.copy().items():
            nct = self.next_check_gen.get_next_check_time(watcher, time_context)

            race_id = self.watching_races[hash].race_id

            if nct is not None:
                continue

            del self.watching_races[hash]

            existing_race_bets = (
                self.db.query(Bet).filter(Bet.race.has(Race.id == race_id)).all()
            )

            for bet in existing_race_bets:
                self.db.delete(bet)

        self.db.commit()

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
            race_hash = race.md5_hash().hexdigest()

            if race_hash in self.watching_races:
                watcher = self.watching_races[race_hash]

                diff: timedelta = (race.post_time - time_context.now)

                if diff <= timedelta(minutes=5) and not (
                    watcher.next_check_time <= time_context.now
                ):
                    logger.error(
                        "Should refresh %s - (%s to posttime) but nct is %s",
                        race,
                        diff,
                        watcher.next_check_time,
                    )

                if watcher.next_check_time <= time_context.now:
                    races_to_refresh.append(race)

        return races_to_refresh

    def _refresh_race_bets(
        self, race: Race, use_pool_totals: bool = False
    ) -> List[Bet]:
        """Regenerate bets for the given race."""
        existing_race_bets: List[Bet] = (
            self.db.query(Bet).filter(Bet.race.has(Race.id == race.id)).all()
        )

        # Map of bet hash -> bet
        bet_map: Dict[str, Bet] = {}

        for bet in existing_race_bets:
            bet_hash = bet.md5_hash().hexdigest()
            bet_map[bet_hash] = bet

            if bet.parent:
                parent_hash = bet.parent.md5_hash().hexdigest()
                bet_map[parent_hash] = bet.parent

            for sub_bet in bet.sub_bets:
                bet_map[sub_bet.md5_hash().hexdigest()] = sub_bet

        bet_gen = BetGen(race=race, use_pool_totals=use_pool_totals)
        bets = bet_gen.all_bets()
        result_bets: List[Bet] = []

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

            result_bets.append(bet_db)

        logger.debug("Saving generated bets %s", result_bets)

        new_bets: List[Bet] = []
        updates_seen = set()

        for bet in result_bets:
            bet_hash = bet.md5_hash().hexdigest()

            if bet_hash in bet_map:
                make_transient(bet)
                bet_map[bet_hash].update_shallow(bet)
                updates_seen.add(bet_hash)
            else:
                new_bets.append(bet)

        hashes_to_delete = set(bet_map.keys()).difference(updates_seen)

        for hash in hashes_to_delete:
            self.db.delete(bet_map[hash])

        self.db.commit()

        if len(new_bets):
            self.db.add_all(new_bets)

        self.db.commit()

        return result_bets

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
            # TODO: improve on punting problems for 500 weeks
            max_dt = datetime.now(timezone.utc) + timedelta(weeks=500)
            return max_dt.astimezone(tz=timezone.utc)

        return min(ncts)

    def _add_watcher(self, race: Race, time_context: TimeContext) -> None:
        """
            Creates a new RaceWatcher for the given race, using the given time_context
            as the basis for the next_check_time. Assumes that _should_watch_race()
            is true at this point, and that since there was previously no watcher,
            next_check_time should be now.
        """
        race_hash = race.md5_hash().hexdigest()
        self.watching_races[race_hash] = RaceWatcher.from_race(race, time_context.now)

    def _del_watcher(self, race: Race) -> None:
        """Removes a watcher for the given race, if one exists."""
        race_hash = race.md5_hash().hexdigest()

        if race_hash in self.watching_races:
            del self.watching_races[race_hash]

    def _update_watcher(
        self, race: Race, time_context: TimeContext, refresh_nct: bool = True
    ) -> None:
        """
            Updates watching_races from the given race, or deletes it 
            if next_check_time() falls outside time_context.
        """
        race_hash = race.md5_hash().hexdigest()
        watcher = self.watching_races[race_hash]

        if watcher is None:
            logger.error("Called _update_watcher() when none exists for race %s", race)
            return None

        if refresh_nct and watcher.next_check_time <= time_context.now:
            nct = self.next_check_gen.get_next_check_time(watcher, time_context)
        else:
            nct = watcher.next_check_time

        if nct is None:
            logger.error()
            del self.watching_races[race_hash]
            return None

        updated_watcher = watcher.from_race(race, nct)

        self.watching_races[race_hash] = updated_watcher

    def _ingest_race_entries(self, race: Race) -> None:
        """Refresh the list of entries for the given race."""
        race_entries: List[StarterDetails] = self.live_race_crawler.get_race_entries(
            race.track_code, race.race_number, race.race_type
        )
        entries_canon: List[RaceEntry] = [
            LiveRaceEntryCanonical(entry).convert() for entry in race_entries
        ]

        # If this is the first time the race has been pulled,
        # there will be no existing entries.
        if len(race.entries) < 1:
            race.entries = entries_canon
            self.db.commit()
            return

        existing_entries = {}
        new_entries = {}

        for entry in race.entries:
            existing_entries[entry.program_no] = entry

        for entry in entries_canon:
            new_entries[entry.program_no] = entry

        if len(set(existing_entries.keys()).difference(set(new_entries.keys()))):
            race.entries = entries_canon
            self.db.commit()
            return

        for (program_no, entry) in existing_entries.items():
            entry.update_shallow(new_entries[program_no])

        self.db.commit()

    def _ingest_race_pool_totals(self, race: Race) -> RacePoolTotals:
        """Refresh the race pool totals for the given race."""
        pool_totals = self.live_race_crawler.get_race_pool_totals(
            race.track_code, race.race_number, race.race_type
        )

        race.win_pool_total = pool_totals.win_total
        race.place_pool_total = pool_totals.place_total
        race.show_pool_total = pool_totals.show_total

        for entry in race.entries:
            entry_totals = pool_totals.entries_to_pools_map[entry.program_no]
            entry.win_pool_total = entry_totals.win_total
            entry.place_pool_total = entry_totals.place_total
            entry.show_pool_total = entry_totals.show_total

        self.db.add(race)
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

    def _log_and_sleep(self, sleep_time: float) -> None:
        """Log the time to be slept, then sleep."""
        logger.info("Sleeping %d seconds.", sleep_time)
        sleep(sleep_time)

    def _log_complete(
        self,
        time_context: TimeContext,
        races: List[Race],
        bets: List[Bet],
        next_check_time: datetime,
        success: bool,
    ):
        self.proc_logger.log(
            lookahead_start=time_context.lookahead_start,
            lookahead_end=time_context.lookahead_end,
            races=races,
            bets=bets,
            next_check_time=next_check_time,
            success=success,
        )
