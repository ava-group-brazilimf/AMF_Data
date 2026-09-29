# Escalation Task

**Task ID:** escalate  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*escalate`  
**Phase:** CORE

---

## Purpose

Formally escalate an issue to the human team when automated resolution has been exhausted (Phoenix failed after 3 attempts, compliance violation, or critical decision required).

---

## Execution Steps

### Step 1: Classify Escalation

```
DETERMINE escalation type:
  - TECHNICAL: Code fix beyond Self-Healing capability
  - COMPLIANCE: Unresolvable security/privacy issue
  - BUSINESS: Business rule ambiguity requiring SME
  - DECISION: Go/No-Go or scope change requiring PM
  - CRITICAL: Data loss risk or system failure
```

### Step 2: Collect Context

```
GATHER:
  - Pipeline ID and wave context
  - Error details and root cause analysis
  - All attempts made (healing-log)
  - Impact assessment (blast radius)
  - Recommended actions
```

### Step 3: Route to Appropriate Human

```
TECHNICAL → Tech Lead + assigned engineer
COMPLIANCE → Security Officer + DPO
BUSINESS → SME + Business Analyst
DECISION → PM + Sponsor
CRITICAL → PM + Tech Lead + Security (all)
```

### Step 4: Notify via Channels

```
SEND notification via:
  - Slack (channel: #migration-escalations)
  - PagerDuty (if CRITICAL)
  - Email (PM always CC'd)
INCLUDE: context, impact, recommended actions, deadline
```

### Step 5: Record in Audit Trail

Log escalation with full context in audit trail.

---

## Output

Escalation ticket created with tracking ID.
