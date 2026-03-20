# Context

## 上游输入

- `fund_universe_membership`
- `dim_fund`
- `fact_fund_market_daily`
- `fact_fund_nav_daily`
- `fact_macro_observation`

## 已确定字段口径

- ETF 参考值：`close`
- LOF / INDEX 参考值：`unit_nav`
- 统一字段：`reference_value`
- 统一口径标记：`reference_basis`
- 主监督样本标记：`is_primary_target`

## 窗口与标签规则

- 特征窗口：`1 / 5 / 10 / 20`
- 标签窗口：`1 / 5 / 20`
- peer group：`benchmark_family`
- 训练样本主键：`fund_code + trade_date`

## 缺失与防泄漏规则

- 所有滚动特征必须完整窗口，不足则为空
- 宏观变量按最近可得日期向前对齐
- 特征只允许使用 `<= t` 的数据
- 标签只允许使用 `(t, t+h]`
- ETF 缺少市场行情时，该日期不得进入标准训练集
- `premium_discount_rate / share_change_20d / aum_change_20d` 仅保留为空字段，不进入标准训练集
