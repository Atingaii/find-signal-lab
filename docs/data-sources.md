# 第二阶段数据源说明

## 结论

第二阶段采用 `AkShare + 公开站点补充` 的最小闭环方案，不引入额外复杂依赖。

数据源优先级如下：

1. `AkShare`：基金名录、ETF/LOF 快照、被动指数基金快照、PMI、LPR、上交所/深交所市场概览。
2. `Eastmoney pingzhongdata`：补齐场外指数基金与 LOF 的长期净值序列。
3. `上交所 / 深交所公开页面`：只做白名单和定义校验，不承担主数据流水线。
4. `Tushare`：仅保留后续适配位，不在第二阶段实际接入。

## 当前接入接口

| 数据对象 | 接口 / 页面 | 用途 | 当前结论 |
| --- | --- | --- | --- |
| 基金主数据 | `ak.fund_name_em()` | 基金代码、简称、基金类型 | 稳定，可直接用 |
| ETF 快照 | `ak.fund_etf_category_ths(symbol='ETF')` | ETF 当日单位净值、最新交易日、申赎状态 | 稳定，可直接用 |
| LOF 快照 | `ak.fund_etf_category_ths(symbol='LOF')` | LOF 当日单位净值、最新交易日、申赎状态 | 稳定，可直接用 |
| 被动指数基金快照 | `ak.fund_info_index_em(symbol='全部', indicator='被动指数型')` | 场外指数基金、LOF 辅助映射 | 可用，但跟踪标的不够干净 |
| ETF 历史行情 | `push2his` 优先，`ak.fund_etf_hist_sina()` 兜底 | 场内基金 OHLCV 序列 | `push2his` 实测不稳，当前实际全部走新浪兜底 |
| 场外净值历史 | `http://fund.eastmoney.com/pingzhongdata/{code}.js` | 单位净值、累计净值、日增长率 | 稳定，已落库 |
| PMI | `ak.macro_china_pmi()` | 最小宏观信号 | 稳定 |
| LPR | `ak.macro_china_lpr()` | 利率信号 | 稳定 |
| 上交所概览 | `ak.stock_sse_summary()` | 市场整体规模、成交概览 | 稳定 |
| 深交所概览 | `ak.stock_szse_summary(date=...)` | ETF / LOF / 基金成交与市值概览 | 稳定 |
| 上交所 ETF 列表页 | `https://etf.sse.com.cn/fundlist/` | ETF 白名单校验 | 作为补充证据 |
| 深交所 LOF 定义页 | `https://www.szse.cn/www/investor/knowledge/fund/lof/t20161123_538832.html` | LOF 范围说明 | 作为补充证据 |

## 本项目里最稳定的字段

ETF / LOF / 指数基金当前最稳定、最适合作为 V1 标准字段的内容：

- `fund_code`
- `fund_name`
- `fund_type`
- `market_type`
- `latest_trade_date`
- `unit_nav` / `accum_nav`
- `trade_date` / `nav_date`
- `open` / `high` / `low` / `close` / `volume` / `amount`
- `purchase_status` / `redemption_status`
- `tracking_mode`

不把以下字段作为第二阶段的强依赖：

- `fund_info_index_em` 返回的 `跟踪标的` 原始值
- 东财场内 K 线接口的稳定性
- 需要额外授权或积分的数据项

## 为什么需要官方页面补充

官方公开页面在第二阶段只承担两类职责：

1. 验证 ETF / LOF 是否属于目标观察范围。
2. 为基金类型定义和白名单边界提供权威参考。

第二阶段不从官方页面抓取大规模可计算时序数据，原因是页面结构变动成本更高，不适合作为 V1 主流水线。

## 代码与分类清洗规则

第二阶段必须做代码与分类清洗，原因是不同接口对基金简称、跟踪标的、基金类型的表达不完全一致。

当前清洗规则：

- 基金代码统一为 6 位字符串。
- 基金名称做空白符清洗。
- 通过 `src/universe/classifier.py` 的关键词规则映射 `benchmark_family`。
- 排除 `QDII / 港股 / 商品 / 黄金 / 原油 / REIT / 联接` 等不在 V1 范围内的基金。
- 最终基金池使用 `config/fund_pool_v1.yaml` 作为单一白名单来源，避免完全依赖自动分类。

## 当前限制

- `eastmoney push2his` 在当前环境里频繁断连，因此场内 ETF 历史行情实际由 `sina_finance_etf_klc2` 完成兜底。
- `pingzhongdata` 是公开接口，不保证长期契约稳定，后续需要加缓存和失败重试。
- `Tushare` 还未接入；如后续需要做对账、补字段或提高稳定性，再单独实现适配层。

## 更新命令

```powershell
python scripts/init_db.py
python scripts/sync_data.py --trade-date 20250318
python scripts/validate_data.py --db-path data/sqlite/fund_data.db
```
