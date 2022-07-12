#!/usr/bin/env python3

from itertools import combinations, permutations
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Union

from app.models.bet import Bet
from app.models.race import Race
from app.models.race_entry import RaceEntry
from app.raceday.bet_strategy.dr_z_eq import DrZPlaceShowResult, get_best_place_show_bets_all

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BetType(Enum):
    WIN_BET = (1,)
    ALL_WIN_ARB = (2,)
    BOX_WIN_ARB = (3,)
    PLACE_BET = (4,)
    SHOW_BET = (5,)
    PLACE_SHOW_ARB = (6, )

    def to_json(self):
        return str(self)


class BetStrategyType(Enum):
    AI_WIN_BET = (1,)
    AI_ALL_WIN_ARB = (2,)
    AI_BOX_WIN_ARB = (3,)

    BOOK_WIN_BET = (4,)
    BOOK_ALL_WIN_ARB = (5,)
    BOOK_BOX_WIN_ARB = (6,)

    BOOK_DR_Z_PLACE_SHOW_ARB = (7)
    AI_DR_Z_PLACE_SHOW_ARB = (8,)

    BOOK_PLACE_BET = (9,)
    BOOK_SHOW_BET = (10,)

    def to_json(self):
        return str(self)


class BetResult:
    def __init__(
        self,
        race: Race = None,
        bet_type: BetType = None,
        bet_strategy_type: BetStrategyType = None,
        horses: List[RaceEntry] = [],
        selection: List[RaceEntry] = [],
        max_reward: Any = 0,
        avg_reward: Any = 0,
        min_reward: Any = 0,
        cost: Any = 0,
        odds: Any = 0.0,
    ) -> None:
        self.bet_type = bet_type
        self.bet_strategy_type = bet_strategy_type
        self.race = race
        self.horses = horses
        self.selection = selection
        self.max_reward = max_reward
        self.avg_reward = avg_reward
        self.min_reward = min_reward
        self.cost = cost
        self.odds = odds

    def gen_description(self) -> str:
        return (
            f"Track = {self.race.track_code}; "
            f"Bet Type = {str(self.bet_type)}; "
            f"Predicted Odds = {self.odds}; "
            f"Cost = {self.cost};"
            f"Min Reward: {self.min_reward}; "
            f"Avg Reward: {self.avg_reward}; "
            f"Max Reward: {self.max_reward}; "
        )

    def to_bet_db(self) -> Bet:
        return Bet(
            title=f"{self.race.track_code} - {str(self.bet_type)} - {self.odds}",
            description=self.gen_description(),
            predicted_odds=self.odds,
            min_reward=self.min_reward,
            max_reward=self.max_reward,
            avg_reward=self.avg_reward,
            cost=self.cost,
            bet_type=str(self.bet_type),
            bet_strategy_type=str(self.bet_strategy_type),
            race=self.race,
            active_entries=self.selection,
            inactive_entries=[
                horse for horse in self.horses if horse not in self.selection
            ],
        )


class MultiBetResult:
    def __init__(
        self,
        race: Race = None,
        bet_type: BetType = None,
        bet_results: List[BetResult] = [],
        bet_strategy_type: BetStrategyType = None,
        max_reward: Any = 0,
        avg_reward: Any = 0,
        min_reward: Any = 0,
        cost: Any = 0,
        odds: Any = 0.0,
    ) -> None:
        self.race = race
        self.bet_results = bet_results
        self.bet_type = bet_type
        self.bet_strategy_type = bet_strategy_type
        self.max_reward = max_reward
        self.avg_reward = avg_reward
        self.min_reward = min_reward
        self.cost = cost
        self.odds = odds

    def gen_description(self) -> str:
        return (
            f"Track = {self.race.track_code}; "
            f"Bet Type = {str(self.bet_type)}; "
            f"Predicted Odds = {self.odds}; "
            f"Cost = {self.cost};"
            f"Min Reward: {self.min_reward}; "
            f"Avg Reward: {self.avg_reward}; "
            f"Max Reward: {self.max_reward}; "
        )

    def to_bet_db(self) -> Bet:
        root_bet = Bet(
            title=f"(MULTI) {self.race.track_code} - {str(self.bet_type)} - {self.odds}",  # noqa E501
            description=self.gen_description(),
            predicted_odds=self.odds,
            min_reward=self.min_reward,
            max_reward=self.max_reward,
            avg_reward=self.avg_reward,
            cost=self.cost,
            bet_type=str(self.bet_type),
            bet_strategy_type=str(self.bet_strategy_type),
            race=self.race,
        )

        root_bet.sub_bets = [bet.to_bet_db() for bet in self.bet_results]

        return root_bet


