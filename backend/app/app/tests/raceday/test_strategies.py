from app.models.race_entry import RaceEntry
from app.raceday.bet_strategy.bet_strategies import AvgCostRewardSortStrategy, BetStrategy, BetType, DrZPlaceBet, DrZPlaceShowArbBet, DrZShowBet, FlatBetOutlayStrategy
from app.tests.utils.race_data import create_race_and_starter_details, create_track_with_race_and_starter_details
import pytest
from app.raceday.race_canonical import LiveRaceExtendedCanonical
from sqlalchemy.orm import Session

def setup_good_dr_z_entry():
    track_race = create_track_with_race_and_starter_details()
    race = create_race_and_starter_details(1, current_race=True)

    starter = race.starters[0]
    starter.scratched = False
    starter.liveOdds = "5/1" # must be > 8/1

    track_race.races = [race]
    race_canon = LiveRaceExtendedCanonical(track_race, race).convert()

    race_canon.win_pool_total = 100_000
    race_canon.place_pool_total = 20_000
    race_canon.show_pool_total = 20_000

    good_entry: RaceEntry = [entry for entry in race_canon.entries if entry.program_no == starter.programNumber][0]

    good_entry.win_pool_total = 50_000
    good_entry.place_pool_total = 500
    good_entry.show_pool_total = 500

    win_remaining = race_canon.win_pool_total - good_entry.win_pool_total
    place_remaining = race_canon.place_pool_total - good_entry.place_pool_total
    show_remaining = race_canon.show_pool_total - good_entry.show_pool_total

    for entry in race_canon.entries:
        if entry.program_no == good_entry.program_no:
            continue

        entry_odds_frac = 1 / entry.latest_odds()

        entry.win_pool_total = win_remaining * entry_odds_frac
        entry.place_pool_total = place_remaining * entry_odds_frac
        entry.show_pool_total = show_remaining * entry_odds_frac

    return (race_canon, good_entry)

def test_dr_z_place_show_arb(db: Session):
    race_canon, good_entry = setup_good_dr_z_entry()

    DefaultBetStrategy = BetStrategy(
        outlay_strategy=FlatBetOutlayStrategy(), sort_strategy=AvgCostRewardSortStrategy(),
    )

    bet = DrZPlaceShowArbBet(race=race_canon, entries=race_canon.entries, selection=race_canon.entries, strategy=DefaultBetStrategy)

    bet_result = bet.result()
    db_bet = bet_result.to_bet_db()
    db_bet_copy = bet_result.to_bet_db()

    assert db_bet.md5_hash().hexdigest() == db_bet_copy.md5_hash().hexdigest()

    assert db_bet.avg_reward > 3

    print(bet.bets)
    assert isinstance(bet.bets[0], DrZPlaceBet)
    assert isinstance(bet.bets[1], DrZShowBet)

    place_bet: DrZPlaceBet = bet.bets[0]
    show_bet: DrZShowBet = bet.bets[1]

    assert place_bet.avg_reward() == 22.998000000000005
    assert show_bet.avg_reward() == 15.846

    pl_bet_db = place_bet.result().to_bet_db()
    sh_bet_db = show_bet.result().to_bet_db()

    print(db_bet.sub_bets)

    sub_pl_bet_db = [bet for bet in db_bet.sub_bets if bet.bet_type == BetType.PLACE_BET.to_json()][0]
    sub_sh_bet_db = [bet for bet in db_bet.sub_bets if bet.bet_type == BetType.SHOW_BET.to_json()][0]

    assert pl_bet_db.md5_hash().hexdigest() != sub_pl_bet_db.md5_hash().hexdigest()
    assert sh_bet_db.md5_hash().hexdigest() != sub_sh_bet_db.md5_hash().hexdigest()



