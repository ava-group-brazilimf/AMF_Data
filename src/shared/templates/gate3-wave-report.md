---
artifact: wave-report
gate: 3
version: "1.0.0"
owner: DownstreamExecutor
status: DRAFT
required_by: orchestrator.gate_criteria.gate_3
discovery_owner_primary: discovery-scout
discovery_owner_fallback: inventory-scout
---

> **Derived artifact:** Prefer the agent-owned templates at
> `src/modules/dmf-fabric-agents/downstream-execution/templates/wave-report-tmpl.{json,md}`
> and `wave-execution-report-tmpl.html`. The JSON is the single source of truth
> read by Orion for Gate 3 promotion and by Scribe for the migration-report.
> This shared file is kept as the minimal contract for `validate_gate3_artifacts.py`.

# Gate 3: Wave Report

## Wave Identification

| Field | Value |
| --- | --- |
| Wave ID | WAVE-XXX |
| Wave Name | |
| Execution Date | YYYY-MM-DD |
| Environment | DEV / UAT / PROD |
| Executor | |

## Discovery Ownership

| Role | Agent | Status |
| --- | --- | --- |
| Primary | discovery-scout | ACTIVE / UNAVAILABLE |
| Fallback | inventory-scout | STANDBY / ACTIVE |

> B-017: Both primary and fallback MUST be declared. If primary was unavailable, state reason.

## Execution Summary

| Step | Status | Duration | Notes |
| --- | --- | --- | --- |
| DDL Execution | PASS / FAIL | | |
| ETL Execution | PASS / FAIL | | |
| Quality Gate | PASS / FAIL | | |
| Reconciliation | PASS / FAIL | | |
| Documentation | PASS / FAIL | | |

## GateScore

```
GateScore = (tests_passed / tests_total) × 40
           + (dq_score / 100) × 30
           + (row_parity / 100) × 30
```

| Metric | Value | Weight | Contribution |
| --- | --- | --- | --- |
| Tests Passed Rate | | 40% | |
| DQ Score | | 30% | |
| Row Parity | | 30% | |
| **GateScore** | | | |

Minimum GateScore to promote: **85**

## Rollback Readiness

- [ ] Rollback scripts tested
- [ ] Rollback time estimated
- [ ] Rollback owner assigned

## Gate 3 Decision

| Outcome | Decided By | Date | Notes |
| --- | --- | --- | --- |
| PASS / FAIL / HOLD | | | |

## Linked Artifacts

- `ddl/` — DDL scripts executed
- `etl/` — ETL scripts executed
- `tests/` — Test results
- `documentation/execution-runbook.md`
- `documentation/quality-gate-evidence.md`
- `documentation/reconciliation-evidence.md`
