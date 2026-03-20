from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from models.config import TARGET_CONFIGS


@dataclass
class LogisticBaselineModel:
    target_name: str
    feature_columns: list[str] = field(default_factory=list)
    model_version: str = "logistic_baseline_v1"
    pipeline: Pipeline | None = None
    feature_fill_values: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.feature_columns:
            self.feature_columns = list(TARGET_CONFIGS[self.target_name]["feature_columns"])

    def fit(self, dataframe: pd.DataFrame, label_column: str) -> "LogisticBaselineModel":
        clean_features = self._clean_features(dataframe[self.feature_columns])
        self.feature_fill_values = {
            column: float(clean_features[column].median()) if clean_features[column].notna().any() else 0.0
            for column in self.feature_columns
        }
        filled_features = clean_features.fillna(self.feature_fill_values)
        self.pipeline = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, random_state=42)),
            ]
        )
        self.pipeline.fit(filled_features, dataframe[label_column].astype(int))
        return self

    def predict(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.pipeline is None:
            raise RuntimeError("Model has not been fitted.")

        prepared = self._clean_features(dataframe[self.feature_columns]).fillna(self.feature_fill_values)
        probabilities = self.pipeline.predict_proba(prepared)[:, 1]
        decision_scores = self.pipeline.decision_function(prepared)
        predicted_labels = (probabilities >= 0.5).astype(int)
        contributions = self._feature_contributions(prepared)

        result = dataframe.copy()
        result["prediction_label"] = predicted_labels
        result["prediction_score"] = decision_scores
        result["prediction_probability"] = probabilities
        result["rank_score"] = result["prediction_probability"]
        result["model_name"] = "logistic_regression"
        result["model_version"] = self.model_version
        result["top_feature_contributors"] = [
            json.dumps(self._top_contributors(contributions.loc[index]), ensure_ascii=False)
            for index in contributions.index
        ]
        return result

    def coefficient_frame(self) -> pd.DataFrame:
        if self.pipeline is None:
            raise RuntimeError("Model has not been fitted.")
        model = self.pipeline.named_steps["model"]
        return pd.DataFrame(
            {
                "feature_name": self.feature_columns,
                "coefficient": model.coef_[0],
                "abs_coefficient": np.abs(model.coef_[0]),
            }
        ).sort_values("abs_coefficient", ascending=False)

    def save(self, output_path: str | Path) -> None:
        if self.pipeline is None:
            raise RuntimeError("Model has not been fitted.")
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "target_name": self.target_name,
                "feature_columns": self.feature_columns,
                "model_version": self.model_version,
                "feature_fill_values": self.feature_fill_values,
                "pipeline": self.pipeline,
            },
            path,
        )

    @classmethod
    def load(cls, input_path: str | Path) -> "LogisticBaselineModel":
        payload = joblib.load(Path(input_path))
        model = cls(
            target_name=payload["target_name"],
            feature_columns=payload["feature_columns"],
        )
        model.model_version = payload["model_version"]
        model.feature_fill_values = payload.get("feature_fill_values", {})
        model.pipeline = payload["pipeline"]
        return model

    def _feature_contributions(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.pipeline is None:
            raise RuntimeError("Model has not been fitted.")
        scaler = self.pipeline.named_steps["scaler"]
        logistic = self.pipeline.named_steps["model"]
        transformed = scaler.transform(dataframe[self.feature_columns])
        contributions = transformed * logistic.coef_[0]
        return pd.DataFrame(contributions, columns=self.feature_columns, index=dataframe.index)

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
