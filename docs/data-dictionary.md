# 第二阶段数据字典

## 最新验证快照

基于 `2026-03-19T09:12:05Z` 的同步结果：

- `dim_fund`: 20
- `fund_universe_membership`: 20
- `fact_fund_market_daily`: 5666
- `fact_fund_nav_daily`: 20177
- `fact_macro_observation`: 7225
- `fact_fund_market_daily` 覆盖 11 只 ETF
- `fact_fund_nav_daily` 覆盖 9 只 LOF / 指数基金

## 表分层

第二阶段明确区分 `raw_*` 原始表 与 `dim/fact` 标准化表。

### 原始表

| 表名 | 粒度 | 说明 |
| --- | --- | --- |
| `raw_fund_master_snapshot` | snapshot_at + fund_code | AkShare 基金主数据快照 |
| `raw_fund_quote_snapshot` | snapshot_at + market_type + fund_code | ETF / LOF 日快照 |
| `raw_index_fund_snapshot` | snapshot_at + fund_code | 被动指数基金快照 |
| `raw_etf_history` | fund_code + trade_date | 场内 ETF 原始历史行情 |
| `raw_fund_nav` | fund_code + nav_date | 净值原始序列 |
| `raw_macro_series` | series_name + observation_date + metric_name | 宏观原始序列 |

### 标准化表

| 表名 | 粒度 | 说明 |
| --- | --- | --- |
| `dim_fund` | fund_code | 标准基金主维表 |
| `fund_classification_map` | fund_code + benchmark_family | 基金分类映射 |
| `fund_universe_membership` | as_of_date + fund_code | V1 基金池成员表 |
| `fact_fund_market_daily` | fund_code + trade_date | ETF 历史行情事实表 |
| `fact_fund_nav_daily` | fund_code + nav_date | LOF / 指数基金净值事实表 |
| `fact_macro_observation` | series_name + observation_date + metric_name | 宏观事实表 |
| `data_validation_run` | run_at | 每次同步后的校验结果 |

## 核心字段说明

### `dim_fund`

- `fund_code`: 6 位基金代码，主键。
- `fund_name`: 清洗后的基金简称。
- `market_type`: `ETF / LOF / INDEX`。
- `is_listed`: 是否场内交易，`1` 表示 ETF 或 LOF。
- `benchmark_family`: V1 统一基准家族代码。
- `benchmark_name`: 可读基准名称。
- `selection_bucket`: `core / companion / reserve`。
- `history_source`: 实际历史源路由，当前为 `eastmoney_push2his_then_sina` 或 `eastmoney_pingzhongdata`。
- `fund_type`, `tracking_mode`, `latest_trade_date`: 来自上游接口的辅助元数据。

### `fact_fund_market_daily`

- `fund_code`
- `trade_date`
- `open`
- `close`
- `high`
- `low`
- `volume`
- `amount`
- `amplitude`
- `pct_chg`
- `chg`
- `turnover`
- `source`
- `ingested_at`

说明：当前落库的场内行情全部来自 `sina_finance_etf_klc2` 兜底链路。

### `fact_fund_nav_daily`

- `fund_code`
- `nav_date`
- `unit_nav`
- `accum_nav`
- `daily_growth_rate`
- `source`
- `ingested_at`

说明：当前净值序列来自 `eastmoney_pingzhongdata`。

### `fact_macro_observation`

- `series_name`: 当前覆盖 `macro_china_pmi`、`macro_china_lpr`、`sse_market_summary`、`szse_market_summary`。
- `observation_date`
- `metric_name`
- `metric_value`
- `unit`
- `source`
- `ingested_at`

## 第三阶段输入格式约束

第三阶段默认从以下表读数据：

1. `fund_universe_membership`
2. `dim_fund`
3. `fact_fund_market_daily`
4. `fact_fund_nav_daily`
5. `fact_macro_observation`

输入约束：

- 训练或样本构建不得跳过 `fund_universe_membership` 直接扩池。
- `benchmark_family` 是 peer group 的唯一默认分组键。
- 对 ETF 目标样本，优先使用 `fact_fund_market_daily.trade_date` 作为样本基准日。
- 对净值陪跑基金，只能作为补充、对照或同类参照，不直接替代 ETF 的市场行情标签。
- 所有特征必须保证时间上 `<= t`，不得使用未来净值或未来宏观值。
- 宏观数据需要按最近可得日期向前对齐，不得向后填充未来观测。
- 若某基金在目标日期缺少 ETF 行情，则该日期不能进入监督样本。

## 推荐建模宽表主键

第三阶段建议的最小建模宽表主键：

- `fund_code`
- `trade_date`

建议补充字段：

- `benchmark_family`
- `selection_bucket`
- `close`
- `pct_chg`
- `unit_nav_ref`
- `macro_snapshot_date`
- `label_h1 / label_h5 / label_h20`
- `peer_rank_h1 / peer_rank_h5 / peer_rank_h20`
