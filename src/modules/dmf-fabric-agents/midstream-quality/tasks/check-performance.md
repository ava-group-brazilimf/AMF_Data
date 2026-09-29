# ✅ Task: Check Performance

> **Command:** `*check-performance`
> **Agent:** Vera (Quality Gate)
> **Phase:** MIDSTREAM | **Gate:** 2

---

## Objective

Analyze the performance characteristics of generated Spark code by examining EXPLAIN plans, estimating runtime cost, comparing against legacy baselines, and flagging performance regressions. Ensures that migrated code does not degrade performance compared to the original system.

---

## Prerequisites

- [ ] Generated code available: `generated-code/{pipeline_id}.py`
- [ ] Spark environment accessible (for EXPLAIN plan generation)
- [ ] Legacy performance baseline (if available): `baselines/{pipeline_id}_baseline.json`
- [ ] Pipeline metadata with data volume estimates

---

## Steps

### Step 1: Generate Spark EXPLAIN Plan

Execute the generated code in dry-run mode to capture the query execution plan.

```
Methods:
  1. Logical Plan:   df.explain(mode="simple")
  2. Physical Plan:  df.explain(mode="extended")
  3. Cost Plan:      df.explain(mode="cost")
  4. Formatted Plan: df.explain(mode="formatted")

Capture:
  - Parsed Logical Plan
  - Analyzed Logical Plan
  - Optimized Logical Plan
  - Physical Plan
```

**Validation:** EXPLAIN plan generated successfully for every terminal action.
**Fail Action:** Flag with `explain_failure` — code may not be executable.

---

### Step 2: Detect Anti-Patterns

Analyze the EXPLAIN plan for known performance anti-patterns.

```
Critical Anti-Patterns (auto-reject):
  ❌ CartesianProduct        — Missing join condition
  ❌ BroadcastNestedLoopJoin — Typically indicates cartesian
  ❌ Full table scan on >1TB table

Warning Anti-Patterns (score reduction):
  ⚠️ SortMergeJoin on small table (should be BroadcastHashJoin)
  ⚠️ Shuffle with high partition count (> 200 for small data)
  ⚠️ Missing predicate pushdown (filter after read)
  ⚠️ Full scan on partitioned table without partition filter
  ⚠️ Coalesce(1) on large dataset
  ⚠️ collect() or toPandas() on large dataset
  ⚠️ UDF usage where native functions exist
  ⚠️ Repeated computation without caching
```

**Detection Rules:**

| Pattern                      | Detection Method                       | Severity |
|------------------------------|----------------------------------------|----------|
| Cartesian Product            | `CartesianProduct` in physical plan    | CRITICAL |
| Missing Broadcast            | `SortMergeJoin` + small table (< 100MB)| WARNING  |
| Missing Predicate Pushdown   | `Filter` above `Scan` in plan          | WARNING  |
| No Partition Pruning         | Full scan on partitioned table         | WARNING  |
| UDF vs Native                | `PythonUDF` in plan for simple ops     | INFO     |
| Repeated Scan                | Same table scanned multiple times      | WARNING  |

---

### Step 3: Analyze Join Strategies

Evaluate the join strategies used in the execution plan.

```
FOR each join in EXPLAIN plan:
  1. Identify join type (Inner, Left, Right, Full, Cross)
  2. Identify strategy (BroadcastHashJoin, SortMergeJoin, ShuffleHashJoin)
  3. Estimate table sizes
  4. Evaluate if optimal:
     - Small table (< 100MB) should use BroadcastHashJoin
     - Large-to-large should use SortMergeJoin
     - Skewed keys should enable AQE skew join handling
  5. Flag suboptimal strategies with recommendation
```

---

### Step 4: Evaluate Partitioning Strategy

Check that the partitioning strategy is appropriate for the data volume.

