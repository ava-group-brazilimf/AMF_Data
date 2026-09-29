"""
reconciliation_tolerance.py
B-012 — Reconciliation tolerance bands for non-critical row/value deltas.

Tolerance bands allow a small percentage deviation between source and target
without failing the wave. Useful for reference data and reporting entities
where exact parity is not required but documented bounds are enforced.

Usage:
    from scripts.reconciliation_tolerance import ToleranceBand, evaluate_tolerance

    band = ToleranceBand(max_row_delta_pct=0.01, max_value_delta_pct=0.005)
    result = evaluate_tolerance(
        entity="orders",
        source_count=10_000,
        target_count=9_999,
        source_sum=100_000.0,
        target_sum=99_998.0,
        band=band,
    )
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ToleranceStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class ToleranceBand:
    max_row_delta_pct: float = 0.01    # 1% row delta allowed
    max_value_delta_pct: float = 0.005 # 0.5% value sum delta allowed


@dataclass
class ToleranceResult:
    entity: str
    status: ToleranceStatus
    row_delta_pct: float
    value_delta_pct: float | None
    violations: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Tolerance [{self.entity}]: {self.status.value}"]
        lines.append(f"  Row delta   : {self.row_delta_pct:.2%}")
        if self.value_delta_pct is not None:
            lines.append(f"  Value delta : {self.value_delta_pct:.2%}")
        for v in self.violations:
            lines.append(f"  VIOLATION: {v}")
        return "\n".join(lines)


def evaluate_tolerance(
    entity: str,
    source_count: int,
    target_count: int,
    band: ToleranceBand,
    source_sum: float | None = None,
    target_sum: float | None = None,
) -> ToleranceResult:
    """Evaluate row count and optional value delta against tolerance band."""
    violations: list[str] = []

    # Row delta
    row_delta = (
        abs(source_count - target_count) / source_count
        if source_count > 0
        else 0.0
    )
    if row_delta > band.max_row_delta_pct:
        violations.append(
            f"row_delta {row_delta:.2%} exceeds band {band.max_row_delta_pct:.2%}"
        )

    # Value delta (optional)
    value_delta: float | None = None
    if source_sum is not None and target_sum is not None:
        value_delta = (
            abs(source_sum - target_sum) / abs(source_sum)
            if source_sum != 0
            else 0.0
        )
        if value_delta > band.max_value_delta_pct:
            violations.append(
                f"value_delta {value_delta:.2%} exceeds band {band.max_value_delta_pct:.2%}"
            )

    return ToleranceResult(
        entity=entity,
        status=ToleranceStatus.PASS if not violations else ToleranceStatus.FAIL,
        row_delta_pct=round(row_delta, 6),
        value_delta_pct=round(value_delta, 6) if value_delta is not None else None,
        violations=violations,
    )
