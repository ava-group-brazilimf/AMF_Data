"""
AST Engine — Data Migration Factory
src/shared/ast/

Transforms legacy artifacts into a canonical semantic model for
deterministic, multi-platform code generation.

Pipeline:
    Legacy Artifact → AST Parser → Canonical Model → Platform Generator

Modules:
    model       — Canonical data model (MigrationNode, MigrationTable, …)
    parsers     — Source-specific AST parsers (SQL, SSIS, …)
    transformers — Model transformations and enrichments
    lineage     — Column-level lineage engine
    generators  — Platform-specific code generators (Fabric, Databricks, Airflow)
"""

from src.shared.pipeline_ast.model.canonical import (
    MigrationColumn,
    MigrationFilter,
    MigrationJoin,
    MigrationNode,
    MigrationPipeline,
    MigrationTable,
    MigrationTransformation,
)

__all__ = [
    "MigrationNode",
    "MigrationTable",
    "MigrationColumn",
    "MigrationJoin",
    "MigrationFilter",
    "MigrationTransformation",
    "MigrationPipeline",
]
