# Migration Orchestration Best Practices

**Reference:** Orion (Migration Coordinator) Agent  
**Version:** 1.0

---

## Wave Planning

### Sizing Waves Correctly

**Pilot Wave (Wave 0):**
- 5-10 pipelines only
- Low complexity exclusively
- Purpose: validate tooling and process
- Duration: 1-2 weeks

**Batch Waves (Waves 1-N):**
- Group by complexity: low → medium → high
- Max 50-80 pipelines per wave (low), 20-30 (medium), 5-10 (high)
- Respect dependency ordering

❌ **Never do this:**
- Mix high and low complexity in the same wave
- Start batch waves before pilot is fully validated
- Skip reconciliation between waves

✅ **Always do this:**
- Complete pilot with 100% success before scaling
- Document lessons learned after each wave
- Adjust parallelism based on wave results

---

## Gate Discipline

### Gate Validation Best Practices

1. **Never bypass a gate** — Gates exist to prevent cascading failures
2. **Complete all checklist items** — Partial passes create technical debt
3. **Involve the right stakeholders** — PMO, Security, Architecture
4. **Document exceptions** — If a conditional pass is given, document why

---

## Rollback Strategy

### When to Rollback

```
ROLLBACK IF:
  - Data parity < 99% after reconciliation
  - Critical compliance violation discovered post-deploy
  - Performance degradation > 50% vs baseline
  - External integration failure affecting business

DO NOT ROLLBACK IF:
  - Minor formatting differences in data
  - Performance within 10% of baseline
  - Non-critical warnings from compliance
```

### Rollback Execution

1. Stop all active processing immediately
2. Revert in reverse dependency order
3. Use Delta Lake time travel for data reversion
4. Validate rollback completeness
5. Notify all stakeholders
6. Post-mortem within 24 hours

---

## Parallelism Guidelines

| Complexity | Max Parallel | Rationale |
|-----------|:------------|-----------|
| Low | 10 workers | Predictable, low risk |
| Medium | 5 workers | Moderate complexity, need oversight |
| High | 2 workers | Complex, benefits from serial attention |
| Critical | 1 worker | Must be hand-monitored |

---

## Communication Patterns

### Status Updates
- Every 30 minutes during active wave execution
- Immediately on gate pass/fail
- Immediately on escalation
- Daily summary email to stakeholders

### Escalation Matrix

| Severity | Response Time | Notification |
|----------|:-------------|-------------|
| Critical | 15 minutes | PagerDuty + Slack + Email |
| High | 1 hour | Slack + Email |
| Medium | 4 hours | Email |
| Low | Next business day | Email |
