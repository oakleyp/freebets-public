from typing import List

from pydantic import BaseModel

from app.models.bet import Bet
from app.models.race import Race


class ProcessOnceResult(BaseModel):
    next_check_secs: float
    races: List[Race]
    bets: List[Bet]

    class Config:
        arbitrary_types_allowed = True
