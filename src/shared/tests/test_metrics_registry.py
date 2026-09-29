"""
test_metrics_registry.py

Unit tests for metrics_registry.py

Tests the generic unified migration metrics registry:
- MetricRecord validation
- MetricsRegistry record methods
- Object/dataclass serialization
- JSONL persistence and reload
- Raw JSON export
- Power BI-friendly JSON export
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pytest

from scripts.metrics_registry import (
    MetricRecord,
    MetricsRegistry,
    object_to_dict,
)


class DummyEnum(Enum):
    """Enum used to validate serialization behavior."""

    PASSED = "passed"
    FAILED = "failed"


@dataclass
class DummyDataclassReport:
    """Dataclass used to validate object_to_dict and record_object."""

    wave_id: str
    status: str
    score: float
    output_path: Path
    result: DummyEnum


class DummyPlainObject:
    """Plain object used to validate object_to_dict fallback."""

    def __init__(self) -> None:
        self.wave_id = "WAVE-PLAIN"
        self.tables_total = 10
        self.tables_migrated = 8
        self._internal_field = "should_not_be_exported"


class DummyToDictReport:
    """Object with to_dict() used to validate preferred conversion path."""

    def to_dict(self) -> dict:
        return {
            "wave_id": "WAVE-TODICT",
            "metric": "benchmark",
            "duration_min": 12.5,
            "status": DummyEnum.PASSED,
            "path": Path("outputs/report.json"),
        }


class DummyGateScoreReport:
    """GateScoreReport-like object used by record_gate_report."""

    def __init__(self) -> None:
        self.wave_id = "WAVE-001"
        self.gate = 2
        self.tests_rate = 0.87
        self.dq_score = 0.82
        self.row_parity = 0.90


@dataclass
class DummyWaveStatusSummary:
    """WaveStatusSummary-like object used by record_wave_status."""

    wave_id: str
    overall_pct: float
    tables_migrated: int
    tables_total: int
    tables_pct: float
    pipelines_migrated: int
    pipelines_total: int
    pipelines_pct: float
    avg_pipeline_time_minutes: float
    gates: list[dict]


@dataclass
class DummyBenchmarkReport:
    """BenchmarkReport-like object used by record_benchmark."""

    wave_id: str
    pipeline_name: str
    avg_runtime_minutes: float
    throughput_gb_day: float


@dataclass
class DummyReconciliationReport:
    """ReconciliationReport-like object used by record_reconciliation."""

    source_rows: int
    target_rows: int
    row_parity: float
    mismatch_count: int


def test_metric_record_valid_payload():
    """Test creating a valid MetricRecord."""

    record = MetricRecord(
        wave_id="WAVE-001",
        metric_type="gate",
        data={
            "gate": 2,
            "tests_rate": 0.87,
            "dq_score": 0.82,
            "row_parity": 0.90,
        },
        environment="UAT",
        notes="Test metric",
    )

    assert record.wave_id == "WAVE-001"
    assert record.metric_type == "gate"
    assert record.data["gate"] == 2
    assert record.environment == "UAT"
    assert record.notes == "Test metric"
    assert record.schema_version == "1.0"
    assert record.recorded_at is not None


def test_metric_record_requires_wave_id():
    """Test MetricRecord validation for required wave_id."""

    with pytest.raises(ValueError, match="wave_id is required"):
        MetricRecord(
            wave_id="",
            metric_type="gate",
            data={"gate": 1},
        )


def test_metric_record_requires_metric_type():
    """Test MetricRecord validation for required metric_type."""

    with pytest.raises(ValueError, match="metric_type is required"):
        MetricRecord(
            wave_id="WAVE-001",
            metric_type="",
            data={"gate": 1},
        )


def test_metric_record_requires_data_dict():
    """Test MetricRecord validation for data type."""

    with pytest.raises(TypeError, match="data must be a dictionary"):
        MetricRecord(
            wave_id="WAVE-001",
            metric_type="gate",
            data=["invalid"],  # type: ignore[arg-type]
        )


def test_metric_record_normalizes_non_json_native_values():
    """Test normalization of Enum, Path, dataclass and nested values."""

    nested_report = DummyDataclassReport(
        wave_id="WAVE-001",
        status="completed",
        score=0.95,
        output_path=Path("outputs/result.json"),
        result=DummyEnum.PASSED,
    )

    record = MetricRecord(
        wave_id="WAVE-001",
        metric_type="custom",
        data={
            "status": DummyEnum.PASSED,
            "path": Path("outputs/metrics.json"),
            "nested": nested_report,
            "items": [
                DummyEnum.FAILED,
                Path("outputs/item.json"),
                {"result": DummyEnum.PASSED},
            ],
        },
    )

    assert record.data["status"] == "passed"
    assert Path(record.data["path"]) == Path("outputs/metrics.json")

    assert record.data["nested"]["wave_id"] == "WAVE-001"
    assert Path(record.data["nested"]["output_path"]) == Path("outputs/result.json")
    assert record.data["nested"]["result"] == "passed"

    assert record.data["items"][0] == "failed" 
    assert Path(record.data["items"][1]) == Path("outputs/item.json")
    assert record.data["items"][2]["result"] == "passed"


def test_record_single_metric():
    """Test recording a single generic metric."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        result = registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={
                "gate": 2,
                "tests_rate": 0.87,
                "dq_score": 0.82,
                "row_parity": 0.90,
                "rejection_rate": 0.33,
                "rework_count": 2,
                "rework_time_min": 90,
            },
            environment="UAT",
            notes="Gate 2 test",
        )

        assert isinstance(result, MetricRecord)
        assert len(registry.get_all()) == 1
        assert registry.count() == 1
        assert registry_path.exists()

        stored = registry.get_all()[0]
        assert stored.wave_id == "WAVE-001"
        assert stored.metric_type == "gate"
        assert stored.environment == "UAT"
        assert stored.notes == "Gate 2 test"
        assert stored.data["rejection_rate"] == 0.33
        assert stored.data["rework_count"] == 2
        assert stored.data["rework_time_min"] == 90


