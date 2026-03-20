# Technical Roadmap

## Purpose

Describe the smallest technical route that can support the future V1 without overbuilding.

## Scope

This document covers the planned stack, execution flow, and repository responsibilities from data ingestion to prediction serving.

## Status

Initialized on `2026-03-19`.

## Stack Decision

Keep the default stack and do not expand it without a concrete need:

- Python
- pandas
- SQLite
- FastAPI
- Streamlit
- AkShare
- Tushare

No additional database, workflow engine, or LLM framework is needed in stage one.

## Planned Flow

### Layer 1: Source Connectors

- `AkShare` connectors for fund master, ETF, LOF, and index-fund metadata
- `Tushare` connector reserved for reconciliation and later hardening
- official public pages reserved for whitelist and benchmark verification

### Layer 2: Local Warehouse

Use `SQLite` in `data/processed/fund_predictor.db`.

Planned core tables:

- `fund_master`
- `trade_calendar`
- `market_daily`
- `nav_daily`
- `universe_membership`
- `prediction_snapshot`

### Layer 3: Feature and Label Pipeline

Planned stage-two outputs:

- next `1 / 5 / 20` trading-day direction labels
- next `1 / 5 / 20` trading-day peer-relative labels
- baseline features from price, volume, turnover, volatility, benchmark family, and peer ranking

### Layer 4: Serving Layer

- FastAPI for health, scope, and later prediction endpoints
- Streamlit for experiment visibility, daily summaries, and diagnostic views

### Layer 5: Explanation Layer

Start with deterministic reasons:

- short-term momentum or reversal
- recent volatility regime
- abnormal turnover or flow context
- benchmark-relative strength or weakness
- peer percentile change

## Repository Mapping

- `src/fund_direction_predictor/api/`: FastAPI entry
- `src/fund_direction_predictor/ui/`: Streamlit entry
- `config/app.yaml`: stage-one decision config
- `scripts/dev/`: local run and syntax-check scripts
- `tasks/`: execution archive by milestone

## Evidence

- `README.md`
- `config/app.yaml`
- `tasks/README.md`

## Related

- `docs/architecture/v1-scope.md`
- `docs/features/fund-universe-v1.md`
- `docs/guides/phase-two-plan.md`

## Changelog

- 2026-03-19: created the minimal technical roadmap for the project
