"""
test_lineage_engine.py — Tests for Lineage Engine (Trilha 4)
"""
import json
import pytest

from src.shared.pipeline_ast.model.canonical import (
    DataType,
    MigrationColumn,
    MigrationPipeline,
    MigrationTable,
    MigrationTransformation,
    TransformationType,
)
from src.shared.pipeline_ast.lineage.lineage_engine import LineageEngine, LineageReport


def _make_pipeline_with_lineage() -> MigrationPipeline:
    src_col = MigrationColumn(column_id="sc1", name="amount", data_type=DataType.DECIMAL)
    src = MigrationTable(table_id="orders", schema_name="dbo", table_name="orders", columns=[src_col])
    tgt_col = MigrationColumn(column_id="tc1", name="total_amount", data_type=DataType.DECIMAL)
    tgt = MigrationTable(table_id="target", schema_name="", table_name="target", columns=[tgt_col])
    tr = MigrationTransformation(
        transformation_id="tr1",
        transformation_type=TransformationType.EXPRESSION,
        source_columns=["orders.amount"],
        target_column="target.total_amount",
        expression="SUM(amount)",
        confidence=0.9,
    )
    return MigrationPipeline(
        pipeline_id="pip1",
        pipeline_name="orders",
        source_platform="SQL Server",
        target_platform="Fabric",
        source_tables=[src],
        target_tables=[tgt],
        transformations=[tr],
    )


class TestLineageEngine:
    def test_build_returns_report(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert isinstance(report, LineageReport)

    def test_report_pipeline_id(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert report.pipeline_id == "pip1"

    def test_lineage_edge_created(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert len(report.lineage) == 1

    def test_lineage_edge_source_column(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        edge = report.lineage[0]
        assert edge.source_column == "amount"
        assert edge.source_table == "orders"

    def test_lineage_edge_target_column(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        edge = report.lineage[0]
        assert edge.target_column == "total_amount"
        assert edge.target_table == "target"

    def test_lineage_confidence(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert report.lineage[0].confidence == 0.9

    def test_coverage_full_when_all_mapped(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert report.coverage_pct == 1.0

    def test_unmapped_target_detected(self):
        pipeline = _make_pipeline_with_lineage()
        # Add an extra target column with no transformation
        pipeline.target_tables[0].columns.append(
            MigrationColumn(column_id="tc2", name="extra_col")
        )
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert "target.extra_col" in report.unmapped_targets

    def test_to_dict(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        d = report.to_dict()
        assert "lineage" in d
        assert "coverage_pct" in d

    def test_to_json(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        j = report.to_json()
        data = json.loads(j)
        assert "lineage" in data

    def test_to_sttm_md_contains_table_headers(self):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        md = report.to_sttm_md()
        assert "Source Table" in md
        assert "Target Column" in md
        assert "orders" in md

    def test_save_json(self, tmp_path):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        out = tmp_path / "column-lineage.json"
        report.save_json(out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert "lineage" in data

    def test_save_sttm(self, tmp_path):
        pipeline = _make_pipeline_with_lineage()
        engine = LineageEngine()
        report = engine.build(pipeline)
        out = tmp_path / "sttm.md"
        report.save_sttm(out)
        assert out.exists()
        content = out.read_text()
        assert "Source-to-Target Mapping" in content

    def test_empty_pipeline_coverage_is_1(self):
        pipeline = MigrationPipeline(
            pipeline_id="empty",
            pipeline_name="empty",
            source_platform="X",
            target_platform="Y",
        )
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert report.coverage_pct == 1.0

    def test_no_source_columns_creates_passthrough_edge(self):
        tgt_col = MigrationColumn(column_id="tc1", name="col1")
        tgt = MigrationTable(table_id="tgt", schema_name="", table_name="tgt", columns=[tgt_col])
        tr = MigrationTransformation(
            transformation_id="tr1",
            transformation_type=TransformationType.DERIVED,
            source_columns=[],
            target_column="tgt.col1",
            expression="CURRENT_TIMESTAMP",
        )
        pipeline = MigrationPipeline(
            pipeline_id="p1",
            pipeline_name="p",
            source_platform="X",
            target_platform="Y",
            target_tables=[tgt],
            transformations=[tr],
        )
        engine = LineageEngine()
        report = engine.build(pipeline)
        assert len(report.lineage) == 1
        assert report.lineage[0].source_column == ""
