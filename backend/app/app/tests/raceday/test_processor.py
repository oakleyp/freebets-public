import itertools
import random
from datetime import timedelta
from typing import Callable, Generator, Iterable, List
from unittest import mock

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.lib.schemas.live_racing import TrackWithRaceDetails
from app.models.bet import Bet
from app.models.race import Race
from app.models.race_entry import RaceEntry
from app.raceday.processor import DefaultNextCheckGen, RaceDayProcessor, RaceWatcher
from app.raceday.race_canonical import LiveTrackBasicCanonical
from app.tests.utils.race_data import (
    create_starters_n,
    create_track_with_race_details,
    create_track_with_race_details_n,
)


def flatmap(func: Callable, *iterable) -> Iterable:
    return itertools.chain.from_iterable(map(func, *iterable))


@pytest.fixture
def clean_db() -> Generator:
    db: Session = SessionLocal()
    # Clear bets
    db.query(Bet).delete()
    # Clear races and entries
    db.query(RaceEntry).delete()
    db.query(Race).delete()

    yield db

    db.close()


@mock.patch("app.raceday.processor.LiveRacingCrawler")
def test_ingest_races_shallow(mock_lrc, clean_db: Session):
    mock_lrc_inst = mock.MagicMock()
    mock_lrc.return_value = mock_lrc_inst

    rdproc = RaceDayProcessor(
        clean_db,
        lookahead_base=timedelta(days=0),
        lookahead_limit=timedelta(days=1),
        resilient=False,
    )
    time_context = rdproc._active_time_context()

    tracks_to_ingest: List[TrackWithRaceDetails] = create_track_with_race_details_n(10)
    tracks_out_of_range: List[TrackWithRaceDetails] = [
        create_track_with_race_details(
            race_details_args={
                "adjacent_dt_start": time_context.lookahead_start
                - timedelta(minutes=2),
                "adjacent_increment": "seconds",
            }
        ),
        create_track_with_race_details(
            race_details_args={
                "adjacent_dt_start": time_context.lookahead_end + timedelta(minutes=2),
                "adjacent_increment": "seconds",
            }
        ),
    ]

    mock_lrc_inst.get_all_track_races_shallow.return_value = (
        tracks_to_ingest + tracks_out_of_range
    )

    # Create existing races for the first track to check that they are not duplicated on next ingest
    existing_races = LiveTrackBasicCanonical(tracks_to_ingest[0]).convert()
    clean_db.add_all(existing_races)
    clean_db.commit()

    rdproc._ingest_races_shallow(time_context)
    mock_lrc_inst.get_all_track_races_shallow.assert_called_with(
        target_date=time_context.now.date()
    )

    ingested_races: List[Race] = clean_db.query(Race).all()

    post_times = []

    # print(time_context.lookahead_start, time_context.lookahead_end)

    # Should ingest all races in range, none outside
    for track in tracks_to_ingest:
        for race in track.races:
            if (
                race.postTime >= time_context.lookahead_start
                and race.postTime < time_context.lookahead_end
            ):
                post_times.append(race.postTime)

    assert post_times == [race.post_time for race in ingested_races]

    # Should not watch races out of range
    should_watch_races = [
        race
        for race in ingested_races
        if race.post_time >= time_context.lookahead_start
        and race.post_time < time_context.lookahead_end
    ]

    # Test watchers were set accordingly
    for race in should_watch_races:
        assert rdproc.watching_races[race.id] is not None
        assert rdproc.watching_races[race.id].post_time == race.post_time
        assert rdproc.watching_races[race.id].race_id == race.id

    # Test no watchers set for other races
    assert list(rdproc.watching_races.keys()) == [
        race.id for race in should_watch_races
    ]