def test_jsonl_file_contains_one_line_per_record():
    """Test append-only JSONL persistence format."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1, "tests_rate": 0.80},
        )
        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 2, "tests_rate": 0.90},
        )

        with open(registry_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 2

        first_line = json.loads(lines[0])
        second_line = json.loads(lines[1])

        assert first_line["wave_id"] == "WAVE-001"
        assert first_line["metric_type"] == "gate"
        assert first_line["data"]["gate"] == 1

        assert second_line["wave_id"] == "WAVE-001"
        assert second_line["metric_type"] == "gate"
        assert second_line["data"]["gate"] == 2


def test_get_by_wave():
    """Test filtering records by wave_id."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1},
        )
        registry.record(
            wave_id="WAVE-001",
            metric_type="benchmark",
            data={"duration_min": 12.5},
        )
        registry.record(
            wave_id="WAVE-002",
            metric_type="gate",
            data={"gate": 1},
        )

        wave_records = registry.get_by_wave("WAVE-001")

        assert len(wave_records) == 2
        assert all(record.wave_id == "WAVE-001" for record in wave_records)


def test_get_by_type():
    """Test filtering records by metric_type."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1},
        )
        registry.record(
            wave_id="WAVE-002",
            metric_type="gate",
            data={"gate": 2},
        )
        registry.record(
            wave_id="WAVE-001",
            metric_type="benchmark",
            data={"duration_min": 12.5},
        )

        gate_records = registry.get_by_type("gate")

        assert len(gate_records) == 2
        assert all(record.metric_type == "gate" for record in gate_records)


def test_get_by_wave_and_type():
    """Test filtering records by wave_id and metric_type."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1},
        )
        registry.record(
            wave_id="WAVE-001",
            metric_type="benchmark",
            data={"duration_min": 12.5},
        )
        registry.record(
            wave_id="WAVE-002",
            metric_type="gate",
            data={"gate": 2},
        )

        records = registry.get_by_wave_and_type(
            wave_id="WAVE-001",
            metric_type="gate",
        )

        assert len(records) == 1
        assert records[0].wave_id == "WAVE-001"
        assert records[0].metric_type == "gate"
        assert records[0].data["gate"] == 1


def test_object_to_dict_with_dict():
    """Test object_to_dict with an existing dictionary."""

    payload = {
        "status": DummyEnum.PASSED,
        "path": Path("outputs/test.json"),
        "nested": {
            "result": DummyEnum.FAILED,
        },
    }

    result = object_to_dict(payload)

    assert result["status"] == "passed"
    assert Path(result["path"]) == Path("outputs/test.json")
    assert result["nested"]["result"] == "failed"


def test_object_to_dict_with_to_dict_method():
    """Test object_to_dict prefers to_dict() when available."""

    report = DummyToDictReport()

    result = object_to_dict(report)

    assert result["wave_id"] == "WAVE-TODICT"
    assert result["metric"] == "benchmark"
    assert result["duration_min"] == 12.5
    assert result["status"] == "passed"
    assert Path(result["path"]) == Path("outputs/report.json")


