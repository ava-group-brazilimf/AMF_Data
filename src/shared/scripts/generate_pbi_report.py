"""
generate_pbi_report.py  — DMF v3 · Bianca (bi-semantic)
=========================================================
Generates a Power BI .pbip project with EMBEDDED data from metrics_registry.json. 
When opened in Power BI Desktop, no data source setup is needed.


Use:
    python -m src.shared.scripts.generate_pbi_report \
                --metrics projects/<project-name>/outputs/summary/metrics_registry.json \
                --output  projects/<project-name>/outputs/downstream/bi/ \
        --wave    WAVE-001

Smoke test (with synthetic metrics file):
        python -m src.shared.scripts.generate_pbi_report \
            --metrics "tmp/metrics_registry.json" \
            --output  "tmp/bi" \
            --wave    "WAVE-001"

Programmatic API (called by Bianca at the end of Gate 3):
    from src.shared.scripts.generate_pbi_report import generate
    pbip_path = generate(
        metrics_path=Path("projects/<project-name>/outputs/summary/metrics_registry.json"),
        output_dir=Path("projects/<project-name>/outputs/downstream/bi/"),
        wave_filter="WAVE-001",
    )
"""

from __future__ import annotations

import argparse
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANVAS_W  = 1280
CANVAS_H  = 720
GRID_COLS = 24
GRID_ROWS = 12
COL_W     = CANVAS_W / GRID_COLS   # 53.333...
ROW_H     = CANVAS_H / GRID_ROWS   # 60.0

# ── General utilities ────────────────────────────────────────────────────────

def uid() -> str:
    return str(uuid.uuid4())


def px(col: float, row: float, colspan: float, rowspan: float) -> dict:
    """Converts grid position to Power BI pixels."""
    return {
        "x":      round(col     * COL_W, 1),
        "y":      round(row     * ROW_H, 1),
        "width":  round(colspan * COL_W, 1),
        "height": round(rowspan * ROW_H, 1),
    }


def write_json(path: Path, data: Any, indent: int = 2, dry_run: bool = False) -> None:
    if dry_run:
        print(f"  [DRY] {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK]  {path}")


def write_text(path: Path, text: str, dry_run: bool = False) -> None:
    if dry_run:
        print(f"  [DRY] {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  [OK]  {path}")


def load_metrics(metrics_path: Path) -> dict:
    with open(metrics_path, encoding="utf-8") as f:
        return json.load(f)


def resolve_wave_id(data: dict, wave_filter: str | None) -> str:
    waves = [w["wave_id"] for w in data.get("wave_summary", [])]
    if not waves:
        raise ValueError("metrics_registry.json não contém wave_summary.")
    if wave_filter:
        if wave_filter not in waves:
            raise ValueError(f"Wave '{wave_filter}' não encontrada. Disponíveis: {waves}")
        return wave_filter
    return waves[0]


# ── M Expression inline — Table.FromRecords() ────────────────────────────────

_M_TYPE_MAP: dict[str, str] = {
    "string":   "type text",
    "int64":    "Int64.Type",
    "double":   "type number",
    "boolean":  "type logical",
    "dateTime": "type text",
}


def _m_literal(val: Any, dtype: str) -> str:
    """Converte um valor Python para literal Power Query M válido."""
    if val is None:
        return "null"
    if dtype == "boolean":
        return "true" if val else "false"
    if dtype in ("int64", "double"):
        return str(val)
    s = str(val).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _make_m_partition(table_name: str, columns: list[dict], rows: list[dict]) -> str:
    """
   Generate M expression with inline data using Table.FromRecords().

    M Records: [key=value, key=value, ...]
    Doesn't contain JSON → no token conflicts.
    """
    T = "\t\t\t\t"

    record_lines: list[str] = []
    for row in rows:
        fields: list[str] = []
        for col in columns:
            name  = col["name"]
            dtype = col["dataType"]
            lit   = _m_literal(row.get(name), dtype)
            safe = name.replace("_", "")
            if " " in name or not safe.isalnum():
                fields.append(f'#"{name}"={lit}')
            else:
                fields.append(f"{name}={lit}")
        record_lines.append(f'[{", ".join(fields)}]')

    type_pairs: list[str] = []
    for col in columns:
        name   = col["name"]
        m_type = _M_TYPE_MAP.get(col["dataType"], "type any")
        safe   = name.replace("_", "")
        quoted = f'#"{name}"' if (" " in name or not safe.isalnum()) else f'"{name}"'
        type_pairs.append(f'{{{quoted}, {m_type}}}')

    sep_r = f",\n{T}        "
    sep_t = f",\n{T}        "

    if not rows:
        col_names = [
            f'#"{c["name"]}"' if (" " in c["name"] or not c["name"].replace("_", "").isalnum())
            else f'"{c["name"]}"'
            for c in columns
        ]
        return (
            f"let\n"
            f"{T}    Source = #table(\n"
            f"{T}        {{{', '.join(col_names)}}},\n"
            f"{T}        {{}}\n"
            f"{T}    ),\n"
            f"{T}    ChangedTypes = Table.TransformColumnTypes(Source, {{{sep_t.join(type_pairs)}}})\n"
            f"{T}in\n"
            f"{T}    ChangedTypes"
        )
    else:
        recs  = sep_r.join(record_lines)
        types = sep_t.join(type_pairs)
        return (
            f"let\n"
            f"{T}    Source = Table.FromRecords(\n"
            f"{T}        {{\n"
            f"{T}        {recs}\n"
            f"{T}    }}),\n"
            f"{T}    ChangedTypes = Table.TransformColumnTypes(Source, {{\n"
            f"{T}        {types}\n"
            f"{T}    }})\n"
            f"{T}in\n"
            f"{T}    ChangedTypes"
        )


