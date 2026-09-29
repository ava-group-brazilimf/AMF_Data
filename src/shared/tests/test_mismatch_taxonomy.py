"""Tests for B-013: mismatch root-cause taxonomy."""
import unittest

from scripts.mismatch_taxonomy import (
    MismatchCategory,
    MismatchRecord,
    classify_mismatch,
    RootCauseSummary,
    summarize_mismatches,
)


class MismatchTaxonomyTests(unittest.TestCase):
    def test_classify_row_count_delta(self) -> None:
        record = MismatchRecord(
            entity="orders",
            source_value=1000,
            target_value=990,
            field="row_count",
        )
        result = classify_mismatch(record)
        self.assertEqual(MismatchCategory.ROW_COUNT_DELTA, result.category)

    def test_classify_data_transformation_error(self) -> None:
        record = MismatchRecord(
            entity="customers",
            source_value="2024-01-01",
            target_value="01/01/2024",
            field="birth_date",
        )
        result = classify_mismatch(record)
        self.assertEqual(MismatchCategory.TRANSFORMATION_ERROR, result.category)

    def test_classify_null_introduced(self) -> None:
        record = MismatchRecord(
            entity="products",
            source_value="ABC",
            target_value=None,
            field="sku",
        )
        result = classify_mismatch(record)
        self.assertEqual(MismatchCategory.NULL_INTRODUCED, result.category)

    def test_classify_truncation(self) -> None:
        record = MismatchRecord(
            entity="notes",
            source_value="A" * 300,
            target_value="A" * 255,  # truncated
            field="description",
        )
        result = classify_mismatch(record)
        self.assertEqual(MismatchCategory.TRUNCATION, result.category)

    def test_summarize_produces_counts_by_category(self) -> None:
        records = [
            MismatchRecord("e", 10, 9, "row_count"),
            MismatchRecord("e", "2024", "01/2024", "date"),
            MismatchRecord("e", "X", None, "code"),
            MismatchRecord("e", "A" * 300, "A" * 255, "desc"),
            MismatchRecord("e", "B" * 300, "B" * 255, "notes"),
        ]
        summary = summarize_mismatches(records)
        self.assertEqual(5, summary.total)
        self.assertEqual(1, summary.by_category[MismatchCategory.ROW_COUNT_DELTA])
        self.assertEqual(1, summary.by_category[MismatchCategory.TRANSFORMATION_ERROR])
        self.assertEqual(1, summary.by_category[MismatchCategory.NULL_INTRODUCED])
        self.assertEqual(2, summary.by_category[MismatchCategory.TRUNCATION])


if __name__ == "__main__":
    unittest.main()