```
Checks:
  1. Write partitioning:
     - Partition columns align with query patterns
     - Expected partition count < 10,000
     - Expected partition file size: 100MB–1GB

  2. Shuffle partitioning:
     - spark.sql.shuffle.partitions appropriate for data size
     - AQE enabled for automatic adjustment

  3. Read partition pruning:
     - Queries filter on partition columns where applicable
     - No full scans on partitioned data
```

---

### Step 5: Estimate Runtime Cost

Estimate the runtime and resource cost of the generated pipeline.

```
Estimation factors:
  - Data volume (rows × avg_row_size)
  - Number of shuffles
  - Number of stages
  - Join complexity (number and types)
  - Write volume and mode (append vs merge)
  - Cluster size assumption (from job definition)

Estimate:
  estimated_runtime_minutes: float
  estimated_dbu_cost: float
  complexity_class: "LOW" | "MEDIUM" | "HIGH"
```

---

### Step 6: Compare Against Legacy Baseline

If a legacy baseline exists, compare estimated performance against historical data.

```
Load: baselines/{pipeline_id}_baseline.json

Compare:
  - legacy_runtime_minutes vs estimated_runtime_minutes
  - legacy_data_volume vs current_data_volume
  - legacy_resource_usage vs estimated_resource_usage

Calculate:
  runtime_delta_pct = (estimated - legacy) / legacy * 100

Flag if:
  runtime_delta_pct > 20% → REGRESSION WARNING
  runtime_delta_pct > 50% → REGRESSION CRITICAL
  runtime_delta_pct < -20% → IMPROVEMENT (positive note)
```

---

### Step 7: Generate Optimization Recommendations

Provide actionable recommendations based on findings.

```
Recommendations format:
  [
    {
      "finding": "SortMergeJoin on small lookup table (50MB)",
      "recommendation": "Add broadcast hint: F.broadcast(df_lookup)",
      "estimated_improvement": "30-50% join speedup",
      "priority": "HIGH"
    },
    {
      "finding": "No Z-ORDER on frequently queried columns",
      "recommendation": "OPTIMIZE table ZORDER BY (customer_id, region)",
      "estimated_improvement": "20-40% scan reduction",
      "priority": "MEDIUM"
    }
  ]
```

---

### Step 8: Calculate Performance Score

Produce a final performance dimension score.

```python
# Base score starts at 10.0
perf_score = 10.0

# Critical deductions
if has_cartesian_product:
    perf_score = 0.0  # Auto-fail

# Warning deductions
perf_score -= 1.0 * count(warning_anti_patterns)
perf_score -= 0.5 * count(info_anti_patterns)

# Regression deduction
if regression_pct > 50:
    perf_score -= 4.0
elif regression_pct > 20:
    perf_score -= 2.0

# Floor at 0
perf_score = max(perf_score, 0.0)
```

---

## Output

```json
{
  "pipeline_id": "{pipeline_id}",
  "check": "performance_analysis",
  "timestamp": "2025-01-15T14:30:22Z",
  "score": 8.0,
  "result": "PASS",
  "explain_plan": {
    "stages": 3,
    "shuffles": 1,
    "joins": [
      { "type": "Inner", "strategy": "BroadcastHashJoin", "optimal": true }
    ]
  },
  "anti_patterns": [],
  "partitioning": {
    "write_columns": ["load_date"],
    "shuffle_partitions": 200,
    "aqe_enabled": true
  },
  "estimated_cost": {
    "runtime_minutes": 8.5,
    "dbu_cost": 2.1,
    "complexity_class": "MEDIUM"
  },
  "baseline_comparison": {
    "legacy_runtime": 10.0,
    "delta_pct": -15.0,
    "status": "IMPROVEMENT"
  },
  "recommendations": []
}
```

---

## Error Handling

| Error                        | Action                                          |
|------------------------------|--------------------------------------------------|
| EXPLAIN plan generation fails| Score as 5.0 with `explain_unavailable` flag     |
| No baseline available        | Skip comparison, note in report                  |
| Cluster not accessible       | Use static analysis only, note limitation        |
| Code not Spark-based         | Skip Spark-specific checks, use generic analysis |