# ── Table definitions ─────────────────────────────────────────────────────

def _def_wave_summary():
    cols = [
        {"name": "wave_id",                   "dataType": "string"},
        {"name": "overall_pct",               "dataType": "double"},
        {"name": "tables_migrated",           "dataType": "int64"},
        {"name": "tables_total",              "dataType": "int64"},
        {"name": "tables_pct",                "dataType": "double"},
        {"name": "pipelines_migrated",        "dataType": "int64"},
        {"name": "pipelines_total",           "dataType": "int64"},
        {"name": "pipelines_pct",             "dataType": "double"},
        {"name": "avg_pipeline_time_minutes", "dataType": "double"},
        {"name": "tables_remaining",          "dataType": "int64"},
        {"name": "backlog_pct",               "dataType": "double"},
        {"name": "gb_remaining",              "dataType": "double"},
        {"name": "wave_estimate_accuracy",    "dataType": "double"},
        {"name": "environment",               "dataType": "string"},
        {"name": "recorded_at",               "dataType": "dateTime"},
        {"name": "notes",                     "dataType": "string"},
    ]
    msrs = [
        ("Overall Progress %",          "MAX(WaveSummary[overall_pct])"),
        ("Tables Migration %",          "MAX(WaveSummary[tables_pct])"),
        ("Pipelines Migration %",       "MAX(WaveSummary[pipelines_pct])"),
        ("Avg Pipeline Time (min)",     "MAX(WaveSummary[avg_pipeline_time_minutes])"),
        ("Tables Remaining",            "MAX(WaveSummary[tables_remaining])"),
        ("Backlog %",                   "MAX(WaveSummary[backlog_pct])"),
        ("GB Remaining",                "MAX(WaveSummary[gb_remaining])"),
        ("Wave Estimate Accuracy %",    "MAX(WaveSummary[wave_estimate_accuracy])"),
    ]
    return cols, msrs


def _def_gate_status():
    cols = [
        {"name": "wave_id",               "dataType": "string"},
        {"name": "gate",                  "dataType": "int64"},
        {"name": "phase_status",          "dataType": "string"},
        {"name": "artifacts_present",     "dataType": "int64"},
        {"name": "artifacts_total",       "dataType": "int64"},
        {"name": "artifacts_pct",         "dataType": "double"},
        {"name": "tasks_completed",       "dataType": "int64"},
        {"name": "tasks_total",           "dataType": "int64"},
        {"name": "tasks_pct",             "dataType": "double"},
        {"name": "avg_task_time_minutes", "dataType": "double"},
        {"name": "gate_score",            "dataType": "double"},
        {"name": "environment",           "dataType": "string"},
        {"name": "recorded_at",           "dataType": "dateTime"},
        {"name": "notes",                 "dataType": "string"},
    ]
    msrs = [
        ("Gate Score G1",  'CALCULATE(MAX(GateStatus[gate_score]), GateStatus[gate] = 1)'),
        ("Gate Score G2",  'CALCULATE(MAX(GateStatus[gate_score]), GateStatus[gate] = 2)'),
        ("Gate Score G3",  'CALCULATE(MAX(GateStatus[gate_score]), GateStatus[gate] = 3)'),
        ("Gates Complete", 'COUNTROWS(FILTER(GateStatus, GateStatus[phase_status] = "COMPLETE"))'),
    ]
    return cols, msrs


