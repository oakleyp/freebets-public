from hashlib import md5
from typing import List

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

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
    cost = Column(Float, index=True)

    parent_id = Column(Integer, ForeignKey("bets.id", ondelete="CASCADE"))
    sub_bets = relationship(
        "Bet", cascade="all, delete-orphan", backref=backref("parent", remote_side=[id])
    )

    bet_type = Column(String, index=True)  # Win / WPS / etc.
    bet_strategy_type = Column(String, index=True)  # AIWin / SafeWin / FreeWin / etc.

    race_id = Column(Integer, ForeignKey("race.id"))
    race = relationship("Race", back_populates="bets")

    tags = relationship("BetTag", secondary=bet_tags)

    active_entries = relationship("RaceEntry", secondary=bet_active_entries)
    inactive_entries = relationship("RaceEntry", secondary=bet_inactive_entries)

    @hybrid_property
    def bet_md5_hex(self):
        return self.md5_hash().hexdigest()

    def md5_hash(self):
        race: Race = self.race
        active_entries: List["RaceEntry"] = self.active_entries
        act_entry_nos: List[str] = []

        for entry in active_entries:
            act_entry_nos.append(entry.program_no)

        base = (
            race.md5_hash().hexdigest()
            + ",".join(act_entry_nos)
            + self.bet_type
            + self.bet_strategy_type
            + str(self.cost)
        )

        if self.parent_id:
            parent: "Bet" = self.parent
            base = "multi" + parent.md5_hash().hexdigest() + base

        return md5(base.encode())

    def update_shallow(self, other: "Bet") -> None:
        self.min_reward = other.min_reward
        self.avg_reward = other.avg_reward
        self.max_reward = other.max_reward
