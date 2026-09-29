# ⚙️ Task: Optimize Code

> **Command:** `*optimize`
> **Agent:** Coda (Code Generator)
> **Phase:** MIDSTREAM | **Gate:** 2

---

## Objective

Apply performance optimizations to generated pipeline code. Analyze execution plans, identify bottlenecks, and apply Spark/Delta Lake best practices to improve runtime and resource efficiency.

---

## Prerequisites

- [ ] Generated code exists: `projects/{project_name}/outputs/midstream/generated-code/{pipeline_id}.py`
- [ ] Pipeline complexity and data volume estimates available
- [ ] Target platform configuration available

---

## Steps

### Step 1: Analyze Spark Explain Plan

Generate and analyze the logical and physical execution plans.

```python
# Generate explain plan
df_result.explain(mode="extended")

# Key areas to analyze:
# - Scan operations (full table scans vs. partition pruning)
# - Shuffle operations (Exchange nodes)
# - Join strategies (SortMergeJoin vs. BroadcastHashJoin)
# - Projection pushdown effectiveness
# - Filter pushdown effectiveness
```

**Red Flags to Detect:**

| Issue                  | Symptom                              | Impact  |
|------------------------|--------------------------------------|---------|
| Full table scan        | No partition pruning in plan         | High    |
| Shuffle-heavy joins    | SortMergeJoin on large tables        | High    |
| Cartesian product      | CartesianProduct node in plan        | Critical|
| Missing predicate push | Filters after scan, not during       | Medium  |
| Data skew              | Uneven partition sizes               | High    |

---

### Step 2: Suggest and Apply Broadcast Joins

Identify join candidates for broadcast optimization.

```python
# BEFORE (SortMergeJoin — expensive)
df_result = df_large.join(df_small, "key_column")

# AFTER (BroadcastHashJoin — optimized)
from pyspark.sql.functions import broadcast
df_result = df_large.join(broadcast(df_small), "key_column")
```

**Broadcast Decision Matrix:**

| Small Table Size | Recommendation              |
|-----------------|------------------------------|
| < 10 MB         | Always broadcast             |
| 10-100 MB       | Broadcast if memory allows   |
| 100-500 MB      | Broadcast with caution       |
| > 500 MB        | Do NOT broadcast             |

---

### Step 3: Optimize Partitioning Strategy

Define optimal partitioning for write operations.

```python
# Partition by date for time-series data
df_result.write \
    .format("delta") \
    .partitionBy("load_date") \
    .mode("overwrite") \
    .saveAsTable("catalog.schema.table")
```

**Partitioning Rules:**

| Data Pattern         | Partition Strategy                    |
|---------------------|---------------------------------------|
| Time-series          | `partitionBy("year", "month")`       |
| Regional data        | `partitionBy("region")`              |
| High cardinality     | Avoid partitioning, use Z-ORDER      |
| Small tables (< 1GB) | No partitioning needed               |

**Target:** Each partition file should be **100MB–1GB**.

---

### Step 4: Apply Z-Ordering

Configure Z-ORDER for frequently queried columns.

```sql
OPTIMIZE catalog.schema.table
ZORDER BY (customer_id, transaction_date);
```

**Z-ORDER Candidate Selection:**
- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- High cardinality columns (NOT partition columns)
- Maximum 4 columns per Z-ORDER

---

### Step 5: Configure Caching Strategy

Apply strategic DataFrame caching for reused DataFrames.

```python
# Cache DataFrames used more than once
df_lookup = spark.table("catalog.schema.lookup_table").cache()

# Use in multiple joins
df_result1 = df_main.join(df_lookup, "key1")
df_result2 = df_other.join(df_lookup, "key2")

# Unpersist when done
df_lookup.unpersist()
```

**Caching Rules:**
- Cache only if DataFrame is reused ≥ 2 times
- Prefer `MEMORY_AND_DISK` storage level
- Always unpersist after use
- Monitor cache hit rate

---

### Step 6: Tune AQE (Adaptive Query Execution) Settings

Configure AQE for optimal runtime behavior.

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionSize", "64MB")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")
```

---

## Optimization Levels

| Level        | Actions                                                    |
|-------------|-------------------------------------------------------------|
| **basic**    | Broadcast joins, basic partitioning, AQE enabled           |
| **advanced** | + Z-ORDER, caching, partition tuning, predicate pushdown   |
| **aggressive** | + Repartition, bucketing, custom shuffle partitions, Photon|

---

## Output

| Artifact                                                              | Description                   |
|-----------------------------------------------------------------------|-------------------------------|
| Updated `projects/{project_name}/outputs/midstream/generated-code/{pipeline_id}.py`             | Optimized code                |
| `projects/{project_name}/outputs/midstream/optimization-reports/{pipeline_id}_optimization.md`  | Optimization report           |

---

## Optimization Report Template

```markdown
# Optimization Report: {pipeline_id}
## Summary
- Optimization level: advanced
- Optimizations applied: 5
- Estimated improvement: 40-60%

## Changes Applied
1. ✅ Broadcast join on `dim_customer` (8MB) — Est. 3x faster
2. ✅ Partition by `load_date` — Enables partition pruning
3. ✅ Z-ORDER by `customer_id` — File skipping for point queries
4. ✅ AQE enabled with skew join handling
5. ✅ Cache `df_lookup` (used 3 times)

## Before/After Metrics (Estimated)
| Metric          | Before   | After    | Improvement |
|----------------|----------|----------|-------------|
| Shuffle bytes  | 2.4 GB   | 0.8 GB   | -67%        |
| Stages         | 8        | 5        | -37%        |
| Est. runtime   | 12 min   | 5 min    | -58%        |
```

---

## Quality Gates

- [ ] All optimizations are safe (no data loss risk)
- [ ] Code still passes all tests after optimization
- [ ] Optimization report generated with rationale
- [ ] AQE settings are appropriate for cluster size
- [ ] No over-caching (memory pressure)
- [ ] Partition sizes are within target range (100MB-1GB)
