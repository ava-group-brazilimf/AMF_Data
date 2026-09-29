# ✅ Task: Score Pipeline

> **Command:** `*score-pipeline`
> **Agent:** Vera (Quality Gate)
> **Phase:** MIDSTREAM | **Gate:** 2

---

## Objective

Calculate the final weighted quality score for a pipeline by aggregating all dimension scores (syntax, lint, semantic, tests, performance, security). Determine the approval decision based on the score and configured thresholds. This is the final step in the validation pipeline that produces the definitive verdict.

---

## Prerequisites

- [ ] All validation checks completed for `{pipeline_id}`
- [ ] Individual dimension scores available
- [ ] Thresholds loaded from `core-config.yaml`
- [ ] Decision routing rules configured

---

## Steps

### Step 1: Collect Dimension Scores

Gather all individual check results from the validation pipeline.

```
Required dimensions:
  syntax_score:   float (0.0–10.0)  — from Step 2 of validate-code
  lint_score:     float (0.0–10.0)  — from Step 3 of validate-code
  semantic_score: float (0.0–10.0)  — from semantic-equivalence task
  test_score:     float (0.0–10.0)  — from run-tests task
  perf_score:     float (0.0–10.0)  — from check-performance task
  security_score: float (0.0–10.0)  — from Step 7 of validate-code

Optional metadata:
  semantic_confidence: float (0.0–1.0)
  test_pass_rate:      float (0.0–100.0)
  test_coverage:       float (0.0–100.0)
  lint_warnings:       int
  security_findings:   int
```

**Validation:** All 6 dimension scores must be present. If any is missing, flag the missing check and use 0.0 as placeholder (which will likely trigger rejection).

---

### Step 2: Apply Weights

Calculate the weighted quality score using configured weights.

```python
# Weights from core-config.yaml
WEIGHTS = {
    "syntax":      0.15,
    "lint":        0.10,
    "semantic":    0.30,
    "tests":       0.25,
    "performance": 0.10,
    "security":    0.10
}

# Weighted calculation
weighted_score = (
    syntax_score   * WEIGHTS["syntax"] +
    lint_score     * WEIGHTS["lint"] +
    semantic_score * WEIGHTS["semantic"] +
    test_score     * WEIGHTS["tests"] +
    perf_score     * WEIGHTS["performance"] +
    security_score * WEIGHTS["security"]
)

# Round to 1 decimal place
final_score = round(weighted_score, 1)
```

---

### Step 3: Check Hard Blockers

Certain conditions override the score and force rejection regardless.

```
Hard Blockers (auto-REJECT):
  ❌ syntax_score == 0.0       → "Code has syntax errors"
  ❌ security_score == 0.0     → "Critical security vulnerabilities"
  ❌ test_pass_rate < 100%     → "Not all tests pass"
  ❌ semantic_confidence < 0.80 → "Semantic equivalence not verified"
  ❌ perf has cartesian product → "Cartesian product detected"

If any hard blocker is triggered:
  decision = "REJECTED"
  override_reason = blocker_description
  (score is recorded but does not change decision)
```

---

### Step 4: Determine Decision

Apply the decision matrix based on the final score.

```python
if has_hard_blocker:
    decision = "REJECTED"
    route_to = "Phoenix 🔧 (Self-Healing)"
elif final_score >= 8.0:
    decision = "APPROVED"
    route_to = "Balance ⚖️ (Reconciliation)"
elif final_score >= 6.0:
    decision = "NEEDS_REVIEW"
    route_to = "Human Reviewer"
else:
    decision = "REJECTED"
    route_to = "Phoenix 🔧 (Self-Healing)"
```

**Decision Matrix:**

| Score     | Hard Blocker | Decision       | Icon | Route To              |
|-----------|-------------|----------------|------|-----------------------|
| ≥ 8.0     | No           | APPROVED       | ✅    | Balance ⚖️            |
| 6.0–7.9   | No           | NEEDS_REVIEW   | ⚠️    | Human Reviewer        |
| < 6.0     | No           | REJECTED       | ❌    | Phoenix 🔧            |
| any       | Yes          | REJECTED       | ❌    | Phoenix 🔧            |

---