def test_object_to_dict_with_dataclass():
    """Test object_to_dict with dataclass objects."""

    report = DummyDataclassReport(
        wave_id="WAVE-001",
        status="completed",
        score=0.95,
        output_path=Path("outputs/result.json"),
        result=DummyEnum.PASSED,
    )

    result = object_to_dict(report)

    assert result["wave_id"] == "WAVE-001"
    assert result["status"] == "completed"
    assert result["score"] == 0.95
    assert Path(result["output_path"]) == Path("outputs/result.json")
    assert result["result"] == "passed"


def test_object_to_dict_with_plain_object():
    """Test object_to_dict fallback for plain Python objects."""

    result = object_to_dict(DummyPlainObject())

    assert result["wave_id"] == "WAVE-PLAIN"
    assert result["tables_total"] == 10
    assert result["tables_migrated"] == 8
    assert "_internal_field" not in result


def test_object_to_dict_invalid_type():
    """Test object_to_dict raises TypeError for unsupported objects."""

    with pytest.raises(TypeError, match="Cannot convert object"):
        object_to_dict(123)


def test_record_object_from_dataclass():
    """Test recording a metric from a dataclass/report object."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        report = DummyDataclassReport(
            wave_id="WAVE-001",
            status="completed",
            score=0.95,
            output_path=Path("outputs/result.json"),
            result=DummyEnum.PASSED,
        )

        result = registry.record_object(
            wave_id="WAVE-001",
            metric_type="custom_report",
            obj=report,
            environment="DEV",
        )

        assert isinstance(result, MetricRecord)
        assert result.metric_type == "custom_report"
        assert result.data["score"] == 0.95
        assert Path(result.data["output_path"]) == Path("outputs/result.json")

        assert result.data["result"] == "passed"
        assert len(registry.get_all()) == 1


def test_record_gate_report():
    """Test recording a GateScoreReport-like object."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        report = DummyGateScoreReport()

        result = registry.record_gate_report(
            report=report,
            rejection_rate=0.10,
            rework_count=2,
            rework_time_min=45.0,
            environment="UAT",
            notes="Gate report test",
        )

        assert isinstance(result, MetricRecord)
        assert result.wave_id == "WAVE-001"
        assert result.metric_type == "gate"
        assert result.environment == "UAT"
        assert result.notes == "Gate report test"

        assert result.data["gate"] == 2
        assert result.data["tests_rate"] == 0.87
        assert result.data["dq_score"] == 0.82
        assert result.data["row_parity"] == 0.90
        assert result.data["rejection_rate"] == 0.10
        assert result.data["rework_count"] == 2
        assert result.data["rework_time_min"] == 45.0


def test_record_wave_status_without_gates():
    """Test recording a wave status summary without nested gates."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        summary = {
            "wave_id": "WAVE-001",
            "overall_pct": 75.0,
            "tables_migrated": 12,
            "tables_total": 20,
            "tables_pct": 60.0,
            "pipelines_migrated": 5,
            "pipelines_total": 8,
            "pipelines_pct": 62.5,
            "avg_pipeline_time_minutes": 14.2,
        }

        result = registry.record_wave_status(summary)

        assert isinstance(result, MetricRecord)
        assert result.wave_id == "WAVE-001"
        assert result.metric_type == "wave_status"
        assert result.data["overall_pct"] == 75.0
        assert "gates" not in result.data
        assert len(registry.get_all()) == 1


def test_record_wave_status_with_nested_gates_creates_gate_status_records():
    """Test wave status recording also records nested gate_status records."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        summary = DummyWaveStatusSummary(
            wave_id="WAVE-001",
            overall_pct=75.0,
            tables_migrated=12,
            tables_total=20,
            tables_pct=60.0,
            pipelines_migrated=5,
            pipelines_total=8,
            pipelines_pct=62.5,
            avg_pipeline_time_minutes=14.2,
            gates=[
                {
                    "gate": 1,
                    "status": "completed",
                    "tasks_completed": 10,
                    "tasks_total": 10,
                },
                {
                    "gate": 2,
                    "status": "in_progress",
                    "tasks_completed": 6,
                    "tasks_total": 10,
                },
            ],
        )

        result = registry.record_wave_status(summary)

        assert isinstance(result, MetricRecord)
        assert result.metric_type == "wave_status"

        all_records = registry.get_all()
        assert len(all_records) == 3

        wave_status_records = registry.get_by_type("wave_status")
        gate_status_records = registry.get_by_type("gate_status")

        assert len(wave_status_records) == 1
        assert len(gate_status_records) == 2

        assert "gates" not in wave_status_records[0].data
        assert gate_status_records[0].data["gate"] == 1
        assert gate_status_records[1].data["gate"] == 2
        assert gate_status_records[0].notes == "Auto-recorded from wave status summary"


