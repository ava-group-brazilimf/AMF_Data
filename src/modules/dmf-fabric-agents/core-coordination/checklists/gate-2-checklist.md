# Gate 2 Checklist — MIDSTREAM → DOWNSTREAM

**Agent:** Orion (Migration Coordinator)  
**Gate:** Gate 2 (Transformation → Validation)  
**Version:** 1.0

---

## Required Artifacts

- [ ] `generated-code/*.py` (Coda ⚙️) — compilable and executable
  - [ ] One file per pipeline
  - [ ] PySpark/SQL code follows best practices
  - [ ] Delta Lake integration implemented
- [ ] `generated-tests/*_test.py` (Coda ⚙️) — unit tests
  - [ ] One test file per pipeline
  - [ ] Positive and negative test cases
  - [ ] Edge cases covered
- [ ] `job-definition/*.json` (Coda ⚙️) — target platform jobs
  - [ ] Schedule matches source
  - [ ] Cluster configuration appropriate
  - [ ] Parameters correctly mapped
- [ ] `validation-report/*.json` (Vera ✅) — score >= 8.0
  - [ ] Syntax check passed
  - [ ] Semantic equivalence verified
  - [ ] All unit tests passing
  - [ ] Performance check acceptable
- [ ] `compliance-report/*.json` (Shield 🔒) — compliant
  - [ ] Zero unmasked PII fields
  - [ ] LGPD/SOX requirements met
  - [ ] Audit trail enabled

---

## Validations

- [ ] >= 85% pipelines approved by Quality Gate on 1st attempt
- [ ] >= 75% errors fixed by Self-Healing automatically
- [ ] Zero LGPD/SOX compliance violations
- [ ] 100% unit tests passing
- [ ] Performance >= baseline (estimated)
- [ ] PII masking applied and validated

---

## Approvals

- [ ] Tech Lead approved generated code (10% sample)
- [ ] Security Officer approved compliance reports
- [ ] PM approved wave success rate

---

## Decision Criteria

### PASS Conditions (ALL required)
- [ ] All 5 required artifacts present
- [ ] All 6 validations pass
- [ ] All 3 approvals obtained

### CONDITIONAL Conditions
- [ ] First-attempt success rate 80-85% (below target but acceptable)
- [ ] Minor performance warnings (non-blocking)

### FAIL Conditions (ANY applies)
- [ ] Compliance violations found
- [ ] First-attempt success rate < 80%
- [ ] Unit test failures unresolved

---

**Status:** [ ] PASS  [ ] CONDITIONAL  [ ] FAIL  
**Validated by:** ___________________  **Date:** ___/___/______
