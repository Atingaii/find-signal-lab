# Fund Universe V1

## Purpose

Define a V1 observation pool that is small enough to execute, liquid enough to study, and clear enough to explain.

## Scope

This document covers which fund categories enter V1, which ones stay out, and how the initial observation pool should be built.

## Status

Approved for stage-one bootstrap on `2026-03-19`.

## Recommended V1 Universe

Use `domestic listed passive equity funds` as the first observation universe.

### Inclusion Priority

1. equity broad-index ETF
2. equity broad-index LOF with acceptable liquidity
3. listed index funds that can be mapped to the same benchmark families

### Exclusions

- active equity funds
- QDII funds
- bond funds
- money-market funds
- commodity funds
- REITs
- leveraged or inverse funds

## Why This Is The Best V1 Starting Point

- benchmark semantics are explicit
- peer grouping is cleaner
- market data is easier to obtain and compare
- liquidity is usually stronger than long-tail fund segments
- explanation logic is easier because benchmark and style context are visible

## Observation-Pool Construction Rule

Build the pool `by benchmark family`, not by randomly mixing fund names.

### Core Benchmark Families

- 上证50
- 沪深300
- 中证500
- 中证1000
- 中证A500
- 创业板指
- 创业板50
- 科创50
- 中证红利
- 红利低波

### Expansion Families

These stay out of the first core pool unless the phase-two data layer is stable:

- 证券公司
- 银行
- 半导体
- 新能源

### Instrument Selection Rule

For each core benchmark family:

- keep `1-2` listed funds
- sort by recent liquidity first
- prefer ETF over LOF
- only include LOF or another listed index product when it tracks the same benchmark family and is liquid enough to compare

### Target Size

- core pool target: `20-30` instruments
- expansion pool target: `10-15` additional instruments after the core pool is stable

## Peer-Group Logic For Later Stages

The default peer group should be:

1. same benchmark family when multiple products exist
2. same style family when benchmark-family coverage is too thin

This avoids comparing a broad-index ETF with a thematic or cross-market product that follows a completely different driver set.

## Evidence

- `docs/integrations/data-source-selection.md`
- `config/app.yaml`
- official sources listed in `docs/integrations/data-source-selection.md`

## Related

- `docs/architecture/v1-scope.md`
- `docs/architecture/technical-roadmap.md`
- `tasks/0002-fund-universe-and-data/README.md`

## Changelog

- 2026-03-19: defined the stage-one recommended V1 universe and observation-pool rule
