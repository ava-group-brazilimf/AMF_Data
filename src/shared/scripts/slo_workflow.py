"""
slo_workflow.py
B-016 — SLO baseline definition and breach action workflow.

Defines SLO baselines for migration KPIs, evaluates actuals against thresholds,
and raises ReviewRequest entries for each SLO breach. Integrates with B-015
(kpi_dashboard_report) metrics and B-003 (review_workflow) for human-in-the-loop
escalation.

Usage:
    from scripts.slo_workflow import SLOBaseline, SLOWorkflow, check_slo_breach

    workflow = SLOWorkflow()
    workflow.register(SLOBaseline(
        kpi_id="first_pass_rate",
        baseline_value=95.0,
        breach_threshold=95.0,
        unit="pct",
        comparison="gte",
    ))
    results = workflow.evaluate_wave({"first_pass_rate": 80.0})
    for r in results:
        if r.breached:
            print(r.kpi_id, r.action_items, r.review_request_id)
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# SLO model
# ---------------------------------------------------------------------------

@dataclass
class SLOBaseline:
    """Defines a Service Level Objective for a single KPI.

    Args:
        kpi_id:           Matches a KPIReportRow.kpi_id (B-015).
        baseline_value:   Historical or agreed baseline for the KPI.
        breach_threshold: Value at which the SLO is considered breached.
        unit:             Unit label (e.g. "pct", "count", "minutes").
        comparison:       "gte" — actual must be >= threshold to pass.
                          "lte" — actual must be <= threshold to pass.
    """
    kpi_id: str
    baseline_value: float
    breach_threshold: float
    unit: str
    comparison: str   # "gte" | "lte"


@dataclass
class SLOBreachResult:
    """Result of evaluating a single SLO against an actual value."""
    kpi_id: str
    breached: bool
    actual: float
    breach_threshold: float
    baseline_value: float
    action_items: list[str] = field(default_factory=list)
    review_request_id: str | None = None


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def check_slo_breach(slo: SLOBaseline, actual_value: float) -> SLOBreachResult:
    """Evaluate whether a single SLO is breached.

    Returns an SLOBreachResult with action_items populated if breached.
    Does NOT raise ReviewRequest — use SLOWorkflow.evaluate_wave() for that.
    """
    if slo.comparison == "gte":
        breached = actual_value < slo.breach_threshold
    elif slo.comparison == "lte":
        breached = actual_value > slo.breach_threshold
    else:
        raise ValueError(f"Unknown comparison '{slo.comparison}'. Use 'gte' or 'lte'.")

    action_items: list[str] = []
    if breached:
        action_items = [
            f"Investigate root cause for KPI '{slo.kpi_id}': "
            f"actual={actual_value} {slo.unit}, "
            f"threshold={slo.breach_threshold} {slo.unit}",
            f"Escalate to wave owner for corrective action on '{slo.kpi_id}'",
            "Update wave runbook with corrective steps before re-execution",
        ]

    return SLOBreachResult(
        kpi_id=slo.kpi_id,
        breached=breached,
        actual=actual_value,
        breach_threshold=slo.breach_threshold,
        baseline_value=slo.baseline_value,
        action_items=action_items,
    )


# ---------------------------------------------------------------------------
# Workflow engine
# ---------------------------------------------------------------------------

class SLOWorkflow:
    """Manages multiple SLO baselines and evaluates a full wave actuals map.

    For each breached SLO, a ReviewRequest ID is generated to trigger
    human-in-the-loop escalation (compatible with review_workflow.py B-003).
    """

    def __init__(self) -> None:
        self._slos: list[SLOBaseline] = []

    def register(self, slo: SLOBaseline) -> None:
        """Register an SLO baseline for this workflow."""
        self._slos.append(slo)

    def evaluate_wave(self, actuals: dict[str, float]) -> list[SLOBreachResult]:
        """Evaluate all registered SLOs against the provided actuals.

        Args:
            actuals: Mapping of kpi_id → actual measured value.

        Returns:
            List of SLOBreachResult — one per registered SLO.
            Missing actuals are treated as 0.0 for numeric KPIs.
        """
        results: list[SLOBreachResult] = []
        for slo in self._slos:
            actual_value = float(actuals.get(slo.kpi_id, 0.0))
            result = check_slo_breach(slo, actual_value)
            if result.breached:
                result.review_request_id = str(uuid.uuid4())
            results.append(result)
        return results
