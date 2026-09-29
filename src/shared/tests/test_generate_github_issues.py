import tempfile
import unittest
from pathlib import Path

from scripts.generate_github_issues import parse_must_items, write_issue_markdown_files


class GenerateGitHubIssuesTests(unittest.TestCase):
    def test_extracts_only_must_items(self) -> None:
        backlog = """| ID | Epic | Item | Priority | Size | Depends On | Acceptance Summary |
| --- | --- | --- | --- | --- | --- | --- |
| B-001 | Epic 1 | One | Must | M | None | A |
| B-002 | Epic 1 | Two | Should | S | B-001 | B |
| B-003 | Epic 2 | Three | Must | L | B-001 | C |
"""
        items = parse_must_items(backlog)
        self.assertEqual(["B-001", "B-003"], [item.id for item in items])

    def test_writes_one_issue_file_per_item(self) -> None:
        backlog = """| ID | Epic | Item | Priority | Size | Depends On | Acceptance Summary |
| --- | --- | --- | --- | --- | --- | --- |
| B-001 | Epic 1 | One | Must | M | None | A |
"""
        items = parse_must_items(backlog)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_issue_markdown_files(items, out)
            created = list(out.glob("*.md"))
            self.assertEqual(1, len(created))
            content = created[0].read_text(encoding="utf-8")
            self.assertIn("B-001", content)
            self.assertIn("Priority: Must", content)


if __name__ == "__main__":
    unittest.main()
