---
artifact: kpis
gate: 1
version: "1.0.0"
owner: DataStrategist
status: DRAFT
required_by: orchestrator.gate_criteria.gate_1
---

# Gate 1: KPIs

## Migration KPIs

| KPI | Definition | Owner | Target | Measurement Method |
| --- | --- | --- | --- | --- |
| Row Count Parity | Source rows = Target rows per entity | Data Owner | 100% | Reconciliation agent |
| Data Quality Score | % records passing all DQ rules | Data Steward | ≥ 98% | Quality Gate agent |
| Migration Duration | Time from wave start to wave validated | Tech Lead | TBD | Execution log |
| First-Pass Success Rate | Waves completed without rollback | Delivery Lead | ≥ 90% | Wave report |
| MTTR | Mean time to recover from failed wave | Tech Lead | ≤ 4 h | Incident log |

## Success Thresholds

| Outcome | Threshold | Action if Breached |
| --- | --- | --- |
| Critical | < 95% row parity | Rollback wave, escalate |
| Warning | < 98% DQ score | Hold promotion, remediate |
| Pass | ≥ 98% DQ + 100% row parity | Proceed to Gate 3 |

## KPI Ownership

| KPI | Measurement Owner | Reporting Cadence |
| --- | --- | --- |
| Row Count Parity | Reconciliation agent | Per wave |
| Data Quality Score | Quality Gate agent | Per wave |
| Migration Duration | Downstream Executor | Per wave |

## Approval

| Reviewer | Date | Status |
| --- | --- | --- |
| | | PENDING |
