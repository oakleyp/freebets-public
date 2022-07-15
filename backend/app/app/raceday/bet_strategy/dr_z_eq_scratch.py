import math
from typing import List

import hyperopt
from pydantic import BaseModel

from app.models.race import Race
from app.models.race_entry import RaceEntry

# UNUSED: This was work started before realizing that the Dr. Z equations below
# would require an NLP solver (the Dr. used CONOPT / GRG). I may revisit this in the future,
# especially since there may be value in changing these equations to use a different basis
# for i,j,k finish probability than his original (the harville formula).

# The following are based on Dr. Z's place-show optimization formulas.
# Since they are direct translations from his math. formulas, semantics
# will be somewhat unpythonic until I get a better grasp of all their
# nuances in order to restructure them as code.

# Track Payback (1 - (track take % / 100))
# This assumes 17% track take
Q = 0.83

# Amount the track rounds down on fractional payback
# This assumes 5 cent breakage, 10 cents would BREAKAGE = 10
# Figure out the exponent calc for this at some point
BREAKAGE = 20


# def expected_place_value(race: Race, entries: List[RaceEntry], l: int, place_outlay: float):
#     total: float = 0

#     P = race.place_pool_total

#     for j in range(len(race.entries)):
#         if j == l:
#             continue

#         q_l = 1 / entries[l].latest_odds()
#         q_j = 1 / entries[j].latest_odds()
#         harville = (q_l * q_j) / (1-q_l)

#         payout_applied_breakage: float = 0

#         P_l = entries[l].place_pool_total
#         P_j = entries[j].place_pool_total
#         payout_app_takeout = (Q(P + 1) - (1 + P_l + P_j)) / 2
#         bet_effect = (1/1+P_l)

#         payout_applied_breakage_limit = payout_app_takeout * bet_effect * BREAKAGE

#         payout_applied_breakage = 1 + (1 / BREAKAGE(payout_applied_breakage))


def get_place_show_all_utility(
    race: Race, place_outlay: float, show_outlay: float, total_wealth: float
) -> float:
    entries: List[RaceEntry] = race.active_entries()

    total: float = 0

    for i in range(len(entries)):
        i_total: float = 0

        for j in range(len(entries)):
            if j == i:
                continue

            j_total: float = 0

            for k in range(len(entries)):
                if k == i or k == j:
                    continue

                k_total: float = 0

                q_i = 1 / entries[i].latest_odds()
                q_j = 1 / entries[j].latest_odds()
                q_k = 1 / entries[k].latest_odds()

                # TODO: Is there a better alternative to harville probability?
                harville_prob_place_show = (q_i * q_j * q_k) / (
                    (1 - q_i) * (1 - q_i - q_j)
                )
                rebate = calc_rebate(
                    race, entries, place_outlay, show_outlay, i, j, k, total_wealth
                )

                k_total += harville_prob_place_show * math.log(rebate)
                j_total += k_total

            i_total += j_total

        total += i_total

    return total


def calc_rebate(
    race: Race,
    entries: List[RaceEntry],
    place_outlay: float,
    show_outlay: float,
    i: int,
    j: int,
    k: int,
    w0: float,
) -> float:
    P = race.place_pool_total
    S = race.show_pool_total
    P_i = entries[i].place_pool_total
    P_j = entries[j].place_pool_total
    P_ij = P_i + P_j
    p_i = place_outlay  # Could vary
    p_j = place_outlay  # Could vary
    p_l = lambda l: place_outlay  # Could vary

    s_l = lambda l: show_outlay  # Could vary
    s_i = show_outlay
    s_j = show_outlay
    s_k = show_outlay
    S_i = entries[i].show_pool_total
    S_j = entries[j].show_pool_total
    S_k = entries[k].show_pool_total
    S_ijk = S_i + S_j + S_k

    player_place_total_outlay = sum([p_l(i) for i in range(len(entries))])
    place_bet_return = ((Q * (P + player_place_total_outlay)) - (p_i + p_j + P_ij)) / 2
    place_bet_effect = (p_i / (p_i + P_i)) + (p_j / (p_j + P_j))

    player_show_total_outlay = sum([s_l(i) for i in range(len(entries))])
    show_bet_return = (
        (Q * (S + player_show_total_outlay)) - (s_i + s_j + s_k + S_ijk)
    ) / 3
    show_bet_effect = (s_i / (s_i + S_i)) + (s_j / (s_j + S_j)) + (s_k / (s_k + S_k))

    sum_s_l: float = 0
    for i_2 in range(len(entries)):
        if i_2 == i or i_2 == j or i_2 == k:
            continue

        sum_s_l += s_l(i_2)

    sum_p_l: float = 0
    for i_2 in range(len(entries)):
        if i_2 == i or i_2 == j:
            continue

        sum_p_l += p_l(i_2)

    total = (
        (place_bet_return * place_bet_effect)
        + (show_bet_return * show_bet_effect)
        + (w0 - sum_s_l - sum_p_l)
    )

    assert total > 0, (
        f"domain error: pl={p_l(0)}; sl={s_l(0)}; "
        f"({place_bet_return} * {place_bet_effect} = {place_bet_return * place_bet_effect})"
        f" + ({show_bet_return} * {show_bet_effect} = {show_bet_return * show_bet_effect})"
        f" + {w0} - {sum_s_l} - {sum_p_l} = {total}"
    )

    return total


def hyperopt_objective(params) -> float:
    expected_utility = get_place_show_all_utility(
        params["race"],
        params["place_outlay"],
        params["show_outlay"],
        params["total_wealth"],
    )

    return 0 - expected_utility


class DrZPlaceShowResult(BaseModel):
    total_outlay: float
    place_outlay: float
    show_outlay: float
    expected_value: float


def get_best_place_show_bets_all(race: Race, max_spend: float) -> DrZPlaceShowResult:
    trials = hyperopt.Trials()

    max_possible_bet = max_spend / len(race.entries) / 2

    # Start value of 2 is based on Keeneland min bet, may vary
    params_space = {
        "race": race,
        "place_outlay": hyperopt.hp.uniform("place_outlay", 2, max_possible_bet),
        "show_outlay": hyperopt.hp.uniform("show_outlay", 2, max_possible_bet),
        "total_wealth": max_spend,
    }

    best = hyperopt.fmin(
        hyperopt_objective,
        space=params_space,
        algo=hyperopt.tpe.suggest,
        max_evals=50,
        trials=trials,
    )

    total_outlay = max_spend
    place_outlay = best["place_outlay"]
    show_outlay = best["show_outlay"]

    expected_value = get_place_show_all_utility(
        race, place_outlay, show_outlay, total_outlay
    )

    return DrZPlaceShowResult(
        total_outlay=total_outlay,
        place_outlay=place_outlay,
        show_outlay=show_outlay,
        expected_value=expected_value,
    )
