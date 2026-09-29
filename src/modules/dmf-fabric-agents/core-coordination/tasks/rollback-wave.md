# Rollback Wave Task

**Task ID:** rollback-wave  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*rollback`  
**Phase:** CORE  
**Priority:** MANDATORY

---

## Purpose

Initiate and execute a controlled rollback of a migration wave, reverting deployed code and data to the pre-migration state.

---

## Prerequisites

- Wave must be in status "in_progress" or "completed_with_issues"
- Rollback plan must exist (rollback-plan-tmpl.md)
- Human PM approval REQUIRED (Level 1 autonomy)

---

## Execution Steps

### Step 1: Identify Rollback Scope

```
LOAD wave details from Migration Control DB
LIST all pipelines deployed in this wave
IDENTIFY dependent downstream consumers
CALCULATE blast radius
PRESENT to human for approval
```

### Step 2: Stop Active Processing

```
PAUSE all Celery workers for this wave
CANCEL pending pipeline executions
SET wave status = "rolling_back"
NOTIFY all agents to halt
```

### Step 3: Revert Target Platform

```
FOR EACH deployed pipeline (reverse order):
  REVERT Delta table to previous version (TIME TRAVEL)
  DISABLE or DELETE deployed job definition
  RESTORE previous schema if changed
  LOG rollback action in audit trail
```

### Step 4: Validate Rollback

```
VERIFY target tables restored to pre-migration state
RUN checksum validation against backup/snapshot
CONFIRM no orphaned resources
```

### Step 5: Generate Rollback Report

Use `rollback-plan-tmpl.md` template with actual results.

---

## Output

Generate rollback report in `projects/{project_name}/outputs/summary/rollback-plans/`.