def _def_gate_metrics():
    cols = [
        {"name": "wave_id",         "dataType": "string"},
        {"name": "gate",            "dataType": "int64"},
        {"name": "tests_rate",      "dataType": "double"},
        {"name": "dq_score",        "dataType": "double"},
        {"name": "row_parity",      "dataType": "double"},
        {"name": "rejection_rate",  "dataType": "double"},
        {"name": "rework_count",    "dataType": "int64"},
        {"name": "rework_time_min", "dataType": "double"},
        {"name": "environment",     "dataType": "string"},
        {"name": "recorded_at",     "dataType": "dateTime"},
        {"name": "notes",           "dataType": "string"},
    ]
    msrs = [
        ("Avg DQ Score",       "AVERAGE(GateMetrics[dq_score])"),
        ("Avg Row Parity",     "AVERAGE(GateMetrics[row_parity])"),
        ("Avg Tests Rate",     "AVERAGE(GateMetrics[tests_rate])"),
        ("Total Rework Count", "SUM(GateMetrics[rework_count])"),
        ("Total Rework Time",  "SUM(GateMetrics[rework_time_min])"),
    ]
    return cols, msrs


def _def_estimate_comparison():
    cols = [
        {"name": "wave_id",         "dataType": "string"},
        {"name": "entity",          "dataType": "string"},
        {"name": "estimated_rows",  "dataType": "int64"},
        {"name": "actual_rows",     "dataType": "int64"},
        {"name": "delta",           "dataType": "int64"},
        {"name": "delta_pct",       "dataType": "double"},
        {"name": "accuracy_pct",    "dataType": "double"},
        {"name": "environment",     "dataType": "string"},
        {"name": "recorded_at",     "dataType": "dateTime"},
        {"name": "notes",           "dataType": "string"},
    ]
    msrs = [
        ("Average Accuracy %", "AVERAGE(EstimateComparison[accuracy_pct])"),
        ("Average Delta %",    "AVERAGE(EstimateComparison[delta_pct])"),
    ]
    return cols, msrs


def _def_benchmarks():
    cols = [
        {"name": "wave_id",               "dataType": "string"},
        {"name": "entity",                "dataType": "string"},
        {"name": "rows_processed",        "dataType": "int64"},
        {"name": "rows_per_second",       "dataType": "double"},
        {"name": "bytes_processed",       "dataType": "int64"},
        {"name": "throughput_gb_per_day", "dataType": "double"},
        {"name": "total_volume",          "dataType": "string"},
        {"name": "table_size",            "dataType": "string"},
        {"name": "avg_table_size",        "dataType": "string"},
        {"name": "duration_seconds",      "dataType": "int64"},
        {"name": "status",                "dataType": "string"},
        {"name": "environment",           "dataType": "string"},
        {"name": "recorded_at",           "dataType": "dateTime"},
        {"name": "notes",                 "dataType": "string"},
    ]
    msrs = [
        ("Avg Throughput GB/day",   "AVERAGE(Benchmarks[throughput_gb_per_day])"),
        ("Avg Rows/sec",            "AVERAGE(Benchmarks[rows_per_second])"),
        ("Benchmarks PASS",         'COUNTROWS(FILTER(Benchmarks, Benchmarks[status] = "PASS"))'),
        ("Processing Time / GB",    "DIVIDE(SUM(Benchmarks[duration_seconds]), SUM(Benchmarks[bytes_processed]) / 1073741824)"),
        ("Lead Time (min)",        "AVERAGE(Benchmarks[duration_seconds]) / 60"),
    ]
    return cols, msrs


def _def_reconciliation():
    cols = [
        {"name": "wave_id",           "dataType": "string"},
        {"name": "entity",            "dataType": "string"},
        {"name": "status",            "dataType": "string"},
        {"name": "source_count",      "dataType": "int64"},
        {"name": "target_count",      "dataType": "int64"},
        {"name": "count_mismatch",    "dataType": "boolean"},
        {"name": "checksum_mismatch", "dataType": "boolean"},
        {"name": "environment",       "dataType": "string"},
        {"name": "recorded_at",       "dataType": "dateTime"},
        {"name": "notes",             "dataType": "string"},
    ]
    msrs = [
        ("Entities PASS", 'COUNTROWS(FILTER(Reconciliation, Reconciliation[status] = "PASS"))'),
        ("Entities FAIL", 'COUNTROWS(FILTER(Reconciliation, Reconciliation[status] = "FAIL"))'),
        ("Parity Rate %", 'DIVIDE([Entities PASS], COUNTROWS(Reconciliation)) * 100'),
        ("Errors per Million", 'DIVIDE( SUM(MismatchCategories[count]), SUM(Reconciliation[source_count]), 0 ) * 1000000'),
    ]
    return cols, msrs


