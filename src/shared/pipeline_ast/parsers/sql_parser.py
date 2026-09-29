"""
sql_parser.py — SQL AST Parser (Trilha 2)

Extracts tables, views, joins, aggregations, filters, CTEs, subqueries
and lineage from SQL legacy artifacts (SQL Server, Oracle, PostgreSQL,
Snowflake, Databricks SQL).

Uses `sqlglot` as the primary AST library. Falls back to regex-based
extraction when sqlglot cannot parse a dialect.

Produces: canonical-model.json (MigrationPipeline)

Supported dialects:
    tsql, oracle, postgres, snowflake, databricks, spark, mysql, bigquery
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.shared.pipeline_ast.model.canonical import (
    DataType,
    FilterOperator,
    JoinType,
    MigrationColumn,
    MigrationFilter,
    MigrationJoin,
    MigrationPipeline,
    MigrationTable,
    MigrationTransformation,
    NodeType,
    MigrationNode,
    TransformationType,
)

try:
    import sqlglot
    import sqlglot.expressions as exp
    SQLGLOT_AVAILABLE = True
except ImportError:  # pragma: no cover
    SQLGLOT_AVAILABLE = False


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class SQLParseResult:
    """Result of parsing a single SQL statement or script."""
    pipeline: MigrationPipeline
    dialect: str
    statement_count: int = 0
    ast_coverage: float = 0.0          # 0.0–1.0
    parse_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dialect mapping (sqlglot name → display name)
# ---------------------------------------------------------------------------

_DIALECT_MAP: dict[str, str] = {
    "tsql": "SQL Server",
    "oracle": "Oracle",
    "postgres": "PostgreSQL",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "spark": "Apache Spark",
    "mysql": "MySQL",
    "bigquery": "BigQuery",
    "": "ANSI SQL",
}

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class SQLASTParser:
    """
    SQL AST Parser backed by sqlglot.

    Usage::

        parser = SQLASTParser(dialect="tsql")
        result = parser.parse_file(Path("legacy/orders.sql"), pipeline_name="orders")
        result.pipeline.save(Path("outputs/canonical-model.json"))
    """

    def __init__(self, dialect: str = "") -> None:
        self.dialect = dialect
        self._table_counter = 0
        self._col_counter = 0
        self._join_counter = 0
        self._filter_counter = 0
        self._transform_counter = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_sql(
        self,
        sql_text: str,
        pipeline_name: str = "pipeline",
        pipeline_id: str | None = None,
        target_platform: str = "(inform target platform)",
    ) -> SQLParseResult:
        """Parse a SQL string and return a SQLParseResult."""
        pid = pipeline_id or f"pipeline-{uuid.uuid4().hex[:8]}"
        pipeline = MigrationPipeline(
            pipeline_id=pid,
            pipeline_name=pipeline_name,
            source_platform=_DIALECT_MAP.get(self.dialect, self.dialect or "SQL"),
            target_platform=target_platform,
        )
        errors: list[str] = []
        warnings: list[str] = []
        statement_count = 0
        ast_count = 0

        if SQLGLOT_AVAILABLE:
            try:
                statements = sqlglot.parse(sql_text, dialect=self.dialect or None, error_level=sqlglot.ErrorLevel.WARN)
                for stmt in statements:
                    if stmt is None:
                        continue
                    statement_count += 1
                    try:
                        self._extract_from_statement(stmt, pipeline)
                        ast_count += 1
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"stmt {statement_count}: {exc}")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"sqlglot parse error: {exc}")
                self._fallback_regex(sql_text, pipeline, warnings)
                statement_count = statement_count or 1
        else:
            warnings.append("sqlglot not installed — using regex fallback")
            self._fallback_regex(sql_text, pipeline, warnings)
            statement_count = 1
            ast_count = 0

        ast_coverage = (ast_count / statement_count) if statement_count else 0.0
        pipeline.ast_coverage = ast_coverage
        pipeline.parse_errors = errors

        # Build execution order from nodes
        pipeline.execution_order = [n.node_id for n in pipeline.nodes]

        return SQLParseResult(
            pipeline=pipeline,
            dialect=self.dialect,
            statement_count=statement_count,
            ast_coverage=ast_coverage,
            parse_errors=errors,
            warnings=warnings,
        )

    def parse_file(
        self,
        path: Path | str,
        pipeline_name: str | None = None,
        target_platform: str = "(inform target platform)",
    ) -> SQLParseResult:
        """Parse a .sql file."""
        p = Path(path)
        name = pipeline_name or p.stem
        sql_text = p.read_text(encoding="utf-8", errors="replace")
        return self.parse_sql(sql_text, pipeline_name=name, target_platform=target_platform)

    # ------------------------------------------------------------------
    # sqlglot-based extraction
    # ------------------------------------------------------------------

    def _extract_from_statement(self, stmt: Any, pipeline: MigrationPipeline) -> None:
        """Walk one sqlglot AST statement and populate the pipeline."""
        # Source tables / views
        for tbl in stmt.find_all(exp.Table):
            table_id = self._table_id(tbl)
            if not pipeline.get_source_table(table_id):
                schema = tbl.db or ""
                name = tbl.name or str(tbl)
                src_table = MigrationTable(
                    table_id=table_id,
                    schema_name=schema,
                    table_name=name,
                    description=f"Extracted from {self.dialect or 'SQL'} AST",
                )
                pipeline.source_tables.append(src_table)
                pipeline.nodes.append(MigrationNode(
                    node_id=table_id,
                    node_type=NodeType.SOURCE,
                    name=src_table.full_name,
                ))

        # CTEs → virtual source tables
        for cte in stmt.find_all(exp.CTE):
            cte_name = cte.alias_or_name
            cte_id = f"cte-{cte_name}"
            if not pipeline.get_source_table(cte_id):
                pipeline.source_tables.append(MigrationTable(
                    table_id=cte_id,
                    schema_name="",
                    table_name=cte_name,
                    is_view=True,
                    description="CTE extracted from AST",
                ))
                pipeline.nodes.append(MigrationNode(
                    node_id=cte_id,
                    node_type=NodeType.SOURCE,
                    name=cte_name,
                    metadata={"cte": True},
                ))

        # SELECT columns → target columns + transformations
        select_cols: list[exp.Expression] = []
        if isinstance(stmt, exp.Select):
            select_cols = stmt.expressions or []
        elif hasattr(stmt, "find"):
            sel = stmt.find(exp.Select)
            if sel:
                select_cols = sel.expressions or []

        if select_cols:
            target_tbl = self._ensure_target_table(pipeline, "target")
            for col_expr in select_cols:
                self._extract_column(col_expr, target_tbl, pipeline)

        # JOINs
        for join in stmt.find_all(exp.Join):
            self._extract_join(join, pipeline)

        # WHERE filters
        where = stmt.find(exp.Where)
        if where:
            self._extract_filters(where, pipeline)

        # GROUP BY / aggregations
        group = stmt.find(exp.Group)
        if group:
            node_id = f"agg-{self._next_id('a')}"
            pipeline.nodes.append(MigrationNode(
                node_id=node_id,
                node_type=NodeType.AGGREGATE,
                name="aggregation",
                metadata={"group_by": str(group)},
            ))

    def _table_id(self, tbl: Any) -> str:
        schema = (tbl.db or "").lower()
        name = (tbl.name or "").lower()
        return f"{schema}.{name}" if schema else name

    def _ensure_target_table(
        self, pipeline: MigrationPipeline, name: str
    ) -> MigrationTable:
        existing = pipeline.get_target_table(name)
        if existing:
            return existing
        tbl = MigrationTable(
            table_id=name,
            schema_name="",
            table_name=name,
            description="Target table derived from SELECT",
        )
        pipeline.target_tables.append(tbl)
        pipeline.nodes.append(MigrationNode(
            node_id=f"sink-{name}",
            node_type=NodeType.SINK,
            name=name,
        ))
        return tbl

    def _extract_column(
        self,
        col_expr: Any,
        target_tbl: MigrationTable,
        pipeline: MigrationPipeline,
    ) -> None:
        alias = getattr(col_expr, "alias_or_name", None) or str(col_expr)
        col_id = f"col-{self._next_id('c')}"
        mc = MigrationColumn(
            column_id=col_id,
            name=alias,
            description=f"Derived from: {col_expr}",
        )
        target_tbl.columns.append(mc)

        # Detect transformation type
        t_type = TransformationType.PASSTHROUGH
        expr_str = str(col_expr)
        if isinstance(col_expr, exp.Cast):
            t_type = TransformationType.CAST
        elif isinstance(col_expr, exp.Anonymous) or isinstance(col_expr, exp.Func):
            t_type = TransformationType.EXPRESSION
        elif isinstance(col_expr, exp.Alias) and not isinstance(col_expr.this, exp.Column):
            t_type = TransformationType.DERIVED

        src_cols: list[str] = [
            str(c) for c in col_expr.find_all(exp.Column)
        ] if SQLGLOT_AVAILABLE else []

        pipeline.transformations.append(MigrationTransformation(
            transformation_id=f"tr-{self._next_id('t')}",
            transformation_type=t_type,
            source_columns=src_cols,
            target_column=f"target.{alias}",
            expression=expr_str,
            confidence=1.0 if SQLGLOT_AVAILABLE else 0.6,
        ))

    def _extract_join(self, join: Any, pipeline: MigrationPipeline) -> None:
        kind = str(getattr(join, "kind", "") or "").upper() or "INNER"
        try:
            join_type = JoinType(kind)
        except ValueError:
            join_type = JoinType.INNER

        # Determine right table
        right_tbl = join.find(exp.Table)
        right_id = self._table_id(right_tbl) if right_tbl else f"unknown-{uuid.uuid4().hex[:4]}"

        # Best-effort left table: first source table
        left_id = pipeline.source_tables[0].table_id if pipeline.source_tables else "unknown"

        conditions: list[dict[str, str]] = []
        on_clause = join.args.get("on")
        if on_clause:
            for eq in on_clause.find_all(exp.EQ):
                left_col = str(eq.left)
                right_col = str(eq.right)
                conditions.append({"left": left_col, "right": right_col})

        pipeline.joins.append(MigrationJoin(
            join_id=f"join-{self._next_id('j')}",
            join_type=join_type,
            left_table_id=left_id,
            right_table_id=right_id,
            conditions=conditions,
        ))
        pipeline.nodes.append(MigrationNode(
            node_id=f"join-node-{self._next_id('jn')}",
            node_type=NodeType.JOIN,
            name=f"{join_type.value} JOIN {right_id}",
        ))

    def _extract_filters(self, where: Any, pipeline: MigrationPipeline) -> None:
        # Extract simple equality / inequality predicates
        for pred in where.find_all((exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE)):
            col = pred.find(exp.Column)
            if not col:
                continue
            col_name = str(col)
            value_node = pred.right if hasattr(pred, "right") else None
            value = str(value_node) if value_node else None
            op_map = {
                exp.EQ: FilterOperator.EQUALS,
                exp.NEQ: FilterOperator.NOT_EQUALS,
                exp.GT: FilterOperator.GREATER,
                exp.GTE: FilterOperator.GREATER_EQ,
                exp.LT: FilterOperator.LESS,
                exp.LTE: FilterOperator.LESS_EQ,
            }
            operator = op_map.get(type(pred), FilterOperator.EQUALS)
            table_ref = col.table or (pipeline.source_tables[0].table_id if pipeline.source_tables else "")
            pipeline.filters.append(MigrationFilter(
                filter_id=f"filter-{self._next_id('f')}",
                table_id=table_ref,
                column=col_name,
                operator=operator,
                value=value,
            ))
        pipeline.nodes.append(MigrationNode(
            node_id=f"filter-node-{self._next_id('fn')}",
            node_type=NodeType.FILTER,
            name="WHERE predicate",
        ))

    # ------------------------------------------------------------------
    # Regex fallback (when sqlglot unavailable or parse fails)
    # ------------------------------------------------------------------

    def _fallback_regex(
        self, sql: str, pipeline: MigrationPipeline, warnings: list[str]
    ) -> None:
        """Best-effort regex extraction when sqlglot is unavailable."""
        warnings.append("Using regex fallback — AST coverage may be incomplete")
        sql_upper = sql.upper()

        # Tables from FROM / JOIN
        table_pattern = re.compile(
            r"(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
            re.IGNORECASE,
        )
        for m in table_pattern.finditer(sql):
            full = m.group(1)
            parts = full.rsplit(".", 1)
            schema, name = (parts[0], parts[1]) if len(parts) == 2 else ("", parts[0])
            tid = full.lower()
            if not pipeline.get_source_table(tid):
                pipeline.source_tables.append(MigrationTable(
                    table_id=tid,
                    schema_name=schema,
                    table_name=name,
                    description="Extracted via regex fallback",
                ))
                pipeline.nodes.append(MigrationNode(
                    node_id=tid,
                    node_type=NodeType.SOURCE,
                    name=full,
                    metadata={"fallback": True},
                ))

    # ------------------------------------------------------------------
    # ID generators
    # ------------------------------------------------------------------

    def _next_id(self, prefix: str) -> str:
        counter_attr = f"_{prefix}_counter"
        current = getattr(self, counter_attr, 0) + 1
        setattr(self, counter_attr, current)
        return str(current)
