from hashlib import md5
from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, Boolean, Column, Date, Float, Integer, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.custom_types import TZDateTime

if TYPE_CHECKING:
    from .race_entry import RaceEntry  # noqa F401
    from .bet import Bet  # noqa F401


class Race(Base):
    id = Column(Integer, primary_key=True, index=True)
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
    current_race = Column(Boolean, default=False, index=True)
    # TODO op:
    # carryoverPool
    # hasExpertPick?

    _race_number = Column("race_number", Integer, nullable=False)
    _race_date = Column("race_date", Date, nullable=False, index=True)
    _track_code = Column("track_code", String, nullable=False, index=True)

    def md5_hash(self):
        """
            Generate an MD5 hash for this race. 
            
            This is used rather than the builtin __hash__,
            [used by builtin hash()], since hash() varies between runtime
            and python implementations, whereas this is used for comparing
            db-persisted objects.
        """
        base = str(self.race_date) + str(self.track_code) + str(self.race_number)
        return md5(base.encode())

    race_md5_hex = Column(String, nullable=False, unique=True)

    @hybrid_property
    def race_number(self) -> int:
        return self._race_number
    
    @race_number.setter
    def race_number(self, val: int) -> None:
        self._race_number = val
        self.race_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def race_date(self):
        return self._race_date

    @race_date.setter
    def race_date(self, val) -> None:
        self._race_date = val
        self.race_md5_hex = self.md5_hash().hexdigest()
        
    @hybrid_property
    def track_code(self) -> str:
        return self._track_code

    @track_code.setter
    def track_code(self, val) -> None:
        self._track_code = val
        self.race_md5_hex = self.md5_hash().hexdigest()


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

    def active_entries(self) -> List["RaceEntry"]:
        return [entry for entry in self.entries if not entry.scratched]

    def has_valid_pool_totals(self) -> bool:
        if not (
            self.win_pool_total > 0
            and self.place_pool_total > 0
            and self.show_pool_total > 0
        ):
            return False

        for entry in self.entries:
            if not entry.has_valid_pool_totals():
                return False

        return True


    def update_shallow(self, other: "Race"):
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
