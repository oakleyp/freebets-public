#!/usr/bin/env python3

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Union

from app.models.bet import Bet
from app.models.race import Race
from app.models.race_entry import RaceEntry

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BetType(Enum):
    WIN_BET = (1,)
    ALL_WIN_ARB = (2,)
    BOX_WIN_ARB = (3,)
    PLACE_SHOW_COMB = (4,)

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

    def cost(self) -> float:
        raise NotImplementedError(
            "cost() not implemented for %s" % self.__class__.__name__
        )

    def avg_reward(self) -> float:
        raise NotImplementedError(
            "avg_reward() not implemented for %s" % self.__class__.__name__
        )

    def min_reward(self) -> float:
        raise NotImplementedError(
            "min_reward() not implemented for %s" % self.__class__.__name__
        )

    def max_reward(self) -> float:
        raise NotImplementedError(
            "max_reward() not implemented for %s" % self.__class__.__name__
        )

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
        self.bet_type: BetType = BetType.BOX_WIN_ARB
        self.bet_strategy_type: BetStrategyType = BetStrategyType.

        self.bets = [
            WinBet(
                race=self.race,
                entries=self.entries,
                selection=s,
                strategy=self.strategy,
            )
            for s in self.selection
        ]