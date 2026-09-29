"""
ssis_parser.py — SSIS AST Parser (Trilha 3)

Structured extraction from SSIS .dtsx packages.
Extracts: Control Flow, Data Flow, Variables, Connections, Dependencies.

Replaces text-based interpretation with XML-tree traversal.
Produces: MigrationPipeline (canonical-model.json)

Supports SSIS Package XML schemas:
    - SQL Server 2008–2019 (DTS namespace)
    - Azure-SSIS (same schema)
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from src.shared.pipeline_ast.model.canonical import (
    DataType,
    JoinType,
    MigrationColumn,
    MigrationJoin,
    MigrationNode,
    MigrationPipeline,
    MigrationTable,
    MigrationTransformation,
    NodeType,
    TransformationType,
)

# ---------------------------------------------------------------------------
# SSIS XML Namespaces
# ---------------------------------------------------------------------------

_NS = {
    "DTS": "www.microsoft.com/SqlServer/Dts",
    "SQLTask": "www.microsoft.com/sqlserver/dts/tasks/sqltask",
    "pipeline": "www.microsoft.com/SqlServer/Dts/PipelineTask",
    "dataflow": "www.microsoft.com/SqlServer/Dts/Tasks/DataFlowTask",
}

# Build Clark-notation ns map for ElementTree
_ET_NS: dict[str, str] = {
    v: v for v in _NS.values()
}


def _dts(tag: str) -> str:
    return f"{{{_NS['DTS']}}}{tag}"


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class SSISParseResult:
    """Result of parsing a single .dtsx package."""
    pipeline: MigrationPipeline
    package_name: str
    connection_count: int = 0
    control_flow_task_count: int = 0
    data_flow_task_count: int = 0
    variable_count: int = 0
    ast_coverage: float = 0.0
    parse_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class SSISASTParser:
    """
    SSIS .dtsx XML Parser.

    Usage::

        parser = SSISASTParser()
        result = parser.parse_file(Path("legacy/ETL_Orders.dtsx"))
        result.pipeline.save(Path("outputs/canonical-model.json"))
    """

    def __init__(self) -> None:
        self._node_counter = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_file(
        self,
        path: Path | str,
        target_platform: str = "(inform target platform)",
    ) -> SSISParseResult:
        """Parse a .dtsx file and return SSISParseResult."""
        p = Path(path)
        xml_text = p.read_text(encoding="utf-8", errors="replace")
        return self.parse_xml(xml_text, package_name=p.stem, target_platform=target_platform)

    def parse_xml(
        self,
        xml_text: str,
        package_name: str = "package",
        pipeline_id: str | None = None,
        target_platform: str = "(inform target platform)",
    ) -> SSISParseResult:
        """Parse raw .dtsx XML string."""
        pid = pipeline_id or f"ssis-{uuid.uuid4().hex[:8]}"
        pipeline = MigrationPipeline(
            pipeline_id=pid,
            pipeline_name=package_name,
            source_platform="SSIS",
            target_platform=target_platform,
        )
        errors: list[str] = []
        warnings: list[str] = []
        stats: dict[str, int] = {
            "connections": 0,
            "cf_tasks": 0,
            "df_tasks": 0,
            "variables": 0,
        }
        ast_objects = 0
        total_objects = 0

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            errors.append(f"XML parse error: {exc}")
            pipeline.ast_coverage = 0.0
            pipeline.parse_errors = errors
            return SSISParseResult(
                pipeline=pipeline,
                package_name=package_name,
                parse_errors=errors,
            )

        # ---- Connections ------------------------------------------------
        for conn in root.iter(_dts("ConnectionManager")):
            total_objects += 1
            conn_name = conn.get(_dts("ObjectName"), "")
            conn_type = conn.get(_dts("CreationName"), "")
            props = _collect_properties(conn)
            connection_str = props.get("ConnectionString", "")
            # OLE DB / ADO connections → source table hint
            if "OLEDB" in conn_type.upper() or "ADO" in conn_type.upper():
                # Try to extract server/database from connection string
                server = _parse_conn_property(connection_str, "Data Source")
                database = _parse_conn_property(connection_str, "Initial Catalog")
                if server or database:
                    table_id = f"conn-{conn_name.lower().replace(' ', '_')}"
                    pipeline.source_tables.append(MigrationTable(
                        table_id=table_id,
                        schema_name=database or "",
                        table_name=conn_name,
                        description=f"SSIS Connection: {conn_type}",
                        tags=["ssis-connection"],
                    ))
            stats["connections"] += 1
            ast_objects += 1

        # ---- Variables --------------------------------------------------
        for var in root.iter(_dts("Variable")):
            total_objects += 1
            stats["variables"] += 1
            ast_objects += 1

        # ---- Executables (Control Flow) ----------------------------------
        for exe in root.iter(_dts("Executable")):
            total_objects += 1
            task_name = exe.get(_dts("ObjectName"), "")
            creation_name = exe.get(_dts("CreationName"), "")
            node_id = f"task-{self._next_node()}"

            if "DataFlow" in creation_name or "Pipeline" in creation_name:
                # Data Flow Task
                stats["df_tasks"] += 1
                self._extract_data_flow(exe, pipeline, node_id, task_name)
            else:
                # Generic Control Flow Task
                stats["cf_tasks"] += 1
                pipeline.nodes.append(MigrationNode(
                    node_id=node_id,
                    node_type=NodeType.TRANSFORM,
                    name=task_name or f"task-{node_id}",
                    metadata={
                        "creation_name": creation_name,
                        "ssis_type": "control_flow",
                    },
                ))
            ast_objects += 1

        # ---- Precedence Constraints (Dependencies) ----------------------
        for pc in root.iter(_dts("PrecedenceConstraint")):
            total_objects += 1
            from_id = pc.get(_dts("From"), "")
            to_id = pc.get(_dts("To"), "")
            # Store as metadata on the destination node
            for node in pipeline.nodes:
                if node.name == to_id or node.node_id.endswith(to_id):
                    node.metadata.setdefault("depends_on", []).append(from_id)
            ast_objects += 1

        # Build execution order from nodes
        pipeline.execution_order = [n.node_id for n in pipeline.nodes]
        ast_coverage = (ast_objects / total_objects) if total_objects else 1.0
        pipeline.ast_coverage = ast_coverage
        pipeline.parse_errors = errors

        return SSISParseResult(
            pipeline=pipeline,
            package_name=package_name,
            connection_count=stats["connections"],
            control_flow_task_count=stats["cf_tasks"],
            data_flow_task_count=stats["df_tasks"],
            variable_count=stats["variables"],
            ast_coverage=ast_coverage,
            parse_errors=errors,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Data Flow extraction
    # ------------------------------------------------------------------

    def _extract_data_flow(
        self,
        task_elem: ET.Element,
        pipeline: MigrationPipeline,
        parent_node_id: str,
        task_name: str,
    ) -> None:
        """Extract OLE DB Sources, Derived Columns, Lookups, Destinations."""
        pipeline.nodes.append(MigrationNode(
            node_id=parent_node_id,
            node_type=NodeType.TRANSFORM,
            name=task_name or "data-flow",
            metadata={"ssis_type": "data_flow"},
        ))

        # OLE DB Source components
        for src in task_elem.iter():
            tag = src.tag.split("}")[-1] if "}" in src.tag else src.tag
            if tag in ("OleDbSource", "AdoNetSource"):
                tbl_name = _get_component_prop(src, "OpenRowset") or \
                           _get_component_prop(src, "SqlCommand") or \
                           src.get("name", "unknown_source")
                tbl_id = f"src-{tbl_name.lower()[:32].replace(' ', '_')}"
                if not pipeline.get_source_table(tbl_id):
                    pipeline.source_tables.append(MigrationTable(
                        table_id=tbl_id,
                        schema_name="",
                        table_name=tbl_name,
                        description=f"SSIS OLE DB Source: {tag}",
                        tags=["ssis-source"],
                    ))

            elif tag in ("OleDbDestination", "AdoNetDestination"):
                tbl_name = _get_component_prop(src, "OpenRowset") or \
                           src.get("name", "unknown_dest")
                tbl_id = f"dest-{tbl_name.lower()[:32].replace(' ', '_')}"
                if not pipeline.get_target_table(tbl_id):
                    pipeline.target_tables.append(MigrationTable(
                        table_id=tbl_id,
                        schema_name="",
                        table_name=tbl_name,
                        description=f"SSIS OLE DB Destination: {tag}",
                        tags=["ssis-destination"],
                    ))
                    pipeline.nodes.append(MigrationNode(
                        node_id=f"sink-{tbl_id}",
                        node_type=NodeType.SINK,
                        name=tbl_name,
                    ))

            elif tag == "DerivedColumn":
                # Each output column → transformation
                for col_node in src.iter():
                    col_tag = col_node.tag.split("}")[-1] if "}" in col_node.tag else col_node.tag
                    if col_tag == "outputColumn":
                        col_name = col_node.get("name", "derived_col")
                        expr = col_node.get("expression", "")
                        pipeline.transformations.append(MigrationTransformation(
                            transformation_id=f"tr-ssis-{self._next_node()}",
                            transformation_type=TransformationType.DERIVED,
                            source_columns=[],
                            target_column=col_name,
                            expression=expr,
                            description="SSIS Derived Column",
                            confidence=0.9,
                        ))

            elif tag == "Lookup":
                join_id = f"join-ssis-{self._next_node()}"
                ref_tbl = _get_component_prop(src, "SqlCommand") or "lookup_table"
                ref_id = f"lookup-{ref_tbl.lower()[:32].replace(' ', '_')}"
                if not pipeline.get_source_table(ref_id):
                    pipeline.source_tables.append(MigrationTable(
                        table_id=ref_id,
                        schema_name="",
                        table_name=ref_tbl,
                        description="SSIS Lookup reference table",
                        tags=["ssis-lookup"],
                    ))
                left_id = pipeline.source_tables[0].table_id if pipeline.source_tables else "unknown"
                pipeline.joins.append(MigrationJoin(
                    join_id=join_id,
                    join_type=JoinType.LEFT,
                    left_table_id=left_id,
                    right_table_id=ref_id,
                    description="SSIS Lookup transformation",
                ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _next_node(self) -> str:
        self._node_counter += 1
        return str(self._node_counter)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _collect_properties(elem: ET.Element) -> dict[str, str]:
    """Collect DTS:Property children into a name→value dict."""
    props: dict[str, str] = {}
    for child in elem:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "Property":
            name = child.get(_dts("Name"), child.get("Name", ""))
            props[name] = (child.text or "").strip()
    return props


def _get_component_prop(elem: ET.Element, prop_name: str) -> str | None:
    """Recursively find a property value by name within a component element."""
    for child in elem.iter():
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "property" and child.get("name", "") == prop_name:
            return (child.text or "").strip() or None
    return None


def _parse_conn_property(conn_str: str, key: str) -> str:
    """Extract a key=value pair from an ADO/OLE DB connection string."""
    pattern = re.compile(rf"{re.escape(key)}\s*=\s*([^;]+)", re.IGNORECASE)
    m = pattern.search(conn_str)
    return m.group(1).strip() if m else ""
