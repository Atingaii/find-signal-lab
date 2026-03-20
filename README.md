# Fund Direction Predictor

`fund-direction-predictor` is a staged project for predicting whether a passive fund is more likely to:

- rise or fall over the next `1 / 5 / 20` trading days
- outperform or underperform its peer group over the same horizons
- return a compact, explainable reason set

The project does not target individual stocks. V1 stays focused on a small, explainable passive-fund universe.

## Current Status

Stage one through stage four are complete.

- Stage one fixed the scope, non-goals, technical stack, and task archives.
- Stage two fixed the V1 fund universe, connected data sources, created the SQLite warehouse, and landed the first working data pipeline.
- Stage three built the feature table, label table, and reusable ETF training dataset.
- Stage four trained baseline models, produced evaluation artifacts, and generated structured prediction outputs.

## V1 Scope

- Target universe: domestic passive equity funds only
- Fund types in scope: `ETF`, `LOF`, `INDEX`
- Universe strategy: `benchmark-first`
- Prediction horizons: `1 / 5 / 20` trading days
- Output types:
  - absolute direction: `up / down`
  - peer-relative result: `outperform / underperform`
  - compact explanation based on observable signals
- Runtime mode: daily batch after market close

## Explicit Non-Goals

- no deep learning in the baseline phase
- no full backtesting platform
- no production frontend
- no auto-trading
- no all-fund active-fund coverage
- no complex LLM integration

## Stage-Four Deliverables

- reusable feature and label tables
- `dataset_training_samples`
- `naive_signal`, `rule_baseline`, and `logistic_regression`
- model artifacts under `data/processed/models`
- evaluation outputs under `reports/modeling`
- latest prediction snapshots under `data/processed/predictions`
- `prediction_snapshot_latest` and `prediction_explanation_input_latest`

## Key Documents

- `docs/data-sources.md`
- `docs/universe.md`
- `docs/features.md`
- `docs/labels.md`
- `docs/dataset-spec.md`
- `docs/modeling.md`
- `docs/evaluation.md`
- `docs/prediction-output-spec.md`
- `docs/reports/stage-four-completion.md`

## Core Commands

```powershell
python scripts/init_db.py
python scripts/sync_data.py --trade-date 20250318
python scripts/build_features.py --db-path data/sqlite/fund_data.db
python scripts/build_labels.py --db-path data/sqlite/fund_data.db
python scripts/export_dataset.py --db-path data/sqlite/fund_data.db
python scripts/train_baseline.py --db-path data/sqlite/fund_data.db
python scripts/evaluate_model.py --db-path data/sqlite/fund_data.db
python scripts/run_prediction.py --db-path data/sqlite/fund_data.db
python scripts/validate_data.py --db-path data/sqlite/fund_data.db
```

## Stage-Five Entry

The next recommended execution target is `0005-explanation-engine`.

Stage five should consume:

- `prediction_explanation_input_latest`
- `prediction_snapshot_latest`
- `data/processed/predictions/*`
