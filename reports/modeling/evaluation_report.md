# 第四阶段评估报告

## future_5d_up

### naive_signal

- valid: accuracy=0.518519, f1=0.622691, auc=0.503775, top_k_hit_rate=0.716049, rank_ic=0.175084, spread=0.010342
- test: accuracy=0.469697, f1=0.526316, auc=0.462701, top_k_hit_rate=0.635802, rank_ic=0.115993, spread=0.0057

### rule_baseline

- valid: accuracy=0.557239, f1=0.6498, auc=0.527331, top_k_hit_rate=0.722222, rank_ic=0.062795, spread=0.003821
- test: accuracy=0.513468, f1=0.64799, auc=0.429345, top_k_hit_rate=0.635802, rank_ic=0.019865, spread=0.001998

### logistic_regression

- valid: accuracy=0.474747, f1=0.469388, auc=0.550862, top_k_hit_rate=0.62963, rank_ic=0.055556, spread=0.005359
- test: accuracy=0.515152, f1=0.588571, auc=0.525225, top_k_hit_rate=0.641975, rank_ic=0.072559, spread=0.001663

## future_20d_relative_strength

### naive_signal

- valid: accuracy=0.56734, f1=0.67995, auc=0.558644, top_k_hit_rate=0.641975, rank_ic=0.165488, spread=0.001353
- test: accuracy=0.520202, f1=0.490161, auc=0.510197, top_k_hit_rate=0.444444, rank_ic=0.109428, spread=0.001817

### rule_baseline

- valid: accuracy=0.592593, f1=0.686528, auc=0.600336, top_k_hit_rate=0.679012, rank_ic=0.191077, spread=0.002496
- test: accuracy=0.491582, f1=0.526646, auc=0.492391, top_k_hit_rate=0.444444, rank_ic=0.06936, spread=0.001276

### logistic_regression

- valid: accuracy=0.405724, f1=0.165485, auc=0.542354, top_k_hit_rate=0.716049, rank_ic=0.153367, spread=0.002666
- test: accuracy=0.589226, f1=0.460177, auc=0.617338, top_k_hit_rate=0.518519, rank_ic=0.143771, spread=0.00386
