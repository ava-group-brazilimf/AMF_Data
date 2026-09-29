import unittest

from scripts.wave_status_tracker import (
    GateStatus,
    PhaseStatus,
    WaveStatusSummary,
    WaveStatusTracker,
    compare_estimates,
    EstimateComparison,
    format_estimate_table,
    wave_estimate_accuracy,
)


class GateStatusTests(unittest.TestCase):
    def test_not_started_when_no_artifacts(self) -> None:
        gs = GateStatus(gate=1, artifacts_present=0, artifacts_total=5)
        self.assertEqual(gs.phase_status, PhaseStatus.NOT_STARTED)

    def test_in_progress_when_partial_artifacts(self) -> None:
        gs = GateStatus(gate=1, artifacts_present=3, artifacts_total=5)
        self.assertEqual(gs.phase_status, PhaseStatus.IN_PROGRESS)

    def test_complete_when_all_artifacts_no_score(self) -> None:
        gs = GateStatus(gate=1, artifacts_present=5, artifacts_total=5)
        self.assertEqual(gs.phase_status, PhaseStatus.COMPLETE)

    def test_complete_when_all_artifacts_and_passing_score(self) -> None:
        gs = GateStatus(gate=2, artifacts_present=5, artifacts_total=5, gate_score=88.0)
        self.assertEqual(gs.phase_status, PhaseStatus.COMPLETE)

    def test_blocked_when_all_artifacts_but_low_score(self) -> None:
        gs = GateStatus(gate=3, artifacts_present=8, artifacts_total=8, gate_score=65.0)
        self.assertEqual(gs.phase_status, PhaseStatus.BLOCKED)

    def test_artifacts_pct_zero_when_no_total(self) -> None:
        gs = GateStatus(gate=1)
        self.assertEqual(gs.artifacts_pct, 0.0)

    def test_artifacts_pct_calculation(self) -> None:
        gs = GateStatus(gate=2, artifacts_present=3, artifacts_total=5)
        self.assertEqual(gs.artifacts_pct, 60.0)


