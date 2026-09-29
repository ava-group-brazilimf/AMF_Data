"""Tests for B-004: audit logger JSONL."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_logger import AuditLogger, AuditEvent


class AuditLoggerTests(unittest.TestCase):
    def test_log_writes_jsonl_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "audit.jsonl"
            logger = AuditLogger(log_path)
            logger.log(AuditEvent(
                agent_id="downstream-executor",
                agent_class="execution",
                action="ddl-execute",
                tool="ddl-execute",
                policy_action="allow",
                gate="3",
                wave_id="WAVE-001",
                approved_by="tech-lead@example.com",
            ))
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(1, len(lines))
            entry = json.loads(lines[0])
            self.assertEqual("downstream-executor", entry["agent_id"])
            self.assertEqual("WAVE-001", entry["wave_id"])
            self.assertIn("timestamp", entry)

    def test_log_appends_multiple_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "audit.jsonl"
            logger = AuditLogger(log_path)
            for i in range(3):
                logger.log(AuditEvent(
                    agent_id=f"agent-{i}",
                    agent_class="control",
                    action="gate-pass",
                    tool="gate-pass",
                    policy_action="allow",
                    gate=str(i + 1),
                    wave_id="WAVE-001",
                ))
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(3, len(lines))

    def test_log_immutable_entries_cannot_be_overwritten(self) -> None:
        """Logger must append, never overwrite."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "audit.jsonl"
            logger = AuditLogger(log_path)
            logger.log(AuditEvent(
                agent_id="orchestrator",
                agent_class="coordination",
                action="gate-pass",
                tool="gate-pass",
                policy_action="allow",
                gate="1",
                wave_id="WAVE-001",
            ))
            # Second logger instance opens same file — must append
            logger2 = AuditLogger(log_path)
            logger2.log(AuditEvent(
                agent_id="orchestrator",
                agent_class="coordination",
                action="gate-override",
                tool="gate-override",
                policy_action="review",
                gate="2",
                wave_id="WAVE-001",
                approved_by="manager@example.com",
            ))
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(2, len(lines))

    def test_gate_decision_fields_present(self) -> None:
        """B-004: 100% gate decisions must include gate + policy_action + timestamp."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "audit.jsonl"
            logger = AuditLogger(log_path)
            logger.log(AuditEvent(
                agent_id="orchestrator",
                agent_class="coordination",
                action="gate-fail",
                tool="gate-fail",
                policy_action="deny",
                gate="2",
                wave_id="WAVE-002",
            ))
            entry = json.loads(log_path.read_text(encoding="utf-8").strip())
            for field in ("timestamp", "agent_id", "agent_class", "action", "policy_action", "gate", "wave_id"):
                self.assertIn(field, entry, f"Missing required field: {field}")


if __name__ == "__main__":
    unittest.main()
