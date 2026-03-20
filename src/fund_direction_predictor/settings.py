from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "app.yaml"


@lru_cache(maxsize=1)
def load_config() -> dict[str, object]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    if not isinstance(raw, dict):
        raise ValueError(f"Expected mapping config at {CONFIG_PATH}")

    return cast(dict[str, object], raw)
