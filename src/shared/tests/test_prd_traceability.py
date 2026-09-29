"""
test_prd_traceability.py
B-019 — Tests for story and epic traceability to PRD IDs.

All backlog items must map back to PRD sections. The traceability matrix
identifies unmapped items and uncovered PRD sections.
"""
import unittest


class TestPRDTraceability(unittest.TestCase):

    def setUp(self):
        from scripts.prd_traceability import (
            PRDSection,
            BacklogItem,
            TraceabilityMatrix,
            TraceabilityReport,
            check_coverage,
        )
        self.PRDSection = PRDSection
        self.BacklogItem = BacklogItem
        self.TraceabilityMatrix = TraceabilityMatrix
        self.TraceabilityReport = TraceabilityReport
        self.check_coverage = check_coverage

    def test_full_coverage_no_unmapped_items(self):
        """All backlog items mapped to PRD sections — zero unmapped."""
        sections = [
            self.PRDSection(prd_id="PRD-1.1", title="Governance Foundation"),
            self.PRDSection(prd_id="PRD-2.1", title="Audit and Control"),
        ]
        items = [
            self.BacklogItem(backlog_id="B-001", title="Policy schema", prd_ids=["PRD-1.1"]),
            self.BacklogItem(backlog_id="B-004", title="Audit logger", prd_ids=["PRD-2.1"]),
        ]
        report = self.check_coverage(items, sections)
        self.assertIsInstance(report, self.TraceabilityReport)
        self.assertEqual(report.unmapped_items, [])
        self.assertEqual(report.uncovered_sections, [])

    def test_unmapped_item_detected(self):
        """Item with empty prd_ids is reported as unmapped."""
        sections = [self.PRDSection(prd_id="PRD-1.1", title="Governance Foundation")]
        items = [
            self.BacklogItem(backlog_id="B-001", title="Policy schema", prd_ids=["PRD-1.1"]),
            self.BacklogItem(backlog_id="B-099", title="Orphan item", prd_ids=[]),
        ]
        report = self.check_coverage(items, sections)
        self.assertEqual(len(report.unmapped_items), 1)
        self.assertEqual(report.unmapped_items[0], "B-099")

    def test_uncovered_section_detected(self):
        """PRD section not referenced by any backlog item is reported."""
        sections = [
            self.PRDSection(prd_id="PRD-1.1", title="Governance Foundation"),
            self.PRDSection(prd_id="PRD-3.0", title="Performance"),
        ]
        items = [
            self.BacklogItem(backlog_id="B-001", title="Policy schema", prd_ids=["PRD-1.1"]),
        ]
        report = self.check_coverage(items, sections)
        self.assertIn("PRD-3.0", report.uncovered_sections)

    def test_report_counts_are_accurate(self):
        """mapped_count, total_backlog, total_prd_sections are correct."""
        sections = [
            self.PRDSection(prd_id="PRD-1.1", title="A"),
            self.PRDSection(prd_id="PRD-1.2", title="B"),
        ]
        items = [
            self.BacklogItem(backlog_id="B-001", title="X", prd_ids=["PRD-1.1"]),
            self.BacklogItem(backlog_id="B-002", title="Y", prd_ids=["PRD-1.1", "PRD-1.2"]),
            self.BacklogItem(backlog_id="B-003", title="Z", prd_ids=[]),
        ]
        report = self.check_coverage(items, sections)
        self.assertEqual(report.total_backlog, 3)
        self.assertEqual(report.total_prd_sections, 2)
        self.assertEqual(report.mapped_count, 2)  # B-001 and B-002 have prd_ids

    def test_matrix_add_and_get(self):
        """TraceabilityMatrix stores items and sections and returns them."""
        matrix = self.TraceabilityMatrix()
        matrix.add_section(self.PRDSection(prd_id="PRD-1.1", title="Foundation"))
        matrix.add_item(self.BacklogItem(backlog_id="B-001", title="Policy", prd_ids=["PRD-1.1"]))
        report = matrix.check_coverage()
        self.assertEqual(report.total_backlog, 1)
        self.assertEqual(report.total_prd_sections, 1)


if __name__ == "__main__":
    unittest.main()
