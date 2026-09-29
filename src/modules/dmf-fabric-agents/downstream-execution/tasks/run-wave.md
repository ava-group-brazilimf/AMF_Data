# 🚀 Task: Run Migration Wave

> **Command:** `*run-wave`
> **Agent:** Diego (Downstream Executor)
> **Phase:** DOWNSTREAM | **Gate:** 3

---

## Objective

Execute one migration wave safely against the target environment, capture every DDL/ETL/test result, and produce the canonical `wave-report.json` plus its derived MD and HTML renderings. The JSON is the single source of truth read by Orion (gate promotion), Scribe (migration-report) and `validate_gate3_artifacts.py` in CI.

---

## Prerequisites

- [ ] Gate 2 approved (validation-scorecard JSON shows `decision = APPROVED`).
- [ ] Wave config `wave-config.yaml` loaded and validated (`validate_wave_config.py`).
- [ ] DDL package available under `ddl/` and ETL package under `etl/`.
- [ ] Quality and reconciliation thresholds defined in wave-config.
- [ ] Rollback path validated and rollback owner assigned.
- [ ] Stakeholder approval for the execution window recorded.

---

## Steps

### Step 1: Pre-flight Checks

Verify environment readiness and abort early on hard blockers.

```
- Confirm target connection (READ + WRITE).
- Confirm service principal / executor identity matches wave-config.executor.
- Verify discovery_owner.primary is ACTIVE (or fallback declared and ACTIVE).
- Snapshot source row counts per object for later reconciliation.
- Open trace (TRACE_ID = GATE-3-{wave_id}-{date}).
```

**Fail Action:** Abort wave and persist `wave-report.json` with `status = FAILED` and an issue per failed pre-check.

---

### Step 2: Execute DDL

Run DDL scripts in dependency order from `ddl/`.

```
For each script in ddl/*.sql:
  - record start_ts
  - execute against target environment
  - record end_ts, duration_seconds, rows_affected
  - on failure: capture stderr into ddl_results[].error and continue or abort per wave-config.on_ddl_error
```

Append one entry per script to `ddl_results[]`.

---

### Step 3: Execute ETL

Run ETL pipelines from `etl/` in planned order.

```
For each pipeline in etl/:
  - record rows_read, rows_loaded, rows_rejected
  - capture duration_seconds and exit status
  - on failure: capture error and respect wave-config.on_etl_error policy
```

Append one entry per pipeline to `etl_results[]`.

---

### Step 4: Run Tests

Execute the post-load validation tests bundled in `tests/`.

```
For each test in tests/:
  - record assertion, actual, expected
  - status ∈ { PASS, FAIL, SKIPPED }
  - duration_seconds
```

Append entries to `tests_results[]` and compute `summary.tests_passed_rate`.

---

### Step 5: Trigger Reconciliation

Invoke Balance (`reconciliation`) to produce `reconciliation-report.json`. Read back `parity_pct` and copy into `summary.parity_pct`.

---

### Step 6: Compute GateScore

```
gate_score = (tests_passed_rate × 0.40) + (dq_score_pct × 0.30) + (parity_pct × 0.30)
```

- Round to 1 decimal place.
- Set `gate_decision.outcome = PASS` when `gate_score >= 85`, `HOLD` when `70 <= gate_score < 85`, otherwise `FAIL`.
- If any issue with severity = `CRITICAL` and `resolved = false` exists, force `gate_decision.outcome = FAIL` regardless of score.

---

### Step 7: Persist Canonical Wave Report JSON (source of truth)

Render the canonical wave report from `templates/wave-report-tmpl.json`.

```
Template:  templates/wave-report-tmpl.json
Output:    projects/{project_name}/outputs/downstream/execution/wave-report.json

Required transformations BEFORE writing the file:
  - Remove the _template_metadata block.
  - Replace every {{...}} placeholder with computed values.
  - Recompute kpis from ddl_results[], etl_results[] and tests_results[]
    (do not trust template defaults).
  - Set status to COMPLETED only when all execution_summary[] entries are PASS;
    PARTIAL when at least one is FAIL but Gate decision was HOLD;
    FAILED when gate_decision.outcome = FAIL.
  - Both discovery_owner.primary and discovery_owner.fallback MUST be declared (B-017).
```

