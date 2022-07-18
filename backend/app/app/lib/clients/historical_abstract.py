from abc import ABC, abstractmethod
from datetime import date


class AbstractHistoricalRacingClientException(Exception):
    pass


class AbstractHistoricalRacingClient(ABC):
    """Client used to pull historical racing data."""

    @abstractmethod
    def download_chart_to_file(
        self,
        file_path: str,
        file_name: str,
        track_code: str,
        tdate: date,
        race_no: str = "A",
    ) -> None:
        raise NotImplementedError(
            "download_chart_to_file() not implemented for %s" % self.__class__.__name__
        )
