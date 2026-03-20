# Acceptance

- [x] `1 / 5 / 20` 交易日标签全部可重建
- [x] 同类相对标签以 `benchmark_family` 为默认分组
- [x] 基础特征表仅使用预测时点可得数据
- [x] 建模宽表主键固定为 `fund_code + trade_date`
- [x] 宽表 schema、缺失策略与泄漏控制已文档化

## 验证证据

- `feature_fund_daily = 25843`
- `label_fund_daily = 25843`
- `dataset_training_samples = 4481`
- `funds in dataset_training_samples = 11`
