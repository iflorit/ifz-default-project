#!/usr/bin/env python3
"""Deterministic, side-effect-free default project feature."""

from __future__ import annotations

import argparse
import json


def verify(increment: int, expected: int) -> dict[str, int | bool]:
    value = increment
    return {"ok": value == expected, "value": value}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--increment", type=int, required=True)
    parser.add_argument("--verify", type=int, required=True)
    args = parser.parse_args()
    result = verify(args.increment, args.verify)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
