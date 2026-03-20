# Phase Two Plan

## Purpose

Turn the stage-one documents and skeleton into the first executable V1 data and baseline pipeline.

## Scope

This document recommends the order of work for the next stage without jumping into full implementation detail.

## Status

Drafted on `2026-03-19` as the next-step guide after stage-one bootstrap.

## Recommended Execution Order

### 1. Build the Universe and Daily Warehouse

Start with `0002-fund-universe-and-data`.

Exit criteria:

- fund master table is populated
- core observation universe is generated from benchmark families
- daily ETF and selected LOF history can be pulled into SQLite
- trade calendar is stored

### 2. Build Labels and Baseline Features

Move to `0003-feature-and-label-pipeline`.

Exit criteria:

- `1 / 5 / 20` day direction labels are generated
- peer-relative labels are generated
- a baseline feature set exists for each observation date

### 3. Train a Lightweight Baseline

Then `0004-baseline-model`.

Exit criteria:

- at least one simple baseline model is trained
- label leakage checks are documented
- evaluation is sliced by horizon and benchmark family

### 4. Add a Deterministic Explanation Engine

Then `0005-explanation-engine`.

Exit criteria:

- explanations map to observable features
- explanation text is reproducible from the same input snapshot

### 5. Add Basic Delivery Surfaces

Finally `0006-dashboard-and-reporting`.

Exit criteria:

- API can expose the latest snapshot
- Streamlit can display daily summaries
- report export is available in a minimal form

## Guardrails For Phase Two

- keep the stack unchanged unless a real bottleneck appears
- baseline-first is mandatory
- do not expand to full-fund coverage before the core pool is stable
- do not add complex model explainability tooling before the deterministic explanation layer exists

## Evidence

- `tasks/0002-fund-universe-and-data/README.md`
- `tasks/0003-feature-and-label-pipeline/README.md`
- `tasks/0004-baseline-model/README.md`
- `tasks/0005-explanation-engine/README.md`
- `tasks/0006-dashboard-and-reporting/README.md`

## Related

- `docs/architecture/technical-roadmap.md`
- `docs/features/fund-universe-v1.md`

## Changelog

- 2026-03-19: created the next-stage execution recommendation