class BetTypeImpl(ABC):
    def __init__(self, race: Race, horses: List[RaceEntry], selection: List[RaceEntry]):
        self.race = race
        self.horses = horses
        self.selection = selection

    def effective_proba(self) -> float:
        return 1 / self.odds()

    @abstractmethod
    def odds(self) -> float:
        raise NotImplementedError(
            "odds() not implemented for %s" % self.__class__.__name__
        )

    @abstractmethod
    def cost(self) -> float:
        raise NotImplementedError(
            "cost() not implemented for %s" % self.__class__.__name__
        )

    @abstractmethod
    def avg_reward(self) -> float:
        raise NotImplementedError(
            "avg_reward() not implemented for %s" % self.__class__.__name__
        )
    @abstractmethod
    def min_reward(self) -> float:
        raise NotImplementedError(
            "min_reward() not implemented for %s" % self.__class__.__name__
        )

    @abstractmethod
    def max_reward(self) -> float:
        raise NotImplementedError(
            "max_reward() not implemented for %s" % self.__class__.__name__
        )

    @abstractmethod
    def min_bet(self) -> float:
        raise NotImplementedError(
            "min_bet() not implemented for %s" % self.__class__.__name__
        )

    @abstractmethod
    def result(self) -> Union[BetResult, MultiBetResult]:
        raise NotImplementedError(
            "result() not implemented for %s" % self.__class__.__name__
        )


class BetOutlayStrategy(ABC):
    @abstractmethod
    def outlay(self, bet: BetTypeImpl) -> float:
        """Determine the outlay (money down) for the given bet."""
        raise NotImplementedError(
            "outlay() not implemented for %s" % self.__class__.__name__
        )


class BetSortStrategy(ABC):
    @abstractmethod
    def sort(self, bets: List[BetTypeImpl]) -> List[BetTypeImpl]:
        """Sort the given bets using a defined strategy, in order of best to worst."""
        raise NotImplementedError(
            "sort() not implemented for %s" % self.__class__.__name__
        )


class BetStrategy:
    def __init__(
        self,
        *,
        outlay_strategy: BetOutlayStrategy = None,
        sort_strategy: BetSortStrategy = None,
    ) -> None:
        self.outlay_strategy = outlay_strategy
        self.sort_strategy = sort_strategy


class FlatBetOutlayStrategy(BetOutlayStrategy):
    def __init__(self, *, outlay: float = 2) -> None:
        super().__init__()
        self._outlay = outlay

    def outlay(self, bet: BetTypeImpl) -> float:
        """Return a static outlay."""
        return self._outlay


class AvgCostRewardSortStrategy(BetSortStrategy):
    """Strategy that sorts bets in order of their cost/avg_reward ratio (best first)."""

    def sort(self, bets: List[BetTypeImpl]) -> List[BetTypeImpl]:
        return sorted(bets, key=lambda a: a.cost() / (a.avg_reward() or 1))


