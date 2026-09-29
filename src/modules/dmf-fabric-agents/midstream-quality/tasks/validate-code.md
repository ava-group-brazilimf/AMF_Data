# ✅ Task: Full Validation Pipeline

> **Command:** `*validate`
> **Agent:** Vera (Quality Gate)
> **Phase:** MIDSTREAM | **Gate:** 2

---

## Objective

Run the complete validation pipeline against generated code and tests from Coda ⚙️. This is the master task that orchestrates all quality checks in sequence: syntax → lint → semantic → tests → performance → security → score.

---

## Prerequisites

- [ ] Generated code available: `generated-code/{pipeline_id}.py`
- [ ] Generated tests available: `generated-tests/{pipeline_id}_test.py`
- [ ] Pseudocode available: `pseudocode/{pipeline_id}.json`
- [ ] Validation thresholds loaded from `core-config.yaml`
- [ ] Required tools installed (Pylint, Flake8, mypy, Bandit, pytest)

---

## Steps

### Step 1: Load Artifacts

Load all required input artifacts and validate their existence.

```
Input artifacts:
  code_file:  projects/{project_name}/outputs/midstream/generated-code/{pipeline_id}.py
  test_file:  projects/{project_name}/outputs/midstream/generated-tests/{pipeline_id}_test.py
  pseudocode: projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json

Validate:
  - All files exist and are non-empty
  - Code file is valid UTF-8
  - Test file contains at least one test function
  - Pseudocode JSON is parseable
```

**Pass Criteria:** All 3 artifacts loaded successfully.
**Fail Action:** REJECT with `missing_artifacts` error.

---

### Step 2: Syntax Check (Weight: 15%)

Verify the generated code has zero syntax errors.

```
Check 1: Python AST Parse
  import ast
  ast.parse(open(code_file).read())

Check 2: py_compile
  python -m py_compile {code_file}

Check 3: Import Resolution
  Verify all imports reference available modules
```

**Scoring:**
| Result              | Score |
|---------------------|-------|
| Zero syntax errors  | 10.0  |
| 1–2 minor issues    | 5.0   |
| Any syntax error    | 0.0   |

**Pass Criteria:** Score ≥ 10.0 (zero syntax errors required)
**Fail Action:** REJECT immediately — syntax errors are blocking.

---

### Step 3: Lint Analysis (Weight: 10%)

Run static analysis tools and count warnings/errors.

```
Tool 1: Pylint
  pylint --output-format=json {code_file}
  Extract: score, messages[], conventions, refactors, warnings, errors

Tool 2: Flake8
  flake8 --format=json {code_file}
  Extract: violations[], per-rule counts

Tool 3: mypy
  mypy --json-report {code_file}
  Extract: type_errors[], coverage_percentage
```

**Scoring:**
| Warnings | Score |
|----------|-------|
| 0        | 10.0  |
| 1–5      | 9.0   |
| 6–10     | 7.5   |
| 11–20    | 5.0   |
| > 20     | 2.0   |

**Pass Criteria:** Total warnings ≤ 10 (from `max_lint_warnings` threshold)
**Fail Action:** Continue pipeline but flag for score reduction.

---

### Step 4: Semantic Equivalence (Weight: 30%)

Compare generated code against original pseudocode using LLM-based analysis.

```
Step 4a: Parse pseudocode structure
  Load pseudocode/{pipeline_id}.json
  Extract: sources[], transformations[], targets[], mappings[]

Step 4b: Parse generated code structure
  Analyze code_file AST
  Extract: read operations, transformations, write operations

Step 4c: LLM Comparison
  Prompt GPT-4 with pseudocode + generated code
  Ask for:
    - Data flow preservation (all sources read, all targets written)
    - Business rule alignment (transformations match pseudocode)
    - Transformation completeness (no missing logic)
    - Edge case handling (nulls, empty sets, type mismatches)

Step 4d: Structural Alignment
  Check 1:1 mapping between pseudocode steps and code functions
  Verify all mappings are implemented
```

**Scoring:**
| Confidence | Score |
|------------|-------|
| ≥ 0.95     | 10.0  |
| 0.90–0.94  | 9.0   |
| 0.85–0.89  | 7.5   |
| 0.80–0.84  | 6.0   |
| < 0.80     | 3.0   |

**Pass Criteria:** Confidence ≥ 0.90 (from `semantic_confidence` threshold)
**Fail Action:** REJECT if confidence < 0.80. Flag for review if 0.80–0.89.

---

### Step 5: Test Execution (Weight: 25%)

Execute pytest suite and measure coverage.

```
Command:
  pytest {test_file} --json-report --cov={module} --cov-report=json -v

Extract:
  - total_tests: int
  - passed: int
  - failed: int
  - errors: int
  - skipped: int
  - duration_seconds: float
  - coverage_percent: float
  - failure_details: [{test_name, reason, traceback}]
```

