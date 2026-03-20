# Context

- The explanation layer must be deterministic, not LLM-first.
- Reasons must map to `top_feature_contributors`, `feature_snapshot`, and `risk_snapshot`.
- Explanations must be reproducible for the same snapshot.
- Keep language compact and compatible with API and report outputs.
- Stage five must not retrain or rescore models.
- `prediction_explanation_input_latest` is the only default source contract.
