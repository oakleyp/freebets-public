from typing import List
from app.db.session import SessionLocal
from app.models.bet import Bet
from app.models.race import Race
from app.models.race_entry import RaceEntry
from app.tests.utils.race_data import create_race_pool_totals, create_track_with_race_and_starter_details_n
from app.raceday.race_canonical import LiveTrackExtendedCanonical
from app.raceday.bet_strategy.generator import BetGen
from app.raceday.bet_strategy.bet_tagger import BetTagger
from sqlalchemy.orm import Session

def clear_all():
    db: Session = SessionLocal()

     # Clear bets
    db.query(Bet).delete()
    # Clear races and entries
    db.query(RaceEntry).delete()
    db.query(Race).delete()

    db.commit()

    db.close()

def seed_all():
    db: Session = SessionLocal()

    track_races = create_track_with_race_and_starter_details_n(30)

    all_races: List[Race] = []

    for track_race in track_races:
        race_pools = [create_race_pool_totals(race) for race in track_race.races]
        races = LiveTrackExtendedCanonical(track_race).convert()

        for (race, pool) in zip(races, race_pools):
            race.win_pool_total = pool.win_total
            race.place_pool_total = pool.place_total
            race.show_pool_total = pool.show_total

            for entry in race.entries:
                entry_pool = pool.entries_to_pools_map[entry.program_no]
                entry.win_pool_total = entry_pool.win_total
                entry.place_pool_total = entry_pool.place_total
                entry.show_pool_total = entry_pool.show_total
 
        all_races.extend(races)

    db.add_all(all_races)
    db.commit()

    bet_tagger = BetTagger(db)

    print("Gen %d races", len(all_races))

    for race in all_races:
        bet_gen = BetGen(race=race)
        bets = bet_gen.arbitrage_bets()

        print("Gen %d bets", len(bets))

        for bet in bets:
            bet_db = bet.result().to_bet_db()
            bet_tagger.assign_tags(bet_db)
            db.add(bet_db)

    db.commit()
    db.close()
            




    
