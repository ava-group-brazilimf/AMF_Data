# ⚖️ Reconciliation Checklist

> **Agent:** Balance (Reconciliation Agent)
> **Phase:** DOWNSTREAM | **Gate:** 3

---

## 1. Pre-Reconciliation

- [ ] Source connection config available and tested
- [ ] Target connection config available and tested
- [ ] Table list for the wave confirmed with Discovery Scout
- [ ] Migration execution completed for all tables in scope
- [ ] PySpark environment provisioned and accessible
- [ ] Great Expectations installed and configured
- [ ] Type mapping rules documented (source → target)
- [ ] Reconciliation thresholds confirmed (parity ≥ 99.9%, row tolerance = 0)
- [ ] Previous reconciliation reports reviewed (if re-run)

---

## 2. Row Count Validation

- [ ] Source row counts queried for all tables
- [ ] Target row counts queried for all tables
- [ ] Delta computed per table (target − source)
- [ ] Zero-tolerance check applied (delta must be 0)
- [ ] Tables with delta ≠ 0 flagged as CRITICAL
- [ ] Extra rows in target investigated (delta > 0)
- [ ] Missing rows in target escalated (delta < 0)
- [ ] Row count summary generated (passed / failed / total)

---

## 3. Checksum Validation

- [ ] Checksum strategy selected per table (full table vs per-partition)
- [ ] Column ordering standardized (sorted alphabetically)
- [ ] SHA-256 computed on source data
- [ ] SHA-256 computed on target data
- [ ] Checksums compared per table/partition
- [ ] Mismatches flagged as CRITICAL
- [ ] Large tables handled with partitioned checksums
- [ ] Execution time per table logged

---

## 4. Schema Comparison

- [ ] Source schema metadata extracted
- [ ] Target schema metadata extracted
- [ ] Column count compared
- [ ] Column names compared (case-sensitive)
- [ ] Data types compared (with type mapping applied)
- [ ] Nullable flags compared
- [ ] Numeric precision and scale compared
- [ ] Primary keys and constraints compared
- [ ] Partition strategy compared
- [ ] Differences classified by severity (CRITICAL / WARNING / INFO)
- [ ] Schema diff report generated

---

## 5. Data Profiling

- [ ] Source data profiled (min, max, avg, null_pct, distinct_count)
- [ ] Target data profiled (same metrics)
- [ ] Drift percentages computed per column
- [ ] Drift thresholds applied (warning / critical)
- [ ] Statistical anomalies flagged
- [ ] Distribution comparison completed for categorical columns
- [ ] Data profile report generated

---

## 6. Discrepancy Resolution

- [ ] All CRITICAL discrepancies documented with root cause
- [ ] Responsible team member assigned per discrepancy
- [ ] Remediation plan defined for each critical issue
- [ ] Re-migration executed for affected tables (if needed)
- [ ] Re-reconciliation passed after remediation
- [ ] WARNING items investigated and documented
- [ ] INFO items logged for audit trail

---

## 7. Post-Reconciliation

- [ ] `reconciliation-report.json` generated and saved
- [ ] `discrepancy-details.json` generated (if discrepancies found)
- [ ] All reports stored in `./projects/{project_name}/outputs/downstream/reconciliation/`
- [ ] Wave sign-off eligibility determined
- [ ] Results communicated to Scribe 📚 (documentation agent)
- [ ] Reconciliation metrics added to migration dashboard
- [ ] Execution performance baseline recorded
- [ ] Checklist completion certified by reconciliation lead
