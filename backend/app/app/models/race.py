from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.custom_types import TZDateTime

if TYPE_CHECKING:
    from .race_entry import RaceEntry  # noqa F401
    from .bet import Bet  # noqa F401


class Race(Base):
    id = Column(Integer, primary_key=True, index=True)
    race_number = Column(Integer, nullable=False)
    race_date = Column(Date, nullable=False, index=True)
    post_time = Column(TZDateTime, nullable=False)
    post_time_stamp = Column(BigInteger, nullable=False)
    mtp = Column(Integer)
    status = Column(String, index=True)
    distance = Column(String)
    distance_long = Column(String)
    surface = Column(String, nullable=True, index=True)
    surface_label = Column(String, nullable=True, index=True)
    age_restrictions = Column(String, nullable=True, index=True)
    sex_restrictions = Column(String, index=True)
    description = Column(String)
    wagers = Column(String)
    country = Column(String, index=True)
    # TODO op:
    # carryoverPool
    # currentRace?
    # hasExpertPick?

    track_code = Column(String, nullable=False, index=True)
    track_country = Column(String)
    race_type = Column(String, nullable=False)  # Thoroughbred, Harness, etc.

    entries = relationship(
        "RaceEntry", back_populates="race", cascade="all", uselist=True
    )
    bets = relationship(
        "Bet", back_populates="race", cascade="all, delete-orphan", uselist=True
    )

    def __repr__(self) -> str:
        return self._repr(
            id=self.id,
            race_number=self.race_number,
            race_date=self.race_date,
            track_code=self.track_code,
            post_time=self.post_time,
        )