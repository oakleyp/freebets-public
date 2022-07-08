from sqlalchemy import Boolean, Column, Integer

from app.db.base_class import Base
from app.db.custom_types import TZDateTime


class RaceDayRefreshLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    lookahead_start = Column(TZDateTime, nullable=False, index=True)
    lookahead_end = Column(TZDateTime, nullable=False, index=True)
    next_check_time = Column(TZDateTime, nullable=False, index=True)
    race_count = Column(Integer, nullable=False)
    entry_count = Column(Integer, nullable=False)
    bet_count = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False, index=True)
