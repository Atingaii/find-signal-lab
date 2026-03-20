# 第四阶段完成报告

## 阶段目标

第四阶段只做三件事：

1. 训练并验证可解释 baseline 模型
2. 输出结构化预测结果
3. 为第五阶段准备稳定解释输入

## 已完成项

1. 实现 `naive_signal` 对照模型
2. 实现 `rule_baseline` 规则打分模型
3. 实现 `logistic_regression` 逻辑回归模型
4. 对 `future_5d_up` 和 `future_20d_relative_strength` 完成验证
5. 输出 `valid / test` 分类、排序和最小组合模拟指标
6. 输出失败样本、边界样本和按 `benchmark_family` 切片结果
7. 输出最新预测快照和解释输入表

## 新增代码与脚本

- `src/models/config.py`
- `src/models/naive_model.py`
- `src/models/rule_baseline.py`
- `src/models/logistic_model.py`
- `src/models/lgbm_model.py`
- `src/evaluation/metrics.py`
- `src/evaluation/backtest.py`
- `src/prediction/predict.py`
- `scripts/train_baseline.py`
- `scripts/evaluate_model.py`
- `scripts/run_prediction.py`

## 关键结果

### future_5d_up

测试集上：

- 分类最稳：`logistic_regression`
- F1 最高：`rule_baseline`
- 排序和 spread 最强：`naive_signal`

说明：短期方向上，当前特征集的强弱排序信息存在，但方向分类优势并不大。

### future_20d_relative_strength

测试集上：

- 当前最优 baseline：`logistic_regression`
- `accuracy = 0.589226`
- `auc = 0.617338`
- `rank_ic = 0.143771`
- `top_bottom_mean_spread = 0.003860`

说明：相对强弱目标更适合当前 V1 特征和基金池结构。

## 产物位置

- 模型工件：`data/processed/models`
- 评估报告与明细：`reports/modeling`
- 最新预测快照：`data/processed/predictions`
- SQLite 表：
  - `prediction_snapshot_latest`
  - `prediction_explanation_input_latest`

## 第五阶段输入说明

第五阶段默认只消费：

- `prediction_explanation_input_latest`

第五阶段要做的是：

1. 把 `top_feature_contributors + feature_snapshot + risk_snapshot` 转成结构化理由
2. 输出每只基金的偏多 / 偏空 / 中性说明
3. 生成 Top 看多 / Top 看空摘要和日报

## 当前限制

- 仍然是 baseline-first，不代表模型已可直接实盘
- 家族切片下部分指标会因为样本太少而退化
- `LightGBM / XGBoost` 还未接入，保留为后续对比项
