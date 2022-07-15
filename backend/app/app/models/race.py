from typing import TYPE_CHECKING, List, Tuple

from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, String, Float, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from hashlib import md5

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
    current_race = Column(Boolean, default=False, nullable=False, index=True)
    # TODO op:
    # carryoverPool
    # hasExpertPick?

    track_code = Column(String, nullable=False, index=True)
    track_country = Column(String)
    race_type = Column(String, nullable=False)  # Thoroughbred, Harness, etc.

    win_pool_total = Column(Float, default=0, nullable=False)
    place_pool_total = Column(Float, default=0, nullable=False)
    show_pool_total = Column(Float, default=0, nullable=False)

    entries = relationship(
        "RaceEntry", back_populates="race", cascade="all, delete-orphan", uselist=True
    )
    bets = relationship(
        "Bet", back_populates="race", cascade="all, delete-orphan", uselist=True
    )

    @hybrid_property
    def race_md5_hex(self):
        base = str(self.race_date) + self.track_code + str(self.race_number)
        return md5(base.encode())

    @race_md5_hex.expression
    def race_md5_hex(cls):
        return func.md5(str(cls.race_date) + cls.track_code + str(cls.race_number))

    def active_entries(self) -> List['RaceEntry']:
        return [entry for entry in self.entries if not entry.scratched]

    def has_valid_pool_totals(self) -> bool:
        if not (self.win_pool_total > 0 and self.place_pool_total > 0 and self.show_pool_total > 0):
            return False

        for entry in self.entries:
            if not entry.has_valid_pool_totals():
                return False

        return True

    def md5_hash(self):
        """
            Generate an MD5 hash for this race. 
            
            This is used rather than the builtin __hash__,
            [used by builtin hash()], since hash() varies between runtime
            and python implementations, whereas this is used for comparing
            db-persisted objects.
        """
        base = str(self.race_date) + self.track_code + str(self.race_number)
        return md5(base.encode())

    def update_shallow(self, other: 'Race'):
        """
            Update race properties based on a shallow race fetch.

            This excludes relationships and other properties that a shallow
            fetch result will not contain.
        """
        self.post_time = other.post_time
        self.post_time_stamp = other.post_time_stamp
        self.mtp = other.mtp
        self.status = other.status
        self.distance = other.distance
        self.distance_long = other.distance_long
        self.surface = other.surface
        self.age_restrictions = other.age_restrictions
        self.sex_restrictions = other.sex_restrictions
        self.description = other.description
        self.wagers = other.wagers
        self.country = other.country
        self.current_race = other.current_race

    def __repr__(self) -> str:
        return self._repr(
            id=self.id,
            race_number=self.race_number,
            race_date=self.race_date,
            track_code=self.track_code,
            post_time=self.post_time,
            current_race=self.current_race,
            win_pool_total=self.win_pool_total,
            place_pool_total=self.place_pool_total,
            show_pool_total=self.show_pool_total,
        )
