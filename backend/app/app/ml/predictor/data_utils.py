import logging
import re
from datetime import date
from typing import Callable, Dict, Optional

import pandas as pd
from pydantic import BaseModel
from regex import Pattern

from app.models.race import Race
from app.models.race_entry import RaceEntry

from .race_entry_canon import RaceEntryDf

logger = logging.getLogger(__name__)


def _canon_meds_equipment(entry: RaceEntry) -> Optional[str]:
    """Joins live meds/equipment to string format used in training data source."""
    meds = entry.medication
    eqp = entry.equipment

    if not meds and not eqp:
        return None

    return " ".join(list(filter(lambda x: x, [meds, eqp])))


def canon_race_breed(race: Race) -> Optional[str]:
    """
    Determine the breed code used in the training data source
    from the live source's race `type`.
    """
    if race.type == "Thoroughbred":
        return "TB"
    else:
        return None


RACE_TYPE_CODES = [
    "SPO",
    "IHS",
    "AOC",
    "OCH",
    "SOC",
    "MOC",
    "MSA",
    "OCS",
    "SPC",
    "WMC",
    "INH",
    "MSW",
    "FCN",
    "INS",
    "CLH",
    "OCL",
    "SPF",
    "SPT",
    "STA",
    "UNK",
    "SPR",
    "STH",
    "ATR",
    "CST",
    "HCS",
    "MCL",
    "WCL",
    "FTR",
    "MTR",
    "STS",
    "MST",
    "CHP",
    "INV",
    "MDT",
    "CON",
    "DTR",
    "MCH",
    "ALW",
    "CLM",
    "FUT",
    "HCP",
    "MAT",
    "MDN",
    "STK",
    "TRL",
    "DBY",
    "FNL",
    "MCH",
    "STK",
    "TRL",
]


def get_race_type_code(race: Race) -> Optional[str]:
    """Return the race type code from the race description, if recognized."""
    if race.description is None or len(race.description) < 3:
        return None

    code = race.description[0:3]

    if code.upper() in RACE_TYPE_CODES:
        return code.upper()


def canon_age_code(race: Race) -> Optional[str]:
    """
    Return the age code used in the training data format from
    the live source's `age_restrictions`.
    """
    if race.age_restrictions is None or not len(race.age_restrictions):
        return None

    return race.age_restrictions.replace("yo", "")


# "4 1/2 F" | "4 F"
FURLONGS_PATTERN = re.compile("(?P<whole>\d+)(?: (?P<num>\d+)\/(?P<denom>\d+))* F") # noqa
# "4 1/2 M" | "4 M"
MILES_PATTERN = re.compile("(?P<whole>\d+)(?: (?P<num>\d+)\/(?P<denom>\d+))* M") # noqa
# "4 1/2 Y" | "4 Y"
YARDS_PATTERN = re.compile("(?P<whole>\d+)(?: (?P<num>\d+)\/(?P<denom>\d+))* Y") # noqa

FURLONGS_CONV_TABLE: Dict[Pattern, Callable[[float], float]] = {
    FURLONGS_PATTERN: lambda x: x,
    MILES_PATTERN: lambda x: x * 7.99998,
    YARDS_PATTERN: lambda x: x * 0.00454545,
}


class DistanceMapping(BaseModel):
    feet: float
    furlongs: float


def parse_distance(distance_comp: str) -> Optional[DistanceMapping]:
    """
    Return a `DistanceMapping` from the compact distance string
    (e.g. "3 1/2 F 120 Y"), if parseable.
    """
    if not len(distance_comp):
        return None

    result_furlongs: float = 0

    patterns = [FURLONGS_PATTERN, MILES_PATTERN, YARDS_PATTERN]

    for pattern in patterns:
        match = pattern.match(distance_comp)
        if match:
            local_sum: float = 0

            if match.group("whole"):
                local_sum += float(match.group("whole"))

            if match.group("num") and match.group("denom"):
                local_sum += float(match.group("num")) / float(match.group("denom"))

            result_furlongs += FURLONGS_CONV_TABLE[pattern](local_sum)

    return DistanceMapping(feet=result_furlongs * 660, furlongs=result_furlongs,)


def try_parse_distance(distance_comp: Optional[str]) -> Optional[DistanceMapping]:
    """Error-handling/logging wrapper for `parse_distance."""
    if distance_comp is None:
        return None

    try:
        return parse_distance(distance_comp)
    except Exception as e:
        logger.error("Failed parsing distance str %s - %s", distance_comp, e)
        return None


def create_race_entry_df_from_race(race: Race) -> pd.DataFrame:
    """
    Creates a DataFrame from the live source's race format,
    converting fields to match the training data source's canonical format
    (RaceEntryDf) where needed.
    """
    results = []

    entries_sorted = sorted(race.entries, key=lambda e: e.id)

    for entry in entries_sorted:
        entry: RaceEntry
        jockey_first_last = (None, None)
        trainer_first_last = (None, None)

        if entry.jockey_name and len(entry.jockey_name):
            jnames = entry.jockey_name.split(" ")
            jockey_first_last = (jnames[0], jnames[-1])

        if entry.trainer_name and len(entry.trainer_name):
            tnames = entry.trainer_name.split(" ")
            trainer_first_last = (tnames[0], tnames[-1])

        distance_mapping = try_parse_distance(race.distance)

        results.append(
            RaceEntryDf(
                horse_id=entry.id,
                race_id=race.id,
                last_raced_days_since=entry.days_off,
                program=entry.program_no,
                entry=entry.sortable_program_no,
                jockey_first=jockey_first_last[0],
                jockey_last=jockey_first_last[1],
                trainer_first=trainer_first_last[0],
                trainer_last=trainer_first_last[1],
                owner=entry.owner_name,
                weight=entry.weight,
                dob=date(int(entry.yob), 1, 1).isoformat() if entry.yob else None,
                color=entry.color,
                sex=entry.sex,
                where_bred=entry.where_bred,
                sire=entry.sire_name,
                dam=entry.dam_name,
                medication_equipment=_canon_meds_equipment(entry),
                claim_price=entry.horse_claiming_price,
                pp=entry.post_pos,
                disqualified=entry.scratched,
                odds=entry.latest_odds(),
                favorite=float(entry.live_odds_fav or entry.morning_line_fav or 0),
                date=race.race_date.isoformat(),
                track_canonical=race.track_code.upper(),
                track_country=race.track_country.upper(),
                number=race.race_number,
                type=get_race_type_code(race),
                age_code=canon_age_code(race),
                sexes_code=race.sex_restrictions,
                female_only=float(race.sex_restrictions == "F"),
                distance_text=race.distance_long,
                distance_compact=race.distance,
                feet=(distance_mapping and distance_mapping.feet),
                furlongs=(distance_mapping and distance_mapping.furlongs),
                surface=race.surface_label,
                number_of_runners=len(
                    [entry for entry in race.entries if not entry.scratched]
                ),
            ).dict()
        )

    return pd.DataFrame(results)
