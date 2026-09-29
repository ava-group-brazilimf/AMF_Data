"""
audit_logger.py
B-004 — Append-only JSONL audit trail for gate pass/fail and overrides.

Every gate decision (allow/deny/review) is written as an immutable JSONL
entry with a UTC timestamp. Log files are opened in append-mode only.

Usage:
    from scripts.audit_logger import AuditLogger, AuditEvent

    logger = AuditLogger(Path("./audit.jsonl"))
    logger.log(AuditEvent(
        agent_id="orchestrator",
        agent_class="coordination",
        action="gate-pass",
        tool="gate-pass",
        policy_action="allow",
        gate="3",
        wave_id="WAVE-001",
        approved_by="lead@example.com",
    ))
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class AuditEvent:
    agent_id: str
    agent_class: str
    action: str
    tool: str
    policy_action: str          # allow | review | deny
    gate: str
    wave_id: str
    approved_by: str | None = None
    details: dict = field(default_factory=dict)
    # timestamp is injected at write time; do not set manually
    timestamp: str = ""


class AuditLogger:
    """Append-only JSONL logger for agent governance audit events.

    B-004 requirements:
    - 100% gate decisions logged with required fields.
    - Entries are immutable: the log file is always opened in append mode.
    - Fields: timestamp, agent_id, agent_class, action, tool,
              policy_action, approved_by, gate, wave_id.
    """

    REQUIRED_FIELDS = (
        "timestamp", "agent_id", "agent_class", "action",
        "tool", "policy_action", "gate", "wave_id",
    )

    def __init__(self, log_path: Path) -> None:
        self._path = log_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: AuditEvent) -> None:
        """Write an audit entry. Always appends; never overwrites."""
        event.timestamp = datetime.now(timezone.utc).isoformat()
        entry = asdict(event)
        # Remove None values for cleaner output (but keep empty strings)
        entry = {k: v for k, v in entry.items() if v is not None}
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict]:
        """Read all entries — useful for reporting/querying."""
        if not self._path.exists():
            return []
        entries = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries
