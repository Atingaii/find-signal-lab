# 第三阶段标签说明

## 设计原则核对

当前标签定义适合基金方向预测，原因如下：

- `future_1d_up / future_5d_up / future_20d_up` 直接对应项目目标中的未来涨跌判断。
- `future_5d_relative_strength / future_20d_relative_strength` 对应项目目标中的跑赢同类/跑输同类。
- 标签只依赖未来窗口，不回流到当前特征。
- ETF 与 LOF / INDEX 统一走参考序列标签公式，但阶段四训练默认只使用 ETF 样本。

## 标签来源口径

标签基于 `feature_fund_reference_daily` 的 `reference_value` 计算：

- ETF：未来市场收盘价收益
- LOF / INDEX：未来单位净值收益

这保证了标签口径可追溯，但也明确区分了 `reference_basis`。

## 已实现标签

### 绝对方向标签

- `future_1d_return`
- `future_5d_return`
- `future_20d_return`
- `future_1d_up = 1(future_1d_return > 0)`
- `future_5d_up = 1(future_5d_return > 0)`
- `future_20d_up = 1(future_20d_return > 0)`

### 相对强弱标签

默认 peer group：`benchmark_family`

- `future_5d_peer_median_return`
- `future_20d_peer_median_return`
- `future_5d_relative_excess = future_5d_return - future_5d_peer_median_return`
- `future_20d_relative_excess = future_20d_return - future_20d_peer_median_return`
- `future_5d_relative_strength = 1(future_5d_relative_excess > 0)`
- `future_20d_relative_strength = 1(future_20d_relative_excess > 0)`

当同家族同日可用未来收益样本少于 2 个时，相对强弱标签保持为空。

## 未来窗口定义

对任意样本 `(fund_code, trade_date = t)`：

- `future_date_1d` 是该基金时间序列中的下 1 个观测日
- `future_date_5d` 是下 5 个观测日
- `future_date_20d` 是下 20 个观测日

收益计算公式：

`future_hd_return = reference_value_(t+h) / reference_value_t - 1`

这里的 `h` 是该基金自身序列中的未来观测步长，不使用未来窗口外的任何信息。

## 缺失值策略

- 若未来窗口不足，相关标签为空
- 相对标签要求同家族至少有 2 个可比较样本，否则为空
- 训练集导出时只保留 `future_1d_up / future_5d_up / future_20d_up / future_5d_relative_strength / future_20d_relative_strength` 全部存在的 ETF 样本

## 结果摘要

`scripts/build_labels.py` 最新结果：

- `rows = 25843`
- `funds = 20`
- `primary_target_rows = 5666`
- `label_ready_1d = 25823`
- `label_ready_5d = 25743`
- `label_ready_20d = 25443`

## 代码入口

- `src/labels/future_returns.py`
- `scripts/build_labels.py`
