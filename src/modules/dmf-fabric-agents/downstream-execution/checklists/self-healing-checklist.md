# Self-Healing Checklist

**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0

---

## Error Classification

- [ ] Validation report loaded from Vera ✅
- [ ] Compliance report loaded from Shield 🔒 (if applicable)
- [ ] Original generated code loaded from Coda ⚙️
- [ ] Stack trace parsed successfully
- [ ] Error class identified (syntax / semantic / runtime / compliance)
- [ ] Error matched against known patterns registry
- [ ] Confidence score ≥ 0.85 for known pattern (or flagged as novel)
- [ ] Error severity assessed (low / medium / high)

---

## Root Cause Analysis

- [ ] Root cause identified (not just symptoms)
- [ ] 5-Whys analysis performed for complex errors
- [ ] Blast radius assessed (impact on other pipeline components)
- [ ] Code snippet around error extracted (±5 lines minimum)
- [ ] LLM root cause analysis completed (for novel errors)
- [ ] Root cause documented in diagnosis report
- [ ] Similar errors in other pipelines flagged (if detected)

---

## Fix Application

- [ ] Fix strategy selected based on attempt number
  - [ ] Attempt 1: Rule-based fix
  - [ ] Attempt 2: LLM with alternative prompt
  - [ ] Attempt 3: LLM with different model
- [ ] Original code backed up before modification
- [ ] Fix applies minimal diff (smallest possible change)
- [ ] Fix does NOT alter business logic
- [ ] Fix preserves code style and formatting
- [ ] Fix diff size within limits (≤ 20 lines rule-based, ≤ 50 lines LLM)
- [ ] Fixed code saved to `fixed-code/{pipeline_id}.py`
- [ ] Attempt recorded in `healing-logs/{pipeline_id}_attempts.json`

---

## Fix Verification

- [ ] Fixed code re-submitted to Vera ✅ for validation
- [ ] Quality score before/after compared
- [ ] Score improvement confirmed (positive delta)
- [ ] No regression detected in any quality dimension
  - [ ] Syntax check: no regression
  - [ ] Semantic check: no regression
  - [ ] Test pass rate: no regression
  - [ ] Security scan: no regression
- [ ] If regression detected: fix reverted to backup
- [ ] Verification result logged in healing log
- [ ] Decision recorded: HEALED / PARTIAL / FAILED / REGRESSION

---

## Pattern Learning

- [ ] Error signature extracted from successful fix
- [ ] Fix template generalized (specific values → placeholders)
- [ ] Pattern stored in MLflow experiment
- [ ] Metrics logged: success rate, time to fix, lines changed
- [ ] Known patterns registry updated
- [ ] Auto-promotion evaluated (LLM fix → rule-based if ≥ 90% success)
- [ ] Learning summary saved to `learned-patterns/`

---

## Escalation Decision

- [ ] 3 attempts exhausted before escalating
- [ ] All attempt details documented in escalation report
- [ ] Root cause analysis included (even if incomplete)
- [ ] Blast radius assessment included
- [ ] Specific human assistance needed described
- [ ] Escalation sent to Orion 🧭 via healing log
- [ ] Pipeline status updated to "ESCALATED"
- [ ] Stakeholders notified of escalation
- [ ] Circuit breaker checked (5 consecutive failures → pause)

---

## Post-Healing

- [ ] Healing report generated (`*healing-report`)
- [ ] Healing metrics updated (rate, avg attempts, patterns)
- [ ] Fixed code routed to downstream flow
- [ ] Audit trail complete for all actions
- [ ] Knowledge base reflects latest learnings
