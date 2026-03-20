# Acceptance

## 结果

- [x] 本地可运行 `init_db / sync_data / validate_data`
- [x] 至少 20 只基金成功建池
- [x] 至少一类场内基金历史行情成功落库
- [x] 至少一类场外基金净值成功落库
- [x] 至少一组宏观数据成功落库
- [x] 数据表结构清晰区分原始层与标准化层
- [x] 文档说明了来源、更新方式和限制

## 验证证据

- 最新同步时间：`2026-03-19T09:12:05Z`
- `dim_fund = 20`
- `fact_fund_market_daily = 5666`
- `fact_fund_nav_daily = 20177`
- `fact_macro_observation = 7225`
- `scripts/validate_data.py` 返回全部检查通过
