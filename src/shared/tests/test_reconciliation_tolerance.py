"""Tests for B-012: reconciliation tolerance bands."""
import unittest

from scripts.reconciliation_tolerance import (
    ToleranceBand,
    ToleranceResult,
    evaluate_tolerance,
    ToleranceStatus,
)


class ReconciliationToleranceBandTests(unittest.TestCase):
    def test_pass_within_tolerance(self) -> None:
        band = ToleranceBand(max_row_delta_pct=0.01, max_value_delta_pct=0.005)
        result = evaluate_tolerance(
            entity="orders",
            source_count=10_000,
            target_count=9_999,   # 0.01% delta
            source_sum=100_000.0,
            target_sum=99_998.0,  # 0.002% delta
            band=band,
        )
        self.assertEqual(ToleranceStatus.PASS, result.status)

    def test_fail_row_delta_exceeds_band(self) -> None:
        band = ToleranceBand(max_row_delta_pct=0.01, max_value_delta_pct=0.01)
        result = evaluate_tolerance(
            entity="transactions",
            source_count=10_000,
            target_count=9_800,   # 2% delta — exceeds 1%
            source_sum=100_000.0,
            target_sum=100_000.0,
            band=band,
        )
        self.assertEqual(ToleranceStatus.FAIL, result.status)
        self.assertIn("row_delta", result.violations[0])

    def test_fail_value_delta_exceeds_band(self) -> None:
        band = ToleranceBand(max_row_delta_pct=0.05, max_value_delta_pct=0.001)
        result = evaluate_tolerance(
            entity="financials",
            source_count=1000,
            target_count=1000,
            source_sum=1_000_000.0,
            target_sum=995_000.0,  # 0.5% > 0.1%
            band=band,
        )
        self.assertEqual(ToleranceStatus.FAIL, result.status)
        self.assertIn("value_delta", result.violations[0])

    def test_no_sum_provided_skips_value_check(self) -> None:
        band = ToleranceBand(max_row_delta_pct=0.01, max_value_delta_pct=0.001)
        result = evaluate_tolerance(
            entity="lookup",
            source_count=100,
            target_count=100,
            band=band,
        )
        self.assertEqual(ToleranceStatus.PASS, result.status)

    def test_actual_deltas_reported(self) -> None:
        band = ToleranceBand(max_row_delta_pct=0.5, max_value_delta_pct=0.5)
        result = evaluate_tolerance(
            entity="ref",
            source_count=200,
            target_count=190,
            band=band,
        )
        self.assertAlmostEqual(0.05, result.row_delta_pct, places=3)


if __name__ == "__main__":
    unittest.main()
