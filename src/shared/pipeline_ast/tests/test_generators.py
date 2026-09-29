"""
test_generators.py — Tests for Platform Generators (Trilhas 5, 6, 7)
"""
import json
import pytest

from src.shared.pipeline_ast.model.canonical import (
    DataType,
    JoinType,
    MigrationColumn,
    MigrationJoin,
    MigrationPipeline,
    MigrationTable,
    MigrationTransformation,
    TransformationType,
)
from src.shared.pipeline_ast.generators.fabric_generator import FabricGenerator, FabricArtifacts
from src.shared.pipeline_ast.generators.databricks_generator import DatabricksGenerator, DatabricksArtifacts
from src.shared.pipeline_ast.generators.airflow_generator import AirflowGenerator, AirflowArtifacts


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_full_pipeline() -> MigrationPipeline:
    src_col = MigrationColumn(column_id="c1", name="id", data_type=DataType.BIGINT, primary_key=True)
    src_col2 = MigrationColumn(column_id="c2", name="amount", data_type=DataType.DECIMAL)
    src = MigrationTable(table_id="dbo.orders", schema_name="dbo", table_name="orders", columns=[src_col, src_col2])

    cust_col = MigrationColumn(column_id="c3", name="id", data_type=DataType.BIGINT, primary_key=True)
    cust_col2 = MigrationColumn(column_id="c4", name="name", data_type=DataType.STRING)
    cust = MigrationTable(table_id="dbo.customers", schema_name="dbo", table_name="customers", columns=[cust_col, cust_col2])

    tgt_col = MigrationColumn(column_id="tc1", name="order_id", data_type=DataType.BIGINT, primary_key=True)
    tgt_col2 = MigrationColumn(column_id="tc2", name="customer_name", data_type=DataType.STRING)
    tgt = MigrationTable(table_id="target", schema_name="gold", table_name="orders_enriched", columns=[tgt_col, tgt_col2])

    join = MigrationJoin(
        join_id="j1",
        join_type=JoinType.INNER,
        left_table_id="dbo.orders",
        right_table_id="dbo.customers",
        conditions=[{"left": "orders.customer_id", "right": "customers.id"}],
    )
    tr = MigrationTransformation(
        transformation_id="tr1",
        transformation_type=TransformationType.PASSTHROUGH,
        source_columns=["orders.id"],
        target_column="target.order_id",
    )
    return MigrationPipeline(
        pipeline_id="pip1",
        pipeline_name="orders_pipeline",
        source_platform="SQL Server",
        target_platform="Fabric",
        source_tables=[src, cust],
        target_tables=[tgt],
        joins=[join],
        transformations=[tr],
    )


def _make_empty_pipeline() -> MigrationPipeline:
    return MigrationPipeline(
        pipeline_id="empty",
        pipeline_name="empty_pipeline",
        source_platform="SQL",
        target_platform="Databricks",
    )


# ---------------------------------------------------------------------------
# Fabric Generator Tests
# ---------------------------------------------------------------------------

class TestFabricGenerator:
    def test_generate_returns_artifacts(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert isinstance(artifacts, FabricArtifacts)

    def test_pipeline_json_has_activities(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        activities = artifacts.pipeline_json.get("properties", {}).get("activities", [])
        assert len(activities) > 0

    def test_bronze_py_contains_pipeline_name(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert "orders_pipeline" in artifacts.bronze_py

    def test_bronze_py_contains_source_table(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert "orders" in artifacts.bronze_py

    def test_silver_py_contains_join(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert "join" in artifacts.silver_py.lower()

    def test_gold_py_contains_target_table(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert "orders_enriched" in artifacts.gold_py

    def test_ddl_contains_create_table(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert any("CREATE TABLE" in s for s in artifacts.ddl_statements)

    def test_ddl_contains_column_types(self):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        ddl = "\n".join(artifacts.ddl_statements)
        assert "BIGINT" in ddl or "INT" in ddl

    def test_save_creates_files(self, tmp_path):
        pipeline = _make_full_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        written = artifacts.save(tmp_path)
        assert len(written) > 0
        for path in written.values():
            assert path.exists()

    def test_empty_pipeline_does_not_crash(self):
        pipeline = _make_empty_pipeline()
        artifacts = FabricGenerator().generate(pipeline)
        assert artifacts is not None


# ---------------------------------------------------------------------------
# Databricks Generator Tests
# ---------------------------------------------------------------------------

class TestDatabricksGenerator:
    def test_generate_returns_artifacts(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        assert isinstance(artifacts, DatabricksArtifacts)

    def test_bronze_py_contains_jdbc(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        assert "jdbc" in artifacts.bronze_py.lower()

    def test_silver_py_contains_join(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        assert "join" in artifacts.silver_py.lower()

    def test_gold_py_contains_merge(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        assert "merge" in artifacts.gold_py.lower() or "MERGE" in artifacts.gold_py

    def test_ddl_contains_delta(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        ddl = "\n".join(artifacts.ddl_statements)
        assert "DELTA" in ddl

    def test_ddl_contains_optimize(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        ddl = "\n".join(artifacts.ddl_statements)
        assert "OPTIMIZE" in ddl

    def test_job_json_has_tasks(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        tasks = artifacts.job_json.get("tasks", [])
        assert len(tasks) == 3  # bronze, silver, gold

    def test_job_json_task_keys(self):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        task_keys = [t["task_key"] for t in artifacts.job_json["tasks"]]
        assert "bronze_extract" in task_keys
        assert "silver_transform" in task_keys
        assert "gold_load" in task_keys

    def test_save_creates_files(self, tmp_path):
        pipeline = _make_full_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        written = artifacts.save(tmp_path)
        assert len(written) > 0

    def test_empty_pipeline_does_not_crash(self):
        pipeline = _make_empty_pipeline()
        artifacts = DatabricksGenerator().generate(pipeline)
        assert artifacts is not None


# ---------------------------------------------------------------------------
# Airflow Generator Tests
# ---------------------------------------------------------------------------

class TestAirflowGenerator:
    def test_generate_returns_artifacts(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert isinstance(artifacts, AirflowArtifacts)

    def test_dag_py_contains_dag_id(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert "orders_pipeline" in artifacts.dag_py

    def test_dag_py_contains_bronze_task(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert "bronze_extract" in artifacts.dag_py

    def test_dag_py_contains_silver_task(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert "silver_transform" in artifacts.dag_py

    def test_dag_py_contains_gold_task(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert "gold_load" in artifacts.dag_py

    def test_dag_py_contains_dependency_chain(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert ">>" in artifacts.dag_py

    def test_dag_py_contains_with_dag(self):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert "with DAG" in artifacts.dag_py

    def test_save_creates_file(self, tmp_path):
        pipeline = _make_full_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        written = artifacts.save(tmp_path)
        assert "dag_py" in written
        assert written["dag_py"].exists()

    def test_empty_pipeline_does_not_crash(self):
        pipeline = _make_empty_pipeline()
        artifacts = AirflowGenerator().generate(pipeline)
        assert artifacts is not None
