# Verify Fix Task

**Task ID:** verify-fix  
**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0  
**Command:** `*verify`  
**Phase:** DOWNSTREAM

---

## Purpose

Re-submit the fixed code to Vera ✅ for validation. Compare quality scores before and after the fix. Confirm no regression was introduced. If the fix passes, trigger pattern learning; if it fails, trigger next attempt or escalation.

---

## Prerequisites

- Fix applied (`fixed-code/{pipeline_id}.py` exists)
- Diagnosis report available (`healing-logs/{pipeline_id}_diagnosis.json`)
- Attempt history available (`healing-logs/{pipeline_id}_attempts.json`)
- Vera ✅ (Quality Gate Agent) operational

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | Yes | Pipeline identifier |
| strict_mode | bool | No | Require score improvement ≥ 1.0 point (default: false) |

---

## Execution Steps

### Step 1: Load Context

```
LOAD fixed_code FROM fixed-code/{pipeline_id}.py
LOAD diagnosis FROM healing-logs/{pipeline_id}_diagnosis.json
LOAD attempt_history FROM healing-logs/{pipeline_id}_attempts.json

EXTRACT baseline_score = diagnosis.quality_score_before
EXTRACT current_attempt = len(attempt_history)
LOG "🔄 Verificando fix do pipeline {pipeline_id} (Tentativa #{current_attempt})"
```

### Step 2: Submit to Vera for Re-Validation

```
INVOKE @quality-gate *validate:
  pipeline_id: {pipeline_id}
  code_path: fixed-code/{pipeline_id}.py
  mode: "re-validation"
  context: "self-healing attempt #{current_attempt}"

AWAIT validation_result FROM Vera
EXTRACT:
  new_score = validation_result.quality_score
  new_decision = validation_result.decision  # approved | rejected | needs_review
  new_errors = validation_result.errors
  detailed_checks = validation_result.checks
```

### Step 3: Compare Before/After

```
CALCULATE score_delta = new_score - baseline_score
CALCULATE errors_delta = len(new_errors) - diagnosis.total_errors

GENERATE comparison:
  | Metric          | Before     | After      | Delta   |
  |-----------------|------------|------------|---------|
  | Quality Score   | {baseline} | {new}      | {delta} |
  | Total Errors    | {before}   | {after}    | {delta} |
  | Syntax Check    | {b_syntax} | {a_syntax} | {diff}  |
  | Semantic Check  | {b_seman}  | {a_seman}  | {diff}  |
  | Test Pass Rate  | {b_tests}  | {a_tests}  | {diff}  |
  | Security Scan   | {b_sec}    | {a_sec}    | {diff}  |

LOG "📊 Score: {baseline} → {new_score} (Δ{score_delta})"
```

### Step 4: Regression Check

```
FOR EACH check IN detailed_checks:
  IF check.after_score < check.before_score:
    FLAG regression on {check.name}
    LOG "⚠️ REGRESSÃO detectada em {check.name}: {before} → {after}"

IF any_regression_detected:
  REVERT to backup: healing-logs/{pipeline_id}_backup_attempt{n}.py
  LOG "🔙 Fix revertido devido a regressão. Tentando próxima estratégia."
  SET verification_result = "REGRESSION"
ELSE:
  SET verification_result = new_decision
```

### Step 5: Determine Next Action

```
MATCH verification_result:
  
  CASE "approved" (score ≥ 8.0):
    LOG "✅ FIX APROVADO! Pipeline {pipeline_id} curado na tentativa #{current_attempt}"
    LOG "📈 Score: {baseline} → {new_score} (+{score_delta})"
    TRIGGER *learn-pattern (auto-learn from successful fix)
    ROUTE fixed code to downstream flow
    SET status = "HEALED"
  
  CASE "needs_review" (score 6.0–7.9):
    LOG "⚠️ Fix parcial — score melhorou mas requer revisão humana"
    IF current_attempt < 3:
      LOG "🔄 Tentando próxima estratégia (Tentativa #{current_attempt + 1})"
      TRIGGER *fix with attempt_number = current_attempt + 1
    ELSE:
      LOG "📤 Escalando para revisão humana via Orion 🧭"
      TRIGGER escalation
    SET status = "PARTIAL"
  
  CASE "rejected" (score < 6.0):
    IF current_attempt < 3:
      LOG "❌ Fix não resolveu o problema. Score: {new_score}"
      LOG "🔄 Tentando próxima estratégia (Tentativa #{current_attempt + 1})"
      TRIGGER *fix with attempt_number = current_attempt + 1
    ELSE:
      LOG "❌ 3 tentativas esgotadas. Escalando para Orion 🧭"
      TRIGGER escalation with full_context
    SET status = "FAILED"
  
  CASE "REGRESSION":
    IF current_attempt < 3:
      LOG "🔙 Regressão detectada. Tentando estratégia diferente."
      TRIGGER *fix with attempt_number = current_attempt + 1
    ELSE:
      LOG "❌ Regressão na tentativa #3. Escalando para Orion 🧭"
      TRIGGER escalation with regression_details
    SET status = "REGRESSION"

UPDATE healing-logs/{pipeline_id}_attempts.json with verification result
```

### Step 6: Update Healing Log

```
APPEND to healing-logs/{pipeline_id}.json:
  verification:
    attempt: {current_attempt}
    timestamp: {now}
    baseline_score: {baseline}
    new_score: {new_score}
    score_delta: {score_delta}
    decision: {new_decision}
    regression_detected: {boolean}
    status: {status}
    next_action: {next_action}

LOG "📋 Verificação registrada no healing log"
```

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `healing-logs/{pipeline_id}.json` | JSON | Updated healing log with verification results |
| Vera re-validation result | JSON | Full validation report from Quality Gate |
| Console summary | Text | Before/after comparison table |

---

## Verification Decision Matrix

| Scenario | Score Delta | Regression? | Attempt | Action |
|----------|-----------|-------------|---------|--------|
| Full fix | ≥ +2.0 | No | Any | ✅ HEALED → Learn pattern |
| Partial fix | +0.1 to +1.9 | No | 1–2 | ⚠️ Try next strategy |
| Partial fix | +0.1 to +1.9 | No | 3 | ⚠️ Escalate for review |
| No improvement | 0 or negative | No | 1–2 | ❌ Try next strategy |
| No improvement | 0 or negative | No | 3 | ❌ Escalate |
| Regression | Any | Yes | 1–2 | 🔙 Revert, try next |
| Regression | Any | Yes | 3 | 🔙 Revert, escalate |
