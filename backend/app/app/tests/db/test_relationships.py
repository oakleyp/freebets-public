from typing import Generator, List

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.bet import Bet
from app.models.race import Race
from app.models.race_entry import RaceEntry
from app.raceday.race_canonical import LiveRaceEntryCanonical, LiveTrackBasicCanonical
from app.tests.utils.race_data import create_starters_n, create_track_with_race_details
from app.tests.utils.utils import random_lower_string


@pytest.fixture(scope="function")
def clean_db() -> Generator:
    db: Session = SessionLocal()
    # Clear bets
    db.query(Bet).delete()
    # Clear races and entries
    db.query(RaceEntry).delete()
    db.query(Race).delete()

    yield db

    db.close()


def create_bet(race: Race) -> Bet:
    bet = Bet(
        title=random_lower_string(),
        description=random_lower_string(),
        predicted_odds=0.8,
        min_reward=13.12,
        max_reward=12345.0,
        avg_reward=200.0,
        cost=33.0,
        bet_type=random_lower_string(),
        bet_strategy_type=random_lower_string(),
    )

    bet.race = race
    bet.active_entries = race.entries[0:3]
    bet.inactive_entries = race.entries[3:]

    return bet


def test_bet_delete_no_delete_entries(clean_db: Session) -> None:
    track_data = create_track_with_race_details()
    races = LiveTrackBasicCanonical(track_data).convert()
    og_races_len = len(races)
    og_entries_len = 10

    for race in races:
        entry_data = create_starters_n(og_entries_len)
        race_entries = [LiveRaceEntryCanonical(entry).convert() for entry in entry_data]

        race.entries = race_entries

    clean_db.add_all(races)
    clean_db.commit()

    clean_db.add(create_bet(races[0]))
    clean_db.commit()

    # Test session query delete syntax - this relies on DB cascades
    # rather than in-python sqlalchemy cascades
    clean_db.query(Bet).delete()
    clean_db.commit()

    races: List[Race] = clean_db.query(Race).all()

    assert len(races) == og_races_len

    for race in races:
        assert len(race.entries) == og_entries_len

    # Test normal session delete, which uses in-python relationship logic for cascades
    bet = create_bet(races[0])
    clean_db.add(bet)
    clean_db.commit()

    clean_db.delete(bet)
    clean_db.commit()

    races: List[Race] = clean_db.query(Race).all()

    assert len(races) == og_races_len

    for race in races:
        assert len(race.entries) == og_entries_len


def test_delete_race_deletes_bets(clean_db: Session) -> None:
    track_data = create_track_with_race_details()
    races = LiveTrackBasicCanonical(track_data).convert()
    og_entries_len = 10

    for race in races:
        entry_data = create_starters_n(og_entries_len)
        race_entries = [LiveRaceEntryCanonical(entry).convert() for entry in entry_data]

        race.entries = race_entries

    clean_db.add_all(races)
    clean_db.commit()

    bet = create_bet(races[0])
    bet.sub_bets = [create_bet(races[0])]
    clean_db.add(bet)
    clean_db.commit()

    bets = clean_db.query(Bet).all()
    assert bets == [bet, bet.sub_bets[0]]

    clean_db.delete(races[0])
    clean_db.commit()

    bets = clean_db.query(Bet).all()
    assert bets == []


def test_delete_entry_no_delete_race(db: Session) -> None:
    track_data = create_track_with_race_details()
    races = LiveTrackBasicCanonical(track_data).convert()
    og_entries_len = 10

    for race in races:
        entry_data = create_starters_n(og_entries_len)
        race_entries = [LiveRaceEntryCanonical(entry).convert() for entry in entry_data]

        race.entries = race_entries

    db.add_all(races)
    db.commit()

    race = races[0]
    race.entries = race.entries[1:]

    db.add(race)
    db.commit()

    assert db.query(Race).filter(Race.id == race.id).all() == [race]