def _def_mismatch_categories():
    cols = [
        {"name": "wave_id",   "dataType": "string"},
        {"name": "category",  "dataType": "string"},
        {"name": "count",     "dataType": "int64"},
        {"name": "environment", "dataType": "string"},
        {"name": "recorded_at", "dataType": "dateTime"},
        {"name": "notes",     "dataType": "string"},
    ]
    msrs = [
        ("Mismatch Count", "SUM(MismatchCategories[count])"),
    ]
    return cols, msrs


def _def_inventory():
    cols = [
        {"name": "wave_id",            "dataType": "string"},
        {"name": "tables_total",       "dataType": "int64"},
        {"name": "tables_migrated",    "dataType": "int64"},
        {"name": "pipelines_total",    "dataType": "int64"},
        {"name": "pipelines_migrated", "dataType": "int64"},
        {"name": "avg_table_size_gb",  "dataType": "double"},
        {"name": "total_volume_gb",    "dataType": "double"},
        {"name": "data_accuracy_pct",   "dataType": "double"},
        {"name": "auto_validated_pct",  "dataType": "double"},
        {"name": "migration_ready_pct", "dataType": "double"},
        {"name": "simple_pct",          "dataType": "double"},
        {"name": "complex_pct",         "dataType": "double"},
        {"name": "environment",        "dataType": "string"},
        {"name": "recorded_at",        "dataType": "dateTime"},
        {"name": "notes",              "dataType": "string"},
    ]
    msrs = [
        ("Data Accuracy %",     "MAX(Inventory[data_accuracy_pct])"),
        ("Auto Validated %",    "MAX(Inventory[auto_validated_pct])"),
        ("Migration Ready %",   "MAX(Inventory[migration_ready_pct])"),
        ("Simple %",            "MAX(Inventory[simple_pct])"),
        ("Complex %",           "MAX(Inventory[complex_pct])"),
    ]
    return cols, msrs


def _def_complexity_distribution():
    cols = [
        {"name": "wave_id",    "dataType": "string"},
        {"name": "complexity", "dataType": "string"},
        {"name": "value",      "dataType": "int64"},
        {"name": "environment", "dataType": "string"},
        {"name": "recorded_at", "dataType": "dateTime"},
        {"name": "notes",      "dataType": "string"},
    ]
    msrs = [
        ("Complexity Count", "SUM(ComplexityDistribution[value])"),
    ]
    return cols, msrs


_TABLE_REGISTRY = [
    ("WaveSummary",            _def_wave_summary,            "wave_summary",            "aaaaaaaa-0001"),
    ("EstimateComparison",     _def_estimate_comparison,     "estimate_comparison",     "aaaaaaaa-0002"),
    ("GateStatus",             _def_gate_status,             "gate_status",             "aaaaaaaa-0003"),
    ("GateMetrics",            _def_gate_metrics,            "gate_metrics",            "aaaaaaaa-0004"),
    ("Benchmarks",             _def_benchmarks,              "benchmarks",              "aaaaaaaa-0005"),
    ("Reconciliation",         _def_reconciliation,          "reconciliation",          "aaaaaaaa-0006"),
    ("MismatchCategories",     _def_mismatch_categories,     "mismatch_categories",     "aaaaaaaa-0007"),
    ("Inventory",              _def_inventory,               "inventory",               "aaaaaaaa-0008"),
    ("ComplexityDistribution", _def_complexity_distribution, "complexity_distribution", "aaaaaaaa-0009"),
]

_DTYPE_TMDL = {
    "string": "string", "int64": "int64", "double": "double",
    "boolean": "boolean", "dateTime": "string",
}
_FMT_STRING = {"double": "#,##0.00", "int64": "#,##0"}