class WinBet(BetTypeImpl):
    def __init__(
        self,
        *,
        race: Race,
        entries: List[RaceEntry],
        selection: RaceEntry,
        strategy: BetStrategy,
    ) -> None:
        self.race = race
        self.entries = entries
        self.selection = selection
        self.strategy = strategy
        self.bet_type = BetType.WIN_BET
        self.bet_strategy_type = BetStrategyType.BOOK_WIN_BET

    def min_reward(self) -> float:
        return 0

    def avg_reward(self) -> float:
        return self.max_reward() / len(self.entries)

    def max_reward(self) -> float:
        return self.odds() * self.outlay()

    def min_bet(self) -> float:
        # TODO - may vary by track
        return 2

    def cost(self) -> float:
        return self.outlay()

    def odds(self) -> float:
        return self.selection.latest_odds() or 0

    def outlay(self) -> float:
        return self.strategy.outlay_strategy.outlay(self)

    def result(self) -> BetResult:
        return BetResult(
            race=self.race,
            bet_strategy_type=self.bet_strategy_type,
            bet_type=self.bet_type,
            horses=self.entries,
            selection=[self.selection],
            max_reward=self.max_reward(),
            min_reward=self.min_reward(),
            cost=self.cost(),
            odds=self.odds(),
        )


class AIWinBet(WinBet):
    def __init__(
        self,
        *,
        race: Race,
        entries: List[RaceEntry],
        selection: RaceEntry,
        strategy: BetStrategy,
    ) -> None:
        super().__init__(
            race=race, entries=entries, selection=selection, strategy=strategy
        )
        self.bet_strategy_type = BetStrategyType.AI_WIN_BET

    def odds(self) -> float:
        return self.selection.predicted_odds or 0


class WinAllArbBet(BetTypeImpl):
    def __init__(
        self, *, race: Race, entries: List[RaceEntry], strategy: BetStrategy,
    ) -> None:
        self.race = race
        self.entries = entries
        self.strategy = strategy
        self.bet_type = BetType.ALL_WIN_ARB
        self.bet_strategy_type = BetStrategyType.BOOK_ALL_WIN_ARB

        self.bets = [
            WinBet(
                race=self.race,
                entries=self.entries,
                selection=s,
                strategy=self.strategy,
            )
            for s in self.entries
        ]

    def min_reward(self):
        return min(b.max_reward() for b in self.bets)

    def avg_reward(self):
        # This assumes that all horses have equal chance of winning,
        # obviously need to weight by odds
        return sum(b.max_reward() for b in self.bets) / len(self.bets)

    def max_reward(self):
        return max(b.max_reward() for b in self.bets)

    def min_bet(self):
        return sum(b.min_bet() for b in self.bets)

    def cost(self):
        return sum(b.cost() for b in self.bets)

    def odds(self):
        return 1

    def result(self) -> BetResult:
        return BetResult(
            bet_type=self.bet_type,
            bet_strategy_type=self.bet_strategy_type,
            race=self.race,
            selection=self.entries,
            horses=self.entries,
            max_reward=self.max_reward(),
            avg_reward=self.avg_reward(),
            min_reward=self.min_reward(),
            cost=self.cost(),
            odds=self.odds(),
        )


