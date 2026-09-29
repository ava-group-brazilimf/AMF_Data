# ⚖️ Task: Reconcile Wave

> **Agent:** Balance (Reconciliation Agent)
> **Phase:** DOWNSTREAM | **Gate:** 3
> **Command:** `*reconcile-wave`

---

## Objective

Execute a full reconciliation suite for a migration wave. Run all checks (row count, checksum, schema diff, data profiling), aggregate results, generate `reconciliation-report.json`, and flag critical discrepancies that block wave sign-off.

---

## Prerequisites

- [ ] All tables in the wave have been migrated to target
- [ ] Source and target connections verified
- [ ] Row count, checksum, schema-diff, and profile-data tasks are available
- [ ] Wave definition (table list, scope) confirmed

---

## Steps

### Step 1 — Initialize Reconciliation

```text
1. Load wave definition (table list, expected counts)
2. Verify source connectivity
3. Verify target connectivity
4. Initialize result containers for all check types
5. Log reconciliation start time
```

### Step 2 — Execute Row Count Comparison

```text
1. Run compare-row-counts task for all tables in wave
2. Collect results: passed, failed, delta per table
3. Store in reconciliation_results["row_count"]
4. Log: "Phase 1/4: Row Counts .............. ✅ 449/450 PASS"
```

### Step 3 — Execute Checksum Validation

```text
1. Run validate-checksums task for all tables in wave
2. Use appropriate strategy (full table vs per-partition)
3. Collect results: passed, failed, checksum mismatches
4. Store in reconciliation_results["checksum"]
5. Log: "Phase 2/4: Checksums ............... ✅ 450/450 PASS"
```

### Step 4 — Execute Schema Diff

```text
1. Run diff-schemas task for all tables in wave
2. Collect results: identical, diffs, severity classification
3. Store in reconciliation_results["schema_diff"]
4. Log: "Phase 3/4: Schema Diffs ............ ✅ 450/450 PASS"
```

### Step 5 — Execute Data Profiling

```text
1. Run profile-data task for all tables in wave
2. Compare statistical profiles between source and target
3. Collect results: no drift, warnings, critical drifts
4. Store in reconciliation_results["data_profile"]
5. Log: "Phase 4/4: Data Profiling .......... ⚠️ 448/450 PASS (2 warnings)"
```

### Step 6 — Aggregate Results

```text
1. Calculate overall parity percentage
2. Count total CRITICAL, WARNING, INFO issues
3. Determine wave sign-off eligibility:
   - IF critical_count == 0 AND parity >= 99.9%: ELIGIBLE
   - ELSE: BLOCKED
4. Generate summary statistics
```

### Step 7 — Generate Reconciliation Report

Generation MUST happen in this order:

```
1. Persist canonical JSON (source of truth):
     Template: templates/reconciliation-report-tmpl.json
     Output:   projects/{project_name}/outputs/downstream/reconciliation/reconciliation-report.json

   Required transformations BEFORE writing the file:
     - Remove the _template_metadata block.
     - Replace every {{...}} placeholder with computed values.
     - parity_pct and status MUST be top-level fields with the exact names
       (validate_gate3_artifacts.py / Diego's wave-report depend on them).
     - Recompute summary, levels.L*.tables_passed/failed and tables[]
       aggregates from the actual check results; do not trust template defaults.
     - sign_off_eligible MUST be true only when status = APPROVED,
       parity_pct >= sign_off_threshold_pct AND critical_count = 0.

2. Render Markdown report (derived):
     Template: templates/reconciliation-report-tmpl.md
     Output:   projects/{project_name}/outputs/downstream/reconciliation/reconciliation-report.md

3. Render HTML dashboard (derived, stakeholder-facing):
     Template: templates/reconciliation-dashboard-tmpl.html
     Output:   projects/{project_name}/outputs/downstream/reconciliation/reconciliation-dashboard.html

   Rendering rules (see template header comment for full spec):
     - Substitute every {{...}} placeholder; never leave placeholders in output.
     - Gauge: stroke-dashoffset = 691 * (1 - parity_pct / 100), rounded to integer.
     - Parity color (PARITY_COLOR_VAR):
         parity_pct >= 99.9    → teal
         95.0 <= parity < 99.9 → amber
         parity_pct < 95.0     → red
     - Status pill class: status-approved | status-partial | status-failed.
     - Level --c color map: L1→blue, L2→teal, L3→amber, L4→coral, L5→purple.
     - Level status pill: pill-pass | pill-warn | pill-fail | pill-manual.
     - Table row class: row-pass | row-warn | row-fail.
     - Issue card class: critical | warning.
     - Render CRITICAL_BLOCK / WARNINGS_BLOCK / TREND_BLOCK /
       RECOMMENDATIONS_BLOCK empty-state when their source arrays are empty.
     - SIGN_OFF_ELIGIBLE_LOWER = sign_off_eligible ? "yes" : "no".
```

For the JSON example shape, see [`templates/reconciliation-report-tmpl.json`](../templates/reconciliation-report-tmpl.json).

### Step 8 — Flag Critical Discrepancies

```text
For each critical issue:
  1. Create discrepancy detail record
  2. Assign to responsible team member
  3. Block wave sign-off until resolved
  4. Notify downstream agents (Scribe)
```

---

## Output Files

| File                                | Location                                            |
| ----------------------------------- | --------------------------------------------------- |
| `wave-{N}-reconciliation-report.json` | `projects/{project_name}/outputs/downstream/reconciliation/reconciliation-reports/` |
| `wave-{N}-discrepancies.json`       | `projects/{project_name}/outputs/downstream/reconciliation/discrepancy-details/`     |
| `wave-{N}-profiles.json`            | `projects/{project_name}/outputs/downstream/reconciliation/data-profiles/`           |
| `wave-{N}-schema-diffs.json`        | `projects/{project_name}/outputs/downstream/reconciliation/schema-diffs/`            |

---

## Success Criteria

- [ ] All four check types executed successfully
- [ ] Aggregate parity percentage calculated
- [ ] Wave sign-off eligibility determined
- [ ] `reconciliation-report.json` generated and saved
- [ ] Critical discrepancies documented in `discrepancy-details.json`
- [ ] Results communicated to downstream agents
- [ ] Execution time logged for performance baseline
