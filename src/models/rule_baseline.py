from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from models.config import TARGET_CONFIGS


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


@dataclass
class RuleBaselineModel:
    target_name: str
    feature_columns: list[str] = field(default_factory=list)
    feature_weights: dict[str, float] = field(default_factory=dict)
    feature_means: dict[str, float] = field(default_factory=dict)
    feature_stds: dict[str, float] = field(default_factory=dict)
    feature_fill_values: dict[str, float] = field(default_factory=dict)
    model_version: str = "rule_baseline_v1"

    def __post_init__(self) -> None:
        if not self.feature_columns or not self.feature_weights:
            config = TARGET_CONFIGS[self.target_name]
            self.feature_columns = list(config["feature_columns"])
            self.feature_weights = dict(config["rule_weights"])

    def fit(self, dataframe: pd.DataFrame) -> "RuleBaselineModel":
        clean_features = self._clean_features(dataframe[self.feature_columns])
        self.feature_fill_values = {
            column: float(clean_features[column].median()) if clean_features[column].notna().any() else 0.0
            for column in self.feature_columns
        }
        filled_features = clean_features.fillna(self.feature_fill_values)
        stats = filled_features.agg(["mean", "std"]).to_dict()
        self.feature_means = {column: float(stats[column]["mean"]) for column in self.feature_columns}
        self.feature_stds = {
            column: float(stats[column]["std"]) if float(stats[column]["std"] or 0.0) > 0 else 1.0
            for column in self.feature_columns
        }
        return self

    def predict(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        standardized = self._standardize(dataframe[self.feature_columns])
        contributions = pd.DataFrame(index=dataframe.index)
        for column in self.feature_columns:
            contributions[column] = standardized[column] * self.feature_weights[column]

        raw_score = contributions.sum(axis=1)
        probability = sigmoid(raw_score.to_numpy())
        prediction = (probability >= 0.5).astype(int)

        result = dataframe.copy()
        result["prediction_label"] = prediction
        result["prediction_score"] = raw_score
        result["prediction_probability"] = probability
        result["rank_score"] = result["prediction_probability"]
        result["model_name"] = "rule_baseline"
        result["model_version"] = self.model_version
        result["top_feature_contributors"] = [
            json.dumps(self._top_contributors(contributions.loc[index]), ensure_ascii=False)
            for index in contributions.index
        ]
        return result

    def save(self, output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "target_name": self.target_name,
            "feature_columns": self.feature_columns,
            "feature_weights": self.feature_weights,
            "feature_means": self.feature_means,
            "feature_stds": self.feature_stds,
            "feature_fill_values": self.feature_fill_values,
            "model_version": self.model_version,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, input_path: str | Path) -> "RuleBaselineModel":
        payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
        model = cls(
            target_name=payload["target_name"],
            feature_columns=payload["feature_columns"],
            feature_weights=payload["feature_weights"],
        )
        model.feature_means = payload["feature_means"]
        model.feature_stds = payload["feature_stds"]
        model.feature_fill_values = payload.get("feature_fill_values", {})
        model.model_version = payload["model_version"]
        return model

    def _standardize(self, features: pd.DataFrame) -> pd.DataFrame:
        result = self._clean_features(features).fillna(self.feature_fill_values)
        for column in self.feature_columns:
            result[column] = (result[column] - self.feature_means[column]) / self.feature_stds[column]
        return result.fillna(0.0)

    @staticmethod
    def _clean_features(features: pd.DataFrame) -> pd.DataFrame:
        return features.replace([np.inf, -np.inf], np.nan)

    @staticmethod
    def _top_contributors(row: pd.Series, limit: int = 3) -> list[dict[str, float | str]]:
        ordered = row.reindex(row.abs().sort_values(ascending=False).index).head(limit)
        return [
            {
                "feature_name": str(feature_name),
                "contribution": float(feature_value),
                "direction": "positive" if float(feature_value) >= 0 else "negative",
            }
            for feature_name, feature_value in ordered.items()
        ]
