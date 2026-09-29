"""
fabric_generator.py — Microsoft Fabric Generator (Trilha 5)

Generates Microsoft Fabric artifacts from a canonical MigrationPipeline:
    - pipeline_<name>.json   — Data Factory pipeline definition
    - bronze_extract.py      — PySpark Bronze layer extraction
    - silver_transform.py    — PySpark Silver layer transformation
    - gold_load.py           — PySpark Gold layer aggregation/load
    - create_<table>.sql     — Fabric Warehouse DDL

Input:  canonical-model.json (MigrationPipeline)
Output: generated-code/fabric/
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
    MigrationTransformation,
    TransformationType,
)


# ---------------------------------------------------------------------------
# Type mapping: canonical → Fabric/T-SQL types
# ---------------------------------------------------------------------------

_FABRIC_TYPE_MAP: dict[DataType, str] = {
    DataType.STRING: "VARCHAR(MAX)",
    DataType.INTEGER: "INT",
    DataType.BIGINT: "BIGINT",
    DataType.FLOAT: "FLOAT",
    DataType.DOUBLE: "FLOAT",
    DataType.DECIMAL: "DECIMAL(18,4)",
    DataType.BOOLEAN: "BIT",
    DataType.DATE: "DATE",
    DataType.TIMESTAMP: "DATETIME2",
    DataType.BINARY: "VARBINARY(MAX)",
    DataType.ARRAY: "NVARCHAR(MAX)",
    DataType.MAP: "NVARCHAR(MAX)",
    DataType.STRUCT: "NVARCHAR(MAX)",
    DataType.UNKNOWN: "NVARCHAR(MAX)",
}

_SPARK_TYPE_MAP: dict[DataType, str] = {
    DataType.STRING: "StringType()",
    DataType.INTEGER: "IntegerType()",
    DataType.BIGINT: "LongType()",
    DataType.FLOAT: "FloatType()",
    DataType.DOUBLE: "DoubleType()",
    DataType.DECIMAL: "DecimalType(18,4)",
    DataType.BOOLEAN: "BooleanType()",
    DataType.DATE: "DateType()",
    DataType.TIMESTAMP: "TimestampType()",
    DataType.BINARY: "BinaryType()",
    DataType.ARRAY: "StringType()",
    DataType.MAP: "StringType()",
    DataType.STRUCT: "StringType()",
    DataType.UNKNOWN: "StringType()",
}


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class FabricArtifacts:
    """Generated Fabric artifacts for a pipeline."""
    pipeline_name: str
    pipeline_json: dict[str, Any] = field(default_factory=dict)
    bronze_py: str = ""
    silver_py: str = ""
    gold_py: str = ""
    ddl_statements: list[str] = field(default_factory=list)

    def save(self, output_dir: Path | str) -> dict[str, Path]:
        """Write all artifacts to output_dir. Returns {artifact_name: path}."""
        base = Path(output_dir) / "fabric"
        base.mkdir(parents=True, exist_ok=True)
        written: dict[str, Path] = {}

        name = self.pipeline_name.lower().replace(" ", "_")

        if self.pipeline_json:
            p = base / f"pipeline_{name}.json"
            p.write_text(json.dumps(self.pipeline_json, indent=2, ensure_ascii=False), encoding="utf-8")
            written["pipeline_json"] = p

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

        return written


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class FabricGenerator:
    """
    Generates Microsoft Fabric artifacts from a canonical MigrationPipeline.

    Usage::

        gen = FabricGenerator()
        artifacts = gen.generate(pipeline)
        artifacts.save(Path("outputs/generated-code"))
    """

    def generate(self, pipeline: MigrationPipeline) -> FabricArtifacts:
        artifacts = FabricArtifacts(pipeline_name=pipeline.pipeline_name)
        artifacts.pipeline_json = self._build_pipeline_json(pipeline)
        artifacts.bronze_py = self._build_bronze(pipeline)
        artifacts.silver_py = self._build_silver(pipeline)
        artifacts.gold_py = self._build_gold(pipeline)
        artifacts.ddl_statements = self._build_ddl(pipeline)
        return artifacts

    # ------------------------------------------------------------------
    # Pipeline JSON (ADF-compatible)
    # ------------------------------------------------------------------

    def _build_pipeline_json(self, pipeline: MigrationPipeline) -> dict[str, Any]:
        activities: list[dict[str, Any]] = []
        prev_name: str | None = None

        for tbl in pipeline.source_tables:
            activity: dict[str, Any] = {
                "name": f"Extract_{tbl.table_name}",
                "type": "Copy",
                "typeProperties": {
                    "source": {"type": "RelationalSource", "query": f"SELECT * FROM {tbl.full_name}"},
                    "sink": {"type": "ParquetSink", "storeSettings": {"type": "LakehouseWriteSettings"}},
                },
            }
            if prev_name:
                activity["dependsOn"] = [{"activity": prev_name, "dependencyConditions": ["Succeeded"]}]
            activities.append(activity)
            prev_name = activity["name"]

        for tbl in pipeline.target_tables:
            activity = {
                "name": f"Load_{tbl.table_name}",
                "type": "Copy",
                "typeProperties": {
                    "source": {"type": "ParquetSource"},
                    "sink": {"type": "SqlDWSink", "tableName": tbl.full_name, "writeBehavior": "Upsert"},
                },
            }
            if prev_name:
                activity["dependsOn"] = [{"activity": prev_name, "dependencyConditions": ["Succeeded"]}]
            activities.append(activity)
            prev_name = activity["name"]

        return {
            "name": pipeline.pipeline_name,
            "properties": {
                "description": f"Generated by AST Engine from {pipeline.source_platform}",
                "activities": activities,
                "annotations": ["ast-generated", f"source:{pipeline.source_platform}"],
            },
        }

    # ------------------------------------------------------------------
    # Bronze layer (raw extraction)
    # ------------------------------------------------------------------

    def _build_bronze(self, pipeline: MigrationPipeline) -> str:
        src_tables = pipeline.source_tables
        if not src_tables:
            return ""

        reads = []
        for tbl in src_tables:
            reads.append(textwrap.dedent(f"""\
                # Extract: {tbl.full_name}
                df_{tbl.table_name} = spark.read \\
                    .format("jdbc") \\
                    .option("url", jdbc_url) \\
                    .option("dbtable", "{tbl.full_name}") \\
                    .option("driver", jdbc_driver) \\
                    .load()
                df_{tbl.table_name}.write \\
                    .format("delta") \\
                    .mode("overwrite") \\
                    .option("overwriteSchema", "true") \\
                    .save(f"{{lakehouse_path}}/bronze/{tbl.table_name}")
                logging.info("Bronze: {tbl.table_name} loaded (%d rows)", df_{tbl.table_name}.count())
            """))

        table_reads = "\n".join(reads)
        return textwrap.dedent(f"""\
            # bronze_extract.py
            # Generated by AST Engine — Fabric Generator
            # Pipeline: {pipeline.pipeline_name}
            # Source: {pipeline.source_platform}
            # DO NOT EDIT MANUALLY — regenerate from canonical-model.json

            import logging
            from pyspark.sql import SparkSession

            logging.basicConfig(level=logging.INFO)

            spark = SparkSession.builder.appName("{pipeline.pipeline_name}_bronze").getOrCreate()

            # ---- Connection parameters (override via Databricks secrets / Key Vault) ----
            jdbc_url = spark.conf.get("spark.jdbc.url", "")
            jdbc_driver = spark.conf.get("spark.jdbc.driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")
            lakehouse_path = spark.conf.get("spark.lakehouse.path", "abfss://lakehouse@storage.dfs.core.windows.net")

            # ---- Bronze extraction ----
            {table_reads}
        """)

    # ------------------------------------------------------------------
    # Silver layer (transformations)
    # ------------------------------------------------------------------

    def _build_silver(self, pipeline: MigrationPipeline) -> str:
        src_tables = pipeline.source_tables
        if not src_tables:
            return ""

        transform_lines: list[str] = []
        for tbl in src_tables:
            transform_lines.append(f'df_{tbl.table_name} = spark.read.format("delta")'
                                   f'.load(f"{{lakehouse_path}}/bronze/{tbl.table_name}")')

        # Joins
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

        # Filters
        for flt in pipeline.filters:
            col = flt.column.split(".")[-1]
            val = f'"{flt.value}"' if isinstance(flt.value, str) else str(flt.value)
            tbl_ref = flt.table_id.split(".")[-1]
            if flt.operator.value in ("IS NULL", "IS NOT NULL"):
                transform_lines.append(f'df_{tbl_ref} = df_{tbl_ref}.filter(col("{col}").{flt.operator.value.lower().replace(" ", "_")}())')
            else:
                transform_lines.append(f'df_{tbl_ref} = df_{tbl_ref}.filter(col("{col}") {flt.operator.value} {val})')

        # Write silver
        for tbl in (pipeline.target_tables or pipeline.source_tables[:1]):
            transform_lines.append(
                f'df_{src_tables[0].table_name}.write.format("delta")'
                f'.mode("overwrite").save(f"{{lakehouse_path}}/silver/{tbl.table_name}")'
            )

        body = "\n".join(f"    {ln}" for ln in transform_lines)
        return textwrap.dedent(f"""\
            # silver_transform.py
            # Generated by AST Engine — Fabric Generator
            # Pipeline: {pipeline.pipeline_name}

            import logging
            from pyspark.sql import SparkSession
            from pyspark.sql.functions import col, lit

            logging.basicConfig(level=logging.INFO)

            spark = SparkSession.builder.appName("{pipeline.pipeline_name}_silver").getOrCreate()
            lakehouse_path = spark.conf.get("spark.lakehouse.path", "abfss://lakehouse@storage.dfs.core.windows.net")

            def transform() -> None:
            {body}
                logging.info("Silver layer transformation complete.")

            transform()
        """)

    # ------------------------------------------------------------------
    # Gold layer (aggregations / load)
    # ------------------------------------------------------------------

    def _build_gold(self, pipeline: MigrationPipeline) -> str:
        target_tables = pipeline.target_tables
        if not target_tables:
            return ""

        load_lines: list[str] = []
        for tbl in target_tables:
            load_lines.append(textwrap.dedent(f"""\
                df_{tbl.table_name} = spark.read.format("delta") \\
                    .load(f"{{lakehouse_path}}/silver/{tbl.table_name}")
                df_{tbl.table_name}.write \\
                    .format("delta") \\
                    .mode("overwrite") \\
                    .option("mergeSchema", "true") \\
                    .saveAsTable("gold.{tbl.table_name}")
                logging.info("Gold: {tbl.table_name} loaded (%d rows)", df_{tbl.table_name}.count())
            """))

        body = "\n".join(f"    {ln}" for ln in load_lines)
        return textwrap.dedent(f"""\
            # gold_load.py
            # Generated by AST Engine — Fabric Generator
            # Pipeline: {pipeline.pipeline_name}

            import logging
            from pyspark.sql import SparkSession

            logging.basicConfig(level=logging.INFO)

            spark = SparkSession.builder.appName("{pipeline.pipeline_name}_gold").getOrCreate()
            lakehouse_path = spark.conf.get("spark.lakehouse.path", "abfss://lakehouse@storage.dfs.core.windows.net")

            def load_gold() -> None:
            {body}
                logging.info("Gold layer load complete.")

            load_gold()
        """)

    # ------------------------------------------------------------------
    # Warehouse DDL (T-SQL / Fabric)
    # ------------------------------------------------------------------

    def _build_ddl(self, pipeline: MigrationPipeline) -> list[str]:
        statements: list[str] = []
        for tbl in pipeline.target_tables:
            cols = []
            for col in tbl.columns:
                fabric_type = _FABRIC_TYPE_MAP.get(col.data_type, "NVARCHAR(MAX)")
                null_clause = "" if col.nullable else " NOT NULL"
                pk_clause = " PRIMARY KEY" if col.primary_key else ""
                cols.append(f"    [{col.name}] {fabric_type}{null_clause}{pk_clause}")
            if not cols:
                cols = ["    [id] BIGINT NOT NULL PRIMARY KEY", "    [created_at] DATETIME2"]
            col_defs = ",\n".join(cols)
            schema = tbl.schema_name or "dbo"
            stmt = (
                f"-- Generated by AST Engine — Fabric Warehouse DDL\n"
                f"-- Pipeline: {pipeline.pipeline_name}\n"
                f"CREATE TABLE [{schema}].[{tbl.table_name}] (\n{col_defs}\n);"
            )
            statements.append(stmt)
        return statements
