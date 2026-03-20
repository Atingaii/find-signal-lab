# 第三阶段特征说明

## 设计原则核对

基于第二阶段已经确认的数据合同和标准时序建模原则，第三阶段采用以下收敛方案：

- `1 / 5 / 10 / 20` 窗口用于收益、动量、波动和回撤，适合基金方向预测的最小闭环。
- ETF 与 LOF / INDEX 不直接混成同一种监督口径，而是通过 `reference_basis` 显式区分。
- 特征全部只使用 `t` 及之前的数据。
- 宏观变量按最近可得观察日向前对齐，不向后填充未来值。

## 数据口径

统一参考序列表：`feature_fund_reference_daily`

- ETF：`reference_basis = market_close`，使用 `fact_fund_market_daily.close`
- LOF / INDEX：`reference_basis = unit_nav`，使用 `fact_fund_nav_daily.unit_nav`

统一特征表：`feature_fund_daily`

- 覆盖基金数：20
- 主监督对象基金数：11
- 日期范围：`2010-02-02` 到 `2026-03-18`

## 已实现特征

### 基础收益与动量

- `daily_return_1d`: `reference_value_t / reference_value_t-1 - 1`
- `return_5d`
- `return_10d`
- `return_20d`
- `momentum_5_minus_20 = return_5d - return_20d`
- `momentum_10_minus_20 = return_10d - return_20d`
- `ma_gap_1d`
- `ma_gap_5d`
- `ma_gap_10d`
- `ma_gap_20d`
- `up_day_ratio_10d`: 最近 10 个观测中正收益日占比

### 波动与回撤

- `volatility_5d`: 最近 5 个观测日收益率标准差
- `volatility_10d`
- `volatility_20d`
- `max_drawdown_20d`: 最近 20 个观测窗口内的最大回撤

### 成交与流动性

以下特征仅对 ETF 主监督样本有值，LOF / INDEX 保留为空：

- `amount_change_1d`
- `amount_change_5d`
- `amount_ma_gap_5d`
- `amount_ma_gap_20d`
- `turnover_avg_5d`
- `turnover_avg_20d`
- `liquidity_feature_ready`

### 相对基准与风格强弱

- `family_return_1d`: 同一 `benchmark_family` 当日中位收益
- `family_return_5d`
- `family_return_20d`
- `excess_return_1d = daily_return_1d - family_return_1d`
- `excess_return_5d`
- `excess_return_20d`
- `family_peer_count`: 同家族当日可用样本数
- `style_strength_5d`: 家族 5 日收益减去当日全家族中位 5 日收益
- `style_strength_20d`

### 最小宏观特征

- `macro_pmi_manufacturing`
- `macro_pmi_non_manufacturing`
- `macro_lpr_1y`
- `macro_lpr_5y`
- `market_turnover_total`: 当日 ETF 样本总成交额
- `market_turnover_5d_avg`
- `macro_snapshot_date`: 当前样本所使用的宏观观测日期

## 保留但未实装为有效训练特征

以下字段已经预留在 `feature_fund_daily` 中，但当前阶段不作为有效训练特征使用：

- `premium_discount_rate`
- `share_change_20d`
- `aum_change_20d`

原因不是方法设计问题，而是第二阶段未落库 ETF 历史净值、份额和 AUM 时序。第三阶段不回头扩数据合同，因此这些字段在 `v1_stage3` 中保留为空。

## 缺失值策略

- 窗口型特征要求完整窗口，窗口不足时保留 `NaN`
- ETF 特有的成交额与换手率特征，对 LOF / INDEX 保留 `NaN`
- 宏观字段通过日历重建后向前填充至 `trade_date`
- 训练集导出时只保留 `CORE_FEATURE_COLUMNS` 完整的 ETF 样本

## 结果摘要

`scripts/build_features.py` 最新结果：

- `rows = 25843`
- `funds = 20`
- `primary_targets = 11`
- `feature_ready_rows = 25443`

## 代码入口

- `src/features/price_features.py`
- `src/features/fund_features.py`
- `src/features/style_features.py`
- `src/features/macro_features.py`
- `scripts/build_features.py`
