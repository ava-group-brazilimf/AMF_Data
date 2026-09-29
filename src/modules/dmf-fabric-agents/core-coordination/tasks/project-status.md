# Project Status Task

**Task ID:** project-status  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*status`  
**Phase:** CORE

---

## Purpose

Generate a comprehensive migration status report showing current wave progress, completed pipelines, failed items, agent performance, and recommended next steps.

---

## Execution Steps

### Step 1: Scan Migration Control DB

Query current state of all waves and pipelines:

```sql
SELECT wave_id, status, COUNT(*) as pipelines,
       SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
       SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed
FROM migrations
GROUP BY wave_id, status
```

### Step 2: Determine Current Phase

```
IF no waves started:
  → Phase: NOT STARTED
  → Next: Run *start-wave with pilot wave

IF active wave in UPSTREAM:
  → Phase: UPSTREAM (Discovery in progress)
  → Next: Wait for Scout and Logan to complete

IF Gate 1 not passed:
  → Phase: UPSTREAM (Ready for Gate 1)
  → Next: Run *gate-1

IF active wave in MIDSTREAM:
  → Phase: MIDSTREAM (Code Generation in progress)
  → Next: Monitor Coda, Vera, Shield progress

IF Gate 2 not passed:
  → Phase: MIDSTREAM (Ready for Gate 2)
  → Next: Run *gate-2

IF active wave in DOWNSTREAM:
  → Phase: DOWNSTREAM (Reconciliation in progress)
  → Next: Monitor Balance and Scribe

IF Gate 3 not passed:
  → Phase: DOWNSTREAM (Ready for Gate 3)
  → Next: Run *gate-3

IF all waves completed:
  → Phase: MIGRATION COMPLETE
  → Next: Generate final report with Scribe
```

### Step 3: Collect Agent Metrics

```
FOR EACH agent:
  GET execution_count, success_rate, avg_time
  GET current_status (idle, active, error)
```

### Step 4: Generate Status Report

Use `wave-status-report-tmpl.md` template with collected data.

---

## Output

Generate migration status report in `projects/{project_name}/outputs/summary/status-reports/`.
