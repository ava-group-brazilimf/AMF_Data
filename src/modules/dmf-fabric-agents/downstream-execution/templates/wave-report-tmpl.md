# 🚀 Template: Wave Execution Report

> **Template ID:** wave-report-tmpl
> **Agent:** Diego (Downstream Executor)
> **Phase:** DOWNSTREAM | **Gate:** 3
> **Output:** `projects/{project_name}/outputs/downstream/execution/wave-report.md`
>
> **Source of truth:** This Markdown report is *derived* from the canonical
> [`wave-report-tmpl.json`](./wave-report-tmpl.json). The visual stakeholder
> rendering is [`wave-execution-report-tmpl.html`](./wave-execution-report-tmpl.html).
> All three artifacts must agree — the JSON is the only file consumed by
> Orion for Gate 3 promotion and by Scribe for the migration-report.

---

## Template

```markdown
---
artifact: wave-report
gate: 3
version: "{{VERSION}}"
owner: downstream-executor
status: {{STATUS}}                    # COMPLETED | PARTIAL | FAILED
required_by: orchestrator.gate_criteria.gate_3
discovery_owner_primary: discovery-scout
discovery_owner_fallback: inventory-scout
trace_id: {{TRACE_ID}}
---

# Gate 3 — Wave Execution Report — {{PROJECT_NAME}}

> Source of truth: `wave-report.json` · Visual: `wave-execution-report.html`

## 1. Wave Identification

| Field            | Value             |
|------------------|-------------------|
| Wave ID          | {{WAVE_ID}}       |
| Wave Name        | {{WAVE_NAME}}     |
| Execution Date   | {{DATE_ISO8601}}  |
| Environment      | {{ENVIRONMENT}}   |
| Executor         | {{EXECUTOR_NAME}} |
| Trace ID         | {{TRACE_ID}}      |

## 2. Discovery Ownership (B-017)

| Role     | Agent              | Status                    |
|----------|--------------------|---------------------------|
| Primary  | discovery-scout    | {{PRIMARY_STATUS}}        |
| Fallback | inventory-scout    | {{FALLBACK_STATUS}}       |

> If primary was UNAVAILABLE, state reason: {{PRIMARY_UNAVAILABLE_REASON}}

## 3. Execution Summary

| Step             | Status        | Duration | Notes        |
|------------------|---------------|----------|--------------|
| DDL Execution    | {{S_DDL}}     | {{D_DDL}} | {{N_DDL}}   |
| ETL Execution    | {{S_ETL}}     | {{D_ETL}} | {{N_ETL}}   |
| Quality Gate     | {{S_QG}}      | {{D_QG}}  | {{N_QG}}    |
| Reconciliation   | {{S_REC}}     | {{D_REC}} | {{N_REC}}   |
| Documentation    | {{S_DOC}}     | {{D_DOC}} | {{N_DOC}}   |

## 4. KPIs

| KPI                         | Value             |
|-----------------------------|-------------------|
| Objects Total               | {{OBJECTS_TOTAL}} |
| DDL Success Rate            | {{DDL_PCT}}%      |
| ETL Success Rate            | {{ETL_PCT}}%      |
| Tests Pass Rate             | {{TESTS_PCT}}%    |
| Parity (vs source)          | {{PARITY_PCT}}%   |
| DQ Score                    | {{DQ_PCT}}%       |
| Open Issues                 | {{OPEN_ISSUES}}   |
| Critical Issues             | {{CRIT_ISSUES}}   |

## 5. GateScore

```
GateScore = (tests_passed_rate × 0.40) + (dq_score_pct × 0.30) + (parity_pct × 0.30)
```

| Metric              | Value         | Weight | Contribution |
|---------------------|---------------|--------|--------------|
| Tests Passed Rate   | {{TESTS_PCT}} | 40%    | {{C_TESTS}}  |
| DQ Score            | {{DQ_PCT}}    | 30%    | {{C_DQ}}     |
| Row Parity          | {{PARITY_PCT}}| 30%    | {{C_PAR}}    |
| **GateScore**       | **{{GATE_SCORE}}** | | |

Minimum GateScore to promote: **85** · Threshold met: **{{THRESHOLD_MET}}**

## 6. DDL Results

| ID | Script | Object | Type | Status | Duration | Rows | Error |
|----|--------|--------|------|--------|----------|------|-------|
| {{DDL_ROWS_BLOCK}} | | | | | | | |

## 7. ETL Results

| ID | Pipeline | Source → Target | Read | Loaded | Rejected | Status | Duration |
|----|----------|------------------|------|--------|----------|--------|----------|
| {{ETL_ROWS_BLOCK}} | | | | | | | |

## 8. Test Results

| ID | Test | Target | Status | Assertion | Actual | Expected |
|----|------|--------|--------|-----------|--------|----------|
| {{TESTS_ROWS_BLOCK}} | | | | | | |

## 9. Issues

| ID | Type | Object | Severity | Description | Resolved |
|----|------|--------|----------|-------------|----------|
| {{ISSUES_ROWS_BLOCK}} | | | | | |

> If issues[] is empty, render literally: *No issues recorded — wave executed cleanly.*

## 10. Rollback Readiness

- [{{ROLLBACK_TESTED_X}}] Rollback scripts tested
- Estimated rollback duration: {{ROLLBACK_MIN}} minutes
- Rollback owner: {{ROLLBACK_OWNER}}

## 11. Gate 3 Decision

| Outcome      | Decided By           | Date              | Notes              |
|--------------|----------------------|-------------------|--------------------|
| {{OUTCOME}}  | {{APPROVER_NAME}}    | {{DECIDED_AT}}    | {{DECISION_NOTES}} |

## 12. Linked Artifacts

- `ddl/` — DDL scripts executed
- `etl/` — ETL pipelines executed
- `tests/` — Test results
- `documentation/execution-runbook.md`
- `documentation/quality-gate-evidence.md`
- `documentation/reconciliation-evidence.md`
- `reconciliation-report.md`
```

---

## Usage Notes

- All `{{...}}` placeholders MUST be replaced from `wave-report.json`.
- Tables with `{{*_ROWS_BLOCK}}` placeholders accept one row per array entry; render
  the literal *empty-state* sentence when the array is empty.
- Status values render with emoji prefix: PASS → ✅ · FAIL → ❌ · SKIPPED → ⏭ · NOT_RUN → ⚪
- Severity values render with emoji prefix: CRITICAL → 🛑 · HIGH → 🔴 · MEDIUM → 🟡 · LOW → 🔵
- The `THRESHOLD_MET` field is `YES` when `gate_score >= 85.0`, otherwise `NO`.
