import tempfile
import unittest
from pathlib import Path

from scripts.check_chatmode_alignment import find_mismatches


class CheckChatmodeAlignmentTests(unittest.TestCase):
    def test_reports_chatmodes_without_agent_folder_except_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".github" / "agents").mkdir(parents=True)
            (root / "inventory-scout-agent").mkdir(parents=True)
            (root / ".github" / "agents" / "inventory-scout.chatmode.md").write_text("x", encoding="utf-8")
            (root / ".github" / "agents" / "master-agent.chatmode.md").write_text("x", encoding="utf-8")
            (root / ".github" / "agents" / "ghost.chatmode.md").write_text("x", encoding="utf-8")

            missing_folders, orphan_folders = find_mismatches(root, allowlist={"master-agent"})

            self.assertEqual(["ghost"], missing_folders)
            self.assertEqual([], orphan_folders)

    def test_reports_agent_folders_without_chatmode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".github" / "agents").mkdir(parents=True)
            (root / "inventory-scout-agent").mkdir(parents=True)
            (root / "downstream-executor-agent").mkdir(parents=True)
            (root / ".github" / "agents" / "inventory-scout.chatmode.md").write_text("x", encoding="utf-8")

            missing_folders, orphan_folders = find_mismatches(root, allowlist=set())

            self.assertEqual([], missing_folders)
            self.assertEqual(["downstream-executor-agent"], orphan_folders)


if __name__ == "__main__":
    unittest.main()
