import logging
from datetime import date
from typing import Generator, List

from app.lib.clients.historical_abstract import (
    AbstractHistoricalRacingClient,
    AbstractHistoricalRacingClientException,
)

logger = logging.getLogger(__name__)


class HistoricalRacingCrawlerException(Exception):
    pass


def create_default_err_handler() -> Generator:
    def default_err_handler() -> Generator:
        while True:
            try:
                yield
            except Exception as e:
                logger.exception(e, stack_info=True)

    err_handler = default_err_handler()
    err_handler.send(None)  # Initialize the handler generator

    return err_handler


class HistoricalRacingCrawler:
    def __init__(self, client: AbstractHistoricalRacingClient) -> None:
        self.client = client

    def crawl_date(
        self,
        file_path: str,
        track_codes: List[str],
        tdate: date,
        *,
        err_handler: Generator = create_default_err_handler(),
    ) -> Generator:
        for track_code in track_codes:
            file_name = f"{track_code.upper()}-{tdate.isoformat()}-A.pdf"

            try:
                self.client.download_chart_to_file(
                    file_path, file_name, track_code, tdate, race_no="A"
                )
            except AbstractHistoricalRacingClientException as e:
                err_handler.throw(e, "Failed downloading file %s" % file_name)
                continue

            yield file_name
