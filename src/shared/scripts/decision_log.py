"""
decision_log.py
B-018 — Governance exception decision log.

Provides an auditable, searchable log for governance exception decisions
(e.g. gate overrides, policy waivers). Entries are stored as JSONL for
auditability and can be exported to Markdown for review.

Usage:
    from scripts.decision_log import DecisionLog, DecisionLogEntry, DecisionOutcome
    from pathlib import Path

    log = DecisionLog(Path("./decisions.jsonl"))
    entry = DecisionLogEntry(
        exception_type="policy-override",
        description="Skip UAT gate for emergency hotfix",
        decision=DecisionOutcome.APPROVED,
        rationale="Hotfix must ship before business open",
        decided_by="lead@example.com",
        wave_id="WAVE-001",
        gate="2",
    )
    log.record(entry)
    results = log.search("hotfix")
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


class DecisionOutcome(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class DecisionLogEntry:
    """A single governance exception decision record."""
    exception_type: str          # e.g. "policy-override", "gate-waiver"
    description: str             # human-readable description of the exception
    decision: DecisionOutcome    # APPROVED or REJECTED
    rationale: str               # justification for the decision
    decided_by: str              # identity (email / agent_id) of decision maker
    wave_id: str                 # migration wave reference
    gate: str                    # gate reference (e.g. "2", "3")
    # Fields injected on record():
    decision_id: str = field(default="")
    decided_at: str = field(default="")


class DecisionLog:
    """Append-only JSONL decision log with keyword search and Markdown export.

    B-018 requirements:
    - Entries are immutable — always appended, never overwritten.
    - Each entry gets a unique decision_id (UUID) and decided_at timestamp.
    - search() supports case-insensitive keyword lookup against description
      and exception_type fields.
    - to_markdown() exports all entries in a human-readable table format.
    """

    def __init__(self, log_path: Path) -> None:
        self._path = log_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, entry: DecisionLogEntry) -> None:
        """Append an entry to the decision log.

        Injects decision_id (UUID4) and decided_at (UTC ISO timestamp)
        if not already set.
        """
        if not entry.decision_id:
            entry.decision_id = str(uuid.uuid4())
        if not entry.decided_at:
            entry.decided_at = datetime.now(timezone.utc).isoformat()
        row = asdict(entry)
        # Serialize enum values as their string value
        row["decision"] = entry.decision.value
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _read_all(self) -> list[DecisionLogEntry]:
        """Load all entries from disk."""
        if not self._path.exists():
            return []
        entries: list[DecisionLogEntry] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            data["decision"] = DecisionOutcome(data["decision"])
            entries.append(DecisionLogEntry(**data))
        return entries

    def search(self, query: str) -> list[DecisionLogEntry]:
        """Return entries whose description or exception_type contain the query.

        Case-insensitive keyword match.
        """
        q = query.lower()
        return [
            e for e in self._read_all()
            if q in e.description.lower() or q in e.exception_type.lower()
        ]

    def to_markdown(self, output_path: Path) -> None:
        """Export all entries as a Markdown table to output_path."""
        entries = self._read_all()
        lines = [
            "# Governance Exception Decision Log",
            "",
            "| Decision ID | Wave | Gate | Type | Description | Decision | Rationale | Decided By | Date |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for e in entries:
            lines.append(
                f"| {e.decision_id[:8]}… | {e.wave_id} | {e.gate} | "
                f"{e.exception_type} | {e.description} | "
                f"**{e.decision.value.upper()}** | {e.rationale} | "
                f"{e.decided_by} | {e.decided_at[:10]} |"
            )
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
