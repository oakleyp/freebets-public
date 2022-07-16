import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

import numpy as np
from wonderwords import RandomWord

from app.lib.schemas.live_racing import (
    EntryPoolTotals,
    Featured,
    RaceDetails,
    RacePoolTotals,
    RaceWithStarterDetails,
    StarterDetails,
    SurfaceConditions,
    TrackWithRaceAndStarterDetails,
    TrackWithRaceDetails,
)
from app.tests.utils.utils import random_datetime_in_range, random_lower_string

rand_word = RandomWord()


def create_uniform_range_for_time_unit(n: int, unit: str) -> List[float]:
    max: float = 0

    if unit == "days":
        max = 365
    elif unit == "hours":
        max = 24
    elif unit == "minutes":
        max = 60
    elif unit == "seconds":
        max = 60
    else:
        raise ValueError("Invalid unit provided (%s)." % unit)

    return sorted(np.random.uniform(0, max, n).tolist())


def create_random_odds_str() -> str:
    """e.g. '5/2'"""
    return f"{random.randint(1, 50)}/{random.randint(1,3)}"


def create_random_horse_name() -> str:
    return " ".join(
        rand_word.random_words(
            random.randint(1, 2), include_parts_of_speech=["noun", "adjective"]
        )
    ).title()


def create_race_details_n(
    n: int,
    *,
    adjacent: bool = False,
    adjacent_dt_start: datetime = None,
    adjacent_increment: str = "minutes",
    **race_detail_args,
) -> List[RaceDetails]:
    start = adjacent_dt_start
    if not start:
        start = datetime.now(timezone.utc)

    if not adjacent:
        return [create_race_details(i + 1, **race_detail_args) for i in range(n)]

    uniform_rng = create_uniform_range_for_time_unit(n, adjacent_increment)

    results: List[RaceDetails] = []

    curr_start = start
    curr_end = start

    for i in range(n):
        curr_end = curr_start + timedelta(**{adjacent_increment: uniform_rng[i]})
        results.append(
            create_race_details(
                i + 1, dt_range=(curr_start, curr_end), precision_mod=adjacent_increment
            )
        )
        curr_start = curr_end

    return results


def create_race_details(
    race_number: int,
    *,
    dt_range: Tuple[datetime, datetime] = None,
    status: str = "Open",
    current_race: bool = False,
    precision_mod: str = "minutes",
) -> RaceDetails:
    effective_dt_range = dt_range
    if not effective_dt_range:
        effective_dt_range = (
            (
                datetime.now(timezone.utc),
                datetime.now(timezone.utc) + timedelta(hours=2),
            ),
        )

    post_time = random_datetime_in_range(*dt_range, precision_modifier=precision_mod)

    print(*effective_dt_range, post_time)

    return RaceDetails(
        raceNumber=race_number,
        raceDate=random_datetime_in_range(*effective_dt_range).date(),
        postTime=post_time,
        postTimeStamp=post_time.timestamp() * 1000,
        mtp=99,
        status=status,
        distance=random_lower_string(),
        distanceLong=random_lower_string(),
        surface=random_lower_string(),
        surfaceLabel=random_lower_string(),
        ageRestrictions=random_lower_string(),
        sexRestrictions=random_lower_string(),
        raceDescription=random_lower_string(),
        wagers=random_lower_string(),
        country=random_lower_string(length=3),
        carryover=[],
        currentRace=current_race,
        hasExpertPick=True,
    )


def create_track_with_race_details_n(
    n: int, race_details_args: Dict[str, Any] = {}, races_per_track: int = 2
) -> List[TrackWithRaceDetails]:
    return [
        create_track_with_race_details(
            race_details_args=race_details_args, races_per_track=races_per_track
        )
        for _ in range(n)
    ]


def create_track_with_race_details(
    race_details_args: Dict[str, Any] = {}, races_per_track: int = 2,
) -> TrackWithRaceDetails:
    return TrackWithRaceDetails(
        brisCode=random_lower_string(length=3),
        name=random_lower_string(),
        type="Thoroughbred",
        status="Open",
        currentRaceNumber=1,
        hostCountry=random_lower_string(length=3),
        hasBetTypes=True,
        allowsConditionalWagering=True,
        surfaceConditions=[SurfaceConditions(type="dirt", condition="fast",)],
        featured=[Featured(featuredTrackId=1, label=random_lower_string(), races=3,)],
        races=create_race_details_n(
            races_per_track, adjacent=True, **race_details_args
        ),
    )


def create_track_with_race_and_starter_details_n(
    n: int,
) -> List[TrackWithRaceAndStarterDetails]:
    return [create_track_with_race_and_starter_details() for _ in range(n)]


def create_track_with_race_and_starter_details(
    race_details_args: Dict[str, Any] = {}
) -> TrackWithRaceAndStarterDetails:
    return TrackWithRaceAndStarterDetails(
        brisCode=random_lower_string(length=3),
        name=random_lower_string(),
        type="Thoroughbred",
        status="Open",
        currentRaceNumber=1,
        hostCountry=random_lower_string(length=3),
        hasBetTypes=True,
        allowsConditionalWagering=True,
        surfaceConditions=[SurfaceConditions(type="dirt", condition="fast",)],
        featured=[Featured(featuredTrackId=1, label=random_lower_string(), races=3,)],
        races=create_race_and_starter_details_n(2, adjacent=True, **race_details_args),
    )


def create_race_and_starter_details_n(
    n: int,
    *,
    adjacent: bool = False,
    adjacent_dt_start: datetime = None,
    adjacent_increment: str = "minutes",
    **race_detail_args,
) -> List[RaceWithStarterDetails]:
    start = adjacent_dt_start

    if not start:
        start = datetime.now(timezone.utc)

    if not adjacent:
        return [
            create_race_and_starter_details(i + 1, **race_detail_args) for i in range(n)
        ]

    uniform_rng = create_uniform_range_for_time_unit(n, adjacent_increment)

    results: List[RaceDetails] = []

    curr_start = start
    curr_end = start

    for i in range(n):
        curr_end = curr_start + timedelta(**{adjacent_increment: uniform_rng[i]})
        results.append(
            create_race_and_starter_details(
                i + 1, dt_range=(curr_start, curr_end), precision_mod=adjacent_increment
            )
        )
        curr_start = curr_end

    return results


def create_race_and_starter_details(
    race_number: int,
    *,
    dt_range: Tuple[datetime, datetime] = None,
    status: str = "Open",
    current_race: bool = False,
    precision_mod: str = "minutes",
) -> RaceWithStarterDetails:
    effective_dt_range = dt_range
    if not effective_dt_range:
        effective_dt_range = (
            datetime.now(timezone.utc),
            datetime.now(timezone.utc) + timedelta(hours=2),
        )

    post_time = random_datetime_in_range(
        *effective_dt_range, precision_modifier=precision_mod
    )

    print(*effective_dt_range, post_time)

    return RaceWithStarterDetails(
        raceNumber=race_number,
        raceDate=random_datetime_in_range(*effective_dt_range).date(),
        postTime=post_time,
        postTimeStamp=post_time.timestamp() * 1000,
        mtp=99,
        status=status,
        distance=random_lower_string(),
        distanceLong=random_lower_string(),
        surface=random_lower_string(),
        surfaceLabel=random_lower_string(),
        ageRestrictions=random_lower_string(),
        sexRestrictions=random_lower_string(),
        raceDescription=random_lower_string(),
        wagers=random_lower_string(),
        country=random_lower_string(length=3),
        carryover=[],
        currentRace=current_race,
        hasExpertPick=True,
        starters=create_starters_n(random.randint(6, 15)),
    )


def create_starters_n(n: int) -> List[StarterDetails]:
    starters = [create_starter(n, n) for n in range(n)]

    active_starters = [starter for starter in starters if not starter.scratched]

    # Fix odds to sum to 1
    odds = [random.randint(3, 50) for _ in active_starters]

    odds_sum = sum(odds)
    odds = [odds / odds_sum for odds in odds]

    for starter, odds in zip(active_starters, odds):
        starter.morningLineOdds = f"{1/odds}/1"
        starter.profitlineOdds = f"{1/odds}/1"
        starter.liveOdds = f"{1/odds}/1"

    return starters


