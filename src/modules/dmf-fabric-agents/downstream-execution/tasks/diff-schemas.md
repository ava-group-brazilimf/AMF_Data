# ⚖️ Task: Diff Schemas

> **Agent:** Balance (Reconciliation Agent)
> **Phase:** DOWNSTREAM | **Gate:** 3
> **Command:** `*schema-diff`

---

## Objective

Compare source and target schemas to identify structural differences in column names, data types, nullable flags, partitioning, and constraints. Flag any differences that could impact data integrity or application compatibility.

---

## Prerequisites

- [ ] Source schema metadata accessible (INFORMATION_SCHEMA or catalog)
- [ ] Target schema metadata accessible (Databricks Unity Catalog)
- [ ] Table list available for the wave
- [ ] Expected type mapping rules documented (e.g., SAP → Databricks type map)

---

## Steps

### Step 1 — Extract Source Schema

```text
For each table in the wave:
  1. Query source system metadata catalog
  2. Extract: column_name, data_type, is_nullable, character_max_length,
             numeric_precision, numeric_scale, column_default, ordinal_position
  3. Extract: primary keys, foreign keys, unique constraints
  4. Extract: partitioning strategy (if applicable)
  5. Store in source_schemas dictionary
```

### Step 2 — Extract Target Schema

```text
For each table in the wave:
  1. Query Databricks INFORMATION_SCHEMA or DESCRIBE TABLE EXTENDED
  2. Extract same metadata fields as source
  3. Store in target_schemas dictionary
```

### Step 3 — Compare Schemas

```text
For each table:
  Compare the following dimensions:

  | Dimension          | Check                                          |
  | ------------------ | ---------------------------------------------- |
  | Column Count       | source_col_count == target_col_count            |
  | Column Names       | All source columns exist in target              |
  | Column Order       | Ordinal positions match (if strict mode)        |
  | Data Types         | Types match after applying type mapping rules   |
  | Nullable           | Nullable flags match                            |
  | Precision/Scale    | Numeric precision and scale match               |
  | Constraints        | PK/FK/Unique constraints preserved              |
  | Partitioning       | Partition columns and strategy match             |
```

### Step 4 — Classify Differences

| Difference Type          | Severity   | Example                                    |
| ------------------------ | ---------- | ------------------------------------------ |
| Missing column           | CRITICAL   | Source has `WERKS`, target does not          |
| Extra column in target   | INFO       | Target has `_load_timestamp` (added by ETL) |
| Data type mismatch       | WARNING    | `DECIMAL(18,2)` → `DOUBLE`                 |
| Nullable flag change     | WARNING    | `NOT NULL` → `NULL`                        |
| Precision loss           | CRITICAL   | `DECIMAL(18,6)` → `DECIMAL(18,2)`          |
| Constraint missing       | WARNING    | PK not enforced in target                   |
| Partition difference     | INFO       | Different partition strategy                 |

### Step 5 — Generate Schema Diff Report

```json
{
  "check_type": "schema_diff",
  "wave": 1,
  "timestamp": "2026-02-13T11:00:00Z",
  "tables_checked": 450,
  "tables_identical": 445,
  "tables_with_diffs": 5,
  "results": [
    {
      "table": "EKPO",
      "status": "WARNING",
      "differences": [
        {
          "column": "NETPR",
          "dimension": "data_type",
          "source_value": "DECIMAL(18,6)",
          "target_value": "DECIMAL(18,2)",
          "severity": "CRITICAL",
          "recommendation": "Alter target column to DECIMAL(18,6) to prevent precision loss"
        }
      ]
    }
  ]
}
```

---

## Success Criteria

- [ ] All table schemas extracted from source and target
- [ ] Column-level comparison completed for all tables
- [ ] Type mapping rules applied before comparison
- [ ] Differences classified by severity
- [ ] Schema diff report written to `projects/{project_name}/outputs/downstream/reconciliation/schema-diffs/`
- [ ] Critical differences flagged for immediate action
