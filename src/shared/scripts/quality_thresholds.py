"""
quality_thresholds.py
B-011 — Threshold-based quality checks by entity tier.

Three tiers with preset (but overridable) thresholds:
  CRITICAL  — financial / transactional data  (strictest)
  STANDARD  — operational / reference data
  REFERENCE — lookup tables, config data       (most lenient)

GateScore formula (same as gate3-wave-report.md template):
  GateScore = completeness * 40 + dq_score * 30 + row_parity * 30

Usage:
    from scripts.quality_thresholds import evaluate_quality, EntityTier

    result = evaluate_quality(
        entity="orders",
        tier=EntityTier.CRITICAL,
        completeness=0.99,
        row_parity=1.0,
        dq_score=0.98,
    )
    print(result.gate_score, result.passed, result.violations)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EntityTier(Enum):
    CRITICAL = "critical"
    STANDARD = "standard"
    REFERENCE = "reference"


@dataclass
class QualityThresholds:
    min_completeness: float = 0.98
    min_row_parity: float = 1.0
    min_dq_score: float = 0.95
    min_gate_score: float = 85.0


# Canonical defaults per tier — versioned in this module
TIER_DEFAULTS: dict[EntityTier, QualityThresholds] = {
    EntityTier.CRITICAL: QualityThresholds(
        min_completeness=0.99,
        min_row_parity=1.0,
        min_dq_score=0.98,
        min_gate_score=90.0,
    ),
    EntityTier.STANDARD: QualityThresholds(
        min_completeness=0.98,
        min_row_parity=1.0,
        min_dq_score=0.95,
        min_gate_score=85.0,
    ),
    EntityTier.REFERENCE: QualityThresholds(
        min_completeness=0.95,
        min_row_parity=0.99,
        min_dq_score=0.90,
        min_gate_score=80.0,
    ),
}


@dataclass
class QualityCheckResult:
    entity: str
    tier: EntityTier
    passed: bool
    gate_score: float
    completeness: float
    row_parity: float
    dq_score: float
    violations: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"Quality [{self.entity} / {self.tier.value}]: {status}",
            f"  GateScore    : {self.gate_score:.1f}",
            f"  Completeness : {self.completeness:.2%}",
            f"  Row Parity   : {self.row_parity:.2%}",
            f"  DQ Score     : {self.dq_score:.2%}",
        ]
        for v in self.violations:
            lines.append(f"  VIOLATION: {v}")
        return "\n".join(lines)


def _gate_score(completeness: float, row_parity: float, dq_score: float) -> float:
    """GateScore = completeness*40 + dq_score*30 + row_parity*30, capped 0–100."""
    raw = completeness * 40.0 + dq_score * 30.0 + row_parity * 30.0
    return round(min(100.0, max(0.0, raw)), 2)


def evaluate_quality(
    entity: str,
    tier: EntityTier,
    completeness: float,
    row_parity: float,
    dq_score: float,
    thresholds: QualityThresholds | None = None,
) -> QualityCheckResult:
    """Evaluate quality metrics against tier thresholds.

    Uses TIER_DEFAULTS[tier] if no custom thresholds provided.
    """
    t = thresholds if thresholds is not None else TIER_DEFAULTS[tier]
    violations: list[str] = []

    if completeness < t.min_completeness:
        violations.append(
            f"completeness {completeness:.2%} < threshold {t.min_completeness:.2%}"
        )
    if row_parity < t.min_row_parity:
        violations.append(
            f"row parity {row_parity:.2%} < threshold {t.min_row_parity:.2%}"
        )
    if dq_score < t.min_dq_score:
        violations.append(
            f"dq_score {dq_score:.2%} < threshold {t.min_dq_score:.2%}"
        )

    score = _gate_score(completeness, row_parity, dq_score)
    if score < t.min_gate_score:
        violations.append(
            f"gate_score {score:.1f} < threshold {t.min_gate_score:.1f}"
        )

    return QualityCheckResult(
        entity=entity,
        tier=tier,
        passed=len(violations) == 0,
        gate_score=score,
        completeness=completeness,
        row_parity=row_parity,
        dq_score=dq_score,
        violations=violations,
    )
