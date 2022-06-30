#!/usr/bin/env python3


import math

import app.lib.clickhouse2pandas as ch2pd
from app.core.config import settings

connection_url = settings.CLICKHOUSE_URI


def get_race_dfs():
    train_df = ch2pd.select(connection_url, "SELECT * FROM race_db.all_races LIMIT 40")
    test_df = ch2pd.select(
        connection_url, "SELECT * FROM race_db.all_races OFFSET 10 LIMIT 100"
    )

    return (train_df, test_df)


def get_complete_race_df():
    train_df = ch2pd.select(connection_url, "SELECT * FROM race_db.all_races")
    train_df_horse = ch2pd.select(connection_url, "SELECT * FROM race_db.starters")

    train_df = train_df.rename(columns={"id": "race_id"})
    train_df_horse = train_df_horse.rename(columns={"id": "horse_id"})

    train_df_horse = train_df_horse.merge(train_df, how="left", on="race_id")

    set_len = len(train_df_horse)

    test_df = train_df_horse.tail(math.floor(set_len / 2))
    return train_df_horse.head(math.ceil(set_len / 2)), test_df


def get_starters_dfs():
    train_df = ch2pd.select(connection_url, "SELECT * FROM race_db.starters LIMIT 400")
    test_df = ch2pd.select(connection_url, "SELECT * FROM race_db.starters OFFSET 401")

    test_df = test_df.drop(
        ["winner", "finish_position", "wagering_position", "official_position"], axis=1
    )

    return (train_df, test_df)


def get_starters_complete_test():
    test_df = ch2pd.select(connection_url, "SELECT * FROM race_db.starters")

    return test_df
