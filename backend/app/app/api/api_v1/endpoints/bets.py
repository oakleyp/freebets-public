import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.models.bet import Bet
from app.models.race import Race
from app.raceday.bet_strategy.bet_strategies import BetStrategyType, BetType
from app.schemas.bet_result import (
    BetGetResponse,
    BetResultConverter,
    BetsQueryResponse,
    MultiBetResult,
    SingleBetResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# DEFAULT_TRACK_CODES = ["kee", "cd", "mrn"]
DEFAULT_TRACK_CODES = []
DEFAULT_BET_STRAT_TYPES = list(
    map(str, [BetStrategyType.BOOK_ALL_WIN_ARB, BetStrategyType.BOOK_BOX_WIN_ARB],)
)
DEFAULT_BET_TYPES = list(
    map(str, [BetType.ALL_WIN_ARB, BetType.BOX_WIN_ARB, BetType.WIN_BET])
)


@router.get("/", response_model=schemas.BetsQueryResponse)
@router.get("", response_model=schemas.BetsQueryResponse, include_in_schema=False)
def read_bets(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    track_codes: List[str] = Query(default=DEFAULT_TRACK_CODES),
    bet_strat_types: List[str] = Query(default=DEFAULT_BET_STRAT_TYPES),
    bet_types: List[str] = Query(default=DEFAULT_BET_TYPES),
) -> Any:
    """
    Retrieve items.
    """
    all_bets_q = db.query(Bet)

    if len(bet_types) > 0:
        all_bets_q = all_bets_q.filter(Bet.bet_type.in_(bet_types))

    if len(track_codes) > 0:
        all_bets_q = all_bets_q.filter(Bet.race.has(Race.track_code.in_(track_codes)))

    if len(bet_strat_types) > 0:
        all_bets_q = all_bets_q.filter(Bet.bet_strategy_type.in_(bet_strat_types))

    if len(bet_types) > 0:
        all_bets_q = all_bets_q.filter(Bet.bet_type.in_(bet_types))

    all_bets: List[Bet] = all_bets_q.order_by(Bet.id.desc()).offset(skip).limit(
        limit
    ).all()
    single_bets: List[SingleBetResult] = []
    multi_bets: List[MultiBetResult] = []
    bet_conv = BetResultConverter()

    for i, bet in enumerate(all_bets):
        if i > limit - 1:
            break

        if len(bet.sub_bets) < 1 and bet.parent_id is None:
            single_bets.append(bet_conv.create_single_bet_result(bet))
        else:
            multi_bets.append(bet_conv.create_multi_bet_result(bet))

    result_track_codes = list(set([bet.race.track_code for bet in all_bets]))
    result_bet_strat_types = list(set([bet.bet_strategy_type for bet in all_bets]))
    result_bet_types = list(set([bet.bet_type for bet in all_bets]))

    # TODO: Cache this (or make static)
    all_track_codes = [race.track_code for race in db.query(Race).distinct(Race.track_code).all()]
    all_bet_strat_types = [str(BetStrategyType[bet_strat_type.name]) for bet_strat_type in BetStrategyType]
    all_bet_types = [str(BetType[bet_type.name]) for bet_type in BetType]

    return BetsQueryResponse(
        single_bets=single_bets,
        multi_bets=multi_bets,
        track_codes=result_track_codes,
        bet_strat_types=result_bet_strat_types,
        bet_types=result_bet_types,
        all_track_codes=all_track_codes,
        all_bet_strat_types=all_bet_strat_types,
        all_bet_types=all_bet_types,
        limit=limit,
        skip=skip,
    )


@router.get("/{id}", response_model=schemas.BetGetResponse)
def read_bet(*, db: Session = Depends(deps.get_db), id: int,) -> Any:
    """
    Get a bet by ID.
    """
    bet: Bet = db.query(Bet).filter(Bet.id == id).first()

    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")

    bet_conv = BetResultConverter()

    if len(bet.sub_bets) < 1:
        return BetGetResponse(
            data=bet_conv.create_single_bet_result(bet), result_type="single"
        )
    else:
        return BetGetResponse(
            data=bet_conv.create_multi_bet_result(bet), result_type="multi",
        )
