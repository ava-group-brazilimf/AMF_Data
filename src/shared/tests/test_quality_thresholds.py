"""Tests for B-011: threshold-based quality checks by entity tier."""
import unittest

from scripts.quality_thresholds import (
    EntityTier,
    QualityThresholds,
    QualityCheckResult,
    evaluate_quality,
    TIER_DEFAULTS,
)


class QualityThresholdsTests(unittest.TestCase):
    def test_tier_critical_has_strictest_thresholds(self) -> None:
        critical = TIER_DEFAULTS[EntityTier.CRITICAL]
        standard = TIER_DEFAULTS[EntityTier.STANDARD]
        self.assertGreaterEqual(critical.min_completeness, standard.min_completeness)
        self.assertGreaterEqual(critical.min_row_parity, standard.min_row_parity)

    def test_pass_when_metrics_above_thresholds(self) -> None:
        thresholds = QualityThresholds(min_completeness=0.98, min_row_parity=1.0, min_dq_score=0.95)
        result = evaluate_quality(
            entity="orders",
            tier=EntityTier.CRITICAL,
            completeness=0.99,
            row_parity=1.0,
            dq_score=0.98,
            thresholds=thresholds,
        )
        self.assertTrue(result.passed)
        self.assertEqual([], result.violations)

    def test_fail_completeness_below_threshold(self) -> None:
        thresholds = QualityThresholds(min_completeness=0.98, min_row_parity=1.0, min_dq_score=0.95)
        result = evaluate_quality(
            entity="customers",
            tier=EntityTier.CRITICAL,
            completeness=0.95,  # below 0.98
            row_parity=1.0,
            dq_score=0.97,
            thresholds=thresholds,
        )
        self.assertFalse(result.passed)
        self.assertTrue(any("completeness" in v.lower() for v in result.violations))

    def test_fail_row_parity_below_threshold(self) -> None:
        thresholds = QualityThresholds(min_completeness=0.98, min_row_parity=1.0, min_dq_score=0.95)
        result = evaluate_quality(
            entity="transactions",
            tier=EntityTier.CRITICAL,
            completeness=0.99,
            row_parity=0.97,  # below 1.0
            dq_score=0.97,
            thresholds=thresholds,
        )
        self.assertFalse(result.passed)
        self.assertTrue(any("parity" in v.lower() for v in result.violations))

    def test_gate_score_computed(self) -> None:
        thresholds = QualityThresholds(min_completeness=0.98, min_row_parity=1.0, min_dq_score=0.95)
        result = evaluate_quality(
            entity="products",
            tier=EntityTier.STANDARD,
            completeness=1.0,
            row_parity=1.0,
            dq_score=1.0,
            thresholds=thresholds,
        )
        self.assertGreater(result.gate_score, 0)
        self.assertLessEqual(result.gate_score, 100)

    def test_default_tier_thresholds_usable_without_custom(self) -> None:
        result = evaluate_quality(
            entity="reference_data",
            tier=EntityTier.REFERENCE,
            completeness=0.99,
            row_parity=1.0,
            dq_score=0.99,
        )
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
