import random
from datetime import date, datetime, timezone
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

        self.create_races_for_day()

    def create_races_for_day(self) -> None:
        track_races = create_track_with_race_details_n(
            random.randint(20, 50),
            race_details_args={"adjacent_increment": "hours"},
            races_per_track=15,
        )

        for track_race in track_races:
            created_race_details = {}

            current_race_i = random.randint(0, len(track_race.races) - 1)

            for (i, race) in enumerate(track_race.races):
                race_override = create_race_and_starter_details(race.raceNumber)
                created_race_details[str(race.raceNumber)] = race_override
                race.raceDate = race_override.raceDate
                race.postTime = race_override.postTime
                race.postTimeStamp = race_override.postTimeStamp

                # This creates multiple active races per track, but that's not an issue... yet
                race.currentRace = i == current_race_i

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

    def get_races_today(self) -> List[TrackWithRaceDetails]:
        if self.last_generated.date() < datetime.now(timezone.utc).date():
            self.create_races_for_day()

        return self.track_races

    def get_races_by_date(self, tdate: date) -> List[TrackWithRaceDetails]:
        if tdate == datetime.now(timezone.utc).date():
            return self.get_races_today()

        return create_track_with_race_details_n(random.randint(20, 50))

    def get_race_pool_totals(
        self, track_code: str, race_no: int, type: str = "Thoroughbred"
    ) -> RacePoolTotals:
        return create_race_pool_totals(self.race_state[track_code][str(race_no)])