### Step 5: Generate Score Breakdown

Create a detailed score breakdown for transparency.

```
Score Breakdown:
┌────────────────┬────────┬────────┬───────────┬────────┐
│ Dimension      │ Score  │ Weight │ Weighted  │ Status │
├────────────────┼────────┼────────┼───────────┼────────┤
│ Syntax         │ 10.0   │ 15%    │ 1.50      │ ✅ PASS│
│ Lint           │  8.5   │ 10%    │ 0.85      │ ✅ PASS│
│ Semantic       │  9.1   │ 30%    │ 2.73      │ ✅ PASS│
│ Tests          │  9.5   │ 25%    │ 2.38      │ ✅ PASS│
│ Performance    │  8.0   │ 10%    │ 0.80      │ ✅ PASS│
│ Security       │ 10.0   │ 10%    │ 1.00      │ ✅ PASS│
├────────────────┼────────┼────────┼───────────┼────────┤
│ TOTAL          │        │ 100%   │ 9.26      │        │
│ FINAL SCORE    │  9.3   │        │           │ ✅     │
└────────────────┴────────┴────────┴───────────┴────────┘
```

---

### Step 6: Prepare Feedback (if rejected or needs_review)

Generate constructive feedback for remediation.

```
IF decision in ["REJECTED", "NEEDS_REVIEW"]:
  feedback = {
    "summary": "Pipeline {pipeline_id} {decision} with score {final_score}/10",
    "failing_dimensions": [
      {
        "dimension": "semantic",
        "score": 6.5,
        "threshold": 8.0,
        "issues": [
          "Business rule BR-003 partially implemented",
          "Missing null handling for column 'region_code'"
        ],
        "remediation": [
          "Review pseudocode step T-005 and ensure mapping is complete",
          "Add COALESCE(region_code, 'UNKNOWN') as per business rule"
        ]
      }
    ],
    "re_validation_eligible": true,
    "max_iterations": 3
  }
```

---

### Step 7: Persist Canonical Scorecard JSON (source of truth)

Render the canonical scorecard from `templates/quality-scores-tmpl.json`. This file is the SINGLE SOURCE OF TRUTH consumed by Orion (gate promotion), Phoenix (rejection feedback), Balance (downstream eligibility) and `validate_gate2_artifacts.py` in CI.

```
Template:  templates/quality-scores-tmpl.json
Output:    projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-quality-scores.json

Required transformations BEFORE writing the file:
  - Remove the _template_metadata block.
  - Replace every {{...}} placeholder with computed values.
  - Recompute kpis from objects_evaluated[] (do not trust template defaults).
  - Set decision = "REJECTED" if hard_blockers[] is non-empty (regardless of score).
  - Populate feedback.failing_dimensions[] for every dimension whose status != PASS.
  - Persist score rounded to 1 decimal place.
```

**Pass Criteria:** JSON validates against the template structure (all required keys present, weights sum to 1.00, decision ∈ {APPROVED, NEEDS_REVIEW, REJECTED}).

---

### Step 8: Render Markdown Validation Report

Generate the human-readable report consumed by reviewers and Scribe.

```
Template:  templates/validation-report-tmpl.md
Input:     projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-quality-scores.json
Output:    projects/{project_name}/outputs/midstream/quality/validation-reports/{pipeline_id}.md
```

The MD report MUST cite the canonical JSON it was derived from in its header so readers can trace back to the source of truth.

---

### Step 9: Render HTML Scorecard (stakeholder-facing)

Generate the visual scorecard for Gate 2 stakeholder review.

```
Template:  templates/validation-scorecard-tmpl.html
Input:     projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-quality-scores.json
Output:    projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-scorecard.html

Rendering rules (see template header comment for full spec):
  - Substitute every {{...}} placeholder; never leave placeholders in output.
  - Gauge: stroke-dashoffset = 691 * (1 - final_score / 10), rounded to integer.
  - Decision color (--c on .hero-gauge) and DECISION_COLOR_VAR:
      APPROVED      → teal
      NEEDS_REVIEW  → amber
      REJECTED      → red
  - Decision pill class: decision-approved | decision-review | decision-rejected.
  - Dimension bar fill width = score * 10 (e.g. 9.3 → 93%).
  - Dimension status pill: status-pass | status-warn | status-fail (based on score vs threshold).
  - Dimension --c color map: syntax→red, lint→coral, semantic→blue, tests→teal,
    performance→amber, security→purple.
  - Render BLOCKERS_BLOCK and FAILING_BLOCK empty-state when their source arrays are empty.
  - Aggregate findings across all dimensions[].findings[] in FINDINGS_BLOCK.
```

