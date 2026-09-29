# ✅ Quality Gate Agent — Quality Checklist

> **Agent:** Vera | **Phase:** MIDSTREAM | **Gate:** 2

---

## 1. Pre-Validation

- [ ] Generated code file loaded (`generated-code/{pipeline_id}.py`)
- [ ] Generated test file loaded (`generated-tests/{pipeline_id}_test.py`)
- [ ] Pseudocode file loaded (`pseudocode/{pipeline_id}.json`)
- [ ] All three artifacts are non-empty and valid UTF-8
- [ ] Validation thresholds loaded from `core-config.yaml`
- [ ] Required tools available (Pylint, Flake8, mypy, Bandit, pytest)
- [ ] Output directory initialized (`projects/{project_name}/outputs/midstream/quality/`)
- [ ] Pipeline metadata available (data volume, complexity class)
- [ ] Upstream dependencies confirmed (Coda ⚙️ + Logan 🧠 completed)

---

## 2. Syntax & Lint

### Syntax
- [ ] Python AST parse succeeds with zero errors
- [ ] `py_compile` succeeds with zero errors
- [ ] All imports reference available modules
- [ ] No undefined variables detected
- [ ] No unreachable code blocks

### Lint
- [ ] Pylint score ≥ 8.0/10
- [ ] Flake8 violations ≤ 10
- [ ] mypy type check passes (no critical type errors)
- [ ] PEP 8 compliance verified
- [ ] No bare `except:` clauses
- [ ] No hardcoded values — all parameters externalized
- [ ] Function docstrings present (Google-style)
- [ ] No function exceeds 50 lines
- [ ] Type hints on function signatures
- [ ] Total lint warnings ≤ 10 (threshold)

---

## 3. Semantic Equivalence

- [ ] Pseudocode structure parsed (sources, transformations, targets, mappings)
- [ ] Generated code structure extracted (reads, transforms, writes)
- [ ] All sources from pseudocode are read in generated code
- [ ] All targets from pseudocode are written in generated code
- [ ] No extra sources/targets introduced (except temp views)
- [ ] Business rules verified 1:1 against pseudocode
- [ ] Transformation completeness ≥ 95%
- [ ] Data flow preservation confirmed
- [ ] Null handling consistent with pseudocode
- [ ] LLM holistic comparison confidence ≥ 0.90
- [ ] No divergent business rules detected
- [ ] Edge case handling present (nulls, empty sets, type mismatches)

---

## 4. Test Execution

- [ ] Test file contains ≥ 1 test function
- [ ] pytest executes without framework errors
- [ ] All tests pass (100% pass rate)
- [ ] Line coverage ≥ 80%
- [ ] Branch coverage measured and reported
- [ ] Positive tests cover all transformation rules (≥ 60% of tests)
- [ ] Negative tests cover error handling (≥ 20% of tests)
- [ ] Edge case tests present (≥ 10% of tests)
- [ ] Test fixtures properly scoped (SparkSession, sample data)
- [ ] Assertions are specific (not just `assert True`)
- [ ] Test execution time < 300 seconds (5 min timeout)
- [ ] No hardcoded file paths in tests

---

## 5. Performance Analysis

- [ ] Spark EXPLAIN plan generated successfully
- [ ] No cartesian products detected (CRITICAL — auto-reject)
- [ ] No BroadcastNestedLoopJoin detected
- [ ] Broadcast hints applied for small tables (< 100MB)
- [ ] Predicate pushdown verified (filters before scan)
- [ ] Partition pruning verified (partition column in WHERE)
- [ ] No Coalesce(1) on large datasets
- [ ] No collect()/toPandas() on large datasets
- [ ] UDFs justified (no native function alternative)
- [ ] Caching applied appropriately (≥ 2 uses to justify)
- [ ] AQE (Adaptive Query Execution) enabled
- [ ] Join strategies optimal for data sizes
- [ ] Runtime estimate within 20% of legacy baseline
- [ ] No performance regressions > 20%

---

## 6. Security Scan

- [ ] Bandit scan executed successfully
- [ ] Zero high/critical severity findings
- [ ] Medium severity findings ≤ 3
- [ ] No hardcoded credentials or secrets
- [ ] No SQL injection patterns
- [ ] No use of `eval()` or `exec()`
- [ ] No unsafe deserialization
- [ ] No insecure file operations (path traversal)
- [ ] Connection strings use environment variables or secrets manager

---

## 7. Scoring & Decision

### Score Calculation
- [ ] All 6 dimension scores collected (syntax, lint, semantic, tests, perf, security)
- [ ] Weights applied correctly (15%, 10%, 30%, 25%, 10%, 10%)
- [ ] Weighted score calculated and rounded to 1 decimal
- [ ] Hard blockers checked before final decision
- [ ] No missing dimension scores

### Decision
- [ ] Decision determined by score and blockers
- [ ] If APPROVED (≥ 8.0): routed to Balance ⚖️
- [ ] If NEEDS_REVIEW (6.0–7.9): escalated to human reviewer
- [ ] If REJECTED (< 6.0 or hard blocker): routed to Phoenix 🔧
- [ ] Constructive feedback generated for rejected/review pipelines
- [ ] Rejection count tracked (max 3 iterations before escalation)

### Reporting
- [ ] Validation report generated (`validation-reports/{pipeline_id}.json`)
- [ ] Test results report generated (`test-results/{pipeline_id}_test_results.json`)
- [ ] Performance report generated (`performance-reports/{pipeline_id}_perf.json`)
- [ ] Pipeline status updated in migration tracker
- [ ] Downstream agent notified with report
- [ ] Audit trail recorded
