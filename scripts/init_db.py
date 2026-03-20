from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from storage.sqlite_store import SQLiteStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the stage-two SQLite database.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="Target SQLite database path.",
    )
    args = parser.parse_args()

    store = SQLiteStore(Path(args.db_path))
    store.initialize()
    print(f"Initialized SQLite schema at {store.path}")


if __name__ == "__main__":
    main()
