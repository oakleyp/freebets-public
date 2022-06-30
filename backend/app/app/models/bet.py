from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

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
    sub_bets = relationship("Bet", cascade="all, delete-orphan")

    bet_type = Column(String, index=True)  # Win / WPS / etc.
    bet_strategy_type = Column(String, index=True)  # AIWin / SafeWin / FreeWin / etc.

    race_id = Column(Integer, ForeignKey("race.id"))
    race = relationship("Race", back_populates="bets")

    tags = relationship("BetTag", secondary=bet_tags)

    active_entries = relationship("RaceEntry", secondary=bet_active_entries)
    inactive_entries = relationship("RaceEntry", secondary=bet_inactive_entries)