def test_record_benchmark():
    """Test recording a BenchmarkReport-like object."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        report = DummyBenchmarkReport(
            wave_id="WAVE-001",
            pipeline_name="pipeline_customer_migration",
            avg_runtime_minutes=18.5,
            throughput_gb_day=120.0,
        )

        result = registry.record_benchmark(
            report=report,
            environment="PROD",
            notes="Benchmark test",
        )

        assert isinstance(result, MetricRecord)
        assert result.wave_id == "WAVE-001"
        assert result.metric_type == "benchmark"
        assert result.environment == "PROD"
        assert result.notes == "Benchmark test"
        assert result.data["pipeline_name"] == "pipeline_customer_migration"
        assert result.data["avg_runtime_minutes"] == 18.5
        assert result.data["throughput_gb_day"] == 120.0


def test_record_reconciliation():
    """Test recording a ReconciliationReport-like object."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        report = DummyReconciliationReport(
            source_rows=1000,
            target_rows=995,
            row_parity=0.995,
            mismatch_count=5,
        )

        result = registry.record_reconciliation(
            report=report,
            wave_id="WAVE-001",
            environment="UAT",
        )

        assert isinstance(result, MetricRecord)
        assert result.wave_id == "WAVE-001"
        assert result.metric_type == "reconciliation"
        assert result.environment == "UAT"
        assert result.data["source_rows"] == 1000
        assert result.data["target_rows"] == 995
        assert result.data["row_parity"] == 0.995
        assert result.data["mismatch_count"] == 5


def test_record_inventory_metric():
    """Test recording inventory-derived metrics."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        result = registry.record_inventory_metric(
            wave_id="WAVE-001",
            data={
                "total_tables": 20,
                "total_pipelines": 8,
                "total_volume_gb": 450.5,
                "avg_table_size_gb": 22.5,
            },
            environment="DEV",
            notes="Inventory test",
        )

        assert isinstance(result, MetricRecord)
        assert result.wave_id == "WAVE-001"
        assert result.metric_type == "inventory"
        assert result.data["total_tables"] == 20
        assert result.data["total_pipelines"] == 8
        assert result.data["total_volume_gb"] == 450.5
        assert result.data["avg_table_size_gb"] == 22.5
        assert result.notes == "Inventory test"


def test_export_json():
    """Test raw JSON export functionality."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={
                "gate": 2,
                "tests_rate": 0.87,
                "dq_score": 0.82,
                "row_parity": 0.90,
            },
        )

        json_path = Path(tmpdir) / "metrics.json"
        registry.export_json(json_path)

        assert json_path.exists()

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["schema_version"] == "1.0"
        assert data["total_records"] == 1
        assert "exported_at" in data
        assert "records" in data
        assert len(data["records"]) == 1

        record = data["records"][0]
        assert record["wave_id"] == "WAVE-001"
        assert record["metric_type"] == "gate"
        assert record["data"]["gate"] == 2
        assert record["data"]["tests_rate"] == 0.87


