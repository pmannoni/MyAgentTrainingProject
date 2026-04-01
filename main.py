from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eu_airports_analysis.pipeline import run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build EU medium/large airport map and country-level analyses."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Redownload source datasets even if cache files already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = run(refresh=args.refresh)
    print("Analysis complete. Generated files:")
    for key, path in outputs.items():
        print(f"- {key}: {path}")


if __name__ == "__main__":
    main()
