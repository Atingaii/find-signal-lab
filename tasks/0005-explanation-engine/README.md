# 0005 Explanation Engine

## Objective

把第四阶段结构化预测输出转换成可复用、可审计的解释结果，不重新训练模型。

## Dependencies

- `0004-baseline-model`

## Fixed Input Contract

- source table: `prediction_explanation_input_latest`
- one row per `fund_code + target_name + model_name + prediction_date`
- mandatory fields:
  - `prediction_label`
  - `prediction_probability`
  - `confidence_level`
  - `top_feature_contributors`
  - `feature_snapshot`
  - `risk_snapshot`
  - `explanation_input_payload`
  - `model_name`
  - `model_version`

## Expected Output

- deterministic explanation payloads
- readable summary text
- daily explanation summary for reporting
