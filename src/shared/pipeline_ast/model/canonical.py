"""
canonical.py — Canonical Migration Model

Platform-agnostic representation of a migration artifact.
Produced by AST parsers and consumed by lineage engine + platform generators.

Schema mirrors canonical-model.json produced at runtime.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BIGINT = "bigint"
    FLOAT = "float"
    DOUBLE = "double"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    BINARY = "binary"
    ARRAY = "array"
    MAP = "map"
    STRUCT = "struct"
    UNKNOWN = "unknown"


class JoinType(str, Enum):
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"
    CROSS = "CROSS"
    LEFT_SEMI = "LEFT_SEMI"
    LEFT_ANTI = "LEFT_ANTI"


class TransformationType(str, Enum):
    CAST = "cast"
    ALIAS = "alias"
    EXPRESSION = "expression"
    AGGREGATION = "aggregation"
    WINDOW = "window"
    LOOKUP = "lookup"
    CONDITIONAL = "conditional"
    DERIVED = "derived"
    PASSTHROUGH = "passthrough"


class FilterOperator(str, Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER = ">"
    GREATER_EQ = ">="
    LESS = "<"
    LESS_EQ = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"
    EXISTS = "EXISTS"


class NodeType(str, Enum):
    SOURCE = "source"
    SINK = "sink"
    TRANSFORM = "transform"
    FILTER = "filter"
    JOIN = "join"
    AGGREGATE = "aggregate"
    UNION = "union"
    LOOKUP = "lookup"
    SORT = "sort"
    WINDOW = "window"


# ---------------------------------------------------------------------------
# Core model
# ---------------------------------------------------------------------------

@dataclass
class MigrationNode:
    """Base unit of a migration pipeline graph."""
    node_id: str
    node_type: NodeType
    name: str
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class MigrationColumn:
    """Represents a column in a source or target table."""
    column_id: str
    name: str
    data_type: DataType = DataType.UNKNOWN
    nullable: bool = True
    primary_key: bool = False
    foreign_key: str | None = None       # "<table>.<column>"
    description: str = ""
    source_column: str | None = None     # original column name in legacy system
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "column_id": self.column_id,
            "name": self.name,
            "data_type": self.data_type.value,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "foreign_key": self.foreign_key,
            "description": self.description,
            "source_column": self.source_column,
            "tags": self.tags,
        }


@dataclass
class MigrationTable:
    """Represents a source or target table/view."""
    table_id: str
    schema_name: str
    table_name: str
    columns: list[MigrationColumn] = field(default_factory=list)
    is_view: bool = False
    partition_keys: list[str] = field(default_factory=list)
    description: str = ""
    row_count_estimate: int | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.schema_name}.{self.table_name}" if self.schema_name else self.table_name

    def get_column(self, name: str) -> MigrationColumn | None:
        return next((c for c in self.columns if c.name.lower() == name.lower()), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "table_id": self.table_id,
            "schema_name": self.schema_name,
            "table_name": self.table_name,
            "full_name": self.full_name,
            "columns": [c.to_dict() for c in self.columns],
            "is_view": self.is_view,
            "partition_keys": self.partition_keys,
            "description": self.description,
            "row_count_estimate": self.row_count_estimate,
            "tags": self.tags,
        }


@dataclass
class MigrationJoin:
    """Represents a JOIN relationship between two tables."""
    join_id: str
    join_type: JoinType
    left_table_id: str
    right_table_id: str
    conditions: list[dict[str, str]] = field(default_factory=list)
    # conditions: [{"left": "orders.customer_id", "right": "customers.id"}]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "join_id": self.join_id,
            "join_type": self.join_type.value,
            "left_table_id": self.left_table_id,
            "right_table_id": self.right_table_id,
            "conditions": self.conditions,
            "description": self.description,
        }


@dataclass
class MigrationFilter:
    """Represents a WHERE / HAVING filter predicate."""
    filter_id: str
    table_id: str
    column: str
    operator: FilterOperator
    value: Any = None
    is_parameterized: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "filter_id": self.filter_id,
            "table_id": self.table_id,
            "column": self.column,
            "operator": self.operator.value,
            "value": self.value,
            "is_parameterized": self.is_parameterized,
            "description": self.description,
        }


@dataclass
class MigrationTransformation:
    """Represents a column-level transformation (cast, expression, aggregation, …)."""
    transformation_id: str
    transformation_type: TransformationType
    source_columns: list[str]           # fully-qualified: "<table>.<column>"
    target_column: str                  # fully-qualified: "<table>.<column>"
    expression: str = ""               # raw transformation expression
    description: str = ""
    confidence: float = 1.0            # 0.0–1.0 extraction confidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "transformation_id": self.transformation_id,
            "transformation_type": self.transformation_type.value,
            "source_columns": self.source_columns,
            "target_column": self.target_column,
            "expression": self.expression,
            "description": self.description,
            "confidence": self.confidence,
        }


@dataclass
class MigrationPipeline:
    """
    Top-level canonical model for a single migration pipeline.

    Produced by AST parsers as canonical-model.json.
    Consumed by:
      - Lineage Engine  → column-lineage.json, sttm.md
      - Platform Generators → Fabric / Databricks / Airflow artifacts
    """
    pipeline_id: str
    pipeline_name: str
    source_platform: str           # e.g. "SQL Server", "SSIS", "Oracle"
    target_platform: str           # e.g. "Fabric", "Databricks", "Snowflake"
    version: str = "1.0"
    source_tables: list[MigrationTable] = field(default_factory=list)
    target_tables: list[MigrationTable] = field(default_factory=list)
    joins: list[MigrationJoin] = field(default_factory=list)
    filters: list[MigrationFilter] = field(default_factory=list)
    transformations: list[MigrationTransformation] = field(default_factory=list)
    nodes: list[MigrationNode] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)  # node_ids in order
    metadata: dict[str, Any] = field(default_factory=dict)

    # AST-level quality metrics
    ast_coverage: float = 0.0          # % objects resolved via AST (0.0–1.0)
    parse_errors: list[str] = field(default_factory=list)

    def get_source_table(self, table_id: str) -> MigrationTable | None:
        return next((t for t in self.source_tables if t.table_id == table_id), None)

    def get_target_table(self, table_id: str) -> MigrationTable | None:
        return next((t for t in self.target_tables if t.table_id == table_id), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_name": self.pipeline_name,
            "source_platform": self.source_platform,
            "target_platform": self.target_platform,
            "version": self.version,
            "source_tables": [t.to_dict() for t in self.source_tables],
            "target_tables": [t.to_dict() for t in self.target_tables],
            "joins": [j.to_dict() for j in self.joins],
            "filters": [f.to_dict() for f in self.filters],
            "transformations": [t.to_dict() for t in self.transformations],
            "nodes": [n.to_dict() for n in self.nodes],
            "execution_order": self.execution_order,
            "metadata": self.metadata,
            "ast_coverage": self.ast_coverage,
            "parse_errors": self.parse_errors,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: Path | str) -> Path:
        """Write canonical-model.json to disk."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_json(), encoding="utf-8")
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MigrationPipeline":
        """Deserialize from dict (canonical-model.json)."""
        pipeline = cls(
            pipeline_id=data["pipeline_id"],
            pipeline_name=data["pipeline_name"],
            source_platform=data.get("source_platform", "unknown"),
            target_platform=data.get("target_platform", "unknown"),
            version=data.get("version", "1.0"),
            ast_coverage=data.get("ast_coverage", 0.0),
            parse_errors=data.get("parse_errors", []),
            execution_order=data.get("execution_order", []),
            metadata=data.get("metadata", {}),
        )
        for t in data.get("source_tables", []):
            pipeline.source_tables.append(_table_from_dict(t))
        for t in data.get("target_tables", []):
            pipeline.target_tables.append(_table_from_dict(t))
        for j in data.get("joins", []):
            pipeline.joins.append(MigrationJoin(
                join_id=j["join_id"],
                join_type=JoinType(j["join_type"]),
                left_table_id=j["left_table_id"],
                right_table_id=j["right_table_id"],
                conditions=j.get("conditions", []),
                description=j.get("description", ""),
            ))
        for f in data.get("filters", []):
            pipeline.filters.append(MigrationFilter(
                filter_id=f["filter_id"],
                table_id=f["table_id"],
                column=f["column"],
                operator=FilterOperator(f["operator"]),
                value=f.get("value"),
                is_parameterized=f.get("is_parameterized", False),
                description=f.get("description", ""),
            ))
        for tr in data.get("transformations", []):
            pipeline.transformations.append(MigrationTransformation(
                transformation_id=tr["transformation_id"],
                transformation_type=TransformationType(tr["transformation_type"]),
                source_columns=tr.get("source_columns", []),
                target_column=tr["target_column"],
                expression=tr.get("expression", ""),
                description=tr.get("description", ""),
                confidence=tr.get("confidence", 1.0),
            ))
        for n in data.get("nodes", []):
            pipeline.nodes.append(MigrationNode(
                node_id=n["node_id"],
                node_type=NodeType(n["node_type"]),
                name=n["name"],
                description=n.get("description", ""),
                metadata=n.get("metadata", {}),
            ))
        return pipeline

    @classmethod
    def load(cls, path: Path | str) -> "MigrationPipeline":
        """Load canonical-model.json from disk."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _table_from_dict(data: dict[str, Any]) -> MigrationTable:
    table = MigrationTable(
        table_id=data["table_id"],
        schema_name=data.get("schema_name", ""),
        table_name=data["table_name"],
        is_view=data.get("is_view", False),
        partition_keys=data.get("partition_keys", []),
        description=data.get("description", ""),
        row_count_estimate=data.get("row_count_estimate"),
        tags=data.get("tags", []),
    )
    for c in data.get("columns", []):
        table.columns.append(MigrationColumn(
            column_id=c["column_id"],
            name=c["name"],
            data_type=DataType(c.get("data_type", "unknown")),
            nullable=c.get("nullable", True),
            primary_key=c.get("primary_key", False),
            foreign_key=c.get("foreign_key"),
            description=c.get("description", ""),
            source_column=c.get("source_column"),
            tags=c.get("tags", []),
        ))
    return table
