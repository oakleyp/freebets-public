from itertools import combinations
from typing import List

from app.models.race import Race

from .bet_strategies import (
    AvgCostRewardSortStrategy,
    BetStrategy,
    FlatBetOutlayStrategy,
    WinAllArbBet,
    WinBoxArbBet,
)

DefaultBetStrategy = BetStrategy(
    outlay_strategy=FlatBetOutlayStrategy(), sort_strategy=AvgCostRewardSortStrategy(),
)


class BetGen:
    def __init__(
        self, *, race: Race, strategy: BetStrategy = DefaultBetStrategy,
    ) -> None:
        self.race = race
        self.strategy = strategy

    def active_entries(self):
        return [entry for entry in self.race.entries if not entry.scratched]

    def all_bets(self):
        # There shouldn't be a race with all scratches,
        # but that's not the generator's concern
        if len(self.active_entries()) < 1:
            return []

        return self.arbitrage_bets()

    def arbitrage_bets(self):
        result = [
            WinAllArbBet(
                race=self.race, entries=self.active_entries(), strategy=self.strategy
            ),
        ]

        # result.extend(self.win_box_bet_gen())

        return result

    def win_box_bet_gen(
        self, min_depth: int = 2, max_depth: int = 8
    ) -> List[WinBoxArbBet]:
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

        return self.strategy.sort_strategy.sort(bets)
