# Plan

## 已执行步骤

1. 定义两个主目标：`future_5d_up`、`future_20d_relative_strength`
2. 实现 `naive_signal`、`rule_baseline`、`logistic_regression`
3. 用 `train` 训练评估模型，用 `valid / test` 验证
4. 输出失败样本、边界样本和家族切片结果
5. 生成最新预测快照与解释输入表

## 后续增强项

1. 需要时再补 `LightGBM / XGBoost` 对比
2. 增加更严格的模型选择和阈值调优
