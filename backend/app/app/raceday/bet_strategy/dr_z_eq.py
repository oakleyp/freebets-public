# The following are based on Dr. Z's model-derived estimation formulas

# Track Payback (1 - (track take % / 100))
# This assumes 17.1% track take
from app.models.race import Race
from app.models.race_entry import RaceEntry

# Track Payback (1 - (track take % / 100))
# This assumes 17.1% track take
Q = 0.829


def get_expected_place_val_per_dollar(
    race: Race, selection: RaceEntry, track_payback: float = Q
) -> float:
    W_i = selection.win_pool_total
    W = race.win_pool_total
    P_i = selection.place_pool_total
    P = race.place_pool_total

    result = 0.319 + (0.559 * ((W_i / W) / (P_i / P)))
    result_payback_adj = (2.22 - (1.29 * (W_i / W))) * (Q - track_payback)

    return result + result_payback_adj


def get_expected_show_val_per_dollar(
    race, selection: RaceEntry, track_payback: float = Q
) -> float:
    W_i = selection.win_pool_total
    W = race.win_pool_total
    S_i = selection.show_pool_total
    S = race.show_pool_total

    result = 0.543 + (0.369 * ((W_i / W) / (S_i / S)))
    result_payback_adj = (3.60 + (2.13 * (W_i / W))) * (Q - track_payback)

    return result + result_payback_adj
