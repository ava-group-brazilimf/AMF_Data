# ⚖️ Task: Profile Data

> **Agent:** Balance (Reconciliation Agent)
> **Phase:** DOWNSTREAM | **Gate:** 3
> **Command:** `*profile-data`

---

## Objective

Run Great Expectations data profiling on target data and compare statistical profiles against source data. Detect statistical drift, distribution changes, and anomalies that may indicate data quality issues post-migration.

---

## Prerequisites

- [ ] Great Expectations installed and configured
- [ ] Source statistical profile available (or source accessible for profiling)
- [ ] Target data loaded and accessible in Databricks
- [ ] Profiling columns and metrics defined per table

---

## Steps

### Step 1 — Profile Source Data

```text
For each table and each numeric/date/string column:
  Compute:
    - min: minimum value
    - max: maximum value
    - avg: mean value (numeric only)
    - null_pct: percentage of NULL values
    - distinct_count: count of distinct values
    - stddev: standard deviation (numeric only)
    - median: median value (numeric only)
    - top_values: top 10 most frequent values (categorical)
```

**Great Expectations approach:**
```python
import great_expectations as gx

context = gx.get_context()
datasource = context.sources.add_spark("source_ds", spark_session=spark)
asset = datasource.add_dataframe_asset("source_table")
batch = asset.add_batch_definition("full").get_batch(dataframe=df_source)

profiler = UserConfigurableProfiler(batch)
source_profile = profiler.build_suite()
```

### Step 2 — Profile Target Data

```text
Repeat Step 1 for target data using the same metrics and columns.
Store results in target_profile dictionary.
```

### Step 3 — Compare Profiles

```text
For each column:
  For each metric (min, max, avg, null_pct, distinct_count):
    delta = abs(target_value - source_value)
    drift_pct = (delta / source_value) * 100  (if source_value != 0)

    IF drift_pct > threshold:
      flag as WARNING or CRITICAL based on metric importance
```

**Drift Thresholds:**

| Metric          | Warning Threshold | Critical Threshold |
| --------------- | ----------------- | ------------------ |
| `min`           | 1%                | 5%                 |
| `max`           | 1%                | 5%                 |
| `avg`           | 2%                | 10%                |
| `null_pct`      | 0.5%              | 2%                 |
| `distinct_count`| 1%                | 5%                 |
| `stddev`        | 5%                | 15%                |

### Step 4 — Generate Data Profile Report

```json
{
  "check_type": "data_profile",
  "wave": 1,
  "timestamp": "2026-02-13T11:30:00Z",
  "tables_profiled": 450,
  "tables_no_drift": 448,
  "tables_with_drift": 2,
  "results": [
    {
      "table": "EKPO",
      "status": "WARNING",
      "columns_with_drift": [
        {
          "column": "NETWR",
          "metric": "avg",
          "source_value": 1523.45,
          "target_value": 1498.22,
          "drift_pct": 1.66,
          "severity": "WARNING",
          "recommendation": "Investigate rounding differences in NETWR column"
        }
      ]
    }
  ]
}
```

---

## Success Criteria

- [ ] All tables profiled in both source and target
- [ ] Statistical metrics computed for all relevant columns
- [ ] Drift percentages calculated and thresholds applied
- [ ] Warnings and critical drifts flagged
- [ ] Data profile report written to `projects/{project_name}/outputs/downstream/reconciliation/data-profiles/`
