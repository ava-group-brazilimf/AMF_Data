# ⚖️ Task: Compare Row Counts

> **Agent:** Balance (Reconciliation Agent)
> **Phase:** DOWNSTREAM | **Gate:** 3
> **Command:** `*row-count`

---

## Objective

Compare row counts between source and target systems for all tables in a given wave. Identify any discrepancies and flag them with appropriate severity.

---

## Prerequisites

- [ ] Source connection config available (`source-connection-config.yaml`)
- [ ] Target connection config available (`target-connection-config.yaml`)
- [ ] Table list available (`table-list.json` from Discovery Scout)
- [ ] Migration for the wave has completed

---

## Steps

### Step 1 — Query Source Counts

```text
For each table in the wave:
  1. Connect to source system using source-connection-config.yaml
  2. Execute: SELECT COUNT(*) FROM <schema>.<table>
  3. Store result in source_counts dictionary
  4. Log query execution time
```

**Output:** `source_counts = { "MARA": 1250000, "MARC": 890432, ... }`

### Step 2 — Query Target Counts

```text
For each table in the wave:
  1. Connect to target system (Databricks) using target-connection-config.yaml
  2. Execute: SELECT COUNT(*) FROM <catalog>.<schema>.<table>
  3. Store result in target_counts dictionary
  4. Log query execution time
```

**Output:** `target_counts = { "MARA": 1250000, "MARC": 890432, ... }`

### Step 3 — Calculate Delta

```text
For each table:
  delta = target_count - source_count
  parity_pct = (min(source, target) / max(source, target)) * 100
  status = PASS if delta == 0 else FAIL
```

### Step 4 — Flag Discrepancies

| Delta     | Severity   | Action                                      |
| --------- | ---------- | ------------------------------------------- |
| `== 0`    | —          | PASS — no action required                   |
| `< 0`     | CRITICAL   | Data loss detected — block wave sign-off    |
| `> 0`     | WARNING    | Extra rows in target — investigate source   |

### Step 5 — Generate Output

```json
{
  "check_type": "row_count",
  "wave": 1,
  "timestamp": "2026-02-13T10:00:00Z",
  "tables_checked": 450,
  "tables_passed": 449,
  "tables_failed": 1,
  "results": [
    {
      "table": "MARD",
      "source_count": 456789,
      "target_count": 456786,
      "delta": -3,
      "parity_pct": 99.9993,
      "status": "FAIL",
      "severity": "CRITICAL"
    }
  ]
}
```

---

## Success Criteria

- [ ] All tables in the wave have been queried in both source and target
- [ ] Delta calculated for every table
- [ ] Zero-tolerance enforced (delta must be 0 for PASS)
- [ ] Results written to `projects/{project_name}/outputs/downstream/reconciliation/reconciliation-reports/`
- [ ] Critical discrepancies flagged for immediate review
