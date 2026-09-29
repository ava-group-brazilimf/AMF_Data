"""
metrics_registry.py
B-016 — Unified Migration Metrics Registry.

Persists migration metrics for dashboard consumption.

This registry is generic and can store multiple metric types, such as:
    - gate metrics
    - benchmark metrics
    - wave status metrics
    - reconciliation metrics
    - inventory metrics

Storage:
    - JSON Lines (.jsonl) for append-only historical records
    - Consolidated JSON for Power BI consumption

Recommended metric types:
    - "gate"
    - "benchmark"
    - "wave_status"
    - "reconciliation"
    - "inventory"

Usage:
    from scripts.metrics_registry import MetricsRegistry

    registry = MetricsRegistry("outputs/metrics/migration_metrics.jsonl")

    registry.record(
        wave_id="WAVE-001",
        metric_type="gate",
        data={
            "gate": 2,
            "tests_rate": 0.87,
            "dq_score": 0.82,
            "row_parity": 0.90,
            "rejection_rate": 0.03,
            "rework_count": 1,
            "rework_time_min": 45.0,
        },
    )

    registry.record(
        wave_id="WAVE-001",
        metric_type="wave_status",
        data={
            "overall_pct": 75.0,
            "tables_migrated": 12,
            "tables_total": 20,
            "tables_pct": 60.0,
            "pipelines_migrated": 5,
            "pipelines_total": 8,
            "pipelines_pct": 62.5,
            "avg_pipeline_time_minutes": 14.2,
        },
    )

    registry.export_powerbi_json("outputs/metrics/powerbi_metrics.json")
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional



def _utc_now() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _serialize_value(value: Any) -> Any:
    """Serialize values that are not JSON-native by default."""
    if isinstance(value, Enum):
        return value.value

    
    if is_dataclass(value):
        return _normalize_payload(asdict(value))


    if isinstance(value, Path):
        return str(value)

    return value


def _normalize_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize a metric payload to make it JSON serializable."""
    normalized: dict[str, Any] = {}

    for key, value in data.items():
        if isinstance(value, dict):
            normalized[key] = _normalize_payload(value)

        elif isinstance(value, list):
            normalized[key] = [
                _serialize_value(item)
                if not isinstance(item, dict)
                else _normalize_payload(item)
                for item in value
            ]

        else:
            normalized[key] = _serialize_value(value)

    return normalized


def object_to_dict(obj: Any) -> dict[str, Any]:
    """Convert dataclasses or plain objects into dictionary payloads.

    This helper is useful for reports such as:
        - BenchmarkReport
        - WaveStatusSummary
        - ReconciliationReport
        - GatePerformanceMetric-like objects

    If the object already has a `to_dict()` method, that method is used.
    """
    if isinstance(obj, dict):
        return _normalize_payload(obj)

    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return _normalize_payload(obj.to_dict())

    if is_dataclass(obj):
        return _normalize_payload(asdict(obj))

    # Fallback for plain Python objects with attributes.
    if hasattr(obj, "__dict__"):
        return _normalize_payload(
            {
                key: value
                for key, value in vars(obj).items()
                if not key.startswith("_")
            }
        )

    raise TypeError(f"Cannot convert object of type {type(obj)!r} to dict")


@dataclass
class MetricRecord:
    """Generic metric record for migration dashboard consumption.

    This is intentionally generic:
    - `metric_type` defines what kind of metric is being stored.
    - `data` contains the metric-specific fields.
    """

    wave_id: str
    metric_type: str
    data: dict[str, Any]

    recorded_at: str = field(default_factory=_utc_now)
    environment: str = "DEV"
    schema_version: str = "1.0"
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.wave_id:
            raise ValueError("wave_id is required")

        if not self.metric_type:
            raise ValueError("metric_type is required")

        if not isinstance(self.data, dict):
            raise TypeError("data must be a dictionary")

        self.data = _normalize_payload(self.data)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        return asdict(self)



