import logging
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Session, joinedload, make_transient

from app.models.bet import Bet
from app.models.race import Race
from app.raceday.bet_strategy.bet_strategies import BetResult, MultiBetResult
from app.raceday.bet_strategy.bet_tagger import BetTagger
from app.raceday.bet_strategy.generator import BetGen

logger = logging.getLogger(__name__)


class RaceBetProcessor:
    """
    A container for the bet generation and merge process per race. 

    Given a db session and a race, uses BetGen to create bets. Where these 
    generated bets conflict with those already in the DB (as determined by a match
    between the bets' md5 hashes), the bets in the DB are updated with the latest
    generation.

    Newly generated bets that have no conflict in the DB are added. 

    Bets that exist in the DB but not in the new generation of bets are deleted.

    Changes to the session are committed as a result of this process.
    """

    def __init__(
        self,
        db: Session,
        race: Race,
        *,
        use_pool_totals: bool = False,
        max_bets: Optional[int] = None
    ) -> None:
        self.db = db
        self.race = race
        self.use_pool_totals = use_pool_totals
        self.max_bets = max_bets

        self.bet_tagger = BetTagger(self.db)

    def existing_bets(self) -> List[Bet]:
        existing_race_bets: List[Bet] = (
            self.db.query(Bet)
            .options(joinedload(Bet.parent))
            .filter(Bet.race.has(Race.id == self.race.id))
            .all()
        )

        return existing_race_bets

    def existing_bet_hash_mapping(self) -> Dict[str, Bet]:
        # Map of bet hash -> bet
        bet_map: Dict[str, Bet] = {}

        for bet in self.existing_bets():
            bet_hash = bet.bet_md5_hex
            bet_map[bet_hash] = bet

            if bet.parent:
                parent_hash = bet.parent.bet_md5_hex
                bet_map[parent_hash] = bet.parent

        return bet_map

    def bet_generator(self) -> BetGen:
        return BetGen(race=self.race, use_pool_totals=self.use_pool_totals)

    def regenerate_bets(self) -> List[Bet]:
        bet_gen = self.bet_generator()
        bets = bet_gen.all_bets()
        result_bets: List[Bet] = []

        logger.debug("Generated %d bets for race %s", len(bets), self.race)

        for (i, bet) in enumerate(bets):
            if self.max_bets and i >= self.max_bets:
                logger.debug("Reached max_bets (%d); breaking", self.max_bets)
                break

            bet_res: Union[BetResult, MultiBetResult] = bet.result()
            db_bet = bet_res.to_bet_db()

            self.bet_tagger.assign_tags(db_bet)

            result_bets.append(db_bet)

        return result_bets

    def reconcile_generated_bets_with_db(self, generated_bets: List[Bet]) -> List[Bet]:
        bet_map = self.existing_bet_hash_mapping()

        new_bets: List[Bet] = []
        updates_seen = set()

        generated_sub_bets: List[Bet] = []

        for bet in generated_bets:
            for sub_bet in bet.sub_bets:
                generated_sub_bets.append(sub_bet)

        for bet in generated_bets + generated_sub_bets:
            bet_hash = bet.md5_hash().hexdigest()

            if bet_hash in bet_map:
                make_transient(bet)
                bet_map[bet_hash].update_shallow(bet)
                updates_seen.add(bet_hash)
            else:
                new_bets.append(bet)

        hashes_to_delete = set(bet_map.keys()).difference(updates_seen)

        for hash in hashes_to_delete:
            self.db.delete(bet_map[hash])

        self.db.commit()

        return new_bets

    def create_bets(self) -> List[Bet]:
        result_bets = self.regenerate_bets()

        logger.debug("Saving generated bets %s", result_bets)

        new_bets = self.reconcile_generated_bets_with_db(result_bets)

        if len(new_bets) > 0:
            self.db.add_all(new_bets)

        self.db.commit()

        return result_bets
