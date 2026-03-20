# 第三阶段完成报告

## 阶段目标

第三阶段只做三件事：

1. 基于第二阶段数据库建立统一特征流水线
2. 落地 `1 / 5 / 20` 标签体系
3. 产出阶段四可直接消费的标准训练数据集

本阶段不训练正式模型，不做前端，不做完整回测。

## 已完成项

1. 建立统一参考序列：ETF 用收盘价，LOF / INDEX 用单位净值。
2. 实现最小可解释特征集合：收益、动量、波动、回撤、成交额、相对强弱、最小宏观。
3. 实现 `future_1d_up / future_5d_up / future_20d_up`。
4. 实现 `future_5d_relative_strength / future_20d_relative_strength`。
5. 建立标准训练数据集导出脚本与时间切分规则。
6. 文档化字段血缘、缺失值策略、样本切分和防未来函数规则。
7. 更新 `tasks/0003`，并补充 `tasks/0004` 的输入约束。

## 新增代码与脚本

- `src/common/db.py`
- `src/features/price_features.py`
- `src/features/fund_features.py`
- `src/features/style_features.py`
- `src/features/macro_features.py`
- `src/labels/future_returns.py`
- `src/datasets/build_training_dataset.py`
- `scripts/build_features.py`
- `scripts/build_labels.py`
- `scripts/export_dataset.py`

## 产物与表

- SQLite 表：`feature_fund_reference_daily`
- SQLite 表：`feature_fund_daily`
- SQLite 表：`label_fund_daily`
- SQLite 表：`dataset_training_samples`
- 导出文件：`data/processed/features/feature_fund_daily.csv`
- 导出文件：`data/processed/labels/label_fund_daily.csv`
- 导出文件：`data/processed/datasets/training_dataset_v1.csv`

## 最新验证结果

- 特征表：`25843` 行，覆盖 `20` 只基金
- 标签表：`25843` 行，覆盖 `20` 只基金
- 标准训练集：`4481` 行，覆盖 `11` 只 ETF
- split 分布：`train=3293`，`valid=594`，`test=594`

## 关键决策

- ETF 是阶段四默认监督对象，LOF / INDEX 主要作为同类参照和净值参考。
- `benchmark_family` 继续作为同类分组锚点。
- 特征窗口收敛为 `1 / 5 / 10 / 20`，标签窗口固定为 `1 / 5 / 20`。
- 宏观变量使用最近可得值对齐，不引入未来信息。
- 由于第二阶段未沉淀 ETF 历史净值、份额和 AUM，`premium_discount_rate / share_change_20d / aum_change_20d` 仅保留字段，不进入标准训练集。

## 第四阶段输入说明

第四阶段建模应直接使用：

- `dataset_training_samples`

推荐最小流程：

1. 先做 rule baseline 或线性 / 树模型 baseline
2. 分别对 `1d / 5d / 20d` 与相对强弱标签建模
3. 严格按 `dataset_split` 评估
4. 输出按 `benchmark_family` 切片的指标
