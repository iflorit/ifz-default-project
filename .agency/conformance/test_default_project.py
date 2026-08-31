import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / ".agency" / "conformance" / "run.py"


class DefaultProjectConformanceTests(unittest.TestCase):
    def _run(self, mode: str) -> dict:
        result = subprocess.run([sys.executable, str(RUNNER), "--mode", mode], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_positive_path_reaches_done(self):
        report = self._run("positive")
        self.assertEqual(report["final_state"], "done")
        self.assertEqual(len(report["transitions"]), 8)

    def test_negative_path_reorients_after_review_failure(self):
        report = self._run("negative")
        self.assertIn("review_rejected_reoriented", report["recovery"])
        self.assertEqual(report["final_state"], "done")

    def test_sabotage_detects_and_recovers_baton(self):
        report = self._run("sabotage")
        self.assertIn("baton_tamper_detected", report["recovery"])
        self.assertIn("council_restored_last_valid_baton", report["recovery"])

    def test_replay_is_deterministic(self):
        report = self._run("replay")
        self.assertTrue(report["replay_deterministic"])


if __name__ == "__main__":
    unittest.main()
