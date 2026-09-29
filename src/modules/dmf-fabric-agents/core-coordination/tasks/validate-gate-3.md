# Validate Gate 3 Task

**Task ID:** validate-gate-3  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*gate-3`  
**Phase:** CORE

---

## Purpose

Validate that DOWNSTREAM phase is complete — data reconciled, documentation generated, rollback tested — before going live to PRODUCTION.

---

## Execution Steps

### Step 1: Load Gate 3 Criteria

Load from `core-config.yaml` → `gate_criteria.gate_3`.

### Step 2: Check Required Artifacts

```
SCAN workspace for:
  - [ ] reconciliation-report.json (Balance ⚖️) — >= 99.9% parity
  - [ ] healing-log/*.json (Phoenix 🔧) — all errors resolved or escalated
  - [ ] migration-report.md (Scribe 📚) — executive + technical report
  - [ ] runbooks/ (Scribe 📚) — operational procedures documented
  - [ ] data-lineage-diagrams/ (Scribe 📚) — complete source → target lineage
```

### Step 3: Apply Quality Validations

```
CHECK 100% pipelines migrated and running on target
CHECK 99.9% data parity (row count + checksum)
CHECK performance >= 100% baseline on 95% queries
CHECK Dry Run executed successfully (min 2x)
CHECK Load Test approved
CHECK Regression Test suite 100% passing
CHECK all external integrations tested
CHECK rollback plan tested and documented
CHECK operations team trained
```

### Step 4: Determine Gate Result

```
IF all artifacts present AND all validations pass:
  → RESULT: ✅ GO
IF minor items pending (non-blocking):
  → RESULT: ⚠️ CONDITIONAL GO
IF critical items missing or parity below threshold:
  → RESULT: ❌ NO-GO
```

### Step 5: Generate Gate Report & Obtain Sign-offs

Use `gate-report-tmpl.md` template. Require:
- PM sign-off on final migration report
- Executive sponsor Go/No-Go decision
- Security Officer final compliance sign-off
- DBA production performance validation

---

## Output

Generate gate report in `projects/{project_name}/outputs/summary/gate-reports/gate-3-report-{date}.md`.
