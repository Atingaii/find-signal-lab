# V1 Scope

## Purpose

Fix the stage-one problem definition and prevent the project from expanding into a full quant platform too early.

## Scope

This document defines the intended V1 target, the phase-one boundary, and the explicit non-goals.

## Status

Approved for stage-one bootstrap on `2026-03-19`.

## Decision Summary

### Problem Definition

The project predicts fund-level direction, not stock-level direction. The first useful question is:

`For a listed passive fund, over the next 1 / 5 / 20 trading days, is it more likely to rise or fall, and is it more likely to outperform or underperform its peer group?`

The output must also explain the prediction in a human-readable way.

### Why V1 Narrows to Listed Passive Funds

- listed funds have clearer market data and trading calendars
- passive funds have clearer benchmark semantics than active funds
- peer grouping is easier when the benchmark family is explicit
- ETF and listed index products are more suitable for a small, repeatable daily batch

### V1 In-Scope

- domestic listed passive equity funds
- daily after-close data collection and prediction flow
- `1 / 5 / 20` trading-day labels
- two output families:
  - absolute direction
  - peer-relative outcome
- simple, deterministic explanation layer
- local storage with SQLite
- thin service layer with FastAPI and Streamlit placeholders

### V1 Non-Goals

- full model training during stage one
- full historical backtesting during stage one
- complex factor library at bootstrap time
- full frontend product design
- auto-trading or order routing
- all-fund coverage across active public funds
- LLM-first explanation generation
- V1 coverage of QDII, bond, money-market, commodity, REIT, leveraged, or inverse products

### Resulting Scope Decision

`ETF / LOF / index fund` is a reasonable V1 boundary only if it is narrowed to `listed passive equity funds first`.

That means:

- ETF is the primary V1 target
- LOF is a secondary target only when it behaves like a listed index-tracking product
- non-listed index funds can inform peer groups later, but they should not blow up the initial prediction target set

## Success Gate For Stage One

Stage one is complete when:

- V1 scope is documented
- non-goals are explicit
- data-source choice is documented
- fund-universe design is documented
- project skeleton exists
- task archives exist

## Evidence

- `README.md`
- `config/app.yaml`
- `docs/integrations/data-source-selection.md`
- `docs/features/fund-universe-v1.md`

## Related

- `docs/architecture/technical-roadmap.md`
- `docs/guides/phase-two-plan.md`

## Changelog

- 2026-03-19: created the initial V1 scope and non-goal definition
