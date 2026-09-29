# Audit Trail Task

**Task ID:** audit-trail  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*audit`  
**Phase:** CORE

---

## Purpose

Display the complete audit trail of all decisions, gate validations, escalations, and agent executions for the migration.

---

## Execution Steps

### Step 1: Query Audit Log

```sql
SELECT timestamp, event_type, agent_name, pipeline_id, 
       wave_id, action, result, details
FROM audit_log
ORDER BY timestamp DESC
LIMIT 100
```

### Step 2: Format Audit Trail

Present as chronological table:

```
| Timestamp | Event | Agent | Pipeline | Action | Result |
|-----------|-------|-------|----------|--------|--------|
| 2026-02-13 10:30 | Gate Validation | Orion | — | Gate 1 | ✅ PASS |
| 2026-02-13 10:25 | Code Generation | Coda | p_045 | Generate PySpark | ✅ 45 LOC |
| 2026-02-13 10:20 | Self-Healing | Phoenix | p_032 | Fix type mismatch | ✅ Fixed |
```

### Step 3: Summary Statistics

```
Total events: {count}
Gate validations: {count} (pass: {n}, fail: {n})
Escalations: {count}
Self-healing attempts: {count} (success rate: {%})
Human interventions: {count}
```

---

## Output

Display audit trail in terminal. Optionally export to `projects/{project_name}/outputs/summary/audit-logs/`.
