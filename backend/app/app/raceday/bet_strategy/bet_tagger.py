import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.bet import Bet
from app.models.bet_tag import BetTag

logger = logging.getLogger(__name__)


class BetTagger:
    """
    Manages mapping of `BetTags` to `Bet`s, based on unique tag names
    listed in the `bet_tags` table, and conditions of a `Bet`s attributes.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.tag_map = self.get_db_tags()

    def get_db_tags(self) -> Dict[str, BetTag]:
        """Creates a mapping of tag names to `BetTag` instances in the db."""
        tags: List[BetTag] = self.db.query(BetTag).all()

        result = {}

        for tag in tags:
            result[tag.name.lower()] = tag

        return result

    def _assign_if_exists(self, bet: Bet, tag_name: str) -> None:
        tag = self.tag_map.get(tag_name)

        if not tag:
            logger.warning(
                "Failed trying to assign tag %s - not found in db.", tag_name
            )
            return None

        bet.tags.append(tag)

    def assign_tags(self, bet: Bet) -> None:
        """
        Assign tags to a given bet based on its attributes.
        Assumes that this bet is not already committed to the db and has no tags,
        given the ethereal, short-lived nature of bets in this application.
        """
        if bet.min_reward >= bet.cost:
            self._assign_if_exists(bet, "free")
            return None

        if bet.avg_reward >= bet.cost:
            self._assign_if_exists(bet, "good value")