class WinBoxArbBet(BetTypeImpl):
    def __init__(
        self,
        *,
        race: Race,
        entries: List[RaceEntry],
        selection: List[RaceEntry],
        strategy: BetStrategy,
    ) -> None:
        self.race: Race = race
        self.entries: List[RaceEntry] = entries
        self.strategy: BetStrategy = strategy
        self.selection: List[RaceEntry] = selection
        self.bet_type: BetType = BetType.BOX_WIN_ARB
        self.bet_strategy_type: BetStrategyType = BetStrategyType.BOOK_BOX_WIN_ARB

        self.bets = [
            WinBet(
                race=self.race,
                entries=self.entries,
                selection=s,
                strategy=self.strategy,
            )
            for s in self.selection
        ]

    def min_reward(self) -> float:
        if len(self.selection) == len(self.entries):
            return min(b.max_reward() for b in self.bets)

        return 0

    def avg_reward(self) -> float:
        return sum(b.max_reward() for b in self.bets) / len(
            self.entries
        )  # Note, avg factors in losses

    def max_reward(self) -> float:
        return max(b.max_reward() for b in self.bets)

    def min_bet(self) -> float:
        return sum(b.min_bet() for b in self.bets)

    def odds(self) -> float:
        return sum((h.latest_odds() or 0) for h in self.selection)

    def cost(self):
        # TODO: outlay based on various leg odds?
        return sum(b.cost() for b in self.bets)

    def result(self) -> MultiBetResult:
        return MultiBetResult(
            race=self.race,
            bet_type=self.bet_type,
            bet_strategy_type=self.bet_strategy_type,
            bet_results=[b.result() for b in self.bets],
            max_reward=self.max_reward(),
            avg_reward=self.avg_reward(),
            min_reward=self.min_reward(),
            cost=self.cost(),
            odds=self.odds(),
        )

def calc_place_reward(race: Race, place_horses: List[RaceEntry], selection: RaceEntry):
    total_place_pool = race.place_pool_total

    (horse_1, horse_2) = place_horses

    # Get remaining pool to be distributed by subtracting 2 place horses from net place pool
    pool_dividend = total_place_pool - (horse_1.place_pool_total + horse_2.place_pool_total)

    # 2 winners, since this is place, divide by 2
    pool_split = pool_dividend / 2

    # Divide the remaining split among the winners
    indiv_payout = pool_split / selection.place_pool_total

    # unit size 1 -> 2 for $2 bets
    indiv_payout *= 2

    return indiv_payout

def calc_place_reward_redux(race: Race, selection: RaceEntry, other_horse: RaceEntry):
    return ((race.place_pool_total - other_horse.place_pool_total) / selection.place_pool_total) - 1

def calc_avg_place_reward(race: Race):
    total: float = 0
    perms = list(permutations(race.entries, 2))
    for selection, other_horse in perms:
        total += calc_place_reward_redux(race, selection, other_horse)
    
    return total / len(perms)

def calc_show_reward(race: Race, selection: RaceEntry, other_horse: RaceEntry, third_horse: RaceEntry):
    total_show_pool = race.show_pool_total

    # Get remaining pool to be distributed by subtracting 2 place horses from net place pool
    pool_dividend = total_show_pool - (selection.show_pool_total + other_horse.show_pool_total + third_horse.show_pool_total)

    # 3 winners, since this is show, divide by 3
    pool_split = pool_dividend / 3

    # Divide the remaining split among the winners
    indiv_payout = pool_split / selection.show_pool_total

    # unit size 1 -> 2 for $2 bets
    indiv_payout *= 2

    return indiv_payout

def calc_avg_show_reward(race: Race):
    total: float = 0
    perms = list(permutations(race.entries, 3))

    for (selection, other_horse, third_horse) in perms:
        total += calc_show_reward(race, selection, other_horse, third_horse)
    
    return total / len(perms)


