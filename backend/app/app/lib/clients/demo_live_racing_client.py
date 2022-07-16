import random
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List

from app.lib.clients.live_abstract import (
    AbstractLiveRacingClient,
    AbstractLiveRacingClientException,
)
from app.lib.schemas.live_racing import (
    RacePoolTotals,
    RaceWithStarterDetails,
    StarterDetails,
    TrackWithRaceDetails,
)
from app.tests.utils.race_data import (
    create_race_and_starter_details,
    create_race_pool_totals,
    create_track_with_race_details_n,
)


class DemoLiveRacingClientException(AbstractLiveRacingClientException):
    pass


class DemoLiveRacingClient(AbstractLiveRacingClient):
    def __init__(self) -> None:
        super().__init__()

        # Map track_code -> race_no -> entries
        self.race_state: Dict[str, Dict[str, RaceWithStarterDetails]] = {}
        self.track_races: List[TrackWithRaceDetails] = []
        self.last_generated = datetime.now(timezone.utc)
        self.pool_totals: Dict[str, Dict[str, RacePoolTotals]] = {}

        self.create_races_for_day()

    def create_races_for_day(self) -> None:
        self.race_state = {}
        self.track_races = []

        track_races = create_track_with_race_details_n(
            random.randint(15, 20),
            race_details_args={"adjacent_increment": "minutes"},
            races_per_track=5,
        )

        for track_race in track_races:
            created_race_details = {}

            self.pool_totals[track_race.brisCode] = {}

            for (i, race) in enumerate(track_race.races):
                race_override = create_race_and_starter_details(race.raceNumber)
                created_race_details[str(race.raceNumber)] = race_override
                race.raceDate = race_override.raceDate
                race.postTime = race_override.postTime
                race.postTimeStamp = race_override.postTimeStamp

                if i == 0:
                    race.currentRace = True

                self.pool_totals[track_race.brisCode][
                    str(race.raceNumber)
                ] = create_race_pool_totals(race_override)

            self.race_state[track_race.brisCode] = created_race_details

        self.track_races = track_races
        self.last_generated = datetime.now(timezone.utc)

    def get_race_entries(
        self, track_code: str, race_no: int, type: str = "Thoroughbred"
    ) -> List[StarterDetails]:

        try:
            return self.race_state[track_code][str(race_no)].starters
        except KeyError as e:
            raise DemoLiveRacingClientException(
                f"Failed to pull race entries for track {track_code} - race {race_no} - type {type}: {e}"
            )

    def _set_current_race_flags(
        self, track_races: List[TrackWithRaceDetails]
    ) -> List[TrackWithRaceDetails]:
        """Set the next race (that has not already passed) as the current race."""
        now = datetime.now(timezone.utc)

        for track_race in track_races:
            for race in sorted(track_race.races, key=lambda r: r.postTime):
                if race.postTime >= now:
                    race.currentRace = True
                    break  # continue in outer loop

        return track_races

    def get_races_today(self) -> List[TrackWithRaceDetails]:
        if datetime.now(timezone.utc) - self.last_generated > timedelta(hours=2):
            self.create_races_for_day()

        return self._set_current_race_flags(self.track_races)

    def get_races_by_date(self, tdate: date) -> List[TrackWithRaceDetails]:
        if tdate == datetime.now(timezone.utc).date():
            return self.get_races_today()

        raise NotImplementedError("This shouldn't happen in the demo.")

    def get_race_pool_totals(
        self, track_code: str, race_no: int, type: str = "Thoroughbred"
    ) -> RacePoolTotals:
        current_totals = self.pool_totals.get(track_code, {}).get(str(race_no))
        if current_totals:
            new_totals = create_race_pool_totals(
                self.race_state[track_code][str(race_no)],
                current_pool_totals=current_totals,
            )
            self.pool_totals[track_code][str(race_no)] = new_totals
            return new_totals

        new_totals = create_race_pool_totals(self.race_state[track_code][str(race_no)])

        if not self.pool_totals.get(track_code):
            self.pool_totals[track_code] = {}

        if not self.pool_totals.get(track_code).get(str(race_no)):
            self.pool_totals[track_code][str(race_no)] = new_totals

        return new_totals