**Scoring:**
| Pass Rate | Coverage | Score |
|-----------|----------|-------|
| 100%      | ≥ 90%   | 10.0  |
| 100%      | 80–89%  | 9.0   |
| 100%      | 70–79%  | 7.5   |
| ≥ 90%     | ≥ 80%   | 6.0   |
| < 90%     | any     | 3.0   |

**Pass Criteria:** 100% pass rate AND coverage ≥ 80%
**Fail Action:** REJECT if any test fails. Flag for review if coverage < 80%.

---

### Step 6: Performance Analysis (Weight: 10%)

Analyze Spark execution plans and estimate performance.

```
Step 6a: Generate EXPLAIN plan
  df.explain(mode="extended")

Step 6b: Analyze plan for anti-patterns
  Check for:
    - Cartesian products (CRITICAL — auto-reject)
    - Full table scans on large tables
    - Missing broadcast hints for small tables
    - Suboptimal join strategies
    - Missing predicate pushdown

Step 6c: Compare against baseline (if available)
  Load legacy performance metrics
  Compare estimated runtime
  Flag regressions > 20%
```

**Scoring:**
| Result                    | Score |
|---------------------------|-------|
| No issues, within baseline| 10.0  |
| Minor issues, no regression| 8.0  |
| Some issues, regression < 20% | 6.0 |
| Cartesian product detected| 0.0   |
| Regression > 20%          | 4.0   |

**Pass Criteria:** No cartesian products AND no regression > 20%
**Fail Action:** Continue pipeline but flag for score reduction.

---

### Step 7: Security Scan (Weight: 10%)

Run security analysis to detect vulnerabilities.

```
Tool: Bandit
  bandit -r {code_file} -f json

Check for:
  - Hardcoded credentials/secrets
  - SQL injection patterns
  - Unsafe deserialization
  - Use of eval/exec
  - Insecure file operations
```

**Scoring:**
| Findings         | Score |
|------------------|-------|
| 0 findings       | 10.0  |
| Low only (≤ 3)   | 8.0   |
| Medium (≤ 3)     | 6.0   |
| High/Critical    | 0.0   |

**Pass Criteria:** Zero high/critical findings
**Fail Action:** REJECT if high/critical found. Flag for review if > 3 medium.

---

### Step 8: Calculate Final Score

Apply weights to each dimension score and determine decision.

```python
final_score = (
    syntax_score   * 0.15 +
    lint_score     * 0.10 +
    semantic_score * 0.30 +
    test_score     * 0.25 +
    perf_score     * 0.10 +
    security_score * 0.10
)

if final_score >= 8.0:
    decision = "APPROVED"
    route_to = "Balance ⚖️"
elif final_score >= 6.0:
    decision = "NEEDS_REVIEW"
    route_to = "Human Reviewer"
else:
    decision = "REJECTED"
    route_to = "Phoenix 🔧"
```

---

### Step 9: Generate Validation Report

Create comprehensive validation report and save to output folder. Generation MUST happen in this order:

```
1. Persist canonical JSON (source of truth):
     Template: templates/quality-scores-tmpl.json
     Output:   projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-quality-scores.json

2. Render Markdown report (derived):
     Template: templates/validation-report-tmpl.md
     Output:   projects/{project_name}/outputs/midstream/quality/validation-reports/{pipeline_id}.md

3. Render HTML scorecard (derived, stakeholder-facing):
     Template: templates/validation-scorecard-tmpl.html
     Output:   projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-scorecard.html
```

See `tasks/score-pipeline.md` Steps 7–9 for the full rendering specification (gauge math, dimension color map, decision class mapping, empty-state handling). The canonical JSON is the only artifact read by `validate_gate2_artifacts.py` for gate promotion.

---

## Output Artifacts

| Artifact                                                                | Description                                       |
|-------------------------------------------------------------------------|---------------------------------------------------|
| `projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-quality-scores.json`       | Canonical scorecard (single source of truth)      |
| `projects/{project_name}/outputs/midstream/quality/validation-reports/{pipeline_id}.md`                | Human-readable validation report                  |
| `projects/{project_name}/outputs/midstream/quality/scorecards/{pipeline_id}-scorecard.html`            | Visual scorecard (stakeholder review)             |
| `projects/{project_name}/outputs/midstream/quality/test-results/{pipeline_id}_test_results.json`       | Test execution results                            |
| `projects/{project_name}/outputs/midstream/quality/performance-reports/{pipeline_id}_perf.json`        | Performance analysis report                       |

---

## Error Handling

| Error                        | Action                                           |
|------------------------------|--------------------------------------------------|
| Missing code artifact        | REJECT with `missing_code` error                 |
| Missing test artifact        | REJECT with `missing_tests` error                |
| Missing pseudocode           | REJECT with `missing_pseudocode` error           |
| Tool execution failure       | Retry once, then REJECT with `tool_failure` error|
| LLM timeout                  | Retry with reduced context, then skip semantic   |
| pytest timeout (> 5 min)     | REJECT with `test_timeout` error                 |
