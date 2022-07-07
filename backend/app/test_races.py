from app.lib_private.clients.live_racing import LiveRacingClient
from app.lib.crawlers.live_racing import LiveRacingCrawler

import logging
from app.models.race import Race
# from app.tasks.create_bets import CreateBetsTask

# from app.tasks.ingest_races import IngestRacesTask

from app.raceday.processor import RaceDayProcessor
from app.db.session import SessionLocal
from datetime import timedelta

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

rdproc = RaceDayProcessor(
    SessionLocal(),
    lookahead_base=timedelta(days=0, hours=0, minutes=5),
    lookahead_limit=timedelta(days=0, minutes=40),
    max_bets_per_race=10,
    race_refresh_interval=timedelta(days=0, minutes=5)
)
