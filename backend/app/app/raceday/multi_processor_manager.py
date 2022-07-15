import concurrent.futures
import logging
from time import sleep
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.race import Race
from app.raceday.processor import RaceDayProcessor

logger = logging.getLogger(__name__)


class RaceDayProcessorManager:
    def __init__(self, procs: List[RaceDayProcessor]) -> None:
        self.procs = procs

    def run_processor(self, proc: RaceDayProcessor) -> None:
        logger.debug("Starting proc")
        try:
            proc.blocking_start()
        except Exception as e:
            logger.exception(
                "Uncaught exception in processor thread: %s", e, stack_info=True
            )

    def clear_races(self) -> None:
        all_races: List[Race] = self.db.query(Race).all()

        logger.info("Cleaning up %d races", len(all_races))

        for race in all_races:
            self.db.delete(race)

        self.db.commit()

    def run_db_sweeper(self, procs: List[RaceDayProcessor]) -> None:
        while True:
            logger.info("Running cleanup...")

            query = self.db.query(Race)

            for proc in procs:
                time_context = proc._active_time_context()
                query = query.filter(
                    or_(
                        Race.post_time
                        < (
                            time_context.lookahead_start - time_context.refresh_interval
                        ),
                        Race.post_time
                        > (time_context.lookahead_end + time_context.refresh_interval),
                    )
                )

            races: List[Race] = query.all()

            logger.info("Deleting %d orphaned races", len(races))

            for race in races:
                self.db.delete(race)

            self.db.commit()

            sleep(30)

    def blocking_start(self) -> None:
        self.db: Session = SessionLocal()
        self.clear_races()

        logger.info("Starting %d procs", len(self.procs))

        proc_futures = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.procs) + 1
        ) as executor:
            executor.submit(self.run_db_sweeper, self.procs.copy())
            proc_futures.extend(
                [executor.submit(self.run_processor, proc) for proc in self.procs]
            )
