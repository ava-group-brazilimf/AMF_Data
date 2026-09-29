# ⚖️ Task: Validate Checksums

> **Agent:** Balance (Reconciliation Agent)
> **Phase:** DOWNSTREAM | **Gate:** 3
> **Command:** `*checksum`

---

## Objective

Compute SHA-256 checksums on source and target data to verify byte-level data integrity. Compare checksums per-partition or full table and report any mismatches.

---

## Prerequisites

- [ ] Source and target connections established
- [ ] Row count validation passed (or acknowledged)
- [ ] Table list and partition strategy defined
- [ ] PySpark environment available for hash computation

---

## Steps

### Step 1 — Determine Checksum Strategy

```text
For each table:
  IF table_row_count < 1,000,000:
    strategy = FULL_TABLE
  ELSE:
    strategy = PER_PARTITION
    partition_column = identify_partition_key(table)
    partition_values = get_distinct_partitions(table, partition_column)
```

### Step 2 — Compute Source Checksums

```text
For each table (or partition):
  1. Query all rows ordered by primary key
  2. Concatenate all column values per row into a single string
  3. Compute SHA-256 hash of concatenated row
  4. Aggregate: XOR all row-level hashes → table/partition checksum
  5. Store in source_checksums dictionary
```

**PySpark approach:**
```python
from pyspark.sql.functions import sha2, concat_ws, col

df_source = spark.read.table("source_schema.TABLE_NAME")
df_hashed = df_source.withColumn(
    "row_hash",
    sha2(concat_ws("||", *[col(c) for c in sorted(df_source.columns)]), 256)
)
source_checksum = df_hashed.select("row_hash").rdd.map(lambda r: r[0]).reduce(xor_hex)
```

### Step 3 — Compute Target Checksums

```text
Repeat Step 2 for target system:
  - Same column ordering
  - Same concatenation separator
  - Same hash algorithm (SHA-256)
```

### Step 4 — Compare Checksums

```text
For each table/partition:
  match = (source_checksum == target_checksum)
  status = PASS if match else FAIL
```

### Step 5 — Report Mismatches

```json
{
  "check_type": "checksum",
  "algorithm": "SHA-256",
  "wave": 1,
  "timestamp": "2026-02-13T10:30:00Z",
  "tables_checked": 450,
  "tables_passed": 450,
  "tables_failed": 0,
  "results": [
    {
      "table": "MARA",
      "strategy": "PER_PARTITION",
      "partitions_checked": 12,
      "partitions_passed": 12,
      "source_checksum": "a3f2...b7c1",
      "target_checksum": "a3f2...b7c1",
      "status": "PASS"
    }
  ]
}
```

---

## Handling Large Tables

- Use **per-partition checksums** for tables > 1M rows
- Consider **sampling** for tables > 100M rows (with explicit approval)
- Log execution time per table for performance monitoring
- Use Spark parallelism to distribute hash computation

---

## Success Criteria

- [ ] SHA-256 checksums computed for all tables in the wave
- [ ] Same column ordering used in source and target
- [ ] All checksums compared and results documented
- [ ] Mismatches flagged as CRITICAL severity
- [ ] Results written to `projects/{project_name}/outputs/downstream/reconciliation/reconciliation-reports/`
