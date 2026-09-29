"""Tests for B-007: GateScore calculation in gate reports."""
import unittest

from scripts.gate_score_report import (
    GateScoreInput,
    GateScoreReport,
    generate_gate_score_report,
    GateDecision,
)


class GateScoreReportTests(unittest.TestCase):
    def _perfect(self, gate: int = 3) -> GateScoreInput:
        return GateScoreInput(
            wave_id="WAVE-001",
            gate=gate,
            tests_passed=10,
            tests_total=10,
            dq_score=1.0,
            row_parity=1.0,
        )

    def test_perfect_score_is_100(self) -> None:
        report = generate_gate_score_report(self._perfect())
        self.assertAlmostEqual(100.0, report.gate_score, places=1)

    def test_zero_score_is_zero(self) -> None:
        inp = GateScoreInput(
            wave_id="WAVE-001", gate=3,
            tests_passed=0, tests_total=10,
            dq_score=0.0, row_parity=0.0,
        )
        report = generate_gate_score_report(inp)
        self.assertAlmostEqual(0.0, report.gate_score, places=1)

    def test_decision_pass_above_threshold(self) -> None:
        inp = GateScoreInput(
            wave_id="WAVE-001", gate=3,
            tests_passed=9, tests_total=10,  # 90%
            dq_score=0.98,
            row_parity=1.0,
        )
        report = generate_gate_score_report(inp)
        self.assertEqual(GateDecision.PASS, report.decision)

    def test_decision_fail_below_threshold(self) -> None:
        inp = GateScoreInput(
            wave_id="WAVE-001", gate=3,
            tests_passed=5, tests_total=10,  # 50%
            dq_score=0.80,
            row_parity=0.90,
        )
        report = generate_gate_score_report(inp)
        self.assertEqual(GateDecision.FAIL, report.decision)

    def test_report_contains_required_fields(self) -> None:
        report = generate_gate_score_report(self._perfect())
        self.assertEqual("WAVE-001", report.wave_id)
        self.assertEqual(3, report.gate)
        self.assertIsNotNone(report.generated_at)
        self.assertGreater(report.gate_score, 0)

    def test_score_formula_correct(self) -> None:
        """GateScore = tests_rate*40 + dq*30 + parity*30."""
        inp = GateScoreInput(
            wave_id="WAVE-001", gate=3,
            tests_passed=8, tests_total=10,  # 0.80
            dq_score=0.90,
            row_parity=0.95,
        )
        expected = round(0.80 * 40 + 0.90 * 30 + 0.95 * 30, 2)
        report = generate_gate_score_report(inp)
        self.assertAlmostEqual(expected, report.gate_score, places=1)


if __name__ == "__main__":
    unittest.main()
