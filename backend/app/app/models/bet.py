from hashlib import md5
from typing import List

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table, and_, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, backref, relationship

from app.db.base_class import Base

from .bet_tag import BetTag  # noqa: F401
from .race import Race  # noqa: F401
from .race_entry import RaceEntry  # noqa: F401

bet_active_entries = Table(
    "bets_active_entries",
    Base.metadata,
    Column("bet_id", ForeignKey("bets.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "entry_id", ForeignKey("race_entries.id", ondelete="CASCADE"), primary_key=True
    ),
)

bet_inactive_entries = Table(
    "bets_inactive_entries",
    Base.metadata,
    Column("bet_id", ForeignKey("bets.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "entry_id", ForeignKey("race_entries.id", ondelete="CASCADE"), primary_key=True
    ),
)

bet_tags = Table(
    "bets_tags",
    Base.metadata,
    Column("bet_id", ForeignKey("bets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("bet_tags.id", ondelete="CASCADE"), primary_key=True),
)


class Bet(Base):
    @declared_attr
    def __tablename__(cls) -> str:
        return "bets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    predicted_odds = Column(Float)
    min_reward = Column(Float)
    max_reward = Column(Float)
    avg_reward = Column(Float)
    _cost = Column("cost", Float, index=True)

    parent_id = Column("parent_id", Integer, ForeignKey("bets.id", ondelete="CASCADE"))
    _sub_bets = relationship(
        "Bet",
        cascade="all, delete-orphan",
        backref=backref("_parent", remote_side=[id]),
    )

    _bet_type = Column("bet_type", String, index=True)  # Win / WPS / etc.
    _bet_strategy_type = Column(
        "bet_strategy_type", String, index=True
    )  # AIWin / SafeWin / FreeWin / etc.

    race_id = Column("race_id", Integer, ForeignKey("race.id"))
    _race = relationship(
        "Race", backref=backref("bets", cascade="all, delete-orphan", uselist=True)
    )

    tags = relationship("BetTag", secondary=bet_tags)

    _active_entries = relationship("RaceEntry", secondary=bet_active_entries)
    inactive_entries = relationship("RaceEntry", secondary=bet_inactive_entries)

    bet_md5_hex = Column(String, nullable=False, unique=True)

    def md5_hash(self):
        active_entries: List["RaceEntry"] = self.active_entries
        act_entry_nos: List[str] = []

        for entry in active_entries:
            act_entry_nos.append(entry.program_no)

        if self.race:
            race_hash = self.race.md5_hash().hexdigest()
        elif self.sub_bets:
            race_hash = ",".join(
                [bet.race.md5_hash().hexdigest() for bet in self.sub_bets]
            )
        else:
            # Maybe raise val error here
            # raise ValueError("bet should have race - %s" % self)
            race_hash = "dupe should fail"

        base = (
            race_hash
            + ",".join(sorted(act_entry_nos))
            + f"{self.bet_type}"
            + f"{self.bet_strategy_type}"
            + "%.2f" % self.cost
        )

        if self.parent:
            base = "sub" + self.parent.md5_hash().hexdigest() + base
        else:
            base = "root" + base

        return md5(base.encode())

    @hybrid_property
    def race(self):
        return self._race

    @race.setter
    def race(self, val) -> None:
        self._race = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def cost(self) -> float:
        return self._cost

    @cost.setter
    def cost(self, val: float) -> None:
        self._cost = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val) -> None:
        self._parent = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def sub_bets(self) -> int:
        return self._sub_bets

    @sub_bets.setter
    def sub_bets(self, val) -> None:
        self._sub_bets = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def bet_type(self) -> str:
        return self._bet_type

    @bet_type.setter
    def bet_type(self, val: str) -> None:
        self._bet_type = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def bet_strategy_type(self) -> str:
        return self._bet_strategy_type

    @bet_strategy_type.setter
    def bet_strategy_type(self, val: str) -> None:
        self._bet_strategy_type = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    @hybrid_property
    def active_entries(self) -> List["RaceEntry"]:
        return self._active_entries

    @active_entries.setter
    def active_entries(self, val: List["RaceEntry"]) -> None:
        self._active_entries = val
        self.bet_md5_hex = self.md5_hash().hexdigest()

    def update_shallow(self, other: "Bet") -> None:
        self.min_reward = other.min_reward
        self.avg_reward = other.avg_reward
        self.max_reward = other.max_reward

    def __repr__(self) -> str:
        act_entry_nos: List[str] = []

        for entry in self.active_entries:
            act_entry_nos.append(entry.program_no)

        return self._repr(
            id=self.id,
            entries=(sorted([entry.program_no for entry in self.active_entries])),
            bet_type=self.bet_type,
            bet_strategy_type=self.bet_strategy_type,
            cost=self.cost,
            race_id=self.race_id,
            md5=self.bet_md5_hex,
            parent=self.parent,
            parent_id=self.parent_id,
        )


# At each flush, make an additional query to delete multibets that have no children.
# This could be expensive at scale (e.g. large batch deletes),
# but currently shouldn't be an issue.
@event.listens_for(Session, "after_flush")
def delete_multis_with_no_subs(session, ctx):
    session.query(Bet).filter(and_(~Bet.sub_bets.any(), Bet.race_id == None)).delete(
        synchronize_session=False
    )
