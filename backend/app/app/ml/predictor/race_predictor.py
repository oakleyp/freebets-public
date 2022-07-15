import logging
from typing import Dict

import numpy as np
from catboost import CatBoostClassifier
from pydantic import BaseModel

from app.models.race import Race

from .data_utils import create_race_entry_df_from_race

logger = logging.getLogger(__name__)


class HorseProbData(BaseModel):
    win_proba: float


class RacePredictResult(BaseModel):
    # Mapping of entry_id -> HorseProbData
    entries_probs: Dict[int, HorseProbData]


class RacePredictor:
    """Predict `Race` outcomes using a pre-trained model."""

    def __init__(self, model_file: str = "./race_model2.dump") -> None:
        self.model_file = model_file
        self.model = CatBoostClassifier()
        self.refresh_model()

    def refresh_model(self):
        self.model.load_model(self.model_file)

    def calc_probs(self, race: Race) -> RacePredictResult:
        result_dct: Dict[int, HorseProbData] = {}

        race_df = create_race_entry_df_from_race(race)
        race_df.fillna(-999, inplace=True)

        # print(race_df.to_json())
        # print(race_df.info())

        race_results: np.ndarray = self.model.predict_proba(race_df)

        # [[x1, y1], [x2, y2], ...] -> [y1, y2, ...]
        # Where x1 = lose probability; y1 = win probability
        winner_probs = race_results[:, 1]

        # Ensure order matches that of race_df
        entries_sorted = sorted(race.entries, key=lambda e: e.id)

        for (entry, prob) in zip(entries_sorted, winner_probs):
            result_dct[entry.id] = HorseProbData(win_proba=prob)

        return RacePredictResult(entries_probs=result_dct)
