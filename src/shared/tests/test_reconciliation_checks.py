"""Tests for B-009: checksum reconciliation checks — disconnected and connected modes."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts.mismatch_taxonomy import MismatchCategory
from scripts.reconciliation_checks import (
    classify_mismatches,
    compute_checksum,
    load_rows_from_csv,
    ReconciliationMode,
    ReconciliationReport,
    reconcile_checksums,
    reconcile_from_sources,
    ReconciliationStatus,
)


class ChecksumReconciliationTests(unittest.TestCase):
    def test_compute_checksum_is_deterministic(self) -> None:
        rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        self.assertEqual(compute_checksum(rows), compute_checksum(rows))

    def test_compute_checksum_differs_for_different_data(self) -> None:
        a = [{"id": 1, "value": 100}]
        b = [{"id": 1, "value": 200}]
        self.assertNotEqual(compute_checksum(a), compute_checksum(b))

    def test_reconcile_pass_when_checksums_match(self) -> None:
        rows = [{"id": i, "v": i * 10} for i in range(100)]
        report = reconcile_checksums(
            entity="orders",
            source_rows=rows,
            target_rows=rows,
        )
        self.assertEqual(ReconciliationStatus.PASS, report.status)
        self.assertEqual(100, report.source_count)
        self.assertEqual(100, report.target_count)

    def test_reconcile_fail_when_checksums_differ(self) -> None:
        source = [{"id": 1, "amount": 500}]
        target = [{"id": 1, "amount": 999}]  # tampered
        report = reconcile_checksums(
            entity="transactions",
            source_rows=source,
            target_rows=target,
        )
        self.assertEqual(ReconciliationStatus.FAIL, report.status)
        self.assertNotEqual(report.source_checksum, report.target_checksum)

    def test_reconcile_fail_when_row_counts_differ(self) -> None:
        source = [{"id": i} for i in range(10)]
        target = [{"id": i} for i in range(8)]  # 2 rows missing
        report = reconcile_checksums(
            entity="customers",
            source_rows=source,
            target_rows=target,
        )
        self.assertEqual(ReconciliationStatus.FAIL, report.status)
        self.assertEqual(10, report.source_count)
        self.assertEqual(8, report.target_count)

    def test_report_includes_entity_name(self) -> None:
        rows = [{"id": 1}]
        report = reconcile_checksums("my_entity", rows, rows)
        self.assertEqual("my_entity", report.entity)

    def test_reconcile_checksums_defaults_to_disconnected_mode(self) -> None:
        rows = [{"id": 1}]
        report = reconcile_checksums("e", rows, rows)
        self.assertEqual(ReconciliationMode.DISCONNECTED, report.mode)


class ClassifiedMismatchSummaryTests(unittest.TestCase):
    def test_classify_mismatches_counts_distinct_categories(self) -> None:
        mismatches = [
            {"entity": "orders", "source_value": 1000, "target_value": 990, "field": "row_count"},
            {"entity": "customers", "source_value": "2024-01-01", "target_value": "01/01/2024", "field": "birth_date"},
            {"entity": "products", "source_value": "ABC", "target_value": None, "field": "sku"},
            {"entity": "notes", "source_value": "A" * 300, "target_value": "A" * 255, "field": "description"},
            {"entity": "items", "source_value": 123, "target_value": "123", "field": "id"},
        ]

        counts = classify_mismatches(mismatches)

        self.assertEqual(1, counts["row_count_delta"])
        self.assertEqual(1, counts["transformation_error"])
        self.assertEqual(1, counts["null_introduced"])
        self.assertEqual(1, counts["truncation"])
        self.assertEqual(1, counts["type_mismatch"])

    def test_classify_mismatches_empty_list_returns_empty_dict(self) -> None:
        self.assertEqual({}, classify_mismatches([]))

    def test_classify_mismatches_uses_existing_taxonomy_only(self) -> None:
        mismatches = [{"entity": "orders", "source_value": 10, "target_value": 9, "field": "row_count"}]
        counts = classify_mismatches(mismatches)
        allowed = {item.value for item in MismatchCategory}
        self.assertTrue(set(counts).issubset(allowed))
        self.assertNotIn("ROUNDING", counts)
        self.assertNotIn("ENCODING", counts)

    def test_classify_mismatches_counts_repeated_categories_correctly(self) -> None:
        mismatches = [
            {"entity": "orders", "source_value": 10, "target_value": 8, "field": "row_count"},
            {"entity": "orders", "source_value": 10, "target_value": 8, "field": "row_count"},
            {"entity": "customers", "source_value": "2024-01-01", "target_value": "01/01/2024", "field": "birth_date"},
            {"entity": "accounts", "source_value": "ABCD", "target_value": None, "field": "code"},
        ]
        counts = classify_mismatches(mismatches)
        self.assertEqual(2, counts["row_count_delta"])
        self.assertEqual(1, counts["transformation_error"])
        self.assertEqual(1, counts["null_introduced"])

    def test_classify_mismatches_does_not_create_non_taxonomy_labels(self) -> None:
        mismatches = [
            {"entity": "inventory", "source_value": 123, "target_value": "123", "field": "id"},
            {"entity": "notes", "source_value": "A" * 300, "target_value": "A" * 255, "field": "description"},
            {"entity": "orders", "source_value": 100, "target_value": 90, "field": "total_rows"},
        ]
        counts = classify_mismatches(mismatches)
        self.assertEqual({"type_mismatch", "truncation", "row_count_delta"}, set(counts.keys()))
        self.assertNotIn("ROUNDING", counts)
        self.assertNotIn("ENCODING", counts)


class LoadRowsFromCsvTests(unittest.TestCase):
    def _write_csv(self, rows: list[dict], path: Path) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def test_load_csv_returns_list_of_dicts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.csv"
            self._write_csv([{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}], path)
            rows = load_rows_from_csv(path)
            self.assertEqual(2, len(rows))
            self.assertEqual("Alice", rows[0]["name"])

    def test_load_csv_raises_for_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_rows_from_csv(Path("/nonexistent/file.csv"))

    def test_load_csv_empty_file_raises_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.csv"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_rows_from_csv(path)


class ReconcileFromSourcesDisconnectedTests(unittest.TestCase):
    """Tests for reconcile_from_sources() in DISCONNECTED mode."""

    def test_disconnected_in_memory_pass(self) -> None:
        rows = [{"id": i} for i in range(5)]
        report = reconcile_from_sources(
            "orders", rows, rows, mode=ReconciliationMode.DISCONNECTED
        )
        self.assertEqual(ReconciliationStatus.PASS, report.status)
        self.assertEqual(ReconciliationMode.DISCONNECTED, report.mode)

    def test_disconnected_in_memory_fail_checksum(self) -> None:
        source = [{"id": 1, "v": 10}]
        target = [{"id": 1, "v": 99}]
        report = reconcile_from_sources(
            "t", source, target, mode=ReconciliationMode.DISCONNECTED
        )
        self.assertEqual(ReconciliationStatus.FAIL, report.status)
        self.assertTrue(report.checksum_mismatch)

    def test_disconnected_csv_pass(self) -> None:
        rows = [{"id": "1", "amount": "100"}, {"id": "2", "amount": "200"}]
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = Path(tmpdir) / "source.csv"
            tgt_path = Path(tmpdir) / "target.csv"
            for path in (src_path, tgt_path):
                with path.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.DictWriter(fh, fieldnames=["id", "amount"])
                    writer.writeheader()
                    writer.writerows(rows)
            report = reconcile_from_sources(
                "orders", src_path, tgt_path, mode=ReconciliationMode.DISCONNECTED
            )
        self.assertEqual(ReconciliationStatus.PASS, report.status)
        self.assertEqual(2, report.source_count)

    def test_disconnected_csv_fail_row_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = Path(tmpdir) / "source.csv"
            tgt_path = Path(tmpdir) / "target.csv"
            for path, rows in [
                (src_path, [{"id": "1"}, {"id": "2"}, {"id": "3"}]),
                (tgt_path, [{"id": "1"}, {"id": "2"}]),
            ]:
                with path.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.DictWriter(fh, fieldnames=["id"])
                    writer.writeheader()
                    writer.writerows(rows)
            report = reconcile_from_sources(
                "customers", src_path, tgt_path, mode=ReconciliationMode.DISCONNECTED
            )
        self.assertEqual(ReconciliationStatus.FAIL, report.status)
        self.assertTrue(report.count_mismatch)
        self.assertEqual(3, report.source_count)
        self.assertEqual(2, report.target_count)

    def test_disconnected_default_mode_is_used_when_omitted(self) -> None:
        rows = [{"x": 1}]
        report = reconcile_from_sources("e", rows, rows)
        self.assertEqual(ReconciliationMode.DISCONNECTED, report.mode)

    def test_path_loader_in_connected_mode_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.csv"
            path.write_text("id\n1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                reconcile_from_sources(
                    "e", path, path, mode=ReconciliationMode.CONNECTED
                )


class ReconcileFromSourcesConnectedTests(unittest.TestCase):
    """Tests for reconcile_from_sources() in CONNECTED mode (callable adapters)."""

    def test_connected_callable_pass(self) -> None:
        rows = [{"id": 1, "val": "x"}, {"id": 2, "val": "y"}]
        report = reconcile_from_sources(
            "orders",
            source_loader=lambda: rows,
            target_loader=lambda: rows,
            mode=ReconciliationMode.CONNECTED,
        )
        self.assertEqual(ReconciliationStatus.PASS, report.status)
        self.assertEqual(ReconciliationMode.CONNECTED, report.mode)
        self.assertEqual(2, report.source_count)

    def test_connected_callable_fail_checksum(self) -> None:
        source_data = [{"id": 1, "amount": 500}]
        target_data = [{"id": 1, "amount": 999}]
        report = reconcile_from_sources(
            "transactions",
            source_loader=lambda: source_data,
            target_loader=lambda: target_data,
            mode=ReconciliationMode.CONNECTED,
        )
        self.assertEqual(ReconciliationStatus.FAIL, report.status)
        self.assertTrue(report.checksum_mismatch)

    def test_connected_callable_fail_row_count(self) -> None:
        report = reconcile_from_sources(
            "items",
            source_loader=lambda: [{"id": i} for i in range(10)],
            target_loader=lambda: [{"id": i} for i in range(7)],
            mode=ReconciliationMode.CONNECTED,
        )
        self.assertEqual(ReconciliationStatus.FAIL, report.status)
        self.assertTrue(report.count_mismatch)
        self.assertEqual(10, report.source_count)
        self.assertEqual(7, report.target_count)

    def test_connected_callable_is_invoked(self) -> None:
        call_log = []

        def fetch():
            call_log.append(1)
            return [{"id": 1}]

        reconcile_from_sources(
            "e",
            source_loader=fetch,
            target_loader=fetch,
            mode=ReconciliationMode.CONNECTED,
        )
        self.assertEqual(2, len(call_log))  # called once for source, once for target

    def test_connected_mode_in_report_str(self) -> None:
        rows = [{"id": 1}]
        report = reconcile_from_sources(
            "orders", lambda: rows, lambda: rows, mode=ReconciliationMode.CONNECTED
        )
        self.assertIn("CONNECTED", str(report))

    def test_disconnected_mode_in_report_str(self) -> None:
        rows = [{"id": 1}]
        report = reconcile_checksums("orders", rows, rows)
        self.assertIn("DISCONNECTED", str(report))


    def test_errors_per_million_normal(self) -> None:
    # 50 erros em 1 milhão de linhas = 50 por milhão
        self.assertEqual(50.0, ReconciliationReport.errors_per_million(50, 1_000_000))

    def test_errors_per_million_scales(self) -> None:
    # 50 erros em 10 milhões = 5 por milhão (qualidade 10x melhor)
        self.assertEqual(5.0, ReconciliationReport.errors_per_million(50, 10_000_000))

    def test_errors_per_million_zero_rows(self) -> None:
        self.assertEqual(0.0, ReconciliationReport.errors_per_million(10, 0))


if __name__ == "__main__":
    unittest.main()
