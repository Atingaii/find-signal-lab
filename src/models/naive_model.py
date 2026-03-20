from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


@dataclass
class NaiveSignalModel:
    target_name: str
    signal_column: str
    scale: float = 1.0
    center: float = 0.0
    model_version: str = "naive_signal_v1"

    def fit(self, dataframe: pd.DataFrame) -> "NaiveSignalModel":
        signal = pd.to_numeric(dataframe[self.signal_column], errors="coerce").replace([np.inf, -np.inf], np.nan)
        std = float(signal.std()) if signal.notna().any() else 0.0
        self.center = float(signal.mean()) if signal.notna().any() else 0.0
        self.scale = std if std > 0 else 1.0
        return self

    def predict(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        signal = pd.to_numeric(dataframe[self.signal_column], errors="coerce").replace([np.inf, -np.inf], np.nan)
        score = (signal.fillna(self.center) - self.center) / self.scale
        probability = sigmoid(score.to_numpy())
        prediction = (probability >= 0.5).astype(int)

        result = dataframe.copy()
        result["prediction_label"] = prediction
        result["prediction_score"] = score
        result["prediction_probability"] = probability
        result["rank_score"] = result["prediction_probability"]
        result["model_name"] = "naive_signal"
        result["model_version"] = self.model_version
        result["top_feature_contributors"] = [
            json.dumps(
                [
                    {
                        "feature_name": self.signal_column,
                        "contribution": float(value),
                        "direction": "positive" if float(value) >= 0 else "negative",
                    }
                ],
                ensure_ascii=False,
            )
            for value in score
        ]
        return result
