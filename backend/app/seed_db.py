from typing import List
from app.db.session import SessionLocal
from app.models.bet import Bet
from app.models.race import Race
from app.tests.utils.race_data import create_track_with_race_and_starter_details_n
from app.raceday.race_canonical import LiveTrackExtendedCanonical
from app.raceday.bet_strategy.generator import BetGen
from app.raceday.bet_strategy.bet_tagger import BetTagger
from sqlalchemy.orm import Session

def seed_all():
    db: Session = SessionLocal()

    track_races = create_track_with_race_and_starter_details_n(10)

    races: List[Race] = []

    for track_race in track_races:
        races = LiveTrackExtendedCanonical(track_race).convert()
        races.extend(races)

    db.add_all(races)
    db.commit()

    bet_tagger = BetTagger(db)

    print("Gen %d races", len(races))

    for race in races:
        bet_gen = BetGen(race=race)
        bets = bet_gen.arbitrage_bets()

        print("Gen %d bets", len(bets))

        for bet in bets:
            bet_db = bet.result().to_bet_db()
            bet_tagger.assign_tags(bet_db)
            db.add(bet_db)

    db.commit()

            




    
