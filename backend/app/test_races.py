from app.lib_private.clients.live_racing import LiveRacingClient
from app.lib.crawlers.live_racing import LiveRacingCrawler

import logging
from app.models.race import Race
from app.raceday.multi_processor_manager import RaceDayProcessorManager
# from app.tasks.create_bets import CreateBetsTask

# from app.tasks.ingest_races import IngestRacesTask

from app.raceday.processor import RaceDayProcessor
from app.db.session import SessionLocal
from datetime import timedelta

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# rdproc = RaceDayProcessor(
#     SessionLocal(),
#     lookahead_base=timedelta(days=0, hours=0, minutes=5),
#     lookahead_limit=timedelta(days=0, minutes=40),
#     max_bets_per_race=10,
#     race_refresh_interval=timedelta(days=0, minutes=5),
#     live_racing_client=LiveRacingClient(),
# )

demordproc = RaceDayProcessor(
    SessionLocal(),
    lookahead_base=timedelta(days=0, hours=0, minutes=0, seconds=10),
    lookahead_limit=timedelta(days=0, minutes=15),
    max_bets_per_race=10,
    race_refresh_interval=timedelta(days=0, minutes=5),
)

proc_manager = RaceDayProcessorManager([demordproc])
