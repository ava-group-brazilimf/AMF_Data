"""
databricks_generator.py — Databricks Generator (Trilha 6)

Generates Databricks artifacts from a canonical MigrationPipeline:
    - bronze_extract.py      — PySpark Bronze notebook
    - silver_transform.py    — PySpark Silver notebook
    - gold_load.py           — PySpark Gold notebook
    - create_<table>.sql     — Delta Lake DDL (CREATE TABLE / MERGE INTO / OPTIMIZE)
    - job_<pipeline>.json    — Databricks Workflow job definition

Input:  canonical-model.json (MigrationPipeline)
Output: generated-code/databricks/
"""
from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.shared.pipeline_ast.model.canonical import (
    DataType,
    MigrationPipeline,
    MigrationTable,
)


# ---------------------------------------------------------------------------
# Type mapping: canonical → Delta Lake / Spark SQL types
# ---------------------------------------------------------------------------

_DELTA_TYPE_MAP: dict[DataType, str] = {
    DataType.STRING: "STRING",
    DataType.INTEGER: "INT",
    DataType.BIGINT: "BIGINT",
    DataType.FLOAT: "FLOAT",
    DataType.DOUBLE: "DOUBLE",
    DataType.DECIMAL: "DECIMAL(18,4)",
    DataType.BOOLEAN: "BOOLEAN",
    DataType.DATE: "DATE",
    DataType.TIMESTAMP: "TIMESTAMP",
    DataType.BINARY: "BINARY",
    DataType.ARRAY: "ARRAY<STRING>",
    DataType.MAP: "MAP<STRING,STRING>",
    DataType.STRUCT: "STRING",
    DataType.UNKNOWN: "STRING",
}


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class DatabricksArtifacts:
    """Generated Databricks artifacts for a pipeline."""
    pipeline_name: str
    bronze_py: str = ""
    silver_py: str = ""
    gold_py: str = ""
    ddl_statements: list[str] = field(default_factory=list)
    job_json: dict[str, Any] = field(default_factory=dict)

    def save(self, output_dir: Path | str) -> dict[str, Path]:
        """Write all artifacts to output_dir. Returns {artifact_name: path}."""
        base = Path(output_dir) / "databricks"
        base.mkdir(parents=True, exist_ok=True)
        written: dict[str, Path] = {}
        name = self.pipeline_name.lower().replace(" ", "_")

        for attr, fname in [
            ("bronze_py", "bronze_extract.py"),
            ("silver_py", "silver_transform.py"),
            ("gold_py", "gold_load.py"),
        ]:
            content = getattr(self, attr)
            if content:
                p = base / fname
                p.write_text(content, encoding="utf-8")
                written[attr] = p

        if self.ddl_statements:
            p = base / f"create_{name}.sql"
            p.write_text("\n\n".join(self.ddl_statements), encoding="utf-8")
            written["ddl"] = p

        if self.job_json:
            p = base / f"job_{name}.json"
            p.write_text(json.dumps(self.job_json, indent=2, ensure_ascii=False), encoding="utf-8")
            written["job_json"] = p

        return written


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class DatabricksGenerator:
    """
    Generates Databricks artifacts from a canonical MigrationPipeline.

    Usage::

        gen = DatabricksGenerator()
        artifacts = gen.generate(pipeline)
        artifacts.save(Path("outputs/generated-code"))
    """

    def generate(self, pipeline: MigrationPipeline) -> DatabricksArtifacts:
        artifacts = DatabricksArtifacts(pipeline_name=pipeline.pipeline_name)
        artifacts.bronze_py = self._build_bronze(pipeline)
        artifacts.silver_py = self._build_silver(pipeline)
        artifacts.gold_py = self._build_gold(pipeline)
        artifacts.ddl_statements = self._build_ddl(pipeline)
        artifacts.job_json = self._build_job(pipeline)
        return artifacts

    # ------------------------------------------------------------------
    # Bronze layer
    # ------------------------------------------------------------------

    def _build_bronze(self, pipeline: MigrationPipeline) -> str:
        if not pipeline.source_tables:
            return ""

        reads: list[str] = []
        for tbl in pipeline.source_tables:
            reads.append(textwrap.dedent(f"""\
                # Extract: {tbl.full_name}
                df_{tbl.table_name} = (
                    spark.read
                    .format("jdbc")
                    .option("url", jdbc_url)
                    .option("dbtable", "{tbl.full_name}")
                    .option("driver", jdbc_driver)
                    .option("numPartitions", "8")
                    .load()
                )
                (
                    df_{tbl.table_name}.write
                    .format("delta")
                    .mode("overwrite")
                    .option("overwriteSchema", "true")
                    .saveAsTable(f"{{catalog}}.bronze.{tbl.table_name}")
                )
                print(f"Bronze: {tbl.table_name} — {{df_{tbl.table_name}.count()}} rows")
            """))

        table_reads = "\n".join(reads)
        return textwrap.dedent(f"""\
            # Databricks Notebook — Bronze Layer
            # Generated by AST Engine — Databricks Generator
            # Pipeline: {pipeline.pipeline_name} | Source: {pipeline.source_platform}
            # DO NOT EDIT MANUALLY — regenerate from canonical-model.json

            # COMMAND ----------
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()

            # COMMAND ----------
            # ---- Parameters (override via Databricks widgets) ----
            jdbc_url = dbutils.widgets.get("jdbc_url") if "dbutils" in dir() else ""
            jdbc_driver = dbutils.widgets.get("jdbc_driver") if "dbutils" in dir() else "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            catalog = dbutils.widgets.get("catalog") if "dbutils" in dir() else "main"

            # COMMAND ----------
            # ---- Bronze extraction ----
            {table_reads}

            print("Bronze extraction complete.")
        """)

    # ------------------------------------------------------------------
    # Silver layer
    # ------------------------------------------------------------------

    def _build_silver(self, pipeline: MigrationPipeline) -> str:
        if not pipeline.source_tables:
            return ""

        transform_lines: list[str] = []
        for tbl in pipeline.source_tables:
            transform_lines.append(
                f'df_{tbl.table_name} = spark.read.table(f"{{catalog}}.bronze.{tbl.table_name}")'
            )

        for join in pipeline.joins:
            left_tbl = pipeline.get_source_table(join.left_table_id)
            right_tbl = pipeline.get_source_table(join.right_table_id)
            if left_tbl and right_tbl:
                cond_parts = [
                    f'df_{left_tbl.table_name}["{c["left"].split(".")[-1]}"] == df_{right_tbl.table_name}["{c["right"].split(".")[-1]}"]'
                    for c in join.conditions
                ] if join.conditions else ["lit(True)"]
                cond_str = " & ".join(cond_parts) if len(cond_parts) > 1 else cond_parts[0]
                transform_lines.append(
                    f'df_{left_tbl.table_name} = df_{left_tbl.table_name}'
                    f'.join(df_{right_tbl.table_name}, {cond_str}, how="{join.join_type.value.lower()}")'
                )

        for flt in pipeline.filters:
            col_name = flt.column.split(".")[-1]
            val = f'"{flt.value}"' if isinstance(flt.value, str) else str(flt.value)
            tbl_ref = flt.table_id.split(".")[-1]
            if flt.operator.value in ("IS NULL", "IS NOT NULL"):
                transform_lines.append(f'df_{tbl_ref} = df_{tbl_ref}.filter(col("{col_name}").{flt.operator.value.lower().replace(" ", "_")}())')
            else:
                transform_lines.append(f'df_{tbl_ref} = df_{tbl_ref}.filter(col("{col_name}") {flt.operator.value} {val})')

        src_name = pipeline.source_tables[0].table_name if pipeline.source_tables else "source"
        for tbl in (pipeline.target_tables or pipeline.source_tables[:1]):
            transform_lines.append(
                f'df_{src_name}.write.format("delta").mode("overwrite").option("mergeSchema", "true")'
                f'.saveAsTable(f"{{catalog}}.silver.{tbl.table_name}")'
            )

        body = "\n".join(f"    {ln}" for ln in transform_lines)
        return textwrap.dedent(f"""\
            # Databricks Notebook — Silver Layer
            # Generated by AST Engine — Databricks Generator
            # Pipeline: {pipeline.pipeline_name}

            # COMMAND ----------
            from pyspark.sql import SparkSession
            from pyspark.sql.functions import col, lit

            spark = SparkSession.builder.getOrCreate()
            catalog = dbutils.widgets.get("catalog") if "dbutils" in dir() else "main"

            # COMMAND ----------
            def transform() -> None:
            {body}
                print("Silver transformation complete.")

            transform()
        """)

    # ------------------------------------------------------------------
    # Gold layer
    # ------------------------------------------------------------------

    def _build_gold(self, pipeline: MigrationPipeline) -> str:
        targets = pipeline.target_tables
        if not targets:
            return ""

        load_lines: list[str] = []
        pk_cols = []
        for tbl in targets:
            pk_cols = [c.name for c in tbl.columns if c.primary_key] or ["id"]
            merge_cond = " AND ".join(f"target.{c} = source.{c}" for c in pk_cols)
            load_lines.append(textwrap.dedent(f"""\
                df_{tbl.table_name} = spark.read.table(f"{{catalog}}.silver.{tbl.table_name}")
                # MERGE INTO (idempotent upsert)
                from delta.tables import DeltaTable
                if DeltaTable.isDeltaTable(spark, f"{{catalog}}.gold.{tbl.table_name}"):
                    delta_tbl = DeltaTable.forName(spark, f"{{catalog}}.gold.{tbl.table_name}")
                    delta_tbl.alias("target").merge(
                        df_{tbl.table_name}.alias("source"),
                        "{merge_cond}"
                    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
                else:
                    df_{tbl.table_name}.write.format("delta").mode("overwrite").saveAsTable(f"{{catalog}}.gold.{tbl.table_name}")
                # OPTIMIZE
                spark.sql(f"OPTIMIZE {{catalog}}.gold.{tbl.table_name}")
                print(f"Gold: {tbl.table_name} complete")
            """))

        body = "\n".join(f"    {ln}" for ln in load_lines)
        return textwrap.dedent(f"""\
            # Databricks Notebook — Gold Layer
            # Generated by AST Engine — Databricks Generator
            # Pipeline: {pipeline.pipeline_name}

            # COMMAND ----------
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()
            catalog = dbutils.widgets.get("catalog") if "dbutils" in dir() else "main"

            # COMMAND ----------
            def load_gold() -> None:
            {body}
                print("Gold layer complete.")

            load_gold()
        """)

    # ------------------------------------------------------------------
    # Delta Lake DDL
    # ------------------------------------------------------------------

    def _build_ddl(self, pipeline: MigrationPipeline) -> list[str]:
        statements: list[str] = []
        for tbl in pipeline.target_tables:
            cols = []
            for col in tbl.columns:
                delta_type = _DELTA_TYPE_MAP.get(col.data_type, "STRING")
                not_null = " NOT NULL" if not col.nullable else ""
                comment = f" COMMENT '{col.description}'" if col.description else ""
                cols.append(f"  {col.name} {delta_type}{not_null}{comment}")
            if not cols:
                cols = ["  id BIGINT NOT NULL", "  created_at TIMESTAMP"]

            partition_clause = ""
            if tbl.partition_keys:
                partition_clause = f"\nPARTITIONED BY ({', '.join(tbl.partition_keys)})"

            schema = tbl.schema_name or "gold"
            col_defs = ",\n".join(cols)
            stmt = (
                f"-- Generated by AST Engine — Databricks Delta DDL\n"
                f"-- Pipeline: {pipeline.pipeline_name}\n"
                f"CREATE TABLE IF NOT EXISTS {schema}.{tbl.table_name} (\n"
                f"{col_defs}\n"
                f") USING DELTA{partition_clause}\n"
                f"TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true');"
            )
            statements.append(stmt)

            # MERGE INTO template
            pk_cols = [c.name for c in tbl.columns if c.primary_key] or ["id"]
            merge_cond = " AND ".join(f"t.{c} = s.{c}" for c in pk_cols)
            merge_stmt = (
                f"-- MERGE INTO — {tbl.table_name}\n"
                f"MERGE INTO {schema}.{tbl.table_name} AS t\n"
                f"USING source_data AS s\n"
                f"ON {merge_cond}\n"
                f"WHEN MATCHED THEN UPDATE SET *\n"
                f"WHEN NOT MATCHED THEN INSERT *;"
            )
            statements.append(merge_stmt)

            # OPTIMIZE
            statements.append(f"-- OPTIMIZE — {tbl.table_name}\nOPTIMIZE {schema}.{tbl.table_name};")

        return statements

    # ------------------------------------------------------------------
    # Databricks Workflow Job JSON
    # ------------------------------------------------------------------

    def _build_job(self, pipeline: MigrationPipeline) -> dict[str, Any]:
        name = pipeline.pipeline_name
        tasks: list[dict[str, Any]] = [
            {
                "task_key": "bronze_extract",
                "description": "Extract raw data from source",
                "notebook_task": {"notebook_path": f"/Workflows/{name}/bronze_extract"},
                "depends_on": [],
            },
            {
                "task_key": "silver_transform",
                "description": "Apply transformations and joins",
                "notebook_task": {"notebook_path": f"/Workflows/{name}/silver_transform"},
                "depends_on": [{"task_key": "bronze_extract"}],
            },
            {
                "task_key": "gold_load",
                "description": "Load to Gold layer with MERGE + OPTIMIZE",
                "notebook_task": {"notebook_path": f"/Workflows/{name}/gold_load"},
                "depends_on": [{"task_key": "silver_transform"}],
            },
        ]
        return {
            "name": f"{name}_workflow",
            "description": f"AST-generated workflow for pipeline: {name}",
            "tasks": tasks,
            "max_concurrent_runs": 1,
            "tags": {"generated_by": "ast-engine", "source_platform": pipeline.source_platform},
        }
