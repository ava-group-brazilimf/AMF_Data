"""
test_decision_log.py
B-018 — Tests for governance exception decision log.

Exception decisions must be auditable (JSONL) and searchable by keyword.
"""
import json
import tempfile
import unittest
from pathlib import Path


class TestDecisionLog(unittest.TestCase):

    def setUp(self):
        from scripts.decision_log import (
            DecisionLogEntry,
            DecisionLog,
            DecisionOutcome,
        )
        self.DecisionLogEntry = DecisionLogEntry
        self.DecisionLog = DecisionLog
        self.DecisionOutcome = DecisionOutcome

    def _make_entry(self, **kwargs):
        defaults = dict(
            exception_type="policy-override",
            description="Skip UAT gate for hotfix wave",
            decision=self.DecisionOutcome.APPROVED,
            rationale="Hotfix must ship before next business day",
            decided_by="lead@example.com",
            wave_id="WAVE-001",
            gate="2",
        )
        defaults.update(kwargs)
        return self.DecisionLogEntry(**defaults)

    def test_record_creates_entry_with_auto_id(self):
        """record() assigns a unique decision_id to each entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = self.DecisionLog(Path(tmpdir) / "decisions.jsonl")
            entry = self._make_entry()
            log.record(entry)
            self.assertIsNotNone(entry.decision_id)
            self.assertGreater(len(entry.decision_id), 0)

    def test_entries_are_persisted_to_jsonl(self):
        """Entries are written to the JSONL file on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "decisions.jsonl"
            log = self.DecisionLog(log_path)
            log.record(self._make_entry())
            log.record(self._make_entry(description="Another exception"))
            lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            parsed = json.loads(lines[0])
            self.assertIn("decision_id", parsed)
            self.assertIn("exception_type", parsed)

    def test_search_returns_matching_entries(self):
        """search() finds entries by keyword in description or exception_type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = self.DecisionLog(Path(tmpdir) / "decisions.jsonl")
            log.record(self._make_entry(description="Skip UAT gate for hotfix"))
            log.record(self._make_entry(description="Approve production override"))
            results = log.search("hotfix")
            self.assertEqual(len(results), 1)
            self.assertIn("hotfix", results[0].description.lower())

    def test_search_is_case_insensitive(self):
        """search() is case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = self.DecisionLog(Path(tmpdir) / "decisions.jsonl")
            log.record(self._make_entry(description="HOTFIX deployment exception"))
            results = log.search("hotfix")
            self.assertEqual(len(results), 1)

    def test_to_markdown_creates_readable_file(self):
        """to_markdown() creates a .md file with all entries formatted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = self.DecisionLog(Path(tmpdir) / "decisions.jsonl")
            log.record(self._make_entry())
            md_path = Path(tmpdir) / "decision-log.md"
            log.to_markdown(md_path)
            self.assertTrue(md_path.exists())
            content = md_path.read_text(encoding="utf-8")
            self.assertIn("policy-override", content)
            self.assertIn("hotfix", content.lower())

    def test_rejected_decision_outcome(self):
        """REJECTED outcome is recorded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log = self.DecisionLog(Path(tmpdir) / "decisions.jsonl")
            entry = self._make_entry(
                decision=self.DecisionOutcome.REJECTED,
                rationale="Risk too high for UAT bypass",
            )
            log.record(entry)
            lines = log.search("hotfix")
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0].decision, self.DecisionOutcome.REJECTED)


if __name__ == "__main__":
    unittest.main()