@pytest.mark.skip(reason="Need to update")
@mock.patch("app.raceday.processor.LiveRacingCrawler")
def test_process_once(mock_lrc, clean_db: Session):
    mock_ksc_inst = mock.MagicMock()
    mock_lrc.return_value = mock_ksc_inst

    rdproc = RaceDayProcessor(
        clean_db,
        lookahead_base=timedelta(days=0, minutes=10),
        lookahead_limit=timedelta(days=1),
        race_refresh_interval=timedelta(days=0, minutes=10),
        resilient=False,
    )
    time_context = rdproc._active_time_context()

    # Setup _ingest_races_shallow - there's already a test for this method,
    # just using the method to seed the db.

    tracks_to_ingest: List[TrackWithRaceDetails] = create_track_with_race_details_n(10)
    tracks_out_of_range: List[TrackWithRaceDetails] = [
        create_track_with_race_details(
            race_details_args={
                "adjacent_dt_start": time_context.lookahead_start
                - timedelta(minutes=2),
                "adjacent_increment": "seconds",
            }
        ),
        create_track_with_race_details(
            race_details_args={
                "adjacent_dt_start": time_context.lookahead_end + timedelta(minutes=2),
                "adjacent_increment": "seconds",
            }
        ),
    ]

    mock_ksc_inst.get_all_track_races_shallow.return_value = (
        tracks_to_ingest + tracks_out_of_range
    )
    rdproc._ingest_races_shallow(time_context)

    # Setup _get_race_entries

    ingested_races: List[Race] = clean_db.query(Race).all()
    ingested_races_entry_map = {
        f"{race.track_code}-{race.race_number}-{race.race_type}": create_starters_n(
            random.randint(6, 18)
        )
        for race in ingested_races
    }

    def get_race_entries(track_code: str, race_number: int, race_type: str):
        return ingested_races_entry_map[f"{track_code}-{race_number}-{race_type}"]

    mock_ksc_inst.get_race_entries.side_effect = get_race_entries

    # Setup the expected list of watchers
    watchers = [
        RaceWatcher(
            race_id=race.id,
            post_time=race.post_time,
            next_check_time=time_context.now,
            last_checked_time=None,
        )
        for race in ingested_races
    ]

    # Should not watch races out of range
    should_watch_races = [
        race
        for (watcher, race) in zip(watchers, ingested_races)
        if rdproc._should_watch_race(race, time_context)
        and DefaultNextCheckGen().get_next_check_time(watcher, time_context) is not None
    ]

    assert len(should_watch_races) > 0

    # Call the method
    with mock.patch.object(RaceDayProcessor, "_refresh_race_bets", return_value=None):
        with mock.patch.object(
            RaceDayProcessor, "_refresh_race_predictions", return_value=None
        ):
            with mock.patch.object(
                RaceDayProcessor, "_ingest_races_shallow", return_value=None
            ) as mock_ing_races_shallow:
                proc_result = rdproc.process_once(time_context)

                mock_ing_races_shallow.assert_called_once()

    # Test RaceWatchers were updated

    assert list(rdproc.watching_races.keys()) == [
        race.id for race in should_watch_races
    ]

    for race in should_watch_races:
        watcher = rdproc.watching_races.get(race.id)
        assert watcher is not None
        assert watcher.next_check_time == DefaultNextCheckGen().get_next_check_time(
            watcher, time_context
        )

    min_nct = (rdproc._get_min_watcher_nct() - time_context.now).total_seconds()

    assert min_nct > 0, (
        f"min_nct is negative: time_context = {time_context.now} "
        f"culprits = {[watcher for watcher in rdproc.watching_races.values() if watcher.next_check_time < time_context.now]}"
    )

    # Test result nct is expected
    assert proc_result == min_nct

    # Test that RaceWatchers with a next_check_time less than or at the current time
    # trigger a refresh of data for the race

    mock_ksc_inst.get_race_entries.assert_has_calls(
        [
            mock.call(race.track_code, race.race_number, race.race_type)
            for race in should_watch_races
        ]
    )
