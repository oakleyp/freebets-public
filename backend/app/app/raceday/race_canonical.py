"""
Defines structures and classes used to convert Race, Track, and Entry data
from their live format/schema into their canonical (DB) formats.
"""

from datetime import datetime, timezone
from typing import List

from app.lib.schemas.live_racing import (
    RaceDetails,
    RaceWithStarterDetails,
    StarterDetails,
    TrackWithRaceAndStarterDetails,
    TrackWithRaceDetails,
)
from app.models.race import Race
from app.models.race_entry import RaceEntry


def fix_post_tz(post_time: datetime) -> datetime:
    """Convert the given post_time to utc if not already in utc."""
    if post_time.tzinfo is not None:
        return post_time.astimezone(timezone.utc)

    return datetime.fromtimestamp(post_time.timestamp, timezone.utc)


class LiveTrackExtendedCanonical:
    def __init__(self, track: TrackWithRaceAndStarterDetails) -> None:
        self.track: TrackWithRaceAndStarterDetails = track

    def convert(self) -> List[Race]:
        results = []

        for race in self.track.races:
            results.append(LiveRaceExtendedCanonical(self.track, race).convert())

        return results


class LiveTrackBasicCanonical:
    def __init__(self, track: TrackWithRaceDetails) -> None:
        self.track: TrackWithRaceDetails = track

    def convert(self) -> List[Race]:
        results = []

        for race in self.track.races:
            results.append(LiveRaceBasicCanonical(self.track, race).convert())

        return results


class LiveRaceExtendedCanonical:
    def __init__(
        self, track: TrackWithRaceAndStarterDetails, race: RaceWithStarterDetails
    ) -> None:
        self.race: RaceWithStarterDetails = race
        self.track: TrackWithRaceAndStarterDetails = track

    def convert(self) -> Race:
        race = self.race
        track = self.track

        new_race: Race = Race(
            race_number=race.raceNumber,
            race_date=race.raceDate,
            post_time=fix_post_tz(race.postTime),
            post_time_stamp=race.postTimeStamp,
            mtp=race.mtp,
            status=race.status,
            distance=race.distance,
            distance_long=race.distanceLong,
            surface=race.surface,
            surface_label=race.surfaceLabel,
            age_restrictions=race.ageRestrictions,
            description=race.raceDescription,
            wagers=race.wagers,
            country=race.country,
            track_code=track.brisCode,
            track_country=track.hostCountry,
            race_type=track.type,
            current_race=race.currentRace,
        )

        for entry in race.starters:
            new_race.entries.append(LiveRaceEntryCanonical(entry).convert())

        return new_race


class LiveRaceBasicCanonical:
    def __init__(self, track: TrackWithRaceDetails, race: RaceDetails) -> None:
        self.track: TrackWithRaceDetails = track
        self.race: RaceDetails = race

    def convert(self) -> Race:
        race = self.race
        track = self.track

        return Race(
            race_number=race.raceNumber,
            race_date=race.raceDate,
            post_time=fix_post_tz(race.postTime),
            post_time_stamp=race.postTimeStamp,
            mtp=race.mtp,
            status=race.status,
            distance=race.distance,
            distance_long=race.distanceLong,
            surface=race.surface,
            surface_label=race.surfaceLabel,
            age_restrictions=race.ageRestrictions,
            description=race.raceDescription,
            wagers=race.wagers,
            country=race.country,
            track_code=track.brisCode,
            track_country=track.hostCountry,
            race_type=track.type,
            current_race=race.currentRace,
        )


class LiveRaceEntryCanonical:
    def __init__(self, race_entry: StarterDetails) -> None:
        self.race_entry: StarterDetails = race_entry

    def convert(self) -> RaceEntry:
        entry = self.race_entry

        return RaceEntry(
            post_pos=entry.postPosition,
            program_no=entry.programNumber,
            sortable_program_no=entry.sortableProgramNumber,
            betting_interest=entry.bettingInterest,
            name=entry.name,
            yob=entry.yob,
            color=entry.color,
            sex=entry.sex,
            where_bred=entry.whereBred,
            equipment=entry.equipment,
            medication=entry.medication,
            formatted_medication=entry.formattedMedication,
            weight=entry.weight,
            overweight_amt=entry.overweightAmount,
            jockey_name=entry.jockeyName,
            trainer_name=entry.trainerName,
            owner_name=entry.ownerName,
            color_desc=entry.colorDescription,
            sire_name=entry.sireName,
            dam_name=entry.damName,
            prior_run_style=entry.priorRunStyle,
            speed_pts=entry.speedPoints,
            average_pace_e1=entry.averagePaceE1,
            average_pace_e2=entry.averagePaceE2,
            average_speed_last3=entry.averageSpeedLast3,
            best_speed_at_dist=entry.bestSpeedAtDistance,
            days_off=entry.daysOff,
            avg_class=entry.averageClass,
            last_class=entry.lastClass,
            prime_power=entry.primePower,
            horse_claiming_price=entry.horseClaimingPrice,
            power_rating=entry.powerRating,
            best_speed=entry.bestSpeed,
            comments_positive=(
                "|".join(entry.commentsPositive) if entry.commentsPositive else None
            ),
            comments_negative=(
                "|".join(entry.commentsNegative) if entry.commentsNegative else None
            ),
            silk_status=entry.silkStatus,
            silk_uri=entry.silkUriPath,
            morning_line_odds=entry.morningLineOddsNumeric(),
            also_eligible=entry.alsoEligible,
            main_track_only=entry.mainTrackOnly,
            morning_line_fav=entry.morningLineFavorite,
            live_odds_fav=entry.liveOddsFavorite,
            jockey_chg=entry.jockeyChange,
            weight_chg=entry.weightChange,
            weight_corrections=entry.weightCorrection,
            other_change=entry.otherChange,
            profitline_odds=entry.profitlineOddsNumeric(),
            live_odds=entry.liveOddsNumeric(),
            scratched=entry.scratched,
        )
