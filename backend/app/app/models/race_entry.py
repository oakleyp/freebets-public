from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .race import Race  # noqa: F401


class RaceEntry(Base):
    @declared_attr
    def __tablename__(cls) -> str:
        return "race_entries"

    id = Column(Integer, primary_key=True, index=True)
    post_pos = Column(Integer, nullable=True, index=True)
    program_no = Column(String, nullable=True)
    sortable_program_no = Column(Integer, nullable=True)
    betting_interest = Column(Integer, nullable=True, index=True)
    name = Column(String)
    yob = Column(String, nullable=True, index=True)
    color = Column(String, nullable=True, index=True)
    sex = Column(String, nullable=True, index=True)
    where_bred = Column(String, nullable=True, index=True)
    equipment = Column(String, nullable=True)
    medication = Column(String, nullable=True, index=True)
    formatted_medication = Column(String, nullable=True, index=True)
    weight = Column(Integer, nullable=True)
    overweight_amt = Column(Integer, nullable=True)
    jockey_name = Column(String, nullable=True, index=True)
    trainer_name = Column(String, nullable=True, index=True)
    owner_name = Column(String, nullable=True, index=True)
    color_desc = Column(String, nullable=True)
    sire_name = Column(String, nullable=True, index=True)
    dam_name = Column(String, nullable=True, index=True)
    prior_run_style = Column(String, nullable=True)
    speed_pts = Column(Integer, nullable=True, index=True)
    average_pace_e1 = Column(Integer, nullable=True)
    average_pace_e2 = Column(Integer, nullable=True)
    average_speed_last3 = Column(Integer, nullable=True, index=True)
    best_speed_at_dist = Column(Integer, nullable=True, index=True)
    days_off = Column(Integer, nullable=True, index=True)
    avg_class = Column(Integer, nullable=True, index=True)
    last_class = Column(Integer, nullable=True, index=True)
    prime_power = Column(Integer, nullable=True)
    horse_claiming_price = Column(Integer, nullable=True)
    power_rating = Column(Integer, nullable=True, index=True)
    best_speed = Column(Integer, nullable=True)
    comments_positive = Column(String, nullable=True)
    comments_negative = Column(String, nullable=True)
    silk_status = Column(String, nullable=True)
    silk_uri = Column(String, nullable=True)
    # expert_pick_rank
    # blinkers = Column()
    # oddstrend
    morning_line_odds = Column(Float, nullable=True)
    also_eligible = Column(Boolean, nullable=True, index=True)
    main_track_only = Column(Boolean, nullable=True, index=True)
    morning_line_fav = Column(Boolean, nullable=True, index=True)
    live_odds_fav = Column(Boolean, nullable=True, index=True)
    jockey_chg = Column(Boolean, nullable=True, index=True)
    weight_chg = Column(Boolean, nullable=True, index=True)
    weight_corrections = Column(Boolean, nullable=True, index=True)
    other_change = Column(Boolean, nullable=True)
    profitline_odds = Column(Float, nullable=True)
    live_odds = Column(Float, nullable=True)
    scratched = Column(Boolean, nullable=True, index=True)
    predicted_odds = Column(Float)

    race_id = Column(Integer, ForeignKey("race.id", ondelete="CASCADE"), nullable=False)
    race = relationship("Race", back_populates="entries")

    win_pool_total = Column(Float, default=0, nullable=False)
    place_pool_total = Column(Float, default=0, nullable=False)
    show_pool_total = Column(Float, default=0, nullable=False)

    def latest_odds(self) -> Optional[float]:
        return self.live_odds or self.morning_line_odds

    def odds_source(self) -> Optional[str]:
        if self.live_odds:
            return "live"
        elif self.morning_line_odds:
            return "morningline"

        return None

    def has_valid_pool_totals(self) -> bool:
        if not (self.win_pool_total > 0 and self.place_pool_total > 0 and self.show_pool_total > 0):
            return False

        return True

    def __repr__(self) -> str:
        return self._repr(
            id=self.id,
            name=self.name,
            program_no=self.program_no,
            win_pool_total=self.win_pool_total,
            place_pool_total=self.place_pool_total,
            show_pool_total=self.show_pool_total,
            odds=self.latest_odds(),
        )
