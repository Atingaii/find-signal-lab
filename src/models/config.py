from __future__ import annotations


TARGET_CONFIGS = {
    "future_5d_up": {
        "label_column": "future_5d_up",
        "actual_return_column": "future_5d_return",
        "feature_columns": [
            "daily_return_1d",
            "return_5d",
            "momentum_5_minus_20",
            "excess_return_5d",
            "style_strength_20d",
            "volatility_20d",
            "max_drawdown_20d",
            "amount_change_1d",
            "market_turnover_5d_avg",
        ],
        "rule_weights": {
            "daily_return_1d": 0.10,
            "return_5d": 0.30,
            "momentum_5_minus_20": 0.20,
            "excess_return_5d": 0.20,
            "style_strength_20d": 0.10,
            "volatility_20d": -0.10,
            "max_drawdown_20d": 0.10,
            "amount_change_1d": 0.05,
            "market_turnover_5d_avg": 0.05,
        },
        "top_k": 3,
    },
    "future_20d_relative_strength": {
        "label_column": "future_20d_relative_strength",
        "actual_return_column": "future_20d_relative_excess",
        "feature_columns": [
            "return_5d",
            "return_20d",
            "momentum_10_minus_20",
            "excess_return_5d",
            "excess_return_20d",
            "style_strength_20d",
            "volatility_20d",
            "max_drawdown_20d",
            "market_turnover_5d_avg",
        ],
        "rule_weights": {
            "return_5d": 0.05,
            "return_20d": 0.20,
            "momentum_10_minus_20": 0.10,
            "excess_return_5d": 0.10,
            "excess_return_20d": 0.30,
            "style_strength_20d": 0.20,
            "volatility_20d": -0.10,
            "max_drawdown_20d": 0.10,
            "market_turnover_5d_avg": 0.05,
        },
        "top_k": 3,
    },
}

