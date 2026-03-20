# Context

## 固定边界

- 继承阶段一结论，不重新发散需求。
- V1 只覆盖国内被动权益基金中的 `ETF / LOF / INDEX`。
- 不做主动基金全覆盖。
- 不做模型训练、完整特征工程、完整标签体系、回测和前端。

## 关键决策

- 基金池采用 `benchmark-first`，覆盖 10 个指数家族。
- 基金池总数固定为 20，只保留 `core / companion / reserve` 三类角色。
- 场内 ETF 历史行情当前采用 `eastmoney_push2his_then_sina` 主备路由。
- LOF / 场外指数基金净值采用 `eastmoney_pingzhongdata`。
- 宏观数据只接入 PMI、LPR、上交所概览、深交所概览四组最小信号。
- `benchmark_family` 是后续 peer group 和标签体系的默认锚点。

## 第二阶段实测结果

- `dim_fund = 20`
- `fact_fund_market_daily = 5666`
- `fact_fund_nav_daily = 20177`
- `fact_macro_observation = 7225`
- ETF 历史行情覆盖 11 只基金
- 净值序列覆盖 9 只基金