def create_starter(horse_num: int, pp: int) -> StarterDetails:
    return StarterDetails(
        startId=random.randint(1, 9999),
        entryId=random.randint(10000, 99999),
        postPosition=pp,
        programNumber=str(horse_num),
        sortableProgramNumber=horse_num,
        bettingInterest=random.randint(0, 12),
        name=create_random_horse_name(),
        oddsTrend=None,
        oddsRank=random.randint(0, 12),
        yob=str(random.randint(2010, 2022)),
        whelpDate=None,
        color=random_lower_string(length=12),
        sex=random_lower_string(length=12),
        whereBred=random_lower_string(length=12),
        equipment=random_lower_string(length=12),
        medication=random_lower_string(length=12),
        formattedMedication=random_lower_string(length=12),
        weight=random.randint(0, 9000),
        overweightAmount=None,  # TODO ?
        jockeyName=random_lower_string(length=12),
        jockeyFirstName=random_lower_string(length=12),
        jockeyMiddleName=random_lower_string(length=12),
        jockeyLastName=random_lower_string(length=12),
        jockeyId=random_lower_string(length=12),
        trainerName=random_lower_string(length=12),
        trainerFirstName=random_lower_string(length=12),
        trainerMiddleName=random_lower_string(length=12),
        trainerLastName=random_lower_string(length=12),
        trainerId=random.randint(0, 9000),
        ownerName=random_lower_string(length=12),
        ownerFirstName=random_lower_string(length=12),
        ownerMiddleName=random_lower_string(length=12),
        ownerLastName=random_lower_string(length=12),
        ownerId=random.randint(0, 9000),
        colorDescription=random_lower_string(length=12),
        sireId=random.randint(0, 9000),
        sireName=random_lower_string(length=12),
        damId=random.randint(0, 9000),
        damName=random_lower_string(length=12),
        priorRunStyle=random_lower_string(length=12),
        speedPoints=random.randint(0, 9000),
        averagePaceE1=random.randint(0, 9000),
        averagePaceE2=random.randint(0, 9000),
        averagePaceLP=random.randint(0, 9000),
        averageSpeed=random.randint(0, 9000),
        averageSpeedLast3=random.randint(0, 9000),
        bestSpeedAtDistance=random.randint(0, 9000),
        daysOff=random.randint(0, 9000),
        averageClass=random.randint(0, 9000),
        lastClass=random.randint(0, 9000),
        primePower=random.randint(0, 9000),
        horseClaimingPrice=random.randint(0, 9000),
        powerRating=None,  # TODO: All these ?
        bestSpeed=None,
        earlyPace=None,
        midPace=None,
        latePace=None,
        commentsPositive=[random_lower_string() for _ in range(3)],
        commentsNegative=[random_lower_string() for _ in range(3)],
        silkStatus=random_lower_string(length=12),
        silkUriPath=random_lower_string(length=12),
        expertPickRank=None,
        blinkers=None,
        morningLineOdds=create_random_odds_str(),
        alsoEligible=[False, None, True][random.randint(0, 2)],
        mainTrackOnly=[False, None, True][random.randint(0, 2)],
        morningLineFavorite=[False, None, True][random.randint(0, 2)],
        liveOddsFavorite=[False, None, True][random.randint(0, 2)],
        jockeyChange=[False, None, True][random.randint(0, 2)],
        weightChange=[False, None, True][random.randint(0, 2)],
        weightCorrection=[False, None, True][random.randint(0, 2)],
        otherChange=[False, None, True][random.randint(0, 2)],
        profitlineOdds=create_random_odds_str(),
        liveOdds=create_random_odds_str(),
        scratched=[False, False, False, False, False, False][random.randint(0, 5)],
    )


def create_entry_pool_totals(
    entry: StarterDetails, pool_total: int = 2_000_000, num_betters: int = None
) -> EntryPoolTotals:
    entry_odds_frac = 1 / entry.liveOddsNumeric()

    def rand_variance():
        return 1 / random.randint(2, 5)

    return EntryPoolTotals(
        program_no=entry.programNumber,
        win_total=(pool_total * entry_odds_frac) + entry.liveOddsNumeric() * rand_variance() * pool_total,
        place_total=(pool_total * entry_odds_frac) + entry.liveOddsNumeric() * rand_variance() * pool_total,
        show_total=(pool_total * entry_odds_frac) + entry.liveOddsNumeric() * rand_variance() * pool_total,
    )


def create_race_pool_totals(
    race: RaceWithStarterDetails,
    current_pool_totals: RacePoolTotals = None,
    num_betters: int = None,
) -> RacePoolTotals:
    if not current_pool_totals:
        pool_total = random.randint(30_000, 50_000)
    else:
        pool_total = (
            current_pool_totals.win_total
            + current_pool_totals.show_total
            + current_pool_totals.place_total
        )

    entries_totals = {
        entry.programNumber: create_entry_pool_totals(entry, pool_total=pool_total)
        for entry in race.starters
    }

    if pool_total == 0:
        print("WTF pool total", current_pool_totals, pool_total)

    win_total: float = 0
    place_total: float = 0
    show_total: float = 0

    for totals in entries_totals.values():
        win_total += totals.win_total
        place_total += totals.place_total
        show_total += totals.show_total

    return RacePoolTotals(
        win_total=win_total,
        place_total=place_total,
        show_total=show_total,
        entries_to_pools_map=entries_totals,
    )