def _build_table_tmdl(tname, cols, msrs, rows, lb):
    L = [f"table '{tname}'", f"\tlineageTag: {lb}-0000-0000-0000-000000000000", ""]
    for i, (mn, me) in enumerate(msrs):
        L += [f"\tmeasure '{mn}' = {me}", f"\t\tlineageTag: {lb}-0000-0000-0000-{i+1:012d}", ""]
    for j, col in enumerate(cols):
        cn = col["name"]
        ct = _DTYPE_TMDL.get(col["dataType"], "string")
        L.append(f"\tcolumn {cn}")
        L.append(f"\t\tdataType: {ct}")
        if col["dataType"] in _FMT_STRING:
            L.append(f"\t\tformatString: {_FMT_STRING[col['dataType']]}")
        L += [
            f"\t\tlineageTag: {lb}-0000-0000-{j+1:04d}-000000000000",
            f"\t\tsummarizeBy: none",
            f"\t\tsourceColumn: {cn}",
            f"\t\tannotation SummarizationSetBy = Automatic", "",
        ]
    m_expr = _make_m_partition(tname, cols, rows)
    L += [f"\tpartition '{tname}-Partition' = m", f"\t\tmode: import", f"\t\tsource ="]
    for ml in m_expr.splitlines():
        L.append(f"\t\t\t{ml}")
    L += ["", f"\tannotation PBI_ResultType = Table"]
    return "\n".join(L)


# ── SemanticModel ─────────────────────────────────────────────────────────────

def write_semantic_model(sm_dir, data, wave_id, dry_run):
    sm_def = sm_dir / "definition"
    sm_tables = sm_def / "tables"

    write_json(sm_dir / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": f"{wave_id} DMF Metrics"},
        "config": {"version": "2.0", "logicalId": uid()},
    }, dry_run=dry_run)

    write_json(sm_dir / "definition.pbism", {"version": "4.0"}, dry_run=dry_run)

    tnames = [t[0] for t in _TABLE_REGISTRY]
    refs   = "\n".join(f"ref table '{n}'" for n in tnames)
    order  = '", "'.join(tnames)
    model_tmdl = (
        "model Model\n\tculture: en-US\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: en-US\n"
        "\tdataAccessOptions\n\t\tlegacyRedirects\n\t\treturnErrorValuesAsNull\n\n"
        f'annotation PBI_QueryOrder = ["{order}"]\n\n{refs}\n'
    )
    write_text(sm_def / "model.tmdl", model_tmdl, dry_run=dry_run)
    write_text(sm_def / "database.tmdl", "database Database\n\tcompatibilityLevel: 1605\n", dry_run=dry_run)
    write_json(sm_def / "diagramLayout.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definition/diagramLayout/1.0.0/schema.json",
        "version": "1.0", "diagrams": [{"name": "Data model"}],
    }, dry_run=dry_run)

    for tname, def_fn, key, lb in _TABLE_REGISTRY:
        cols, msrs = def_fn()
        rows = [r for r in data.get(key, []) if r.get("wave_id") == wave_id]

        if tname == "ComplexityDistribution":
            rows = [
                {
                    "wave_id": row.get("wave_id"),
                    "complexity": row.get("complexity"),
                    "value": row.get("value"),
                    "environment": row.get("environment"),
                    "recorded_at": row.get("recorded_at"),
                    "notes": row.get("notes"),
                }
                for row in data.get("complexity_distribution", [])
                if row.get("wave_id") == wave_id
            ]
        if tname == "MismatchCategories":
            rows = [
                {
                    "wave_id": row.get("wave_id"),
                    "category": row.get("category"),
                    "count": row.get("count"),
                    "environment": row.get("environment"),
                    "recorded_at": row.get("recorded_at"),
                    "notes": row.get("notes"),
                }
                for row in data.get("mismatch_categories", [])
                if row.get("wave_id") == wave_id
            ]
        if tname == "EstimateComparison":
            rows = [
                {"wave_id": row.get("wave_id"), "entity": row.get("entity"), "estimated_rows": row.get("estimated_rows"), "actual_rows": row.get("actual_rows"), "delta": row.get("delta"), "delta_pct": row.get("delta_pct"), "accuracy_pct": row.get("accuracy_pct"), "environment": row.get("environment"), "recorded_at": row.get("recorded_at"), "notes": row.get("notes")}
                for row in data.get("estimate_comparison", [])
                if row.get("wave_id") == wave_id
            ]
        write_text(sm_tables / f"{tname}.tmdl",
                   _build_table_tmdl(tname, cols, msrs, rows, lb), dry_run=dry_run)

    print(f"[OK] SemanticModel TMDL — wave '{wave_id}'")


# ── Report ────────────────────────────────────────────────────────────────────

def _vis(name, pos, vtype, qstate, z=1000, tab=1000):
    v = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
        "name": name,
        "position": {"x": pos["x"], "y": pos["y"], "z": z,
                     "height": pos["height"], "width": pos["width"], "tabOrder": tab},
        "visual": {"visualType": vtype, "drillFilterOtherVisuals": True},
    }
    if qstate:
        v["visual"]["query"] = {"queryState": qstate}
    return v

