import asyncio
import logging
from datetime import date, timedelta
from typing import Dict, Generator, List, Tuple

from pydantic import BaseModel

from app.core.config import settings
from app.lib.clients.historical_abstract import AbstractHistoricalRacingClient
from app.lib_private.clients.historical_racing import HistoricalRacingClient
from app.lib.crawlers.historical_racing import HistoricalRacingCrawler, HistoricalRacingCrawlerException
from app.rabbitmq.pika_client import PikaClient, RmqMessage

logger = logging.getLogger(__name__)


class TrackDataDescriptor(BaseModel):
    track_name: str
    track_code: str
    date_ranges: List[Tuple[date, date]]

    def __repr__(self):
        return f"<TrackDataDescriptor(track_name={self.track_name}, track_code={self.track_code})>"


class DateWiseTrackList(BaseModel):
    tdate: date
    track_list: List[TrackDataDescriptor]

    def __repr__(self):
        return f"<DateWiseTrackList(tdate={self.tdate}, track_list={self.track_list})>"


class RaceResultSearchConfig(BaseModel):
    track_list: List[TrackDataDescriptor]

    def __repr__(self):
        return f"<RaceResultSearchConfig({self.track_list})>"

    def orient_date_wise(self) -> List[DateWiseTrackList]:
        """
            Orient track_lists [A, B, C] to DateWiseTrackList [[A, B], [A, B], [A, B, C]]
            such that each DateWiseTrackList contains the complete track_list for a single day,
            where originally each track_list item contains a range of dates.
        """
        result_map: Dict[date, DateWiseTrackList] = {}

        for track in self.track_list:
            for date_rg in track.date_ranges:
                start, end = date_rg

                if end < start:
                    continue

                delta = end - start

                for i in range(delta.days + 1):
                    day = start + timedelta(days=i)

                    if day in result_map:
                        result_map[day].track_list.append(track)
                    else:
                        result_map[day] = DateWiseTrackList(
                            tdate=day, track_list=[track]
                        )

        return list(result_map.values())


class RaceResultsProcessor:
    """
    Downloads historical race results and sends the resulting file path out
    to rabbitmq to be parsed and uploaded to clickhouse by the parser service.
    """
    def __init__(
        self,
        start_date: date,
        end_date: date,
        rr_search_config: RaceResultSearchConfig,
        *,
        download_path: str = "pdf",
    ) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.rr_search_config = rr_search_config
        self.download_path = download_path

        self.hist_client: AbstractHistoricalRacingClient = HistoricalRacingClient()
        self.hist_crawler = HistoricalRacingCrawler(self.hist_client)

        self.rmq_client = PikaClient()
        self.download_exchange = settings.RMQ_CRAWLER_DOWNLOAD_EXCHANGE
        self.event_loop = asyncio.get_event_loop()

    async def send_queue_ingest(self, file_name: str) -> None:
        await self.rmq_client.send_msg(
            self.download_exchange,
            "",
            RmqMessage(
                message_type="IngestSignal",
                body={"file": self.download_path + "/" + file_name,},
            ),
        )

    def get_datewise_track_lists(self) -> List[DateWiseTrackList]:
        return self.rr_search_config.orient_date_wise()

    def read_and_handle_errors(self) -> Generator:
        while True:
            try:
                yield
            except HistoricalRacingCrawlerException:
                logger.exception("Failed ingest for item", stack_info=True)
            except Exception as e:
                raise e

    def blocking_start(self) -> None:
        dw_track_lists = self.get_datewise_track_lists()

        for dw_track_list in dw_track_lists:
            if (
                dw_track_list.tdate < self.start_date
                or dw_track_list.tdate > self.end_date
            ):
                continue

            track_codes = [track.track_code for track in dw_track_list.track_list]

            err_handler = self.read_and_handle_errors()
            err_handler.send(None)  # Initialize the error handler generator

            for file_name in self.hist_crawler.crawl_date(
                self.download_path,
                track_codes,
                dw_track_list.tdate,
                err_handler=err_handler,
            ):
                coroutine = self.send_queue_ingest(file_name)
                self.event_loop.run_until_complete(coroutine)
