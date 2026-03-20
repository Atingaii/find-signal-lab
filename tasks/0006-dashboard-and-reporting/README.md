# 0006 Dashboard And Reporting

## Objective

Expose the latest prediction and explanation snapshots through a thin API layer, Streamlit views, and simple report outputs.

## Dependencies

- `0004-baseline-model`
- `0005-explanation-engine`

## Fixed Input Protocol

- prediction source: `prediction_snapshot_latest`
- explanation source: `prediction_explanation_input_latest` and stage-five explanation outputs
- delivery surfaces must stay read-only and thin
