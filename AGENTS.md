# Project Agents Guide

This repository is currently in `stage-1 bootstrap`.

## Active Working Mode

- primary method: `glue-coding`
- fallback method for ambiguity: `philosophy-toolbox`
- deliver small, verifiable steps
- prefer mature libraries and wrappers over self-built infrastructure

## Stage-One Guardrails

- do not enter full implementation
- do not add full backtesting
- do not add auto-trading
- do not add a full frontend experience
- do not add broad active-fund coverage
- do not add complex LLM dependencies

## Source-of-Truth Documents

Update these first when the project direction changes:

- `docs/architecture/v1-scope.md`
- `docs/integrations/data-source-selection.md`
- `docs/features/fund-universe-v1.md`
- `docs/architecture/technical-roadmap.md`
- `docs/guides/phase-two-plan.md`

## Task-Archive Rule

Every substantial change should update the matching task folder under `tasks/`.

## Technical Direction

- Python
- pandas
- SQLite
- FastAPI
- Streamlit
- AkShare as the default V1 ingestion wrapper
- Tushare as the secondary source for later hardening

