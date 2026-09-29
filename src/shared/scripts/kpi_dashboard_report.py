"""
kpi_dashboard_report.py
B-015 — Wave KPI dashboard report artifact.

Consumes wave execution metrics (first-pass rate, rollback count, MTTR,
cycle time) and produces a structured per-KPI report with actual vs target
comparison and a PASS/FAIL status for each KPI.

Usage:
    from scripts.kpi_dashboard_report import (
        WaveExecutionMetrics,
        generate_kpi_dashboard_report,
    )

    metrics = WaveExecutionMetrics(
        wave_id="WAVE-001",
        first_pass_rate_pct=98.5,
        rollback_count=0,
        mttr_minutes=0.0,
        cycle_time_minutes=120.0,
    )
    report = generate_kpi_dashboard_report(metrics)
    for row in report.rows:
        print(row.kpi_id, row.actual, row.status)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from scripts.performance_benchmark import BenchmarkReport, lead_time_by_entity

try:
    from headroom import compress
    HEADROOM_AVAILABLE = True
except ImportError:
    HEADROOM_AVAILABLE = False


class ReportStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


@dataclass
class WaveExecutionMetrics:
    """Execution-level metrics collected after a migration wave completes."""
    wave_id: str
    first_pass_rate_pct: float   # % entities migrated without rollback on first try
    rollback_count: int          # number of rollback events during the wave
    mttr_minutes: float          # mean time to recovery (minutes)
    cycle_time_minutes: float    # total elapsed time from start to validated (minutes)
    # AST Engine quality metrics (optional — defaults to None = not measured)
    ast_coverage_pct: float | None = None         # % objects resolved via AST (target >90)
    transformation_accuracy_pct: float | None = None  # % transformations identified (target >95)
    code_generation_accuracy_pct: float | None = None  # % artifacts generated without manual correction (target >80)
    data_accuracy_pct: float | None = None # % row_parity entre origem e destino (target ≥ 99.9%)
    auto_validated_pct: float | None = None # % entities that passed automatic reconciliation without manual review (target ≥ 90%)
    migration_ready_pct: float | None = None

@dataclass
class KPIReportRow:
    """One row in the KPI dashboard report."""
    kpi_id: str
    kpi_name: str
    actual: str           # human-readable actual value string
    target: str           # human-readable target string
    status: ReportStatus


@dataclass
class KPIDashboardReport:
    """Full KPI dashboard report for a single wave."""
    wave_id: str
    rows: list[KPIReportRow]
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

# ---------------------------------------------------------------------------
# KPI definitions: thresholds and targets
# ---------------------------------------------------------------------------
_KPI_SPECS = [
    {
        "kpi_id": "first_pass_rate",
        "kpi_name": "First-Pass Rate",
        "target": "≥ 95%",
        "threshold": 95.0,
        "comparison": "gte",
        "unit": "pct",
        "field": "first_pass_rate_pct",
    },
    {
        "kpi_id": "rollback_count",
        "kpi_name": "Rollback Count",
        "target": "= 0",
        "threshold": 0,
        "comparison": "lte",
        "unit": "count",
        "field": "rollback_count",
    },
    {
        "kpi_id": "mttr",
        "kpi_name": "Mean Time to Recovery",
        "target": "≤ 60 min",
        "threshold": 60.0,
        "comparison": "lte",
        "unit": "minutes",
        "field": "mttr_minutes",
    },
    {
        "kpi_id": "cycle_time",
        "kpi_name": "Migration Cycle Time",
        "target": "≤ 240 min",
        "threshold": 240.0,
        "comparison": "lte",
        "unit": "minutes",
        "field": "cycle_time_minutes",
    },
]

# AST Engine KPI specs — evaluated only when the metric is present (not None)
_AST_KPI_SPECS = [
    {
        "kpi_id": "ast_coverage",
        "kpi_name": "AST Coverage",
        "target": "> 90%",
        "threshold": 90.0,
        "comparison": "gte",
        "unit": "pct",
        "field": "ast_coverage_pct",
    },
    {
        "kpi_id": "transformation_accuracy",
        "kpi_name": "Transformation Accuracy",
        "target": "> 95%",
        "threshold": 95.0,
        "comparison": "gte",
        "unit": "pct",
        "field": "transformation_accuracy_pct",
    },
    {
        "kpi_id": "code_generation_accuracy",
        "kpi_name": "Code Generation Accuracy",
        "target": "> 80%",
        "threshold": 80.0,
        "comparison": "gte",
        "unit": "pct",
        "field": "code_generation_accuracy_pct",
    },
    {

        "kpi_id": "data_accuracy",
        "kpi_name": "Data Accuracy",
        "target": "≥ 99.9%",
        "threshold": 99.9,
        "comparison": "gte",
        "unit": "pct",
        "field": "data_accuracy_pct",
    },
    {       
        "kpi_id": "auto_validated",
        "kpi_name": "Tabelas Validadas Automaticamente",
        "target": "≥ 90%",
        "threshold": 90.0,
        "comparison": "gte",
        "unit": "pct",
        "field": "auto_validated_pct",
    },
    {
    "kpi_id": "migration_ready",
    "kpi_name": "Dados Prontos para Migração",
    "target": "≥ 80%",
    "threshold": 80.0,
    "comparison": "gte",
    "unit": "pct",
    "field": "migration_ready_pct",
},
]

def _evaluate_status(comparison: str, actual: float, threshold: float) -> ReportStatus:
    if comparison == "gte":
        return ReportStatus.PASS if actual >= threshold else ReportStatus.FAIL
    if comparison == "lte":
        return ReportStatus.PASS if actual <= threshold else ReportStatus.FAIL
    return ReportStatus.PARTIAL

def generate_kpi_dashboard_report(metrics: WaveExecutionMetrics) -> KPIDashboardReport:
    """Generate a per-KPI dashboard report from wave execution metrics.

    Includes standard wave KPIs plus AST Engine quality KPIs when present.

    Args:
        metrics: Execution data collected after the wave completes.

    Returns:
        KPIDashboardReport with one KPIReportRow per KPI.
    """
    rows: list[KPIReportRow] = []
    all_specs = list(_KPI_SPECS)

    # Include AST KPIs only when the metric has been measured (not None)
    for spec in _AST_KPI_SPECS:
        if getattr(metrics, spec["field"], None) is not None:
            all_specs.append(spec)

    for spec in all_specs:
        actual_val = getattr(metrics, spec["field"])
        status = _evaluate_status(spec["comparison"], float(actual_val), float(spec["threshold"]))
        unit = spec["unit"]
        if unit == "pct":
            actual_str = f"{actual_val:.1f}%"
        elif unit == "minutes":
            actual_str = f"{actual_val:.1f} min"
        else:
            actual_str = str(actual_val)
        rows.append(KPIReportRow(
            kpi_id=spec["kpi_id"],
            kpi_name=spec["kpi_name"],
            actual=actual_str,
            target=spec["target"],
            status=status,
        ))
    return KPIDashboardReport(wave_id=metrics.wave_id, rows=rows)

def calc_auto_validated_pct(auto_passed: int, total_entities: int) -> float:
    """% de entidades que passaram na reconciliação automática, sem revisão manual."""
    if total_entities == 0:
        return 0.0
    return round(auto_passed / total_entities * 100, 1)


def calc_migration_ready_pct(migration_ready: int, total_entities: int) -> float:
    """% de entidades prontas para migração com gate de readiness aprovado."""
    if total_entities == 0:
        return 0.0
    return round(migration_ready / total_entities * 100, 1)


SIMPLE_CLASSES = {"LOW", "MEDIUM"}


def complexity_distribution(classifications: list[dict]) -> dict[str, int]:
    """Conta objetos por classe de complexidade declarada no classification.json."""
    dist: dict[str, int] = {}

    for item in classifications:
        klass = item.get("complexity", "UNKNOWN")
        dist[klass] = dist.get(klass, 0) + 1

    return dist


def simple_vs_complex_pct(classifications: list[dict]) -> tuple[float, float]:
    """Retorna (% simples, % complexos) usando LOW/MEDIUM e COMPLEX/VERY_COMPLEX."""
    if not classifications:
        return (0.0, 0.0)

    simple = sum(1 for item in classifications if item.get("complexity") in SIMPLE_CLASSES)
    total = len(classifications)
    simple_pct = round(simple / total * 100, 1)

    return (simple_pct, round(100 - simple_pct, 1))


def generate_kpi_dashboard_report_compressed(
    metrics: WaveExecutionMetrics,
) -> dict:
    """Generate KPI dashboard report with optional Headroom compression.

    Returns a compressed dict when Headroom is available, otherwise
    falls back to the standard report as a dict.
    """
    report = generate_kpi_dashboard_report(metrics)
    report_dict = {
        "wave_id": report.wave_id,
        "generated_at": report.generated_at,
        "rows": [
            {
                "kpi_id": row.kpi_id,
                "kpi_name": row.kpi_name,
                "actual": row.actual,
                "target": row.target,
                "status": row.status.value,
            }
            for row in report.rows
        ],
    }

    if HEADROOM_AVAILABLE:
        compressed = compress(
            [{"role": "tool", "content": json.dumps(report_dict)}],
            model="claude-sonnet-4-6",
        )
        return {"_headroom_compressed": True, "content": compressed}

    return report_dict


def generate_kpi_dashboard_report_with_lead_times(
    metrics: WaveExecutionMetrics, reports: list[BenchmarkReport]
) -> dict:
    """Generate a KPI dashboard report and include lead-time-by-entity list.

    Builds the same dict structure as generate_kpi_dashboard_report_compressed,
    then appends `lead_time_by_entity`. If Headroom is available, the full
    report (including the lead-time list) is compressed and returned in the
    same compressed wrapper format.
    """
    # Build base report dict from the standard report generator
    report = generate_kpi_dashboard_report(metrics)
    report_dict = {
        "wave_id": report.wave_id,
        "generated_at": report.generated_at,
        "rows": [
            {
                "kpi_id": row.kpi_id,
                "kpi_name": row.kpi_name,
                "actual": row.actual,
                "target": row.target,
                "status": row.status.value,
            }
            for row in report.rows
        ],
    }

    # Attach lead-time-by-entity list (slowest -> fastest)
    lead_pairs = lead_time_by_entity(reports)
    report_dict["lead_time_by_entity"] = [
        {"entity": entity, "duration_minutes": minutes} for entity, minutes in lead_pairs
    ]

    # Compress if available, matching existing compressed function behavior
    if HEADROOM_AVAILABLE:
        compressed = compress(
            [{"role": "tool", "content": json.dumps(report_dict)}],
            model="claude-sonnet-4-6",
        )
        return {"_headroom_compressed": True, "content": compressed}

    return report_dict
