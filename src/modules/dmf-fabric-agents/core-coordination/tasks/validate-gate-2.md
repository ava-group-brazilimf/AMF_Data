# Validate Gate 2 Task

**Task ID:** validate-gate-2  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*gate-2`  
**Phase:** CORE

---

## Purpose

Validate that MIDSTREAM phase is complete — code generated, quality validated, and compliance approved — before transitioning to DOWNSTREAM.

---

## Execution Steps

### Step 1: Load Gate 2 Criteria

Load from `core-config.yaml` → `gate_criteria.gate_2`.

### Step 2: Check Required Artifacts

```
SCAN workspace for:
  - [ ] generated-code/*.py (Coda ⚙️) — compilable and executable on target
  - [ ] generated-tests/*_test.py (Coda ⚙️) — unit tests for each pipeline
  - [ ] job-definition/*.json (Coda ⚙️) — job definitions for target platform
  - [ ] validation-report/*.json with "approved" (Vera ✅) — score >= 8.0/10
  - [ ] compliance-report/*.json with "compliant" (Shield 🔒) — zero unmasked PII
```

### Step 3: Apply Quality Validations

```
CHECK >= 85% pipelines approved by Quality Gate on 1st attempt
CHECK >= 75% errors fixed by Self-Healing automatically
CHECK zero LGPD/SOX compliance violations
CHECK 100% unit tests passing
CHECK performance >= baseline (estimated)
CHECK PII masking applied and validated
```

### Step 4: Determine Gate Result

```
IF all artifacts present AND all validations pass:
  → RESULT: ✅ PASS
IF artifacts present but metrics below threshold:
  → RESULT: ⚠️ CONDITIONAL
IF critical artifacts missing or compliance violations:
  → RESULT: ❌ FAIL
```

### Step 5: Generate Gate Report

Use `gate-report-tmpl.md` template. Record in audit trail.

---

## Output

Generate gate report in `projects/{project_name}/outputs/summary/gate-reports/gate-2-report-{date}.md`.
