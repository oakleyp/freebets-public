from abc import ABC, abstractmethod
from datetime import date
from typing import List

from app.lib.schemas.live_racing import StarterDetails, TrackWithRaceDetails

class AbstractLiveRacingClientException(Exception):
    pass

class AbstractLiveRacingClient(ABC):
    """Client used to pull live racing data."""
    @abstractmethod
    def get_race_entries(
        self, track_code: str, race_no: int, type: str = "Thoroughbred"
    ) -> List[StarterDetails]:
        """Get all entries for a given race no. and track code."""
        raise NotImplementedError("get_race_entries() not implemented for %s" % self.__class__.__name__)

    @abstractmethod
    def get_races_today(self) -> List[TrackWithRaceDetails]:
        """Get all today's listed races."""
        raise NotImplementedError("get_races_today() not implemented for %s" % self.__class__.__name__)

    @abstractmethod
    def get_races_by_date(self, tdate: date) -> List[TrackWithRaceDetails]:
        """Get all races for a given date."""
        raise NotImplementedError("get_races_by_date() not implemented for %s" % self.__class__.__name__)
