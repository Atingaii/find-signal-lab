# Data Source Selection

## Purpose

Choose a realistic V1 data-source stack for fund master data, listed-fund market data, and future validation.

## Scope

This document compares `AkShare`, `Tushare`, and official public sources for the stage-one and V1 context.

## Status

Decision fixed for stage one on `2026-03-19`.

## Recommendation

- primary V1 ingestion: `AkShare`
- secondary backup and later hardening path: `Tushare`
- official public sources: validation, benchmark verification, and universe maintenance

## Evaluation

### AkShare

Fit:

- best for V1 speed and low-friction integration
- already exposes fund master data, index-fund metadata, ETF data, and LOF data

Observed evidence from the official documentation:

- `fund_name_em`: all-fund basic information
- `fund_info_index_em`: index-fund metadata with benchmark and tracking mode
- `fund_etf_spot_em`: ETF real-time data
- `fund_lof_spot_em`: LOF real-time data
- `fund_etf_hist_em`: ETF historical daily data

Trade-off:

- excellent bootstrap speed
- underlying upstreams are third-party finance sites, so schema drift and anti-scrape changes remain a risk

Decision:

- use as the V1 default source

### Tushare

Fit:

- good candidate for later standardization and production hardening
- useful as a second opinion and reconciliation source

Observed evidence from the official documentation:

- `fund_basic`, `fund_nav`, `fund_daily` are official documented fund endpoints
- token setup is required through the SDK
- fund endpoints have points thresholds, and `fund_adj` is gated even higher

Trade-off:

- cleaner contracts
- not zero-friction because token and积分 are part of real access cost

Decision:

- do not make it the stage-one primary source
- keep it as the planned secondary source once credentials and points are prepared

### Official Public Sources

Fit:

- authoritative for product lists, definitions, and market-structure context
- useful as the correctness layer for the observation universe

Observed evidence from official pages:

- SSE fund website exposes fund list filtering and Excel export
- SZSE explicitly defines LOF as a listed open-ended fund that trades on the secondary market
- official exchange reports show that broad-based ETF liquidity and investor participation are already strong

Trade-off:

- authoritative but fragmented
- more suitable for validation than for the main V1 ingestion workflow

Decision:

- use as verification and whitelist support, not as the primary daily batch source

## Selection Result

The V1 stack should be:

1. AkShare for bootstrap ingestion
2. SQLite as the first warehouse
3. Tushare as an optional reconciliation and hardening path
4. Official exchange pages as the authoritative check layer

## Evidence

Validated on `2026-03-19` with the following sources:

- AkShare public-fund documentation: <https://akshare.akfamily.xyz/data/fund/fund_public.html>
- Tushare data catalog: <https://tushare.pro/document/1?doc_id=108>
- Tushare SDK token setup: <https://tushare.pro/document/1?doc_id=131>
- SSE fund list page: <https://etf.sse.com.cn/fundlist/>
- SSE ETF development report 2025: <https://etf.sse.com.cn/fundtrends/c/10770698/files/69a55dcfb84b4e8e87dc6cf396c628f7.pdf>
- SZSE LOF definition page: <https://www.szse.cn/www/investor/knowledge/fund/lof/t20161123_538832.html>
- SZSE index-fund development news: <https://www.szse.cn/aboutus/trends/news/t20230810_602615.html>

## Related

- `docs/architecture/v1-scope.md`
- `docs/features/fund-universe-v1.md`
- `config/app.yaml`

## Changelog

- 2026-03-19: recorded the stage-one source-selection decision and evidence links
