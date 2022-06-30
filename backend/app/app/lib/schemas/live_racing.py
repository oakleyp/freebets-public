from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class SurfaceConditions(BaseModel):
    type: str
    condition: str


class Featured(BaseModel):
    featuredTrackId: int
    label: str
    races: int
    raceList: List[Any] = []  # TODO: Figure out what this is


class CarryOverPool(BaseModel):
    poolName: str
    poolCode: str
    amount: float


class RaceDetails(BaseModel):
    raceNumber: int
    raceDate: date
    postTime: datetime
    postTimeStamp: int
    mtp: int
    status: str
    distance: str
    distanceLong: str
    surface: Optional[str]
    surfaceLabel: Optional[str]
    ageRestrictions: Optional[str]
    sexRestrictions: str
    raceDescription: Optional[str]
    wagers: Optional[str]
    country: str
    carryover: List[CarryOverPool] = []
    currentRace: bool
    hasExpertPick: bool


class TrackWithRaceDetailsBase(BaseModel):
    brisCode: str
    name: str
    type: str
    status: str
    currentRaceNumber: Optional[int]
    hostCountry: str
    hasBetTypes: bool
    allowsConditionalWagering: bool
    surfaceConditions: List[SurfaceConditions] = []
    featured: List[Featured] = []


class TrackWithRaceDetails(TrackWithRaceDetailsBase):
    races: List[RaceDetails]


class OddsTrendItem(BaseModel):
    oddsNumeric: int
    oddsText: str
    change: int


class OddsTrend(BaseModel):
    current: OddsTrendItem
    # TODO: odds2, .., oddsN ?


class StarterDetails(BaseModel):
    startId: Optional[int]
    entryId: Optional[int]
    postPosition: Optional[int]
    programNumber: Optional[str]
    sortableProgramNumber: Optional[int]
    bettingInterest: Optional[int]
    name: Optional[str]
    oddsTrend: Optional[OddsTrend]
    oddsRank: Optional[int]
    yob: Optional[str]
    whelpDate: Optional[Any]  # TODO: Optional[?]
    color: Optional[str]
    sex: Optional[str]
    whereBred: Optional[str]
    equipment: Optional[str]
    medication: Optional[str]
    formattedMedication: Optional[str]
    weight: Optional[int]
    overweightAmount: Optional[Any]  # TODO ?
    jockeyName: Optional[str]
    jockeyFirstName: Optional[str]
    jockeyMiddleName: Optional[str]
    jockeyLastName: Optional[str]
    jockeyId: Optional[str]
    trainerName: Optional[str]
    trainerFirstName: Optional[str]
    trainerMiddleName: Optional[str]
    trainerLastName: Optional[str]
    trainerId: Optional[int]
    ownerName: Optional[str]
    ownerFirstName: Optional[str]
    ownerMiddleName: Optional[str]
    ownerLastName: Optional[str]
    ownerId: Optional[int]
    colorDescription: Optional[str]
    sireId: Optional[int]
    sireName: Optional[str]
    damId: Optional[int]
    damName: Optional[str]
    priorRunStyle: Optional[str]
    speedPoints: Optional[int]
    averagePaceE1: Optional[int]
    averagePaceE2: Optional[int]
    averagePaceLP: Optional[int]
    averageSpeed: Optional[int]
    averageSpeedLast3: Optional[int]
    bestSpeedAtDistance: Optional[int]
    daysOff: Optional[int]
    averageClass: Optional[int]
    lastClass: Optional[int]
    primePower: Optional[int]
    horseClaimingPrice: Optional[int]
    powerRating: Optional[Any]  # TODO: All these ?
    bestSpeed: Optional[Any]
    earlyPace: Optional[Any]
    midPace: Optional[Any]
    latePace: Optional[Any]
    commentsPositive: List[str]
    commentsNegative: List[str]
    silkStatus: Optional[str]
    silkUriPath: Optional[str]
    expertPickRank: Optional[Any]
    blinkers: Optional[Any]
    morningLineOdds: Optional[str]
    alsoEligible: Optional[bool]
    mainTrackOnly: Optional[bool]
    morningLineFavorite: Optional[bool]
    liveOddsFavorite: Optional[bool]
    jockeyChange: Optional[bool]
    weightChange: Optional[bool]
    weightCorrection: Optional[bool]
    otherChange: Optional[bool]
    profitlineOdds: Optional[str]
    liveOdds: Optional[str]
    scratched: Optional[bool]

    def liveOddsNumeric(self) -> Optional[float]:
        if not self.liveOdds:
            return None

        try:
            return parse_odds(self.liveOdds)
        except:
            return None

    def profitlineOddsNumeric(self) -> Optional[float]:
        if not self.profitlineOdds:
            return None

        try:
            return parse_odds(self.profitlineOdds)
        except:
            return None

    def morningLineOddsNumeric(self) -> Optional[float]:
        if not self.morningLineOdds:
            return None

        try:
            return parse_odds(self.morningLineOdds)
        except:
            return None


def parse_odds(odds: str) -> Optional[float]:
    """Parse odds str to float, e.g. parse_odds(" 15/2") == 7.5.

    Raises ValueError on failure.
    """
    if not odds or len(odds) < 1:
        raise ValueError("Given odds str is empty")

    input = odds.strip()

    if "/" in input:
        num, denom = input.split("/")
        return float(num) / float(denom)
    else:
        return float(input)


class RaceWithStarterDetails(RaceDetails):
    starters: List[StarterDetails]


class TrackWithRaceAndStarterDetails(TrackWithRaceDetailsBase):
    races: List[RaceWithStarterDetails]
