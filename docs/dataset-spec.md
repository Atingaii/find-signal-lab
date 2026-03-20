# 第三阶段训练数据集规范

## 标准输入结论

阶段四建模的标准输入为：`dataset_training_samples`

同时会导出到：

- `data/processed/datasets/training_dataset_v1.csv`
- `data/processed/datasets/training_dataset_v1_train.csv`
- `data/processed/datasets/training_dataset_v1_valid.csv`
- `data/processed/datasets/training_dataset_v1_test.csv`

## 训练样本边界

- 训练样本只保留 ETF 主监督对象
- LOF / INDEX 进入特征流水线和 peer group 计算，但不进入阶段四标准训练样本
- 主键固定为 `fund_code + trade_date`

## 数据集筛选规则

样本必须同时满足：

1. `is_primary_target = 1`
2. `CORE_FEATURE_COLUMNS` 全部非空
3. `CORE_LABEL_COLUMNS` 全部非空

当前核心特征列：

- `daily_return_1d`
- `return_5d`
- `return_10d`
- `return_20d`
- `momentum_5_minus_20`
- `momentum_10_minus_20`
- `volatility_20d`
- `max_drawdown_20d`
- `excess_return_5d`
- `excess_return_20d`
- `style_strength_20d`
- `macro_pmi_manufacturing`
- `macro_pmi_non_manufacturing`
- `macro_lpr_1y`
- `macro_lpr_5y`
- `market_turnover_5d_avg`

当前核心标签列：

- `future_1d_up`
- `future_5d_up`
- `future_20d_up`
- `future_5d_relative_strength`
- `future_20d_relative_strength`

## 时间切分规则

采用严格按时间顺序的 `train / valid / test` 切分：

- `train = 70%`
- `valid = 15%`
- `test = 15%`

并在切分之间加入 `20` 个交易日 purge gap，避免 20 日未来标签跨区间污染。

当前最新导出结果：

- `train`: `2024-01-30` 到 `2025-07-07`
- `valid`: `2025-08-05` 到 `2025-10-27`
- `test`: `2025-11-25` 到 `2026-02-10`

对应的 20 日未来标签终点分别为：

- `train future_end = 2025-08-04`
- `valid future_end = 2025-11-24`
- `test future_end = 2026-03-18`

因此不同 split 之间没有 20 日标签窗口重叠。

## 防未来函数约束

- 特征只使用 `trade_date <= t` 的数据
- 标签只使用 `(t, t+h]` 的未来窗口
- 宏观变量只允许使用最近一个 `observation_date <= trade_date` 的值
- 不允许用 `future_date_h` 或未来收益反向参与任何特征计算
- 不允许把 companion 的未来净值直接写回目标 ETF 的特征

## 缺失值处理策略

- 滚动窗口不足直接保留为空，不做回填
- ETF 专属成交额特征对非 ETF 保留为空
- 保留字段 `premium_discount_rate / share_change_20d / aum_change_20d` 目前为空，不进入标准训练集
- 最终训练集通过显式筛选剔除缺失核心特征或核心标签的样本

## 最新导出摘要

`scripts/export_dataset.py` 最新结果：

- `rows = 4481`
- `funds = 11`
- `date_range = 2024-01-30 ~ 2026-02-10`
- `train = 3293`
- `valid = 594`
- `test = 594`

## 代码入口

- `src/datasets/build_training_dataset.py`
- `scripts/export_dataset.py`
