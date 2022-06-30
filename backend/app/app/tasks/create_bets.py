import logging
from typing import List

from app.db.session import SessionLocal
from app.models.race import Race
from app.raceday.bet_strategy.analyzer import BetAnalyzer
from app.raceday.bet_strategy.bet_strategies import BetWeightConfig, CustomBetStrategy
from app.raceday.bet_strategy.generator import BetGen

logger = logging.getLogger(__name__)


class CreateBetsTask:
    def __init__(self) -> None:
        self.db = SessionLocal()
        self.strategy = CustomBetStrategy(
            BetWeightConfig(book_odds=2, cost_return_avg=2, cost_return_max=1),
            min_outlay=2,
            max_results=10,
        )

    def run(self):
        races: List[Race] = self.db.query(Race).all()

        for race in races:
            bet_gen = BetGen(race, strategy=self.strategy)
            bet_an = BetAnalyzer(bet_gen, strategy=self.strategy)

            free_bets = bet_an.free_bets()
            custom_bets = bet_an.custom_bets()

            all_bets = free_bets + custom_bets

            for bet in all_bets:
                self.db.add(bet.to_bet_db())

            self.db.commit()
