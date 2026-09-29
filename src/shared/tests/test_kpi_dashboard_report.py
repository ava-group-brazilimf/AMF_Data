"""
test_kpi_dashboard_report.py
B-015 — Tests for wave KPI dashboard report artifact.

The dashboard report consumes wave execution metrics and the KPI dictionary
to produce a per-KPI row report with actual vs target comparison.
"""
import unittest
from dataclasses import dataclass

from src.shared.scripts.kpi_dashboard_report import WaveExecutionMetrics, generate_kpi_dashboard_report


class TestKPIDashboardReport(unittest.TestCase):

    def setUp(self):
        from scripts.kpi_dashboard_report import (
            WaveExecutionMetrics,
            KPIDashboardReport,
            KPIReportRow,
            ReportStatus,
            generate_kpi_dashboard_report,
        )
        self.WaveExecutionMetrics = WaveExecutionMetrics
        self.KPIDashboardReport = KPIDashboardReport
        self.KPIReportRow = KPIReportRow
        self.ReportStatus = ReportStatus
        self.generate_kpi_dashboard_report = generate_kpi_dashboard_report

    def test_report_contains_required_kpi_fields(self):
        """Report rows include first_pass_rate, rollback_count, mttr, cycle_time."""
        metrics = self.WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=98.5,
            rollback_count=0,
            mttr_minutes=0.0,
            cycle_time_minutes=120.0,
        )
        report = self.generate_kpi_dashboard_report(metrics)
        self.assertIsInstance(report, self.KPIDashboardReport)
        self.assertEqual(report.wave_id, "WAVE-001")
        self.assertGreater(len(report.rows), 0)
        kpi_ids = {row.kpi_id for row in report.rows}
        self.assertIn("first_pass_rate", kpi_ids)
        self.assertIn("rollback_count", kpi_ids)
        self.assertIn("mttr", kpi_ids)
        self.assertIn("cycle_time", kpi_ids)

    def test_pass_status_when_all_within_targets(self):
        """All KPI rows show PASS when metrics meet targets."""
        metrics = self.WaveExecutionMetrics(
            wave_id="WAVE-002",
            first_pass_rate_pct=100.0,
            rollback_count=0,
            mttr_minutes=0.0,
            cycle_time_minutes=60.0,
        )
        report = self.generate_kpi_dashboard_report(metrics)
        first_pass_row = next(r for r in report.rows if r.kpi_id == "first_pass_rate")
        self.assertEqual(first_pass_row.status, self.ReportStatus.PASS)
        rollback_row = next(r for r in report.rows if r.kpi_id == "rollback_count")
        self.assertEqual(rollback_row.status, self.ReportStatus.PASS)

    def test_fail_status_when_below_target(self):
        """first_pass_rate shows FAIL when below 95% threshold."""
        metrics = self.WaveExecutionMetrics(
            wave_id="WAVE-003",
            first_pass_rate_pct=80.0,
            rollback_count=3,
            mttr_minutes=90.0,
            cycle_time_minutes=480.0,
        )
        report = self.generate_kpi_dashboard_report(metrics)
        first_pass_row = next(r for r in report.rows if r.kpi_id == "first_pass_rate")
        self.assertEqual(first_pass_row.status, self.ReportStatus.FAIL)

    def test_report_has_generated_at_timestamp(self):
        """Report includes a generated_at ISO timestamp."""
        metrics = self.WaveExecutionMetrics(
            wave_id="WAVE-004",
            first_pass_rate_pct=99.0,
            rollback_count=0,
            mttr_minutes=5.0,
            cycle_time_minutes=90.0,
        )
        report = self.generate_kpi_dashboard_report(metrics)
        self.assertIsNotNone(report.generated_at)
        self.assertGreater(len(report.generated_at), 0)

    def test_report_row_includes_actual_and_target(self):
        """Each KPI report row includes actual value and target string."""
        metrics = self.WaveExecutionMetrics(
            wave_id="WAVE-005",
            first_pass_rate_pct=97.3,
            rollback_count=1,
            mttr_minutes=30.0,
            cycle_time_minutes=150.0,
        )
        report = self.generate_kpi_dashboard_report(metrics)
        for row in report.rows:
            self.assertIsInstance(row.kpi_id, str)
            self.assertIsInstance(row.kpi_name, str)
            self.assertIsNotNone(row.actual)
            self.assertIsNotNone(row.target)

    def test_rollback_count_fail_when_above_zero(self):
        """rollback_count KPI is FAIL when rollback_count > 0."""
        metrics = self.WaveExecutionMetrics(
            wave_id="WAVE-006",
            first_pass_rate_pct=98.0,
            rollback_count=2,
            mttr_minutes=45.0,
            cycle_time_minutes=200.0,
        )
        report = self.generate_kpi_dashboard_report(metrics)
        rollback_row = next(r for r in report.rows if r.kpi_id == "rollback_count")
        self.assertEqual(rollback_row.status, self.ReportStatus.FAIL)


    def test_data_accuracy_kpi_appears_when_measured(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=96.0,
            rollback_count=0,
            mttr_minutes=30.0,
            cycle_time_minutes=180.0,
            data_accuracy_pct=99.95,
        )
        report = generate_kpi_dashboard_report(metrics)
        ids = [row.kpi_id for row in report.rows]
        self.assertIn("data_accuracy", ids)

    def test_data_accuracy_absent_when_not_measured(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=96.0,
            rollback_count=0,
            mttr_minutes=30.0,
            cycle_time_minutes=180.0,
        )
        report = generate_kpi_dashboard_report(metrics)
        ids = [row.kpi_id for row in report.rows]
        self.assertNotIn("data_accuracy", ids)

    def test_auto_validated_kpi_appears_when_measured(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=96.0,
            rollback_count=0,
            mttr_minutes=30.0,
            cycle_time_minutes=180.0,
            auto_validated_pct=92.0,
        )
        report = generate_kpi_dashboard_report(metrics)
        ids = [row.kpi_id for row in report.rows]
        self.assertIn("auto_validated", ids)

    def test_auto_validated_absent_when_not_measured(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=96.0,
            rollback_count=0,
            mttr_minutes=30.0,
            cycle_time_minutes=180.0,
        )
        report = generate_kpi_dashboard_report(metrics)
        ids = [row.kpi_id for row in report.rows]
        self.assertNotIn("auto_validated", ids)

    def test_migration_ready_kpi_appears_when_measured(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=96.0,
            rollback_count=0,
            mttr_minutes=30.0,
            cycle_time_minutes=180.0,
            migration_ready_pct=85.0,
        )
        report = generate_kpi_dashboard_report(metrics)
        ids = [row.kpi_id for row in report.rows]
        self.assertIn("migration_ready", ids)

    def test_migration_ready_absent_when_not_measured(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-001",
            first_pass_rate_pct=96.0,
            rollback_count=0,
            mttr_minutes=30.0,
            cycle_time_minutes=180.0,
        )
        report = generate_kpi_dashboard_report(metrics)
        ids = [row.kpi_id for row in report.rows]
        self.assertNotIn("migration_ready", ids)

    def test_calc_auto_validated_pct_zero_total(self) -> None:
        from scripts.kpi_dashboard_report import calc_auto_validated_pct
        self.assertEqual(0.0, calc_auto_validated_pct(10, 0))

    def test_calc_migration_ready_pct_zero_total(self) -> None:
        from scripts.kpi_dashboard_report import calc_migration_ready_pct
        self.assertEqual(0.0, calc_migration_ready_pct(10, 0))

    def test_complexity_distribution_counts_existing_classes(self) -> None:
        from scripts.kpi_dashboard_report import complexity_distribution

        classifications = [
            {"complexity": "LOW"},
            {"complexity": "MEDIUM"},
            {"complexity": "COMPLEX"},
            {"complexity": "VERY_COMPLEX"},
            {"complexity": "LOW"},
        ]

        result = complexity_distribution(classifications)
        self.assertEqual({"LOW": 2, "MEDIUM": 1, "COMPLEX": 1, "VERY_COMPLEX": 1}, result)

    def test_simple_vs_complex_pct_uses_existing_low_medium_split(self) -> None:
        from scripts.kpi_dashboard_report import simple_vs_complex_pct

        classifications = [
            {"complexity": "LOW"},
            {"complexity": "MEDIUM"},
            {"complexity": "COMPLEX"},
            {"complexity": "VERY_COMPLEX"},
        ]

        self.assertEqual((50.0, 50.0), simple_vs_complex_pct(classifications))

    def test_simple_vs_complex_pct_empty_returns_zeroes(self) -> None:
        from scripts.kpi_dashboard_report import simple_vs_complex_pct

        self.assertEqual((0.0, 0.0), simple_vs_complex_pct([]))

if __name__ == "__main__":
    unittest.main()
    