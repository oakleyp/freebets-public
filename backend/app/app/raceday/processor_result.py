from typing import List
from app.models.bet import Bet
from app.models.race import Race
from pydantic import BaseModel


class ProcessOnceResult(BaseModel):
    next_check_secs: float
    races: List[Race]
    bets: List[Bet]

    class Config:
        arbitrary_types_allowed = True