def test_export_powerbi_json_groups_records_by_metric_type():
    """Test Power BI JSON export groups records into table-like arrays."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="wave_status",
            data={
                "overall_pct": 75.0,
                "tables_migrated": 12,
                "tables_total": 20,
            },
        )

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={
                "gate": 2,
                "tests_rate": 0.87,
                "dq_score": 0.82,
                "row_parity": 0.90,
            },
        )

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate_status",
            data={
                "gate": 2,
                "status": "completed",
                "tasks_completed": 10,
                "tasks_total": 10,
            },
        )

        registry.record(
            wave_id="WAVE-001",
            metric_type="benchmark",
            data={
                "pipeline_name": "pipeline_customer_migration",
                "avg_runtime_minutes": 18.5,
            },
        )

        registry.record(
            wave_id="WAVE-001",
            metric_type="reconciliation",
            data={
                "source_rows": 1000,
                "target_rows": 995,
                "row_parity": 0.995,
            },
        )

        registry.record(
            wave_id="WAVE-001",
            metric_type="inventory",
            data={
                "total_tables": 20,
                "total_pipelines": 8,
            },
        )

        registry.record(
            wave_id="WAVE-001",
            metric_type="custom_metric",
            data={
                "custom_value": 123,
            },
        )

        powerbi_path = Path(tmpdir) / "powerbi_metrics.json"
        registry.export_powerbi_json(powerbi_path)

        assert powerbi_path.exists()

        with open(powerbi_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["schema_version"] == "1.0"
        assert "exported_at" in data

        assert len(data["wave_summary"]) == 1
        assert len(data["gate_metrics"]) == 1
        assert len(data["gate_status"]) == 1
        assert len(data["benchmarks"]) == 1
        assert len(data["reconciliation"]) == 1
        assert len(data["inventory"]) == 1
        assert len(data["other_metrics"]) == 1

        assert data["wave_summary"][0]["wave_id"] == "WAVE-001"
        assert data["wave_summary"][0]["overall_pct"] == 75.0

        assert data["gate_metrics"][0]["gate"] == 2
        assert data["gate_metrics"][0]["tests_rate"] == 0.87

        assert data["gate_status"][0]["status"] == "completed"

        assert data["benchmarks"][0]["pipeline_name"] == "pipeline_customer_migration"

        assert data["reconciliation"][0]["row_parity"] == 0.995

        assert data["inventory"][0]["total_tables"] == 20

        assert data["other_metrics"][0]["metric_type"] == "custom_metric"
        assert data["other_metrics"][0]["custom_value"] == 123


def test_powerbi_payload_contains_common_metadata_fields():
    """Test every Power BI payload receives common metadata fields."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1},
            environment="UAT",
            notes="Metadata test",
        )

        powerbi_path = Path(tmpdir) / "powerbi_metrics.json"
        registry.export_powerbi_json(powerbi_path)

        with open(powerbi_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        payload = data["gate_metrics"][0]

        assert payload["wave_id"] == "WAVE-001"
        assert payload["environment"] == "UAT"
        assert payload["notes"] == "Metadata test"
        assert "recorded_at" in payload


def test_persistence_reload():
    """Test that metrics persist across registry instances."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"

        registry1 = MetricsRegistry(registry_path)
        registry1.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={
                "gate": 2,
                "tests_rate": 0.87,
                "dq_score": 0.82,
                "row_parity": 0.90,
                "rejection_rate": 0.33,
                "rework_count": 2,
                "rework_time_min": 90,
            },
            environment="UAT",
            notes="Reload test",
        )

        registry2 = MetricsRegistry(registry_path)

        assert len(registry2.get_all()) == 1

        reloaded = registry2.get_all()[0]

        assert reloaded.wave_id == "WAVE-001"
        assert reloaded.metric_type == "gate"
        assert reloaded.environment == "UAT"
        assert reloaded.notes == "Reload test"
        assert reloaded.data["gate"] == 2
        assert reloaded.data["tests_rate"] == 0.87
        assert reloaded.data["dq_score"] == 0.82
        assert reloaded.data["row_parity"] == 0.90
        assert reloaded.data["rejection_rate"] == 0.33
        assert reloaded.data["rework_count"] == 2
        assert reloaded.data["rework_time_min"] == 90


def test_clear_memory_does_not_delete_jsonl_file():
    """Test clear_memory clears only in-memory records, not persisted file."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"
        registry = MetricsRegistry(registry_path)

        registry.record(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1},
        )

        assert registry.count() == 1
        assert registry_path.exists()

        registry.clear_memory()

        assert registry.count() == 0
        assert registry_path.exists()

        reloaded_registry = MetricsRegistry(registry_path)

        assert reloaded_registry.count() == 1
        assert reloaded_registry.get_all()[0].wave_id == "WAVE-001"


def test_load_ignores_empty_lines():
    """Test _load ignores empty lines in JSONL file."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"

        valid_record = MetricRecord(
            wave_id="WAVE-001",
            metric_type="gate",
            data={"gate": 1},
        )

        with open(registry_path, "w", encoding="utf-8") as f:
            f.write("\n")
            f.write(json.dumps(valid_record.to_dict(), ensure_ascii=False) + "\n")
            f.write("\n")

        registry = MetricsRegistry(registry_path)

        assert registry.count() == 1
        assert registry.get_all()[0].wave_id == "WAVE-001"


def test_load_invalid_json_does_not_raise():
    """Test invalid JSONL content does not raise during registry initialization."""

    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "metrics.jsonl"

        with open(registry_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        registry = MetricsRegistry(registry_path)

        assert registry.count() == 0