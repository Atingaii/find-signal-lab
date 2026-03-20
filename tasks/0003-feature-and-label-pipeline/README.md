# 0003 Feature And Label Pipeline

## Objective

基于第二阶段 SQLite 仓库，落地统一特征表、标签表和可复用训练数据集。

## Delivered Artifacts

- `feature_fund_reference_daily`
- `feature_fund_daily`
- `label_fund_daily`
- `dataset_training_samples`
- `docs/features.md`
- `docs/labels.md`
- `docs/dataset-spec.md`
- `docs/reports/stage-three-completion.md`

## Fixed Input Constraints

- 只能使用 `0002` 的 V1 基金池与 SQLite 表
- 不允许自行扩池
- ETF 是主监督对象
- LOF / INDEX 只作为补充特征、同类参考和净值参照
- `benchmark_family` 是默认 peer group 分组键
