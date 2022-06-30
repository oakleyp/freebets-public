from typing import Optional

from pydantic import BaseModel


class RaceEntryDf(BaseModel):
    """
    Defines the categorical features that are shared by both the model
    training data source and live data source in `RacePredictor`.

    This list is generally limited by the live data available on race day,
    since historical race data is easier to find, and in greater detail.

    These fields/features, and their data format must match as closely as possible
    in order for the model to work effectively at making predictions against live data.

    Utils for munging this data from the live source's format into the trained model
    format are found in `data_utils` in this module.
    """

    horse_id: str
    race_id: str
    #     last_raced_date             3000 non-null   object
    #  3   last_raced_days_since       3000 non-null   float64
    #  4   last_raced_track            3000 non-null   object
    #  5   last_raced_track_canonical  3000 non-null   object
    #  6   last_raced_track_state      3000 non-null   object
    #  7   last_raced_track_country    3000 non-null   object
    #  8   last_raced_track_name       3000 non-null   object
    #  9   last_raced_number           3000 non-null   float64
    #  10  last_raced_position         3000 non-null   float64
    last_raced_days_since: int
    # program: str
    # entry_program: str
    last_raced_days_since: Optional[float]
    program: Optional[str]
    entry: Optional[int]
    # entry_program: Optional[str]
    horse: Optional[str]
    jockey_first: Optional[str]
    jockey_last: Optional[str]
    trainer_first: Optional[str]
    trainer_last: Optional[str]
    owner: Optional[str]
    weight: Optional[int]
    medication_equipment: Optional[str]
    claim_price: Optional[int]
    pp: Optional[int]
    # jockey_allowance: Optional[int]
    # claimed: Optional[float]
    # new_trainer_name: Optional[str]
    # new_owner_name: Optional[str]
    # position_dead_heat: Optional[int]
    disqualified: Optional[int]
    odds: Optional[float]
    favorite: Optional[float]
    # choice: Optional[int]
    sire: Optional[str]
    dam: Optional[str]
    where_bred: Optional[str]
    color: Optional[str]
    sex: Optional[str]
    dob: Optional[str]
    date: Optional[str]
    # track: Optional[str]
    track_canonical: Optional[str]
    # track_state: Optional[str]
    track_country: Optional[str]
    # track_name: Optional[str]
    number: Optional[int]
    # TODO: Maybe?
    # breed: Optional[str]
    # type: Optional[str]
    code: Optional[str]
    # race_name: Optional[str]
    # grade: Optional[float]
    # black_type: Optional[str]
    # conditions: Optional[str]
    # TODO Need to pull
    # min_claim: Optional[float]
    # max_claim: Optional[float]
    # restrictions: Optional[str]
    # min_age: Optional[float]
    # max_age: Optional[float]
    age_code: Optional[str]
    # sexes: Optional[float]
    sexes_code: Optional[str]
    female_only: Optional[float]
    # state_bred: Optional[float]
    distance_text: Optional[str]
    distance_compact: Optional[str]
    feet: Optional[float]
    furlongs: Optional[float]
    # exact: Optional[float]
    # run_up: Optional[float]
    # temp_rail: Optional[float]
    surface: Optional[str]
    # course: Optional[str]
    # TODO Maybe pull these
    # track_condition: Optional[str]
    # scheduled_surface: Optional[int]
    # scheduled_course: Optional[int]
    # off_turf: Optional[float]
    # format: Optional[str]
    # TODO Can pull these:
    # track_record_holder: Optional[int]
    # track_record_time: Optional[int64]
    # track_record_millis: Optional[int64]
    # track_record_date: Optional[int64]
    # TODO Need to pull
    # purse: Optional[float]
    # purse_text: Optional[str]
    # available_money: Optional[str]
    # purse_enhancements: Optional[str]
    # value_of_race: Optional[str]
    # weather: Optional[str]
    # wind_speed: Optional[float]
    # wind_direction: Optional[str]
    # post_time: Optional[datetime]
    # start_comments: Optional[str]
    # timer: Optional[str]
    # dead_heat: Optional[int64]
    number_of_runners: Optional[int]
    # total_wps_pool: Optional[float]
