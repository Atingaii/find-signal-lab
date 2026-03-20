from __future__ import annotations


class OptionalLGBMModel:
    """Compatibility placeholder for a later LightGBM/XGBoost comparison path."""

    def __init__(self) -> None:
        self.model_name = "optional_lgbm"

    def fit(self, *args, **kwargs) -> None:
        raise RuntimeError(
            "LightGBM/XGBoost comparison is optional and not enabled in the baseline-first stage."
        )

