# 第四阶段建模说明

## 目标理解

第四阶段不是追求最优收益，而是建立一个可运行、可解释、可验证的 baseline 闭环：

- 从 `dataset_training_samples` 读取标准训练样本
- 训练最小 baseline 模型
- 输出带概率和特征贡献的预测结果
- 为第五阶段解释引擎准备结构化输入

## 范围收敛

- 监督对象只保留 ETF 主样本
- 当前目标聚焦：
  - `future_5d_up`
  - `future_20d_relative_strength`
- 模型顺序：
  - `naive_signal` 只作为对照
  - `rule_baseline`
  - `logistic_regression`
- `LightGBM / XGBoost` 只保留兼容位，不在当前阶段启用

## 输入数据

训练表：`dataset_training_samples`

关键字段：

- 主键：`fund_code + trade_date`
- 时间切分：`dataset_split`
- 特征：来自第三阶段 `CORE_FEATURE_COLUMNS`
- 标签：
  - `future_5d_up`
  - `future_20d_relative_strength`

## 模型设计

### 1. naive_signal

用途：只做最简单的对照，不参与最终最新快照产物。

- `future_5d_up` 使用 `return_5d`
- `future_20d_relative_strength` 使用 `excess_return_20d`

输出：

- `prediction_score`
- `prediction_probability`
- `top_feature_contributors`

### 2. rule_baseline

用途：最小可解释规则打分模型。

实现方式：

- 先对输入特征按训练集均值和标准差标准化
- 用手工权重求和生成 `prediction_score`
- 经 sigmoid 变换为 `prediction_probability`
- 取绝对贡献最高的 3 个特征作为 `top_feature_contributors`

### 3. logistic_regression

用途：可训练、可解释的线性分类 baseline。

实现方式：

- `StandardScaler + LogisticRegression`
- 保留模型系数文件
- 为每条样本计算线性贡献并输出前 3 个贡献特征

## 训练规则

- 最终模型工件用 `train + valid` 拟合
- 评估时用 `train` 拟合，在 `valid / test` 上验证
- 不允许随机打乱切分
- 训练前将 `inf/-inf` 视作缺失，并用训练集特征中位数填补

## 输出工件

模型工件目录：`data/processed/models`

已生成：

- `future_5d_up_rule_baseline.json`
- `future_5d_up_logistic.joblib`
- `future_5d_up_logistic_coefficients.csv`
- `future_20d_relative_strength_rule_baseline.json`
- `future_20d_relative_strength_logistic.joblib`
- `future_20d_relative_strength_logistic_coefficients.csv`
- `training_summary.json`

## 代码入口

- `src/models/config.py`
- `src/models/naive_model.py`
- `src/models/rule_baseline.py`
- `src/models/logistic_model.py`
- `src/models/lgbm_model.py`
- `scripts/train_baseline.py`
