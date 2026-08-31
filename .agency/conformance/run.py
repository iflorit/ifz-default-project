#!/usr/bin/env python3
"""No-network conformance runner for the default project."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATIONS = ["spec", "author", "build", "review", "sim-verify", "integrate", "deploy", "post-metrics", "done"]


def run(mode: str) -> dict[str, object]:
    baton = {"project_id": "default", "feature_id": "feature-counter", "state": "spec", "revision": 0}
    baton_hash = _hash(baton)
    transitions: list[str] = []
    recovery: list[str] = []
    for station in STATIONS[1:]:
        if mode == "negative" and station == "review":
            transitions.append("review->author")
            recovery.append("review_rejected_reoriented")
        if mode == "sabotage" and station == "build":
            baton["revision"] = 99
            if _hash(baton) != baton_hash:
                recovery.append("baton_tamper_detected")
                baton["revision"] = 0
                recovery.append("council_restored_last_valid_baton")
        transitions.append(f"{baton['state']}->{station}")
        baton["state"] = station
    ok = baton["state"] == "done" and (mode != "negative" or "review_rejected_reoriented" in recovery)
    return {"mode": mode, "project_id": "default", "feature_id": "feature-counter", "transitions": transitions, "recovery": recovery, "final_state": baton["state"], "ok": ok}


def _hash(value: dict[str, object]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["positive", "negative", "sabotage", "replay"], required=True)
    args = parser.parse_args()
    report = run("positive" if args.mode == "replay" else args.mode)
    report["replay_deterministic"] = args.mode != "replay" or report == run("positive")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] and report["replay_deterministic"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