class PlaceBet(BetTypeImpl):
    def __init__(
        self,
        *,
        race: Race,
        entries: List[RaceEntry],
        selection: List[RaceEntry],
        strategy: BetStrategy,
    ) -> None:
        self.race: Race = race
        self.entries: List[RaceEntry] = entries
        self.strategy: BetStrategy = strategy
        self.selection: RaceEntry = selection[0]
        self.bet_type: BetType = BetType.PLACE_BET
        self.bet_strategy_type: BetStrategyType = BetStrategyType.BOOK_PLACE_BET

    def min_reward(self) -> float:
        return 0

    def avg_reward(self) -> float:
        # TODO: avg reward for pl show
        return calc_avg_place_reward(self.race) * self.effective_proba()

    def max_reward(self) -> float:
        total_place_pool = self.race.place_pool_total
        selection = self.selection

        # Make the lowest odds horse other_horse, or the next-lowest
        # if this bet is already targetting it, so the remaining pool 
        # is large as possible
        entries_worst = self.entries.copy()
        entries_worst.sort(key=lambda e: e.latest_odds(), reverse=True)
        other_horse = entries_worst[0] if not entries_worst[0].id == selection.id else entries_worst[1]

        # Get remaining pool to be distributed by subtracting 2 place horses from net place pool
        pool_dividend = total_place_pool - (other_horse.place_pool_total + selection.place_pool_total)

        # 2 winners, since this is place, divide by 2
        pool_split = pool_dividend / 2

        # Divide the remaining split among the winners
        indiv_payout = pool_split / selection.place_pool_total

        # unit size 1 -> 2 for $2 bets
        indiv_payout *= 2

        return indiv_payout + self.strategy.outlay_strategy.outlay(self)

    def min_bet(self) -> float:
        return sum(b.min_bet() for b in self.bets)

    def odds(self) -> float:
        return self.selection.latest_odds()

    def cost(self) -> float:
        return self.strategy.outlay_strategy.outlay(self)

    def result(self) -> BetResult:
        return BetResult(
            race=self.race,
            bet_type=self.bet_type,
            bet_strategy_type=self.bet_strategy_type,
            horses=self.entries,
            selection=[self.selection],
            max_reward=self.max_reward(),
            avg_reward=self.avg_reward(),
            min_reward=self.min_reward(),
            cost=self.cost(),
            odds=self.odds(),
        )


class ShowBet(BetTypeImpl):
    def __init__(
        self,
        *,
        race: Race,
        entries: List[RaceEntry],
        selection: List[RaceEntry],
        strategy: BetStrategy,
    ) -> None:
        self.race: Race = race
        self.entries: List[RaceEntry] = entries
        self.strategy: BetStrategy = strategy
        self.selection: RaceEntry = selection[0]
        self.bet_type: BetType = BetType.SHOW_BET
        self.bet_strategy_type: BetStrategyType = BetStrategyType.BOOK_SHOW_BET

    def min_reward(self) -> float:
        return 0

    def avg_reward(self) -> float:
        # TODO: avg reward for pl show
        return calc_avg_show_reward(self.race) * self.effective_proba()

    def max_reward(self) -> float:
        total_show_pool = self.race.show_pool_total
        selection = self.selection

        # Make the lowest odds horse other_horse, or the next-lowest
        # if this bet is already targetting it, so the remaining pool 
        # is large as possible
        entries_worst = self.entries.copy()
        entries_worst.sort(key=lambda e: e.latest_odds(), reverse=True)
        other_horse = entries_worst[0] if not entries_worst[0].id == selection.id else entries_worst[1]
        third_horse = entries_worst[1] if not entries_worst[0].id == selection.id else entries_worst[2]

        # Get remaining pool to be distributed by subtracting 3 show horses from net show pool
        pool_dividend = total_show_pool - (other_horse.show_pool_total + selection.show_pool_total + third_horse.show_pool_total)

        # 3 winners, since this is show, divide by 3
        pool_split = pool_dividend / 2

        # Divide the remaining split among the winners
        indiv_payout = pool_split / selection.show_pool_total

        # unit size 1 -> 2 for $2 bets
        indiv_payout *= 2

        return indiv_payout + self.strategy.outlay_strategy.outlay(self)

    def min_bet(self) -> float:
        return sum(b.min_bet() for b in self.bets)

    def odds(self) -> float:
        return self.selection.latest_odds()

    def cost(self) -> float:
        return self.strategy.outlay_strategy.outlay(self)

    def result(self) -> BetResult:
        return BetResult(
            race=self.race,
            bet_type=self.bet_type,
            bet_strategy_type=self.bet_strategy_type,
            horses=self.entries,
            selection=[self.selection],
            max_reward=self.max_reward(),
            avg_reward=self.avg_reward(),
            min_reward=self.min_reward(),
            cost=self.cost(),
            odds=self.odds(),
        )


