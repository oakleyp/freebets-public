import math
from typing import List, Tuple

from app.models.race import Race
from app.models.race_entry import RaceEntry
import hyperopt
from pydantic import BaseModel

# Track Rebate
Q = 0

# Based on Dr. Z's place-show optimization formula

def get_place_show_all_utility(race: Race, place_outlay: float, show_outlay: float, total_wealth: float) -> float:
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

                qi = 1 / entries[i].latest_odds()
                qj = 1 / entries[j].latest_odds()
                qk = 1 / entries[k].latest_odds()
                
                harville_prob_place_show = (qi * qj * qk) /  ((1-qi) * (1-qi-qj))
                rebate = calc_rebate(race, entries, place_outlay, show_outlay, i, j, k, total_wealth)
                
                k_total += (harville_prob_place_show * math.log(rebate))
                j_total += k_total

            i_total += j_total

        total += i_total

    return total

def calc_rebate(race: Race, entries: List[RaceEntry], place_outlay: float, show_outlay: float, i: int, j: int, k: int, w0: float) -> float:
    P = race.place_pool_total
    S = race.show_pool_total
    P_i = entries[i].place_pool_total
    P_j = entries[j].place_pool_total
    P_ij = P_i + P_j
    p_i = place_outlay # Could vary
    p_j = place_outlay # Could vary
    p_l = lambda l: place_outlay # Could vary

    s_l = lambda l: show_outlay # Could vary
    s_i = show_outlay
    s_j = show_outlay
    s_k = show_outlay
    S_i = entries[i].show_pool_total
    S_j = entries[j].show_pool_total
    S_k = entries[k].show_pool_total
    S_ijk = S_i + S_j + S_k

    player_place_total_outlay = sum([p_l(i) for i in range(len(entries))])

    first = ((Q * (P + player_place_total_outlay)) - (p_i + p_j + P_ij)) / 2
    second = (p_i / (p_i + P_i)) + (p_j / (p_j + P_j))

    player_show_total_outlay = sum([s_l(i) for i in range(len(entries))])
    third = ((Q * (S + player_show_total_outlay)) - (s_i + s_j + s_k + S_ijk)) / 3

    fourth = (s_i / (s_i + S_i)) + (s_j / (s_j + S_j)) + (s_k / (s_k + S_k))

    outer_total: float = 0
    for i_2 in range(len(entries)):
        if i_2 == i or i_2 == j or i_2 == k:
            continue

        inner_total: float = 0
        
        for i_3 in range(len(entries)):
            if i_3 == i_2 or i_3 == j:
                continue

            inner_total += p_l(i_3)
        
        outer_total += (s_l(i_2) - inner_total)

    fifth = outer_total
    
    total = first * second + third * fourth + w0 - fifth
    
    return total

def hyperopt_objective(params) -> float:
    expected_utility = get_place_show_all_utility(
        params['race'],
        params['place_outlay'],
        params['show_outlay'],
        params['total_wealth'],
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
        'race': race,
        'place_outlay': hyperopt.hp.uniform('place_outlay', 2, max_possible_bet),
        'show_outlay': hyperopt.hp.uniform('show_outlay', 2, max_possible_bet),
        'total_wealth': max_spend,
    }


    best = hyperopt.fmin(
        hyperopt_objective,
        space=params_space,
        algo=hyperopt.tpe.suggest,
        max_evals=50,
        trials=trials,
    )

    total_outlay = best['total_wealth']
    place_outlay = best['place_outlay']
    show_outlay = best['show_outlay']

    expected_value = get_place_show_all_utility(place_outlay, show_outlay, total_outlay)

    return DrZPlaceShowResult(
        total_outlay=total_outlay,
        place_outlay=place_outlay,
        show_outlay=show_outlay,
        expected_value=expected_value,
    )