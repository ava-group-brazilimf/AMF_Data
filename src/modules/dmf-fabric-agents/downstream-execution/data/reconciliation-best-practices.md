# ⚖️ Reconciliation Best Practices

> **Agent:** Balance (Reconciliation Agent)
> **AI-Agent Migration Factory™**

---

## 1. Row Count Comparison Strategies

### Direct Count
- Use `SELECT COUNT(*)` for tables < 10M rows — simple and reliable.
- Always query source and target in the same time window to avoid drift from ongoing operations.

### Partitioned Count
- For tables > 10M rows, count per partition (e.g., by `MANDT`, `BUKRS`, date range).
- Sum partition counts to get total — enables parallel execution.

### Incremental Count
- For delta/CDC migrations, compare only new/changed records since last reconciliation.
- Track high-water marks (max timestamp, max sequence ID).

### Best Practices
- Run counts during maintenance windows when source is stable.
- Account for soft-deleted rows (e.g., `LOEKZ` flag in SAP).
- Document and justify any tolerance overrides (tolerance should default to 0).

---

## 2. Checksum Algorithms

### SHA-256 (Recommended)
- Industry standard for data integrity verification.
- Collision probability is negligible (1 in 2^256).
- Use deterministic column ordering (alphabetical) for reproducibility.

### MD5 (Legacy / Speed)
- Faster than SHA-256 but cryptographically broken.
- Acceptable only for non-security-critical comparisons.
- Not recommended for production reconciliation.

### Row-Level vs Table-Level
- **Row-level:** Hash each row, then aggregate (XOR or concatenate + hash).
- **Table-level:** Hash the entire result set — faster but less granular.
- Prefer row-level for tables where identifying specific mismatched rows matters.

### Best Practices
- Normalize data before hashing: trim whitespace, standardize NULLs, consistent encoding.
- Handle floating-point precision: round to agreed decimal places before hashing.
- Exclude metadata columns added by ETL (`_load_timestamp`, `_source_file`).

---

## 3. Schema Evolution Handling

### Expected Differences
Some schema changes are intentional during migration:
- Type widening (e.g., `INT` → `BIGINT`) — acceptable.
- Column additions (`_load_timestamp`, `_batch_id`) — INFO severity.
- Constraint relaxation (PK not enforced in lakehouse) — WARNING severity.

### Dangerous Differences
- Column missing in target — CRITICAL.
- Precision loss (e.g., `DECIMAL(18,6)` → `DECIMAL(18,2)`) — CRITICAL.
- Type narrowing (e.g., `VARCHAR(100)` → `VARCHAR(50)`) — CRITICAL.

### Best Practices
- Maintain a **type mapping reference** (source type → expected target type).
- Run schema diff before and after each migration wave.
- Version-control schema definitions for audit trail.
- Document all intentional deviations in a "schema exceptions" register.

---

## 4. Statistical Profiling

### Key Metrics
| Metric           | Purpose                                     |
| ---------------- | ------------------------------------------- |
| `min / max`      | Detect truncation or out-of-range values    |
| `avg`            | Detect systematic data transformation errors|
| `null_pct`       | Detect NULL handling differences             |
| `distinct_count` | Detect deduplication or data loss           |
| `stddev`         | Detect distribution changes                  |

### Tools
- **Great Expectations:** Primary profiling framework. Supports custom expectations.
- **PySpark `.describe()`**: Quick statistical summary for initial checks.
- **Databricks Data Quality Dashboard**: Visual monitoring post-migration.

### Best Practices
- Profile source once and cache results — avoid repeated source queries.
- Set drift thresholds per column based on business criticality.
- Use percentage-based thresholds (not absolute) for scalability.
- Profile after each wave, not just at the end.

---

## 5. Handling Large Tables

### Partitioned Reconciliation
- Split large tables into partitions for parallel comparison.
- Reconcile each partition independently.
- Aggregate results for final report.

### Sampling Strategy (Use with Caution)
- For tables > 100M rows, consider statistical sampling.
- Use stratified sampling (by partition key) for representativeness.
- Document sampling parameters: sample size, confidence level, margin of error.
- **Never use sampling alone** — always combine with row count comparison.

### Performance Optimization
- Use Spark's distributed computing for hash calculations.
- Leverage Databricks SQL Warehouse for count queries.
- Schedule reconciliation during off-peak hours.
- Monitor Spark executor memory — large hash operations can cause OOM.

### Best Practices
- Set timeout limits per table (e.g., 30 min max per table).
- Use checkpointing for interrupted reconciliations.
- Log execution time per table for capacity planning.

---

## 6. Discrepancy Resolution

### Triage Process
1. **Identify:** Detect discrepancy (automated by reconciliation checks).
2. **Classify:** Assign severity (CRITICAL / WARNING / INFO).
3. **Investigate:** Root cause analysis — source data, ETL logic, timing.
4. **Remediate:** Fix root cause, re-migrate affected data.
5. **Verify:** Re-run reconciliation to confirm resolution.

### Common Root Causes
| Symptom                  | Likely Cause                                      |
| ------------------------ | ------------------------------------------------- |
| Missing rows             | Filter condition in ETL, failed partition load     |
| Extra rows               | Duplicate load, missing dedup logic                |
| Checksum mismatch        | Encoding difference, NULL handling, type conversion|
| Schema diff              | Missing DDL step, incorrect type mapping           |
| Statistical drift        | Rounding, truncation, timezone conversion          |

### Best Practices
- Always investigate CRITICAL issues before the next wave.
- Keep a "known issues" register for recurring discrepancies.
- Automate re-reconciliation after remediation.
- Escalate unresolved CRITICALs to migration lead within 24 hours.

---

## 7. Continuous Reconciliation

### During Migration
- Run reconciliation after each wave completes.
- Track parity trend across waves (should be stable or improving).
- Block subsequent waves if previous wave has unresolved CRITICALs.

### Post-Migration
- Schedule daily reconciliation for the first 2 weeks after go-live.
- Reduce to weekly for the next month.
- Transition to monthly after 6 weeks of clean runs.

### Monitoring
- Integrate reconciliation metrics into the migration dashboard.
- Set up alerts for parity drops below 99.9%.
- Track mean time to resolve (MTTR) for discrepancies.

### Best Practices
- Treat reconciliation as a **continuous process**, not a one-time check.
- Automate reconciliation pipelines using Databricks Jobs / Workflows.
- Archive reconciliation reports for audit and compliance.
- Review reconciliation performance quarterly and optimize slow checks.
