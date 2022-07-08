import random
from datetime import date
from typing import List

from app.lib.clients.live_abstract import AbstractLiveRacingClient
from app.lib.schemas.live_racing import StarterDetails, TrackWithRaceDetails
from app.tests.utils.race_data import (
    create_starters_n,
    create_track_with_race_details_n,
)


class DemoLiveRacingClient(AbstractLiveRacingClient):
    def __init__(self) -> None:
        super().__init__()

    def get_race_entries(
        self, track_code: str, race_no: int, type: str = "Thoroughbred"
    ) -> List[StarterDetails]:
        return create_starters_n(random.randint(5, 15))

    def get_races_today(self) -> List[TrackWithRaceDetails]:
        return create_track_with_race_details_n(random.randint(20, 50))

    def get_races_by_date(self, tdate: date) -> List[TrackWithRaceDetails]:
        return create_track_with_race_details_n(random.randint(20, 50))
