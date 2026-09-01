"""Behaviour tests for acceptance criterion 1 of feature `feat-counter`.

Criterion: "Verification returns success only when the expected count matches."
Verification command: `python3 src/counter.py --increment 2 --verify 2`.

The tests assert the observable contract (CLI exit status and JSON report,
plus the public `verify` function), not the shape of the implementation.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTER = ROOT / "src" / "counter.py"

sys.path.insert(0, str(ROOT / "src"))

import counter  # noqa: E402  (import needs the path shim above)


class CounterVerificationTests(unittest.TestCase):
    def _cli(self, increment: int, expected: int) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(COUNTER), "--increment", str(increment), "--verify", str(expected)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout)

    def test_cli_succeeds_when_expected_count_matches(self):
        """The documented verification command must report success."""
        code, report = self._cli(2, 2)
        self.assertEqual(code, 0)
        self.assertTrue(report["ok"])
        self.assertEqual(report["value"], 2)

    def test_cli_fails_when_expected_count_does_not_match(self):
        """Any expectation other than the counted value must not report success."""
        for expected in (1, 3, -2, 0):
            with self.subTest(expected=expected):
                code, report = self._cli(2, expected)
                self.assertNotEqual(code, 0)
                self.assertFalse(report["ok"])
                self.assertEqual(report["value"], 2)

    def test_verify_returns_success_only_on_match(self):
        """`ok` is true for exactly the expectation that equals the count."""
        for increment in (0, 1, 2, 5):
            for expected in range(-2, 6):
                with self.subTest(increment=increment, expected=expected):
                    result = counter.verify(increment, expected)
                    self.assertEqual(result["ok"], increment == expected)
                    self.assertEqual(result["value"], increment)


if __name__ == "__main__":
    unittest.main()
