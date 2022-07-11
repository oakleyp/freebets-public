import random
from datetime import date
from typing import Dict, List, Optional

from app.lib.clients.live_abstract import AbstractLiveRacingClient
from app.lib.schemas.live_racing import RacePoolTotals, RaceWithStarterDetails, StarterDetails, TrackWithRaceAndStarterDetails, TrackWithRaceDetails
from app.tests.utils.race_data import (
    create_starters_n,
    create_track_with_race_details_n,
    create_race_pool_totals,
)


class DemoLiveRacingClient(AbstractLiveRacingClient):
    def __init__(self) -> None:
        super().__init__()

        # Map track_code -> race_no -> entries
        self.race_state: Dict[str, Dict[str, List[StarterDetails]]] = {}

    def _add_to_race_state(self, track_code: str, race_no: int, entries: List[StarterDetails]):
        current = self.race_state.get(track_code)

        if not current:
            self.race_state[track_code] = {}

        self.race_state[track_code][str(race_no)] = entries

    def get_race_entries(
        self, track_code: str, race_no: int, type: str = "Thoroughbred"
    ) -> List[StarterDetails]:
        entries = create_starters_n(random.randint(5, 15))

        self._add_to_race_state(track_code, race_no, entries)

        return entries

    def get_races_today(self) -> List[TrackWithRaceDetails]:
        self.race_state = {}

        return create_track_with_race_details_n(random.randint(20, 50))

    def get_races_by_date(self, tdate: date) -> List[TrackWithRaceDetails]:
        return create_track_with_race_details_n(random.randint(20, 50))

    def get_race_pool_totals(self, track_code: str, race_no: str, type: str = "Thoroughbred") -> RacePoolTotals:
        return create_race_pool_totals(self.race_state[track_code][str(race_no)])
