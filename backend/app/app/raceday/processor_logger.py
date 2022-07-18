from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.models.bet import Bet
from app.models.race import Race
from app.models.raceday_refresh_log import RaceDayRefreshLog


class RaceDayProcessorLogger:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        lookahead_start: datetime,
        lookahead_end: datetime,
        races: List[Race] = None,
        bets: List[Bet] = None,
        next_check_time: datetime = None,
        success: bool = False,
    ):
        """Log the given results to the race_day_refresh_log table."""

        if races is None or bets is None or next_check_time is None:
            args = {
                "lookahead_start": lookahead_start,
                "lookahead_end": lookahead_end,
                "races": races,
                "bets": bets,
                "next_check_time": next_check_time,
            }

            param_items: List[str] = []

            for (name, val) in args.items():
                param_items.append(f"{name}={val}")

            raise ValueError(f"Missing required args ({', '.join(param_items)}")

        entry_count = 0

        for race in races:
            entry_count += len(race.entries)

        log_entry = RaceDayRefreshLog(
            lookahead_start=lookahead_start,
            lookahead_end=lookahead_end,
            next_check_time=next_check_time,
            race_count=len(races),
            entry_count=entry_count,
            bet_count=len(bets),
            success=success,
        )

        self.db.add(log_entry)
        self.db.commit()
