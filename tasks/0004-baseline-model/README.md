# 0004 Baseline Model

## Objective

在第三阶段训练数据集之上，训练并验证可解释 baseline 模型，输出结构化预测结果和解释输入。

## Delivered Artifacts

- `naive_signal` 对照模型
- `rule_baseline` 规则打分模型
- `logistic_regression` baseline 模型
- `reports/modeling/evaluation_summary.json`
- `reports/modeling/evaluation_report.md`
- `data/processed/predictions/`
- `docs/modeling.md`
- `docs/evaluation.md`
- `docs/prediction-output-spec.md`
- `docs/reports/stage-four-completion.md`

## Fixed Input Contract

- training table: `dataset_training_samples`
- primary key: `fund_code + trade_date`
- split column: `dataset_split`
- primary targets: ETF only
- target set:
  - `future_5d_up`
  - `future_20d_relative_strength`

## Fixed Output Contract

- `prediction_snapshot_latest`
- `prediction_explanation_input_latest`
- model artifacts under `data/processed/models`
- evaluation artifacts under `reports/modeling`
