# 0002 Fund Universe And Data

## Objective

落地第二阶段的数据地基：确认 V1 基金池、接入可用数据源、建立 SQLite 表结构，并跑通最小数据流水线。

## Scope Summary

- 最终基金池固定为 20 只基金。
- 数据源采用 `AkShare + 公开站点补充`。
- 落地 `raw_* + dim/fact` 双层表结构。
- 跑通 `抓取 -> 清洗 -> 落库 -> 校验`。

## Delivered Artifacts

- `config/fund_pool_v1.yaml`
- `src/data_sources/`
- `src/universe/`
- `src/storage/sqlite_store.py`
- `scripts/init_db.py`
- `scripts/sync_data.py`
- `scripts/validate_data.py`
- `docs/data-sources.md`
- `docs/universe.md`
- `docs/data-dictionary.md`
- `docs/reports/stage-two-completion.md`
