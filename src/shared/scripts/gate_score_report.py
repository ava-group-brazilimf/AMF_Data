"""
gate_score_report.py
B-007 — GateScore calculation and gate report generation.

GateScore formula (mirrors gate3-wave-report.md template):
  GateScore = (tests_passed / tests_total) * 40
            + dq_score              * 30
            + row_parity            * 30

Minimum pass threshold: 85 (configurable per gate).

Usage:
    from scripts.gate_score_report import generate_gate_score_report, GateScoreInput

    inp = GateScoreInput(wave_id="WAVE-001", gate=3,
                         tests_passed=9, tests_total=10,
                         dq_score=0.98, row_parity=1.0)
    report = generate_gate_score_report(inp)
    print(report)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

try:
    from headroom import compress
    HEADROOM_AVAILABLE = True
except ImportError:
    HEADROOM_AVAILABLE = False


class GateDecision(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


# Minimum GateScore per gate to promote
GATE_PASS_THRESHOLDS: dict[int, float] = {
    1: 80.0,
    2: 85.0,
    3: 85.0,
}


@dataclass
class GateScoreInput:
    wave_id: str
    gate: int
    tests_passed: int
    tests_total: int
    dq_score: float      # 0.0–1.0
    row_parity: float    # 0.0–1.0


@dataclass
class GateScoreReport:
    wave_id: str
    gate: int
    gate_score: float
    decision: GateDecision
    tests_rate: float
    dq_score: float
    row_parity: float
    pass_threshold: float
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __str__(self) -> str:
        lines = [
            f"Gate {self.gate} Score Report — {self.wave_id}",
            f"  Decision      : {self.decision.value}",
            f"  GateScore     : {self.gate_score:.1f} (threshold: {self.pass_threshold:.1f})",
            f"  Tests Passed  : {self.tests_rate:.1%}  × 40  = {self.tests_rate * 40:.1f}",
            f"  DQ Score      : {self.dq_score:.1%}   × 30  = {self.dq_score * 30:.1f}",
            f"  Row Parity    : {self.row_parity:.1%}  × 30  = {self.row_parity * 30:.1f}",
            f"  Generated At  : {self.generated_at}",
        ]
        return "\n".join(lines)


def generate_gate_score_report(inp: GateScoreInput) -> GateScoreReport:
    """Compute GateScore and produce a gate report."""
    tests_rate = inp.tests_passed / inp.tests_total if inp.tests_total > 0 else 0.0
    raw = tests_rate * 40.0 + inp.dq_score * 30.0 + inp.row_parity * 30.0
    score = round(min(100.0, max(0.0, raw)), 2)
    threshold = GATE_PASS_THRESHOLDS.get(inp.gate, 85.0)
    return GateScoreReport(
        wave_id=inp.wave_id,
        gate=inp.gate,
        gate_score=score,
        decision=GateDecision.PASS if score >= threshold else GateDecision.FAIL,
        tests_rate=tests_rate,
        dq_score=inp.dq_score,
        row_parity=inp.row_parity,
        pass_threshold=threshold,
    )


def generate_gate_score_report_compressed(inp: GateScoreInput) -> dict:
    """Compute GateScore and produce a compressed report for agent context.

    Returns a compressed dict when Headroom is available, otherwise
    falls back to the standard report as a dict.
    """
    report = generate_gate_score_report(inp)
    report_dict = {
        "wave_id": report.wave_id,
        "gate": report.gate,
        "gate_score": report.gate_score,
        "decision": report.decision.value,
        "tests_rate": report.tests_rate,
        "dq_score": report.dq_score,
        "row_parity": report.row_parity,
        "pass_threshold": report.pass_threshold,
        "generated_at": report.generated_at,
    }

    if HEADROOM_AVAILABLE:
        compressed = compress(
            [{"role": "tool", "content": json.dumps(report_dict)}],
            model="claude-sonnet-4-6",
        )
        return {"_headroom_compressed": True, "content": compressed}

    return report_dict
