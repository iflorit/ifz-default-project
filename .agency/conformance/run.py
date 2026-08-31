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
    baton = {"project_id": "default", "feature_id": "feat-counter", "state": "spec", "revision": 0}
    baton_hash = _hash(baton)
    transitions: list[str] = []
    recovery: list[str] = []
    stations = list(STATIONS[1:])
    index = 0
    while index < len(stations):
        station = stations[index]
        if mode == "sabotage" and station == "build" and "baton_tamper_detected" not in recovery:
            baton["revision"] = 99
            if _hash(baton) != baton_hash:
                recovery.append("baton_tamper_detected")
                baton["revision"] = 0
                recovery.append("council_restored_last_valid_baton")
        transitions.append(f"{baton['state']}->{station}")
        baton["state"] = station
        baton_hash = _hash(baton)
        if mode == "negative" and station == "review" and "review_rejected_reoriented" not in recovery:
            transitions.append("review->author")
            recovery.append("review_rejected_reoriented")
            baton["state"] = "author"
            baton["revision"] += 1
            baton_hash = _hash(baton)
            # Re-run author, build and review before continuing downstream.
            transitions.extend(("author->build", "build->review"))
            baton["state"] = "review"
            baton_hash = _hash(baton)
        index += 1
    ok = baton["state"] == "done" and (mode != "negative" or "review_rejected_reoriented" in recovery)
    return {"mode": mode, "project_id": "default", "feature_id": baton["feature_id"], "transitions": transitions, "recovery": recovery, "final_state": baton["state"], "ok": ok}


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
