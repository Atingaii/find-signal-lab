# 第二阶段完成报告

## 阶段目标

第二阶段只解决一件事：把 V1 基金池、数据源、SQLite 表结构和最小数据流水线真正落地，并用真实数据验证可用性。

本阶段不进入模型训练、完整特征工程、完整标签系统、回测或前端实现。

## 已完成项

1. 最终确认 V1 基金池为 20 只基金，覆盖 10 个基准家族。
2. 完成 `AkShare + 公开站点补充` 的统一数据访问层。
3. 建立 SQLite 原始表与标准化表结构。
4. 实现 `抓取 -> 清洗 -> 落库 -> 校验` 的最小同步链路。
5. 成功落库一批真实 ETF 历史行情、净值序列和宏观数据。
6. 产出数据源说明、基金池说明、数据字典和第三阶段输入约束。
7. 更新 `tasks/0002` 与 `tasks/0003` 的任务档案。

## 代码与脚本

核心代码：

- `src/data_sources/akshare_client.py`
- `src/data_sources/official_client.py`
- `src/universe/builder.py`
- `src/universe/classifier.py`
- `src/storage/sqlite_store.py`

核心脚本：

- `scripts/init_db.py`
- `scripts/sync_data.py`
- `scripts/validate_data.py`

核心配置与产物：

- `config/fund_pool_v1.yaml`
- `data/processed/fund_universe_v1.csv`
- `data/processed/sync_summary.json`
- `data/sqlite/fund_data.db`

## 最新验证结果

基于 `2026-03-19T09:12:05Z` 的同步结果：

- 基金池数量：20
- 场内 ETF 历史行情基金数：11
- 净值序列基金数：9
- 宏观序列数：4
- `fact_fund_market_daily` 行数：5666
- `fact_fund_nav_daily` 行数：20177
- `fact_macro_observation` 行数：7225

验证脚本结果：

- `universe_count_ge_20 = true`
- `etf_history_rows_gt_0 = true`
- `nav_history_rows_gt_0 = true`
- `macro_rows_gt_0 = true`

## 关键决策

- V1 只保留国内被动权益基金，不扩展到主动基金、债券、商品或海外市场。
- 基金池采用 `benchmark-first`，不是全市场无约束抓取。
- 场内历史行情保留 `eastmoney_push2his_then_sina` 双路策略，但当前实测实际由新浪兜底完成落库。
- 场外净值序列使用 `eastmoney_pingzhongdata`，因为 AkShare 对部分净值接口包装不稳定。
- `benchmark_family` 作为第三阶段同类比较和标签体系的默认分组锚点。

## 已知限制

- `eastmoney push2his` 在当前环境中不稳定，因此第二阶段对场内历史行情的稳定性仍依赖新浪兜底。
- 当前基金池是人工确认的 V1 白名单，不是自动发现系统。
- 第二阶段只提供数据可用性，不保证第三阶段直接拿来就有最佳预测效果。

## 第三阶段输入准备

第三阶段可直接使用：

- `dim_fund`
- `fund_universe_membership`
- `fact_fund_market_daily`
- `fact_fund_nav_daily`
- `fact_macro_observation`

第三阶段优先事项：

1. 定义 `1 / 5 / 20` 交易日标签。
2. 定义同类比较逻辑，默认按 `benchmark_family` 分组。
3. 建立最小特征表，先从收益、波动、成交、宏观滞后特征开始。
4. 做严格时间对齐和防泄漏检查。
