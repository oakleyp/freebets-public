from itertools import combinations
from typing import List
import logging

from app.models.race import Race
from app.models.race_entry import RaceEntry

from .bet_strategies import (
    AvgCostRewardSortStrategy,
    BetStrategy,
    BetTypeImpl,
    DrZPlaceBet,
    DrZShowBet,
    FlatBetOutlayStrategy,
    WinAllArbBet,
    WinBoxArbBet,
    DrZPlaceShowArbBet
)

DefaultBetStrategy = BetStrategy(
    outlay_strategy=FlatBetOutlayStrategy(), sort_strategy=AvgCostRewardSortStrategy(),
)

logger = logging.getLogger(__name__)


class BetGen:
    def __init__(
        self, *, race: Race, strategy: BetStrategy = DefaultBetStrategy, use_pool_totals: bool = False
    ) -> None:
        self.race = race
        self.strategy = strategy
        self.use_pool_totals = use_pool_totals

    def active_entries(self) -> List[RaceEntry]:
        return [entry for entry in self.race.entries if not entry.scratched]

    def all_bets(self) -> List[BetTypeImpl]:
        # There shouldn't be a race with all scratches,
        # but that's not the generator's concern
        if len(self.active_entries()) < 1:
            return []

        return self.arbitrage_bets()

    def arbitrage_bets(self) -> List[BetTypeImpl]:
        result = [
            WinAllArbBet(
                race=self.race, entries=self.active_entries(), strategy=self.strategy
            ),
        ]

        # result.extend(self.win_box_bet_gen())
        if self.use_pool_totals:
            result.extend(self.dr_z_bets())

        return self.strategy.sort_strategy.sort(result)

    def dr_z_bets(self) -> List[BetTypeImpl]:
        result: List[BetTypeImpl] = []

        # Generate Arb. bets
        ps_arb_bet = DrZPlaceShowArbBet(race=self.race, entries=self.active_entries(), selection=self.active_entries(), strategy=self.strategy)

        if len(ps_arb_bet.bets) > 0:
            result.append(ps_arb_bet)

        # Generate individual place/show bets, and append if expected value > limit
        place_bets: List[BetTypeImpl] = []
        show_bets: List[BetTypeImpl] = []

        for entry in self.active_entries():
            place_bet = DrZPlaceBet(race=self.race, entries=self.active_entries(), selection=[entry], strategy=self.strategy)
            show_bet = DrZShowBet(race=self.race, entries=self.active_entries(), selection=[entry], strategy=self.strategy)

            # Use Dr. Z recommended value limits (could vary by track/race)
            if place_bet.expected_place_val_per_dollar() > 1.18 and place_bet.effective_proba() > (1 / 8):
                place_bets.append(place_bet)

            if show_bet.expected_show_val_per_dollar() > 1.18 and show_bet.effective_proba() > (1 / 8):
                show_bets.append(show_bet)

        result.extend(place_bets + show_bets)

        return result

    def win_box_bet_gen(
        self, min_depth: int = 2, max_depth: int = 8
    ) -> List[BetTypeImpl]:
        """
            Generate all possible bets for a boxed win bet.

            The min_depth and max_depth constrain the min and max number of entries that boxed
            bet generation will scale between, e.g. with a min_depth of 2, and max_depth of 8,
            this will generate all possible 2-entry bets up to all possible
            8-entry bets, stopping early when the depth meets the number of entries.
        """
        if min_depth < 1:
            raise ValueError(
                "Invalid min/max depth (%d/%d) given for race %s with %d entries",
                min_depth,
                max_depth,
                self.race,
                len(self.race.entries),
            )

        bets = []
        gen_ct = min_depth

        while gen_ct <= len(self.race.entries) and gen_ct <= max_depth:
            combs = combinations(self.race.entries, gen_ct)
            gen_ct += 1

            for comb in combs:
                bets.append(
                    WinBoxArbBet(
                        race=self.race,
                        entries=self.active_entries(),
                        selection=comb,
                        strategy=self.strategy,
                    )
                )

        return bets
