import logging
from datetime import date
from typing import List

from app.lib.clients.live_abstract import (
    AbstractLiveRacingClient,
    AbstractLiveRacingClientException,
)
from app.lib.schemas.live_racing import StarterDetails, TrackWithRaceDetails

logger = logging.getLogger(__name__)


class LiveRacingCrawlerException(Exception):
    pass


class LiveRacingCrawler:
    def __init__(self, client: AbstractLiveRacingClient) -> None:
        self.client = client

    def get_race_entries(
        self, track_code: str, race_no: int, race_type: str
    ) -> List[StarterDetails]:
        try:
            return self.client.get_race_entries(track_code, race_no, type=race_type)
        except AbstractLiveRacingClientException as e:
            logger.error(
                "Error looking up race entries for (track_code=%s, race_no=%d, race_type=%s) - %s",
                track_code,
                race_no,
                race_type,
                e,
            )
            raise LiveRacingCrawlerException(f"Failed to retrieve race entries - {e}")

    def get_all_track_races_shallow(
        self, *, track_codes: List[str] = [], target_date: date = None,
    ) -> List[TrackWithRaceDetails]:
        tdate = target_date or date.today()

        try:
            track_races_today = self.client.get_races_by_date(tdate)
        except AbstractLiveRacingClientException as e:
            logger.error("Error looking up track races for date %s - %s", tdate, e)
            raise LiveRacingCrawlerException(
                f"Failed to retrieve track races for {tdate} - {e}"
            )

        if track_codes and len(track_codes) > 0:
            track_races_today = list(
                filter(lambda track: track.brisCode in track_codes, track_races_today)
            )

        return track_races_today
