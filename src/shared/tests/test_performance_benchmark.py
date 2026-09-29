"""Tests for B-010: performance benchmark stage."""
import unittest
import json

from scripts.performance_benchmark import (
    BenchmarkRun,
    BenchmarkReport,
    run_benchmark,
    BenchmarkStatus,
    lead_time_by_entity,
)
from scripts.kpi_dashboard_report import generate_kpi_dashboard_report_with_lead_times, WaveExecutionMetrics


class PerformanceBenchmarkTests(unittest.TestCase):
    def test_pass_when_within_baseline(self) -> None:
        run = BenchmarkRun(
            wave_id="WAVE-001",
            entity="orders",
            rows_processed=1_000_000,
            duration_seconds=60.0,
            baseline_rows_per_second=10_000.0,  # 1M/60 ≈ 16k > baseline
            bytes_processed=1_000_000,
        )
        report = run_benchmark(run)
        self.assertEqual(BenchmarkStatus.PASS, report.status)

    def test_fail_when_throughput_below_baseline(self) -> None:
        run = BenchmarkRun(
            wave_id="WAVE-001",
            entity="transactions",
            rows_processed=100,
            duration_seconds=60.0,
            baseline_rows_per_second=10_000.0,  # 100/60 ≈ 1.7 << 10k
            bytes_processed=1_000_000,
        )
        report = run_benchmark(run)
        self.assertEqual(BenchmarkStatus.FAIL, report.status)

    def test_rows_per_second_computed(self) -> None:
        run = BenchmarkRun(
            wave_id="WAVE-001",
            entity="customers",
            rows_processed=300,
            duration_seconds=30.0,
            baseline_rows_per_second=5.0,
            bytes_processed=1_000_000,
        )
        report = run_benchmark(run)
        self.assertAlmostEqual(10.0, report.rows_per_second, places=1)

    def test_report_includes_entity_and_wave(self) -> None:
        run = BenchmarkRun(
            wave_id="WAVE-002",
            entity="products",
            rows_processed=500,
            duration_seconds=10.0,
            baseline_rows_per_second=1.0,
            bytes_processed=1_000_000,
        )
        report = run_benchmark(run)
        self.assertEqual("WAVE-002", report.wave_id)
        self.assertEqual("products", report.entity)

    def test_zero_duration_raises(self) -> None:
        run = BenchmarkRun(
            wave_id="WAVE-001",
            entity="edge",
            rows_processed=100,
            duration_seconds=0.0,
            baseline_rows_per_second=1.0,
            bytes_processed=1_000_000,
        )
        with self.assertRaises(ValueError):
            run_benchmark(run)

    def test_processing_time_per_gb(self) -> None:
        run = BenchmarkRun(
            wave_id="WAVE-001",
            entity="orders",
            rows_processed=1_000_000,
            duration_seconds=120.0,
            baseline_rows_per_second=1_000.0,
            bytes_processed=1_073_741_824,   # exatamente 1 GB
        )
        report = run_benchmark(run)
        self.assertEqual(120.0, report.processing_time_per_gb)

    def test_processing_time_per_gb_zero_bytes(self) -> None:
        report = BenchmarkReport(
        wave_id="WAVE-001",
        entity="empty",
        rows_processed=100,
        rows_per_second=10.0,
        baseline_rows_per_second=1.0,
        tolerance_pct=0.1,
        status=BenchmarkStatus.PASS,
        delta_pct=9.0,
        bytes_processed=0,        # <- o que estamos testando
        duration_seconds=10.0,
    )
        self.assertEqual(0.0, report.processing_time_per_gb)

    def test_lead_time_by_entity_order(self) -> None:
        # three reports in unsorted order
        r_fast = BenchmarkReport(
            wave_id="WAVE-001",
            entity="fast",
            rows_processed=1,
            rows_per_second=1.0,
            baseline_rows_per_second=1.0,
            tolerance_pct=0.1,
            status=BenchmarkStatus.PASS,
            delta_pct=0.0,
            bytes_processed=1000,
            duration_seconds=60.0,   # 1.0 minute
        )
        r_slow = BenchmarkReport(
            wave_id="WAVE-001",
            entity="slow",
            rows_processed=1,
            rows_per_second=1.0,
            baseline_rows_per_second=1.0,
            tolerance_pct=0.1,
            status=BenchmarkStatus.PASS,
            delta_pct=0.0,
            bytes_processed=1000,
            duration_seconds=600.0,  # 10.0 minutes
        )
        r_medium = BenchmarkReport(
            wave_id="WAVE-001",
            entity="medium",
            rows_processed=1,
            rows_per_second=1.0,
            baseline_rows_per_second=1.0,
            tolerance_pct=0.1,
            status=BenchmarkStatus.PASS,
            delta_pct=0.0,
            bytes_processed=1000,
            duration_seconds=300.0,  # 5.0 minutes
        )

        reports = [r_medium, r_fast, r_slow]
        result = lead_time_by_entity(reports)
        expected = [("slow", r_slow.duration_minutes), ("medium", r_medium.duration_minutes), ("fast", r_fast.duration_minutes)]
        self.assertEqual(expected, result)

    def test_lead_time_by_entity_empty(self) -> None:
        self.assertEqual([], lead_time_by_entity([]))

    def test_dashboard_includes_lead_time_list(self) -> None:
        # create simple metrics and reports, verify lead_time_by_entity is present and ordered
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-TEST",
            first_pass_rate_pct=100.0,
            rollback_count=0,
            mttr_minutes=0.0,
            cycle_time_minutes=10.0,
        )
        r1 = BenchmarkReport(
            wave_id="WAVE-TEST",
            entity="A",
            rows_processed=1,
            rows_per_second=1.0,
            baseline_rows_per_second=1.0,
            tolerance_pct=0.1,
            status=BenchmarkStatus.PASS,
            delta_pct=0.0,
            bytes_processed=1000,
            duration_seconds=120.0,  # 2.0 minutes
        )
        r2 = BenchmarkReport(
            wave_id="WAVE-TEST",
            entity="B",
            rows_processed=1,
            rows_per_second=1.0,
            baseline_rows_per_second=1.0,
            tolerance_pct=0.1,
            status=BenchmarkStatus.PASS,
            delta_pct=0.0,
            bytes_processed=1000,
            duration_seconds=60.0,  # 1.0 minute
        )
        report = generate_kpi_dashboard_report_with_lead_times(metrics, [r1, r2])
        # handle possible headroom-compressed wrapper
        if isinstance(report, dict) and report.get("_headroom_compressed"):
            inner = json.loads(report["content"].messages[0]["content"])
        else:
            inner = report
        self.assertIn("lead_time_by_entity", inner)
        self.assertEqual(inner["lead_time_by_entity"], [{"entity": "A", "duration_minutes": r1.duration_minutes}, {"entity": "B", "duration_minutes": r2.duration_minutes}])

    def test_dashboard_lead_time_empty(self) -> None:
        metrics = WaveExecutionMetrics(
            wave_id="WAVE-TEST",
            first_pass_rate_pct=100.0,
            rollback_count=0,
            mttr_minutes=0.0,
            cycle_time_minutes=10.0,
        )
        report = generate_kpi_dashboard_report_with_lead_times(metrics, [])
        if isinstance(report, dict) and report.get("_headroom_compressed"):
            inner = json.loads(report["content"].messages[0]["content"])
        else:
            inner = report
        self.assertIn("lead_time_by_entity", inner)
        self.assertEqual(inner["lead_time_by_entity"], [])


if __name__ == "__main__":
    unittest.main()
