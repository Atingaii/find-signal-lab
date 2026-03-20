# 第四阶段预测输出协议

## 目标

第四阶段必须输出可直接供第五阶段解释引擎和第六阶段展示层消费的结构化结果，而不是只输出涨跌结论。

## 最新快照表

表：`prediction_snapshot_latest`

用途：保存最新一个预测日的完整预测快照。

当前行数：`44`

构成方式：

- `2` 个 target
- `2` 个 model
- `11` 只 ETF

## 解释输入表

表：`prediction_explanation_input_latest`

用途：为第五阶段解释引擎提供最小、稳定、结构化输入。

## 核心字段

### 预测输出字段

- `fund_code`
- `fund_name`
- `benchmark_family`
- `prediction_date`
- `target_name`
- `prediction_label`
- `prediction_score`
- `prediction_probability`
- `rank_score`
- `confidence_level`
- `model_name`
- `model_version`

### 解释输入字段

- `top_feature_contributors`
- `feature_snapshot`
- `risk_snapshot`
- `explanation_input_payload`

## 字段含义

- `prediction_label`: 二分类结果，`1` 表示偏多或更强，`0` 表示偏空或更弱
- `prediction_score`: 模型原始分数
- `prediction_probability`: 归一化后的概率
- `rank_score`: 用于排序的分数，当前默认等于 `prediction_probability`
- `confidence_level`: `high / medium / low`
- `top_feature_contributors`: 当前样本最主要的 3 个贡献特征
- `feature_snapshot`: 解释相关的主要特征快照
- `risk_snapshot`: 波动、回撤、流动性等风险快照
- `explanation_input_payload`: 为第五阶段准备的整包结构化输入

## confidence_level 规则

- `|probability - 0.5| >= 0.25` -> `high`
- `|probability - 0.5| >= 0.10` -> `medium`
- 其他 -> `low`

## 当前文件产物

目录：`data/processed/predictions`

已生成：

- `rule_baseline_future_5d_up_latest.csv/json`
- `logistic_regression_future_5d_up_latest.csv/json`
- `rule_baseline_future_20d_relative_strength_latest.csv/json`
- `logistic_regression_future_20d_relative_strength_latest.csv/json`
- `prediction_explanation_input_latest.csv/json`
- `prediction_summary.json`

## 与第五阶段的接口

第五阶段默认只消费：

- `prediction_explanation_input_latest`

第五阶段不需要重新训练模型，也不需要重新回放特征工程，只需要在该表基础上做原因模板、风险规则和报告生成。