def _col(e, p): return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": e}}, "Property": p}}, "queryRef": f"{e}.{p}", "active": True}
def _msr(e, p): return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": e}}, "Property": p}}, "queryRef": f"{e}.{p}", "active": True}
def _wv(pg, v, dry): write_json(pg / "visuals" / v["name"] / "visual.json", v, dry_run=dry)


def write_report(rpt_dir, wave_id, dry_run):
    rpt_def = rpt_dir / "definition"
    rpt_pages = rpt_def / "pages"

    write_json(rpt_dir / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": f"{wave_id} DMF Metrics"},
        "config": {"version": "2.0", "logicalId": uid()},
    }, dry_run=dry_run)
    write_json(rpt_dir / "definition.pbir", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../.SemanticModel"}},
    }, dry_run=dry_run)
    write_json(rpt_def / "version.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0",
    }, dry_run=dry_run)
    write_json(rpt_def / "report.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json",
        "themeCollection": {"baseTheme": {"name": "CY24SU06",
            "reportVersionAtImport": {"visual": "1.8.50", "report": "2.0.50", "page": "1.3.50"},
            "type": "SharedResources"}},
        "resourcePackages": [{"name": "SharedResources", "type": "SharedResources",
            "items": [{"name": "CY24SU06", "path": "BaseThemes/CY24SU06.json", "type": "BaseTheme"}]}],
        "settings": {"hideVisualContainerHeader": False, "useStylableVisualContainerHeader": True,
                     "exportDataMode": "None", "defaultDrillFilterOtherVisuals": True,
                     "allowChangeFilterTypes": True, "useEnhancedTooltips": True},
        "annotations": [{"name": "DMF_WaveId", "value": wave_id},
                         {"name": "DMF_GeneratedAt", "value": datetime.now(timezone.utc).isoformat()}],
    }, dry_run=dry_run)

    pages = []
    def mk(folder, display, rank):
        pg = rpt_pages / folder
        write_json(pg / "page.json", {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
            "name": folder, "displayName": display, "displayOption": "FitToPage",
            "height": CANVAS_H, "width": CANVAS_W,
        }, dry_run=dry_run)
        pages.append((folder, display, rank))
        return pg

    p1 = mk("page_exec", "Executive Wave Summary", 0)
    for v in [
        _vis(uid(), px(0,0,6,4),   "card",             {"Values": {"projections": [_msr("WaveSummary","Overall Progress %")]}}),
        _vis(uid(), px(6,0,6,4),   "card",             {"Values": {"projections": [_msr("WaveSummary","Tables Migration %")]}}),
        _vis(uid(), px(12,0,6,4),  "card",             {"Values": {"projections": [_msr("WaveSummary","Pipelines Migration %")]}}),
        _vis(uid(), px(18,0,6,4),  "card",             {"Values": {"projections": [_msr("WaveSummary","Avg Pipeline Time (min)")]}}),
        _vis(uid(), px(0,4,8,4),   "card",             {"Values": {"projections": [_msr("WaveSummary","Tables Remaining")]}}),
        _vis(uid(), px(8,4,8,4),   "card",             {"Values": {"projections": [_msr("WaveSummary","Backlog %")]}}),
        _vis(uid(), px(16,4,8,4),  "card",             {"Values": {"projections": [_msr("WaveSummary","GB Remaining")]}}),
        _vis(uid(), px(0,8,12,4),  "clusteredBarChart",{"Category":{"projections":[_col("WaveSummary","wave_id")]},"Y":{"projections":[_msr("WaveSummary","Tables Migration %"),_msr("WaveSummary","Pipelines Migration %")]}}),
        _vis(uid(), px(12,8,12,4), "gauge",            {"Y": {"projections": [_msr("WaveSummary","Overall Progress %")]}}),
    ]: _wv(p1, v, dry_run)

    p2 = mk("page_gate", "Gate Scorecard", 1)
    for v in [
        _vis(uid(), px(0,0,8,4),  "card",    {"Values": {"projections": [_msr("GateStatus","Gate Score G1")]}}),
        _vis(uid(), px(8,0,8,4),  "card",    {"Values": {"projections": [_msr("GateStatus","Gate Score G2")]}}),
        _vis(uid(), px(16,0,8,4), "card",    {"Values": {"projections": [_msr("GateStatus","Gate Score G3")]}}),
        _vis(uid(), px(0,4,14,8), "tableEx", {"Values": {"projections": [_col("GateStatus","gate"),_col("GateStatus","phase_status"),_col("GateStatus","artifacts_pct"),_col("GateStatus","tasks_pct"),_col("GateStatus","gate_score")]}}),
        _vis(uid(), px(14,4,10,8),"donutChart",{"Category":{"projections":[_col("GateStatus","phase_status")]},"Y":{"projections":[_msr("GateStatus","Gates Complete")]}}),
    ]: _wv(p2, v, dry_run)

    p_est = mk("page_estimates", "Estimate vs Actual", 2)
    for v in [
        _vis(uid(), px(0,0,12,4),  "card", {"Values": {"projections": [_msr("WaveSummary","Wave Estimate Accuracy %")]}}),
        _vis(uid(), px(12,0,12,4), "card", {"Values": {"projections": [_msr("EstimateComparison","Average Accuracy %")]}}),
        _vis(uid(), px(0,4,24,8),  "tableEx", {"Values": {"projections": [_col("EstimateComparison","entity"),_col("EstimateComparison","estimated_rows"),_col("EstimateComparison","actual_rows"),_col("EstimateComparison","delta"),_col("EstimateComparison","delta_pct"),_col("EstimateComparison","accuracy_pct")]}}),
    ]: _wv(p_est, v, dry_run)

    p3 = mk("page_quality", "Quality & Tech Metrics", 3)
    for v in [
        _vis(uid(), px(0,0,6,4),  "card",    {"Values": {"projections": [_msr("GateMetrics","Avg DQ Score")]}}),
        _vis(uid(), px(6,0,6,4),  "card",    {"Values": {"projections": [_msr("GateMetrics","Avg Row Parity")]}}),
        _vis(uid(), px(12,0,6,4), "card",    {"Values": {"projections": [_msr("GateMetrics","Avg Tests Rate")]}}),
        _vis(uid(), px(18,0,6,4), "card",    {"Values": {"projections": [_msr("GateMetrics","Total Rework Count")]}}),
        _vis(uid(), px(0,4,8,4),  "card",    {"Values": {"projections": [_msr("Inventory","Data Accuracy %")]}}),
        _vis(uid(), px(8,4,8,4),  "card",    {"Values": {"projections": [_msr("Inventory","Auto Validated %")]}}),
        _vis(uid(), px(16,4,8,4), "card",    {"Values": {"projections": [_msr("Inventory","Migration Ready %")]}}),
        _vis(uid(), px(0,8,24,4), "tableEx", {"Values": {"projections": [_col("GateMetrics","gate"),_col("GateMetrics","tests_rate"),_col("GateMetrics","dq_score"),_col("GateMetrics","row_parity"),_col("GateMetrics","rejection_rate"),_col("GateMetrics","rework_count")]}}),
    ]: _wv(p3, v, dry_run)

    p_complex = mk("page_complexity", "Complexity Distribution", 4)
    for v in [
        _vis(uid(), px(0,0,12,4), "card", {"Values": {"projections": [_msr("Inventory","Simple %")]}}),
        _vis(uid(), px(12,0,12,4), "card", {"Values": {"projections": [_msr("Inventory","Complex %")]}}),
        _vis(uid(), px(0,4,24,8), "clusteredBarChart", {"Category":{"projections":[_col("ComplexityDistribution","complexity")]},"Y":{"projections":[_msr("ComplexityDistribution","Complexity Count")]}}),
    ]: _wv(p_complex, v, dry_run)

    p4 = mk("page_recon", "Reconciliation & Health", 5)
    for v in [
        _vis(uid(), px(0,0,6,4),  "card",       {"Values": {"projections": [_msr("Reconciliation","Entities PASS")]}}),
        _vis(uid(), px(6,0,6,4),  "card",       {"Values": {"projections": [_msr("Reconciliation","Entities FAIL")]}}),
        _vis(uid(), px(12,0,6,4), "card",       {"Values": {"projections": [_msr("Reconciliation","Parity Rate %")]}}),
        _vis(uid(), px(18,0,6,4), "card",       {"Values": {"projections": [_msr("Reconciliation","Errors per Million")]}}),
        _vis(uid(), px(0,4,14,8), "tableEx",    {"Values": {"projections": [_col("Reconciliation","entity"),_col("Reconciliation","status"),_col("Reconciliation","source_count"),_col("Reconciliation","target_count"),_col("Reconciliation","count_mismatch"),_col("Reconciliation","checksum_mismatch")]}}),
        _vis(uid(), px(14,4,10,8),"donutChart", {"Category":{"projections":[_col("Reconciliation","status")]},"Y":{"projections":[_msr("Reconciliation","Entities PASS")]}}),
    ]: _wv(p4, v, dry_run)

    p_mismatch = mk("page_mismatch", "Mismatch Categories", 6)
    for v in [
        _vis(uid(), px(0,0,12,4), "card", {"Values": {"projections": [_msr("MismatchCategories","Mismatch Count")]}}),
        _vis(uid(), px(0,4,24,8), "clusteredBarChart", {"Category":{"projections":[_col("MismatchCategories","category")]},"Y":{"projections":[_msr("MismatchCategories","Mismatch Count")]}}),
    ]: _wv(p_mismatch, v, dry_run)

    p5 = mk("page_bench", "Performance & Benchmarks", 7)
    for v in [
        _vis(uid(), px(0,0,8,4),   "card",                {"Values": {"projections": [_msr("Benchmarks","Avg Throughput GB/day")]}}),
        _vis(uid(), px(8,0,8,4),   "card",                {"Values": {"projections": [_msr("Benchmarks","Avg Rows/sec")]}}),
        _vis(uid(), px(16,0,8,4),  "card",                {"Values": {"projections": [_msr("Benchmarks","Benchmarks PASS")]}}),
        _vis(uid(), px(0,4,12,4),  "card",                {"Values": {"projections": [_msr("Benchmarks","Processing Time / GB")]}}),
        _vis(uid(), px(12,4,12,4), "card",                {"Values": {"projections": [_msr("Benchmarks","Lead Time (min)")]}}),
        _vis(uid(), px(0,8,12,4),  "clusteredColumnChart",{"Category":{"projections":[_col("Benchmarks","entity")]},"Y":{"projections":[_msr("Benchmarks","Avg Rows/sec"),_msr("Benchmarks","Avg Throughput GB/day")]}}),
        _vis(uid(), px(12,8,12,4), "tableEx",             {"Values": {"projections": [_col("Benchmarks","entity"),_col("Benchmarks","status"),_col("Benchmarks","rows_processed"),_col("Benchmarks","duration_seconds"),_col("Benchmarks","throughput_gb_per_day")]}}),
    ]: _wv(p5, v, dry_run)

    ps = sorted(pages, key=lambda x: x[2])
    write_json(rpt_pages / "pages.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p[0] for p in ps], "activePageName": ps[0][0],
    }, dry_run=dry_run)
    print(f"[OK] Report — {len(pages)} páginas — wave '{wave_id}'")