class DrZPlaceShowArbBet(BetTypeImpl):
    def __init__(
        self,
        *,
        race: Race,
        entries: List[RaceEntry],
        selection: List[RaceEntry],
        strategy: BetStrategy,
    ) -> None:
        self.race: Race = race
        self.entries: List[RaceEntry] = entries
        self.strategy: BetStrategy = strategy
        self.selection: List[RaceEntry] = selection
        self.bet_type: BetType = BetType.PLACE_SHOW_ARB
        self.bet_strategy_type: BetStrategyType = BetStrategyType.BOOK_DR_Z_PLACE_SHOW_ARB

        # TODO: better use of outlay strat for max starting wealth
        self.dr_z_result = get_best_place_show_bets_all(race, self.strategy.outlay_strategy.outlay(self) * 4 * len(self.entries))
        logger.debug("Got dr z result for place_show_arb: %s", self.dr_z_result)

        place_outlay_strat = FlatBetOutlayStrategy(outlay=self.dr_z_result.place_outlay)
        show_outlay_strat = FlatBetOutlayStrategy(outlay=self.dr_z_result.show_outlay)

        self.place_strat = BetStrategy(outlay_strategy=place_outlay_strat, sort_strategy=self.strategy.sort_strategy)
        self.show_strat = BetStrategy(outlay_strategy=show_outlay_strat, sort_strategy=self.strategy.sort_strategy)

        self.bets = self._generate_bets(self.dr_z_result)

    def _generate_bets(self, dr_z_result: DrZPlaceShowResult) -> List[BetTypeImpl]:
        result: List[BetTypeImpl] = []

        for entry in self.entries:
            result.extend([
                PlaceBet(race=self.race, entries=self.entries, selection=[entry], strategy=self.place_strat),
                ShowBet(race=self.race, entries=self.entries, selection=[entry], strategy=self.show_strat)
            ])

        return result

    def min_reward(self) -> float:
        return min(b.max_reward() for b in self.bets)

    def avg_reward(self) -> float:
        return self.dr_z_result.expected_value * self.dr_z_result.total_outlay

    def max_reward(self) -> float:
        # Generate place and show bets for the lowest odds 3 horses
        entries_sorted = self.entries.copy()
        entries_sorted.sort(key=lambda e: e.latest_odds(), reverse=True)
        lowest_3 = entries_sorted[0:3]

        bets1 = [
            PlaceBet(race=self.race, entries=self.entries, selection=[lowest_3[0]], strategy=self.place_strat),
            ShowBet(race=self.race, entries=self.entries, selection=[lowest_3[0]], strategy=self.show_strat)
        ]
        bets2 = [
            PlaceBet(race=self.race, entries=self.entries, selection=[lowest_3[1]], strategy=self.place_strat),
            ShowBet(race=self.race, entries=self.entries, selection=[lowest_3[1]], strategy=self.show_strat)
        ]
        bets3 = [
            ShowBet(race=self.race, entries=self.entries, selection=[lowest_3[2]], strategy=self.show_strat)
        ]

        comb_bets = []

        for bets in (bets1, bets2, bets3):
            comb_bets.extend(bets)

        return sum([bet.max_reward() for bet in comb_bets])

    def min_bet(self) -> float:
        return self.dr_z_result.total_outlay

    def odds(self) -> float:
        return 1

    def cost(self):
        return self.dr_z_result.total_outlay

    def result(self) -> MultiBetResult:
        return MultiBetResult(
            race=self.race,
            bet_type=self.bet_type,
            bet_strategy_type=self.bet_strategy_type,
            bet_results=[b.result() for b in self.bets],
            max_reward=self.max_reward(),
            avg_reward=self.avg_reward(),
            min_reward=self.min_reward(),
            cost=self.cost(),
            odds=self.odds(),
        )
