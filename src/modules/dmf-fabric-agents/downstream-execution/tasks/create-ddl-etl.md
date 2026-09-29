# Task: Create DDL and ETL Package

## Objective

Create a first executable package for DDL and ETL from approved Gate 2 artifacts.

## Inputs

- architecture.md
- data-model.md
- dq-rules.md
- sttm.md (if available)

## Steps

1. Validate mandatory inputs exist.
2. Create output folders: ddl, etl, tests, documentation.
3. Generate baseline DDL scripts by layer.
4. Generate ETL scripts by priority domain.
5. Add basic data quality assertions for each critical table.
6. Record assumptions and open items.

## Outputs

- ddl/*
- etl/*
- tests/*
- documentation/execution-notes.md
