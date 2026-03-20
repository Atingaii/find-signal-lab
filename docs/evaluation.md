# 第四阶段评估说明

## 评估原则

- 严格使用第三阶段的时间切分
- 不做随机打乱
- 同时看分类效果和排序效果
- 输出失败样本与边界样本
- 做最小 `Top-K` 组合模拟

## 当前评估对象

- `future_5d_up`
- `future_20d_relative_strength`

当前对比模型：

- `naive_signal`
- `rule_baseline`
- `logistic_regression`

## 指标定义

- `accuracy`
- `precision`
- `recall`
- `f1`
- `auc`
- `top_k_hit_rate`
- `rank_ic`
- `grouped_return_spread`
- `top_k_mean_return`
- `top_bottom_mean_spread`
- `top_k_max_drawdown`
- `top_bottom_max_drawdown`

## 样本分析产物

每个 `model + target + split` 都落盘：

- `*_predictions.csv`
- `*_backtest.csv`
- `*_failures.csv`
- `*_boundary.csv`
- `*_by_family.csv`

目录：`reports/modeling`

## 当前结果摘要

### target: `future_5d_up`

测试集关键结果：

- `naive_signal`: `rank_ic=0.115993`，`spread=0.005700`
- `rule_baseline`: `accuracy=0.513468`，`f1=0.647990`
- `logistic_regression`: `accuracy=0.515152`，`auc=0.525225`，`top_k_hit_rate=0.641975`

结论：

- 方向分类上，逻辑回归略优于规则模型
- 排序与分组收益差异上，`naive_signal` 并不弱，说明短期方向里简单动量仍有解释力

### target: `future_20d_relative_strength`

测试集关键结果：

- `naive_signal`: `accuracy=0.520202`，`rank_ic=0.109428`
- `rule_baseline`: `f1=0.526646`
- `logistic_regression`: `accuracy=0.589226`，`auc=0.617338`，`rank_ic=0.143771`，`spread=0.003860`

结论：

- `future_20d_relative_strength` 上，逻辑回归是当前最稳的 baseline
- 相对强弱目标比短期涨跌目标更适合当前 V1 特征集

## 限制说明

- 家族切片下部分 `benchmark_family` 只有单只 ETF，因此 `rank_ic` 和 `spread` 可能为空或退化为 0
- 目前只是最小组合模拟，不是完整回测平台
- 评估结果足够支持解释引擎开发，但还不足以证明实盘价值

## 文件入口

- `reports/modeling/evaluation_summary.json`
- `reports/modeling/evaluation_report.md`
- `scripts/evaluate_model.py`