class WaveStatusTrackerTests(unittest.TestCase):
    def test_initial_state_all_not_started(self) -> None:
        tracker = WaveStatusTracker(wave_id="WAVE-001")
        summary = tracker.summary()
        self.assertEqual(summary.wave_id, "WAVE-001")
        self.assertEqual(summary.overall_pct, 0.0)
        for gs in summary.gates:
            self.assertEqual(gs.phase_status, PhaseStatus.NOT_STARTED)

    def test_set_gate_artifacts(self) -> None:
        tracker = WaveStatusTracker(wave_id="WAVE-002")
        tracker.set_gate_artifacts(1, present=5, total=5)
        tracker.set_gate_artifacts(2, present=3, total=5)
        tracker.set_gate_artifacts(3, present=0, total=8)

        summary = tracker.summary()
        self.assertEqual(summary.gates[0].artifacts_present, 5)
        self.assertEqual(summary.gates[1].artifacts_present, 3)
        self.assertEqual(summary.gates[2].artifacts_present, 0)
        # overall: 8 out of 18
        expected_pct = round(8 / 18 * 100, 1)
        self.assertEqual(summary.overall_pct, expected_pct)

    def test_set_gate_score(self) -> None:
        tracker = WaveStatusTracker(wave_id="WAVE-003")
        tracker.set_gate_artifacts(1, present=5, total=5)
        tracker.set_gate_score(1, 92.0)

        summary = tracker.summary()
        self.assertEqual(summary.gates[0].gate_score, 92.0)
        self.assertEqual(summary.gates[0].phase_status, PhaseStatus.COMPLETE)

    def test_invalid_gate_raises(self) -> None:
        tracker = WaveStatusTracker(wave_id="WAVE-X")
        with self.assertRaises(ValueError):
            tracker.set_gate_artifacts(4, present=1, total=1)
        with self.assertRaises(ValueError):
            tracker.set_gate_score(0, 80.0)

    def test_summary_str_contains_wave_id(self) -> None:
        tracker = WaveStatusTracker(wave_id="WAVE-010")
        tracker.set_gate_artifacts(1, present=5, total=5)
        tracker.set_gate_score(1, 88.0)
        output = str(tracker.summary())
        self.assertIn("WAVE-010", output)
        self.assertIn("Gate 1", output)
        self.assertIn("COMPLETE", output)

    def test_blocked_gate_appears_in_summary(self) -> None:
        tracker = WaveStatusTracker(wave_id="WAVE-BLK")
        tracker.set_gate_artifacts(3, present=8, total=8)
        tracker.set_gate_score(3, 55.0)
        summary = tracker.summary()
        self.assertEqual(summary.gates[2].phase_status, PhaseStatus.BLOCKED)

    def test_tables_remaining_normal(self) -> None:
        summary = WaveStatusSummary(
            wave_id="WAVE-001",
            gates=[],
            overall_pct=0.0,
            tables_migrated=7,
            tables_total=10,
        )

        self.assertEqual(3, summary.tables_remaining)
        self.assertEqual(30.0, summary.backlog_pct)

    def test_backlog_pct_zero_total(self) -> None:
        summary = WaveStatusSummary(
        wave_id="WAVE-001",
        gates=[],
        overall_pct=0.0,
        tables_migrated=0,
        tables_total=0,
    )

        self.assertEqual(0.0, summary.backlog_pct)


    def test_tables_remaining_never_negative(self) -> None:
        summary = WaveStatusSummary(
        wave_id="WAVE-001",
        gates=[],
        overall_pct=0.0,
        tables_migrated=15,
        tables_total=10,
    )

        self.assertEqual(0, summary.tables_remaining)
        self.assertEqual(0.0, summary.backlog_pct)

    def test_gb_remaining(self) -> None:
        summary = WaveStatusSummary(
        wave_id="WAVE-001",
        gates=[],
        overall_pct=0.0,
        gb_total=100.0,
        gb_migrated=25.5,
    )

        self.assertEqual(74.5, summary.gb_remaining)

    def test_gb_remaining_never_negative(self) -> None:
        summary = WaveStatusSummary(
        wave_id="WAVE-001",
        gates=[],
        overall_pct=0.0,
        gb_total=10.0,
        gb_migrated=20.0,
    )

        self.assertEqual(0.0, summary.gb_remaining)

    def test_compare_estimates_exact_match(self) -> None:
        entities = [{"name": "Customer", "estimated_rows": 1000}]
        actuals = {"Customer": 1000}
        result = compare_estimates(entities, actuals)
        self.assertEqual(0, result[0].delta)
        self.assertEqual(0.0, result[0].delta_pct)

    def test_compare_estimates_above_estimate(self) -> None:
        entities = [{"name": "Order", "estimated_rows": 1000}]
        actuals = {"Order": 1200}
        result = compare_estimates(entities, actuals)
        self.assertEqual(200, result[0].delta)
        self.assertEqual(20.0, result[0].delta_pct)

    def test_compare_estimates_below_estimate(self) -> None:
        entities = [{"name": "Invoice", "estimated_rows": 1000}]
        actuals = {"Invoice": 800}
        result = compare_estimates(entities, actuals)
        self.assertEqual(-200, result[0].delta)
        self.assertEqual(-20.0, result[0].delta_pct)

    def test_compare_estimates_not_migrated_yet(self) -> None:
        entities = [{"name": "Product", "estimated_rows": 500}]
        actuals: dict[str, int] = {}
        result = compare_estimates(entities, actuals)
        self.assertEqual(0, result[0].actual_rows)
        self.assertEqual(-500, result[0].delta)

    def test_compare_estimates_zero_estimated(self) -> None:
        entities = [{"name": "Legacy", "estimated_rows": 0}]
        actuals = {"Legacy": 50}
        result = compare_estimates(entities, actuals)
        self.assertEqual(0.0, result[0].delta_pct)  # guarda de divisão por zero

    def test_format_estimate_table(self) -> None:
        comps = [EstimateComparison(entity="Customer", estimated_rows=19820, actual_rows=19820)]
        table = format_estimate_table(comps)
        self.assertIn("Customer", table)
        self.assertIn("19,820", table)
        self.assertIn("+0", table)


    def test_accuracy_pct_exact_estimate(self) -> None:
        comparison = EstimateComparison(
            entity="Customer",
            estimated_rows=1000,
            actual_rows=1000,
        )

        self.assertEqual(100.0, comparison.accuracy_pct)

    def test_accuracy_pct_over_estimate(self) -> None:
        comparison = EstimateComparison(
            entity="Customer",
            estimated_rows=1000,
            actual_rows=1200,
        )

        self.assertEqual(80.0, comparison.accuracy_pct)

    def test_accuracy_pct_under_estimate(self) -> None:
        comparison = EstimateComparison(
            entity="Customer",
            estimated_rows=1000,
            actual_rows=800,
        )

        self.assertEqual(80.0, comparison.accuracy_pct)

    def test_accuracy_pct_zero_estimated_rows(self) -> None:
        comparison = EstimateComparison(
            entity="Customer",
            estimated_rows=0,
            actual_rows=100,
        )

        self.assertEqual(0.0, comparison.accuracy_pct)

    def test_wave_estimate_accuracy_average(self) -> None:
        comparisons = [
            EstimateComparison(entity="Customer", estimated_rows=1000, actual_rows=1000),
            EstimateComparison(entity="Order", estimated_rows=1000, actual_rows=1200),
        ]

        self.assertEqual(90.0, wave_estimate_accuracy(comparisons))

    def test_wave_estimate_accuracy_empty_list(self) -> None:
        self.assertEqual(0.0, wave_estimate_accuracy([]))

    def test_wave_estimate_accuracy_ignores_zero_estimated_rows(self) -> None:
        comparisons = [
            EstimateComparison(entity="Customer", estimated_rows=1000, actual_rows=1000),
            EstimateComparison(entity="Empty", estimated_rows=0, actual_rows=500),
        ]

        self.assertEqual(100.0, wave_estimate_accuracy(comparisons))


if __name__ == "__main__":
    unittest.main()