class MetricsRegistry:
    """Generic registry for migration metrics with JSONL persistence.

    The registry stores raw metric records in JSON Lines format and can export
    a Power BI-friendly JSON grouped into table-like arrays.
    """

    def __init__(self, registry_path: str | Path):
        """Initialize registry.

        Args:
            registry_path: Path to a JSONL file.
        """
        self.path = Path(registry_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: list[MetricRecord] = []
        self._load()


    def _load(self) -> None:
        """Load existing metrics from JSONL file."""
        if not self.path.exists():
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        record = MetricRecord(**data)
                        self.records.append(record)

        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load metrics from {self.path}: {e}")

    def record(
        self,
        wave_id: str,
        metric_type: str,
        data: dict[str, Any],
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record a new metric payload.

        Args:
            wave_id: Migration wave identifier.
            metric_type: Metric category, e.g. "gate", "benchmark", "wave_status".
            data: Metric-specific payload.
            environment: DEV, UAT, PROD, etc.
            notes: Optional notes.

        Returns:
            MetricRecord persisted in JSONL.
        """
        record = MetricRecord(
            wave_id=wave_id,
            metric_type=metric_type,
            data=data,
            environment=environment,
            notes=notes,
        )

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

        self.records.append(record)
        return record

    def record_object(
        self,
        wave_id: str,
        metric_type: str,
        obj: Any,
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record a metric from a dataclass/report object.

        Useful for:
            - BenchmarkReport
            - WaveStatusSummary
            - ReconciliationReport
        """
        return self.record(
            wave_id=wave_id,
            metric_type=metric_type,
            data=object_to_dict(obj),
            environment=environment,
            notes=notes,
        )


    def record_gate_report(
        self,
        report: Any,
        rejection_rate: float = 0.0,
        rework_count: int = 0,
        rework_time_min: float = 0.0,
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record gate metrics from a GateScoreReport-like object.

        Expected report attributes:
            - wave_id
            - gate
            - tests_rate
            - dq_score
            - row_parity
        """
        data = {
            "gate": report.gate,
            "tests_rate": report.tests_rate,
            "dq_score": report.dq_score,
            "row_parity": report.row_parity,
            "rejection_rate": rejection_rate,
            "rework_count": rework_count,
            "rework_time_min": rework_time_min,
        }

        return self.record(
            wave_id=report.wave_id,
            metric_type="gate",
            data=data,
            environment=environment,
            notes=notes,
        )

    def record_wave_status(
        self,
        summary: Any,
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record a WaveStatusSummary-like object."""
        data = object_to_dict(summary)

        # Remove nested gate objects from wave-level summary if present.
        # Gate/task details should go into `gate_status` records.
        gates = data.pop("gates", None)

        record = self.record(
            wave_id=data["wave_id"],
            metric_type="wave_status",
            data=data,
            environment=environment,
            notes=notes,
        )

        if gates:
            for gate in gates:
                self.record(
                    wave_id=data["wave_id"],
                    metric_type="gate_status",
                    data=gate,
                    environment=environment,
                    notes="Auto-recorded from wave status summary",
                )

        return record

    def record_benchmark(
        self,
        report: Any,
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record a BenchmarkReport-like object."""
        data = object_to_dict(report)

        return self.record(
            wave_id=data["wave_id"],
            metric_type="benchmark",
            data=data,
            environment=environment,
            notes=notes,
        )

    def record_reconciliation(
        self,
        report: Any,
        wave_id: str,
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record a ReconciliationReport-like object.

        ReconciliationReport may not contain wave_id, so wave_id is passed
        explicitly.
        """
        data = object_to_dict(report)

        return self.record(
            wave_id=wave_id,
            metric_type="reconciliation",
            data=data,
            environment=environment,
            notes=notes,
        )

    def record_inventory_metric(
        self,
        wave_id: str,
        data: dict[str, Any],
        environment: str = "DEV",
        notes: Optional[str] = None,
    ) -> MetricRecord:
        """Record inventory-derived metrics.

        Examples:
            - total tables
            - total pipelines
            - avg table size
            - total volume
        """
        return self.record(
            wave_id=wave_id,
            metric_type="inventory",
            data=data,
            environment=environment,
            notes=notes,
        )


    def get_all(self) -> list[MetricRecord]:
        """Return all recorded metric records."""
        return self.records.copy()

    def get_by_wave(self, wave_id: str) -> list[MetricRecord]:
        """Return all records for one wave."""
        return [
            record
            for record in self.records
            if record.wave_id == wave_id
        ]

    def get_by_type(self, metric_type: str) -> list[MetricRecord]:
        """Return all records for one metric type."""
        return [
            record
            for record in self.records
            if record.metric_type == metric_type
        ]

    def get_by_wave_and_type(
        self,
        wave_id: str,
        metric_type: str,
    ) -> list[MetricRecord]:
        """Return all records for one wave and metric type."""
        return [
            record
            for record in self.records
            if record.wave_id == wave_id and record.metric_type == metric_type
        ]


    def export_json(self, json_path: str | Path) -> None:
        """Export raw records as a single JSON file.

        This preserves the generic metric envelope:
            - wave_id
            - metric_type
            - data
            - recorded_at
            - environment
        """
        json_path = Path(json_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "schema_version": "1.0",
            "total_records": len(self.records),
            "exported_at": _utc_now(),
            "records": [record.to_dict() for record in self.records],
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(self.records)} raw metric records to {json_path}")

    def export_powerbi_json(self, json_path: str | Path) -> None:
        """Export records grouped into Power BI-friendly table arrays.

        Each top-level array can be imported into Power BI as a table:
            - wave_summary
            - gate_metrics
            - gate_status
            - benchmarks
            - reconciliation
            - inventory
        """
        json_path = Path(json_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "schema_version": "1.0",
            "exported_at": _utc_now(),
            "wave_summary": [],
            "gate_metrics": [],
            "gate_status": [],
            "benchmarks": [],
            "reconciliation": [],
            "inventory": [],
            "other_metrics": [],
        }

        for record in self.records:
            payload = {
                **record.data,
                "wave_id": record.wave_id,
                "environment": record.environment,
                "recorded_at": record.recorded_at,
                "notes": record.notes,
            }

            if record.metric_type == "wave_status":
                data["wave_summary"].append(payload)

            elif record.metric_type == "gate":
                data["gate_metrics"].append(payload)

            elif record.metric_type == "gate_status":
                data["gate_status"].append(payload)

            elif record.metric_type == "benchmark":
                data["benchmarks"].append(payload)

            elif record.metric_type == "reconciliation":
                data["reconciliation"].append(payload)

            elif record.metric_type == "inventory":
                data["inventory"].append(payload)

            else:
                data["other_metrics"].append(
                    {
                        "metric_type": record.metric_type,
                        **payload,
                    }
                )

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported Power BI metrics JSON to {json_path}")



    def clear_memory(self) -> None:
        """Clear in-memory records only. Does not delete the JSONL file."""
        self.records.clear()

    def count(self) -> int:
        """Return number of loaded records."""
        return len(self.records)