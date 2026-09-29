# Validate Gate 1 Task

**Task ID:** validate-gate-1  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*gate-1`  
**Phase:** CORE

---

## Purpose

Validate that UPSTREAM phase is complete and all required artifacts from Scout 🔍 and Logan 🧠 meet quality criteria before transitioning to MIDSTREAM.

---

## Execution Steps

### Step 1: Load Gate 1 Criteria

Load from `core-config.yaml` → `gate_criteria.gate_1`.

### Step 2: Check Required Artifacts

```
SCAN workspace for:
  - [ ] inventory.json (Scout 🔍) — all pipelines listed with classification
  - [ ] dependency-graph.json (Scout 🔍) — DAG without unresolved cycles
  - [ ] dead-code-report.md (Scout 🔍) — orphans identified and excluded
  - [ ] pseudocode/*.json (Logan 🧠) — confidence >= 85% for all pipelines
  - [ ] digital-twin.json (Logan 🧠) — semantic blueprint complete
```

### Step 3: Apply Quality Validations

```
CHECK 100% of pipelines in scope were scanned
CHECK complexity classification validated by SME
CHECK business logic reviewed by SME (20% sample)
CHECK zero unresolved dependency cycles
CHECK data volume estimated and approved
```

### Step 4: Determine Gate Result

```
IF all artifacts present AND all validations pass:
  → RESULT: ✅ PASS
IF artifacts present but some validations incomplete:
  → RESULT: ⚠️ CONDITIONAL (list conditions)
IF critical artifacts missing:
  → RESULT: ❌ FAIL (list missing items)
```

### Step 5: Generate Gate Report

Use `gate-report-tmpl.md` template. Record in audit trail.

---

## Output

Generate gate report in `projects/{project_name}/outputs/summary/gate-reports/gate-1-report-{date}.md`.
