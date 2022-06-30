from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declared_attr

from app.db.base_class import Base


class BetTag(Base):
    @declared_attr
    def __tablename__(cls) -> str:
        return "bet_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # TODO Unique?
    description = Column(String, nullable=True)
