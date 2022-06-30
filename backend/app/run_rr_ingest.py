from datetime import date, datetime, timezone
from typing import List, Tuple
from app.ml.race_results_proc import RaceResultSearchConfig, RaceResultsProcessor, TrackDataDescriptor
import csv
import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def track_race_dates_from_csv(file: str) -> List[TrackDataDescriptor]:
    result: List[TrackDataDescriptor] = []

    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        # 10/29/2022
        dt_format = "%m/%d/%Y"
        for row in reader:
            date_ranges: List[Tuple[date, date]] = []

            for date_rg in row['dates'].split('|'):
                rg = date_rg.split('-')

                if len(rg) > 1:
                    (start, end) = rg
                else:
                    start = rg[0]
                    end = rg[0]

                date_ranges.append(
                    (
                        datetime.strptime(start, dt_format).astimezone(timezone.utc).date(),
                        datetime.strptime(end, dt_format).astimezone(timezone.utc).date()
                    )
                )

            result.append(TrackDataDescriptor(
                track_name=row['track_name'],
                track_code=row['track_code'],
                date_ranges=date_ranges,
            ))

    return result


track_descs = track_race_dates_from_csv('./race_dates.csv')
rr_cfg = RaceResultSearchConfig(
    track_list=track_descs
)
rr_proc = RaceResultsProcessor(date.fromisoformat("2022-03-01"), date.fromisoformat("2022-04-08"), rr_cfg)
