#!/usr/bin/env python3
"""Dry-run CLI for the first Granja Luna operational MVP.

The script intentionally uses local rules only. It does not call an LLM, does
not use an agent framework, and does not modify files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.dry_run import build_dry_run


def main() -> int:
    parser = argparse.ArgumentParser(description="Granja Luna dry-run CLI")
    parser.add_argument("message", help="Mensaje natural a analizar")
    parser.add_argument(
        "--today",
        help="Fecha ISO para pruebas o reproduccion. Por defecto usa la fecha local.",
    )
    args = parser.parse_args()
    result = build_dry_run(args.message, today=args.today)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