**Pass Criteria:** JSON validates against the template structure (all required keys present, weights consistent, decision in allowed set).

---

### Step 8: Render Markdown Wave Report

Generate the human-readable report consumed by reviewers and Scribe.

```
Template:  templates/wave-report-tmpl.md
Input:     projects/{project_name}/outputs/downstream/execution/wave-report.json
Output:    projects/{project_name}/outputs/downstream/execution/wave-report.md
```

The MD report MUST cite the canonical JSON it was derived from in its header. Status and severity values render with the emoji prefix specified in the template usage notes.

---

### Step 9: Render HTML Execution Dashboard (stakeholder-facing)

Generate the visual dashboard for Gate 3 stakeholder review.

```
Template:  templates/wave-execution-report-tmpl.html
Input:     projects/{project_name}/outputs/downstream/execution/wave-report.json
Output:    projects/{project_name}/outputs/downstream/execution/wave-execution-report.html

Rendering rules (see template header comment for full spec):
  - Substitute every {{...}} placeholder; never leave placeholders in output.
  - Gauge: stroke-dashoffset = 691 * (1 - gate_score / 100), rounded to integer.
  - Decision color (DECISION_COLOR_VAR) and decision pill class:
      PASS → green / decision-pass
      HOLD → amber / decision-hold
      FAIL → red   / decision-fail
  - Status pill class on header:
      COMPLETED → status-completed
      PARTIAL   → status-partial
      FAILED    → status-failed
  - Timeline --c color map per step:
      DDL Execution  → bronze
      ETL Execution  → silver
      Quality Gate   → gold
      Reconciliation → green
      Documentation  → fabric
  - Step status pill: step-pass | step-fail | step-skipped | step-notrun
  - Result row classes: row-pass | row-fail | row-skipped
  - Issue card severity class: sev-critical | sev-high | sev-medium | sev-low
  - Render ISSUES_BLOCK empty-state when issues[] is empty.
```

---

### Step 10: Update Migration Tracker and Route

Record the gate decision and route to the next agent.

```
- Persist gate_decision into wave-report.json.
- IF outcome = PASS:
    Notify Orion → promote wave to PRODUCTION (or next environment).
    Notify Scribe → generate migration-report from this wave-report.json.
- IF outcome = HOLD:
    Open review ticket with link to wave-report.html and list of issues.
- IF outcome = FAIL:
    Notify Phoenix (self-healing) with rejection feedback per failed object.
    Notify Orion to evaluate rollback execution.
```

---

## Output Artifacts

| Artifact                                                          | Description                                       |
|-------------------------------------------------------------------|---------------------------------------------------|
| `projects/{project_name}/outputs/downstream/execution/wave-report.json`                         | Canonical wave report (single source of truth)    |
| `projects/{project_name}/outputs/downstream/execution/wave-report.md`                           | Human-readable wave report                        |
| `projects/{project_name}/outputs/downstream/execution/wave-execution-report.html`               | Visual execution dashboard (Gate 3 review)        |
| `projects/{project_name}/outputs/downstream/execution/documentation/execution-runbook.md`       | Step-by-step runbook record                       |
| `projects/{project_name}/outputs/downstream/execution/documentation/quality-gate-evidence.md`   | Evidence package for quality gate                 |
| `projects/{project_name}/outputs/downstream/execution/documentation/reconciliation-evidence.md` | Evidence package for reconciliation               |

---

## Error Handling

| Error                                | Action                                                              |
|--------------------------------------|---------------------------------------------------------------------|
| Pre-flight check fails               | Abort wave; persist wave-report with `status = FAILED`              |
| DDL script fails                     | Honor `wave-config.on_ddl_error` (HALT or CONTINUE); record error   |
| ETL pipeline fails                   | Honor `wave-config.on_etl_error`; record error                      |
| Reconciliation report missing        | Block Step 6; cannot compute GateScore without `parity_pct`         |
| GateScore below threshold            | Set decision = FAIL; route to Phoenix; do NOT promote               |
| Critical unresolved issue present    | Force decision = FAIL regardless of GateScore                       |
