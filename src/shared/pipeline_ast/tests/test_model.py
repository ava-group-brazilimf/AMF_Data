"""
test_model.py — Tests for Canonical Migration Model (Trilha 1)
"""
import json
import pytest

from src.shared.pipeline_ast.model.canonical import (
    DataType,
    FilterOperator,
    JoinType,
    MigrationColumn,
    MigrationFilter,
    MigrationJoin,
    MigrationNode,
    MigrationPipeline,
    MigrationTable,
    MigrationTransformation,
    NodeType,
    TransformationType,
)


# ---------------------------------------------------------------------------
# MigrationColumn
# ---------------------------------------------------------------------------

class TestMigrationColumn:
    def test_to_dict_defaults(self):
        col = MigrationColumn(column_id="c1", name="customer_id")
        d = col.to_dict()
        assert d["column_id"] == "c1"
        assert d["name"] == "customer_id"
        assert d["data_type"] == DataType.UNKNOWN.value
        assert d["nullable"] is True
        assert d["primary_key"] is False

    def test_to_dict_with_values(self):
        col = MigrationColumn(
            column_id="c2",
            name="id",
            data_type=DataType.BIGINT,
            nullable=False,
            primary_key=True,
        )
        d = col.to_dict()
        assert d["data_type"] == "bigint"
        assert d["primary_key"] is True
        assert d["nullable"] is False


# ---------------------------------------------------------------------------
# MigrationTable
# ---------------------------------------------------------------------------

class TestMigrationTable:
    def test_full_name_with_schema(self):
        tbl = MigrationTable(table_id="t1", schema_name="dbo", table_name="orders")
        assert tbl.full_name == "dbo.orders"

    def test_full_name_without_schema(self):
        tbl = MigrationTable(table_id="t1", schema_name="", table_name="orders")
        assert tbl.full_name == "orders"

    def test_get_column_found(self):
        col = MigrationColumn(column_id="c1", name="id")
        tbl = MigrationTable(table_id="t1", schema_name="", table_name="t", columns=[col])
        assert tbl.get_column("ID") is col  # case-insensitive

    def test_get_column_not_found(self):
        tbl = MigrationTable(table_id="t1", schema_name="", table_name="t")
        assert tbl.get_column("missing") is None

    def test_to_dict_includes_columns(self):
        col = MigrationColumn(column_id="c1", name="id")
        tbl = MigrationTable(table_id="t1", schema_name="dbo", table_name="orders", columns=[col])
        d = tbl.to_dict()
        assert len(d["columns"]) == 1
        assert d["full_name"] == "dbo.orders"


# ---------------------------------------------------------------------------
# MigrationJoin
# ---------------------------------------------------------------------------

class TestMigrationJoin:
    def test_to_dict(self):
        j = MigrationJoin(
            join_id="j1",
            join_type=JoinType.LEFT,
            left_table_id="orders",
            right_table_id="customers",
            conditions=[{"left": "orders.customer_id", "right": "customers.id"}],
        )
        d = j.to_dict()
        assert d["join_type"] == "LEFT"
        assert len(d["conditions"]) == 1


# ---------------------------------------------------------------------------
# MigrationFilter
# ---------------------------------------------------------------------------

class TestMigrationFilter:
    def test_to_dict(self):
        f = MigrationFilter(
            filter_id="f1",
            table_id="orders",
            column="status",
            operator=FilterOperator.EQUALS,
            value="active",
        )
        d = f.to_dict()
        assert d["operator"] == "="
        assert d["value"] == "active"


# ---------------------------------------------------------------------------
# MigrationTransformation
# ---------------------------------------------------------------------------

class TestMigrationTransformation:
    def test_to_dict(self):
        tr = MigrationTransformation(
            transformation_id="tr1",
            transformation_type=TransformationType.CAST,
            source_columns=["orders.amount"],
            target_column="target.amount",
            expression="CAST(amount AS DECIMAL(18,2))",
            confidence=0.95,
        )
        d = tr.to_dict()
        assert d["transformation_type"] == "cast"
        assert d["confidence"] == 0.95


# ---------------------------------------------------------------------------
# MigrationPipeline — serialization roundtrip
# ---------------------------------------------------------------------------

class TestMigrationPipeline:
    def _make_pipeline(self) -> MigrationPipeline:
        col = MigrationColumn(column_id="c1", name="id", data_type=DataType.BIGINT, primary_key=True)
        src = MigrationTable(table_id="orders", schema_name="dbo", table_name="orders", columns=[col])
        tgt = MigrationTable(table_id="target", schema_name="", table_name="target")
        tgt.columns.append(MigrationColumn(column_id="c2", name="id", data_type=DataType.BIGINT))
        tr = MigrationTransformation(
            transformation_id="tr1",
            transformation_type=TransformationType.PASSTHROUGH,
            source_columns=["dbo.orders.id"],
            target_column="target.id",
        )
        return MigrationPipeline(
            pipeline_id="pip1",
            pipeline_name="orders_pipeline",
            source_platform="SQL Server",
            target_platform="Fabric",
            source_tables=[src],
            target_tables=[tgt],
            transformations=[tr],
            ast_coverage=0.97,
        )

    def test_to_dict_structure(self):
        p = self._make_pipeline()
        d = p.to_dict()
        assert d["pipeline_id"] == "pip1"
        assert len(d["source_tables"]) == 1
        assert len(d["target_tables"]) == 1
        assert len(d["transformations"]) == 1
        assert d["ast_coverage"] == 0.97

    def test_json_roundtrip(self):
        p = self._make_pipeline()
        j = p.to_json()
        data = json.loads(j)
        p2 = MigrationPipeline.from_dict(data)
        assert p2.pipeline_id == p.pipeline_id
        assert p2.pipeline_name == p.pipeline_name
        assert len(p2.source_tables) == 1
        assert p2.source_tables[0].full_name == "dbo.orders"
        assert len(p2.transformations) == 1

    def test_save_and_load(self, tmp_path):
        p = self._make_pipeline()
        out = tmp_path / "canonical-model.json"
        p.save(out)
        assert out.exists()
        p2 = MigrationPipeline.load(out)
        assert p2.pipeline_id == "pip1"

    def test_get_source_table(self):
        p = self._make_pipeline()
        t = p.get_source_table("orders")
        assert t is not None
        assert t.table_name == "orders"

    def test_get_source_table_missing(self):
        p = self._make_pipeline()
        assert p.get_source_table("nonexistent") is None
