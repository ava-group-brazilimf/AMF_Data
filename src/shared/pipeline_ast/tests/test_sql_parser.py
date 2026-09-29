"""
test_sql_parser.py — Tests for SQL AST Parser (Trilha 2)
"""
import pytest

from src.shared.pipeline_ast.parsers.sql_parser import SQLASTParser, SQLParseResult, SQLGLOT_AVAILABLE
from src.shared.pipeline_ast.model.canonical import NodeType

requires_sqlglot = pytest.mark.skipif(
    not SQLGLOT_AVAILABLE,
    reason="sqlglot not installed — install with: pip install sqlglot",
)


SIMPLE_SELECT = "SELECT id, name, amount FROM dbo.orders WHERE status = 'active';"

MULTI_TABLE_SQL = """
SELECT o.id, o.amount, c.name
FROM dbo.orders o
JOIN dbo.customers c ON o.customer_id = c.id
WHERE o.amount > 100;
"""

CTE_SQL = """
WITH recent AS (
    SELECT id, amount FROM orders WHERE created_at > '2024-01-01'
)
SELECT * FROM recent;
"""

AGGREGATION_SQL = """
SELECT customer_id, SUM(amount) as total
FROM orders
GROUP BY customer_id;
"""


class TestSQLASTParser:
    def test_parse_simple_select_returns_result(self):
        parser = SQLASTParser()
        result = parser.parse_sql(SIMPLE_SELECT, pipeline_name="test")
        assert isinstance(result, SQLParseResult)
        assert result.pipeline is not None

    def test_parse_simple_select_pipeline_name(self):
        parser = SQLASTParser()
        result = parser.parse_sql(SIMPLE_SELECT, pipeline_name="orders_pipeline")
        assert result.pipeline.pipeline_name == "orders_pipeline"

    def test_parse_detects_source_table(self):
        parser = SQLASTParser()
        result = parser.parse_sql(SIMPLE_SELECT, pipeline_name="test")
        table_names = [t.table_name.lower() for t in result.pipeline.source_tables]
        assert any("orders" in n for n in table_names), f"Expected 'orders' in {table_names}"

    @requires_sqlglot
    def test_parse_join_produces_join_entry(self):
        parser = SQLASTParser()
        result = parser.parse_sql(MULTI_TABLE_SQL, pipeline_name="join_test")
        assert len(result.pipeline.joins) > 0, "Expected at least one join"

    def test_parse_cte_creates_virtual_table(self):
        parser = SQLASTParser()
        result = parser.parse_sql(CTE_SQL, pipeline_name="cte_test")
        # CTEs appear as source tables or in nodes
        node_names = [n.name.lower() for n in result.pipeline.nodes]
        source_names = [t.table_name.lower() for t in result.pipeline.source_tables]
        assert any("recent" in x for x in node_names + source_names), \
            f"Expected 'recent' CTE. nodes={node_names}, sources={source_names}"

    @requires_sqlglot
    def test_parse_aggregation_creates_aggregate_node(self):
        parser = SQLASTParser()
        result = parser.parse_sql(AGGREGATION_SQL, pipeline_name="agg_test")
        node_types = [n.node_type for n in result.pipeline.nodes]
        assert NodeType.AGGREGATE in node_types, f"Expected AGGREGATE node. Got: {node_types}"

    def test_parse_tsql_dialect(self):
        parser = SQLASTParser(dialect="tsql")
        result = parser.parse_sql(SIMPLE_SELECT, pipeline_name="tsql_test")
        assert result.dialect == "tsql"
        assert result.pipeline.source_platform == "SQL Server"

    def test_ast_coverage_between_0_and_1(self):
        parser = SQLASTParser()
        result = parser.parse_sql(SIMPLE_SELECT, pipeline_name="cov_test")
        assert 0.0 <= result.ast_coverage <= 1.0

    def test_parse_file(self, tmp_path):
        sql_file = tmp_path / "test.sql"
        sql_file.write_text(SIMPLE_SELECT, encoding="utf-8")
        parser = SQLASTParser()
        result = parser.parse_file(sql_file)
        assert result.pipeline.pipeline_name == "test"

    def test_empty_sql_does_not_crash(self):
        parser = SQLASTParser()
        result = parser.parse_sql("", pipeline_name="empty")
        assert result.pipeline is not None

    def test_pipeline_serializable(self):
        import json
        parser = SQLASTParser()
        result = parser.parse_sql(MULTI_TABLE_SQL, pipeline_name="serial_test")
        json_str = result.pipeline.to_json()
        data = json.loads(json_str)
        assert "pipeline_id" in data
        assert "source_tables" in data

    def test_target_platform_propagated(self):
        parser = SQLASTParser()
        result = parser.parse_sql(
            SIMPLE_SELECT,
            pipeline_name="tp_test",
            target_platform="Databricks",
        )
        assert result.pipeline.target_platform == "Databricks"