---

### Step 10: Record Decision and Route

Route to the appropriate downstream agent and update the migration tracker.

```
Save: projects/{project_name}/outputs/midstream/quality/validation-reports/{pipeline_id}.json

Route:
  IF APPROVED:
    Notify Balance ⚖️ with pipeline_id + validation_report
    Update migration tracker: status = "VALIDATED"

  IF NEEDS_REVIEW:
    Create review ticket with report + feedback
    Update migration tracker: status = "PENDING_REVIEW"

  IF REJECTED:
    Notify Phoenix 🔧 with pipeline_id + validation_report + feedback
    Update migration tracker: status = "REJECTED"
    Increment rejection_count for pipeline
    IF rejection_count >= 3:
      Escalate to human with "exceeded_max_iterations" flag
```

---

## Output

```json
{
  "pipeline_id": "{pipeline_id}",
  "check": "final_score",
  "timestamp": "2025-01-15T14:30:22Z",
  "final_score": 9.3,
  "decision": "APPROVED",
  "route_to": "Balance ⚖️",
  "hard_blockers": [],
  "dimension_scores": {
    "syntax":      { "score": 10.0, "weight": 0.15, "weighted": 1.50, "status": "PASS" },
    "lint":        { "score":  8.5, "weight": 0.10, "weighted": 0.85, "status": "PASS" },
    "semantic":    { "score":  9.1, "weight": 0.30, "weighted": 2.73, "status": "PASS" },
    "tests":       { "score":  9.5, "weight": 0.25, "weighted": 2.38, "status": "PASS" },
    "performance": { "score":  8.0, "weight": 0.10, "weighted": 0.80, "status": "PASS" },
    "security":    { "score": 10.0, "weight": 0.10, "weighted": 1.00, "status": "PASS" }
  },
  "metadata": {
    "semantic_confidence": 0.94,
    "test_pass_rate": 100.0,
    "test_coverage": 92.0,
    "lint_warnings": 3,
    "security_findings": 0,
    "rejection_count": 0
  },
  "feedback": null
}
```

---

## Scoring Examples

### Example 1: Perfect Pipeline (APPROVED)
| Dimension   | Score | Note                     |
|-------------|-------|--------------------------|
| Syntax      | 10.0  | Zero errors              |
| Lint        | 10.0  | Zero warnings            |
| Semantic    | 9.5   | Confidence 0.96          |
| Tests       | 10.0  | 8/8 pass, 95% coverage   |
| Performance | 9.0   | 10% faster than baseline |
| Security    | 10.0  | Zero findings            |
| **Final**   | **9.7**| **✅ APPROVED**          |

### Example 2: Minor Issues (APPROVED)
| Dimension   | Score | Note                     |
|-------------|-------|--------------------------|
| Syntax      | 10.0  | Zero errors              |
| Lint        | 7.5   | 8 warnings               |
| Semantic    | 9.0   | Confidence 0.92          |
| Tests       | 9.0   | 6/6 pass, 85% coverage   |
| Performance | 8.0   | Within baseline          |
| Security    | 8.0   | 2 low findings           |
| **Final**   | **8.8**| **✅ APPROVED**          |

### Example 3: Failing Tests (REJECTED)
| Dimension   | Score | Note                     |
|-------------|-------|--------------------------|
| Syntax      | 10.0  | Zero errors              |
| Lint        | 9.0   | 3 warnings               |
| Semantic    | 8.5   | Confidence 0.91          |
| Tests       | 3.0   | 4/6 pass, 72% coverage   |
| Performance | 7.0   | Minor issues             |
| Security    | 10.0  | Zero findings            |
| **Final**   | **7.2**| **❌ REJECTED** (hard blocker: test failures) |
