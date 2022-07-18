from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel

from app.models.bet import Bet
from app.models.race_entry import RaceEntry


class RaceEntryResult(BaseModel):
    program_no: str
    name: str
    odds: Optional[float]
    odds_source: Optional[str]
    ai_predicted_odds: Optional[float]
    owner_name: Optional[str]
    jockey_name: Optional[str]
    trainer_name: Optional[str]
    sire_name: Optional[str]
    dam_name: Optional[str]
    win_pool_total: float
    place_pool_total: float
    show_pool_total: float


class RaceResult(BaseModel):
    track_code: str
    race_number: int
    race_date: str
    mtp: int
    status: str
    post_time: Optional[datetime]
    post_time_stamp: Optional[int]
    win_pool_total: float
    place_pool_total: float
    show_pool_total: float


class BetTagResult(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class BaseBetResult(BaseModel):
    id: int
    title: str
    description: str
    predicted_odds: float

    min_reward: float
    avg_reward: float
    max_reward: float
    cost: float

    bet_type: str  # e.g. Win / WPS / Super / Ex
    bet_strategy_type: str  # e.g. AIWin / SafeWin / FreeWin
    tags: List[BetTagResult]  # AI / Safe / Free


class SingleBetResult(BaseBetResult):
    race: RaceResult

    active_entries: List[RaceEntryResult]
    inactive_entries: List[RaceEntryResult]


class MultiBetResult(BaseBetResult):
    sub_bets: List[SingleBetResult]


class BetsQueryResponse(BaseModel):
    single_bets: List[SingleBetResult]
    multi_bets: List[MultiBetResult]
    track_codes: List[str]
    limit: int
    skip: int
    bet_types: List[str]
    bet_strat_types: List[str]
    all_bet_strat_types: List[str]
    all_bet_types: List[str]
    all_track_codes: List[str]
    next_refresh_ts: Optional[int]


class BetGetResponse(BaseModel):
    data: Union[SingleBetResult, MultiBetResult]
    result_type: str
    next_refresh_ts: int


class BetResultConverter:
    """Provide conversion methods from SA Model schema to serializable result schema."""

    def create_race_entry_result(self, entry: RaceEntry) -> RaceEntryResult:
        return RaceEntryResult(
            program_no=entry.program_no,
            name=entry.name,
            odds=entry.latest_odds(),
            odds_source=entry.odds_source(),
            ai_predicted_odds=entry.predicted_odds,
            jockey_name=entry.jockey_name,
            owner_name=entry.owner_name,
            trainer_name=entry.trainer_name,
            sire_name=entry.sire_name,
            dam_name=entry.dam_name,
            win_pool_total=entry.win_pool_total,
            place_pool_total=entry.place_pool_total,
            show_pool_total=entry.show_pool_total,
        )

    def create_single_bet_result(self, bet: Bet) -> SingleBetResult:
        race_res = RaceResult(
            track_code=bet.race.track_code,
            race_number=bet.race.race_number,
            race_date=bet.race.race_date.isoformat(),
            mtp=bet.race.mtp,
            post_time=bet.race.post_time,
            post_time_stamp=bet.race.post_time_stamp,
            status=bet.race.status,
            win_pool_total=bet.race.win_pool_total,
            place_pool_total=bet.race.place_pool_total,
            show_pool_total=bet.race.show_pool_total,
        )

        bet_res = SingleBetResult(
            id=bet.id,
            title=bet.title,
            description=bet.description,
            predicted_odds=bet.predicted_odds,
            min_reward=bet.min_reward,
            avg_reward=bet.avg_reward,
            max_reward=bet.max_reward,
            cost=bet.cost,
            bet_type=bet.bet_type,
            bet_strategy_type=bet.bet_strategy_type,
            tags=bet.tags,
            race=race_res,
            active_entries=[
                self.create_race_entry_result(entry) for entry in bet.active_entries
            ],
            inactive_entries=[
                self.create_race_entry_result(entry) for entry in bet.inactive_entries
            ],
        )

        return bet_res

    def create_multi_bet_result(self, bet: Bet) -> MultiBetResult:
        for sb in bet.sub_bets:
            if not sb.race:
                print("WTF??", sb.id)

        return MultiBetResult(
            id=bet.id,
            title=bet.title,
            description=bet.description,
            predicted_odds=bet.predicted_odds,
            min_reward=bet.min_reward,
            avg_reward=bet.avg_reward,
            max_reward=bet.max_reward,
            cost=bet.cost,
            bet_type=bet.bet_type,
            bet_strategy_type=bet.bet_strategy_type,
            tags=bet.tags,
            sub_bets=[
                self.create_single_bet_result(sub_bet) for sub_bet in bet.sub_bets
            ],
        )
