import logging
from typing import List

import sqlalchemy

from app.db.session import SessionLocal
from app.lib_private.clients.live_racing import LiveRacingClient
from app.lib.crawlers.live_racing import LiveRacingCrawler
from app.lib.schemas.live_racing import TrackWithRaceAndStarterDetails
from app.models.race import Race
from app.models.race_entry import RaceEntry

logger = logging.getLogger(__name__)


class IngestRacesTask:
    def __init__(self) -> None:
        self.db = SessionLocal()

    def clear_current_race_data(self):
        stmts = [
            sqlalchemy.delete(RaceEntry).execution_options(synchronize_session="fetch"),
            sqlalchemy.delete(Race).execution_options(synchronize_session="fetch"),
        ]

        for stmt in stmts:
            self.db.execute(stmt)

        self.db.commit()

    def populate_race_data(self, race_data: List[TrackWithRaceAndStarterDetails]):
        for track in race_data:
            races = Race.create_races_from_track_details(track)

            for race in races:
                print("adding", race)
                self.db.add(race)

        self.db.commit()

    def run(self):
        client = LiveRacingClient()
        crawler = LiveRacingCrawler(client)

        latest_race_data = crawler.get_all_track_races()

        self.clear_current_race_data()

        self.populate_race_data(latest_race_data)
