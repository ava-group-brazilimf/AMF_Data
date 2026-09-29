"""
test_slo_workflow.py
B-016 — Tests for SLO baseline and breach action workflow.

SLO breaches must trigger action items (review requests). The workflow
defines baselines, evaluates actuals, and raises items when breached.
"""
import unittest


class TestSLOWorkflow(unittest.TestCase):

    def setUp(self):
        from scripts.slo_workflow import (
            SLOBaseline,
            SLOBreachResult,
            SLOWorkflow,
            check_slo_breach,
        )
        self.SLOBaseline = SLOBaseline
        self.SLOBreachResult = SLOBreachResult
        self.SLOWorkflow = SLOWorkflow
        self.check_slo_breach = check_slo_breach

    def test_no_breach_when_within_threshold(self):
        """No breach when actual value meets or exceeds the SLO target."""
        slo = self.SLOBaseline(
            kpi_id="first_pass_rate",
            baseline_value=95.0,
            breach_threshold=95.0,
            unit="pct",
            comparison="gte",   # actual must be >= threshold to pass
        )
        result = self.check_slo_breach(slo, actual_value=98.0)
        self.assertIsInstance(result, self.SLOBreachResult)
        self.assertFalse(result.breached)
        self.assertEqual(result.kpi_id, "first_pass_rate")

    def test_breach_when_below_threshold(self):
        """Breach detected when actual value falls below the SLO threshold."""
        slo = self.SLOBaseline(
            kpi_id="first_pass_rate",
            baseline_value=95.0,
            breach_threshold=95.0,
            unit="pct",
            comparison="gte",
        )
        result = self.check_slo_breach(slo, actual_value=80.0)
        self.assertTrue(result.breached)
        self.assertEqual(result.actual, 80.0)
        self.assertEqual(result.breach_threshold, 95.0)

    def test_breach_result_includes_action_items(self):
        """Breached result includes at least one action item."""
        slo = self.SLOBaseline(
            kpi_id="rollback_count",
            baseline_value=0,
            breach_threshold=0,
            unit="count",
            comparison="lte",   # actual must be <= threshold to pass
        )
        result = self.check_slo_breach(slo, actual_value=3)
        self.assertTrue(result.breached)
        self.assertIsInstance(result.action_items, list)
        self.assertGreater(len(result.action_items), 0)

    def test_workflow_evaluate_wave_returns_all_results(self):
        """SLOWorkflow.evaluate_wave returns one result per registered SLO."""
        from scripts.slo_workflow import SLOWorkflow, SLOBaseline
        workflow = SLOWorkflow()
        workflow.register(self.SLOBaseline(
            kpi_id="first_pass_rate", baseline_value=95.0,
            breach_threshold=95.0, unit="pct", comparison="gte",
        ))
        workflow.register(self.SLOBaseline(
            kpi_id="rollback_count", baseline_value=0,
            breach_threshold=0, unit="count", comparison="lte",
        ))
        actuals = {"first_pass_rate": 99.0, "rollback_count": 0}
        results = workflow.evaluate_wave(actuals)
        self.assertEqual(len(results), 2)

    def test_workflow_raises_review_on_breach(self):
        """evaluate_wave raises ReviewRequest entries for each breached SLO."""
        from scripts.slo_workflow import SLOWorkflow, SLOBaseline
        workflow = SLOWorkflow()
        workflow.register(self.SLOBaseline(
            kpi_id="first_pass_rate", baseline_value=95.0,
            breach_threshold=95.0, unit="pct", comparison="gte",
        ))
        actuals = {"first_pass_rate": 70.0}
        results = workflow.evaluate_wave(actuals)
        breached = [r for r in results if r.breached]
        self.assertEqual(len(breached), 1)
        self.assertIsNotNone(breached[0].review_request_id)

    def test_lte_comparison_no_breach(self):
        """lte comparison: no breach when actual <= threshold."""
        slo = self.SLOBaseline(
            kpi_id="error_rate",
            baseline_value=2.0,
            breach_threshold=5.0,
            unit="pct",
            comparison="lte",
        )
        result = self.check_slo_breach(slo, actual_value=2.0)
        self.assertFalse(result.breached)


if __name__ == "__main__":
    unittest.main()