# ── Public API ───────────────────────────────────────────────────────────────

def generate(
    metrics_path: Path,
    output_dir: Path,
    wave_filter: str | None = None,
    dry_run: bool = False,
) -> Path:
    """
    Generates .pbip with embedded data. Called by Bianca at the end of Gate 3.

    Example:
        from src.shared.scripts.generate_pbi_report import generate
        pbip = generate(
            metrics_path=Path("projects/<project-name>/outputs/summary/metrics_registry.json"),
            output_dir=Path("projects/<project-name>/outputs/downstream/bi/"),
            wave_filter="WAVE-001",
        )
    """
    sep = "=" * 60
    print(f"\n{sep}\nDMF v3 | generate_pbi_report.py\n  metrics: {metrics_path}\n  output : {output_dir}\n{sep}\n")

    data    = load_metrics(metrics_path)
    wave_id = resolve_wave_id(data, wave_filter)
    print(f"Wave: {wave_id}\n")

    safe      = wave_id.replace("/", "-").replace("\\", "-")
    pbip_root = output_dir / f"{safe}.pbip"

    if pbip_root.exists() and not dry_run:
        shutil.rmtree(pbip_root)

    write_semantic_model(pbip_root / ".SemanticModel", data, wave_id, dry_run)
    write_report(pbip_root / ".Report", wave_id, dry_run)

    write_json(pbip_root / f"{safe}.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": ".Report"}}],
    }, dry_run=dry_run)

    if not dry_run:
        (pbip_root / ".gitignore").write_text("*.pbix\n.pbi/localSettings.json\n")

    print(f"\n{sep}\n✅ PBIP: {pbip_root}\n   → Sem configuração de fonte de dados!\n{sep}\n")
    return pbip_root


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="DMF v3 — Gera .pbip com dados embutidos")
    ap.add_argument("--metrics",      required=True)
    ap.add_argument("--output",       required=True)
    ap.add_argument("--wave",         default=None)
    ap.add_argument("--dry-run",      action="store_true")
    a = ap.parse_args()
    generate(Path(a.metrics), Path(a.output), a.wave, a.dry_run)


if __name__ == "__main__":
    main()