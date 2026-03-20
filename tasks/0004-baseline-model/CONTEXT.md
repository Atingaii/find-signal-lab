# Context

- Baseline-first is mandatory.
- Stage four consumes `dataset_training_samples` directly.
- Evaluation must respect `dataset_split` and preserve time order.
- ETF is the only default supervised target set.
- Benchmark-family slicing is mandatory.
- Output must include prediction probability, rank score, and top feature contributors.
- Stage five consumes `prediction_explanation_input_latest` rather than retraining models.
