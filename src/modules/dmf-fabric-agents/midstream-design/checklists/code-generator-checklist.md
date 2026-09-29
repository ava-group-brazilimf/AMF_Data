# ⚙️ Code Generator Agent — Quality Checklist

> **Agent:** Coda | **Phase:** MIDSTREAM | **Gate:** 2

---

## 1. Pre-Generation

- [ ] Pseudocode file loaded and validated (`pseudocode/{pipeline_id}.json`)
- [ ] Target platform configuration confirmed (`target-config.yaml`)
- [ ] Pipeline complexity classified (low / medium / high)
- [ ] Transformation pattern identified (ETL / Join / Aggregation / SCD2 / etc.)
- [ ] Code generation strategy selected (Template / LLM / Hybrid)
- [ ] Source schema definitions available and validated
- [ ] Target schema definitions available and validated
- [ ] All mapping rules present (no TODOs or placeholders)
- [ ] Upstream dependencies resolved (Logan 🧠 pseudocode approved)

---

## 2. Code Quality

- [ ] Code compiles/parses without syntax errors
- [ ] All imports are valid and available on target platform
- [ ] PEP 8 compliance (for Python/PySpark code)
- [ ] Functions documented with Google-style docstrings
- [ ] No function exceeds 50 lines
- [ ] No hardcoded values — all parameters externalized
- [ ] Structured logging included (start, end, metrics, errors)
- [ ] Error handling with specific exception types (not bare `except:`)
- [ ] Type hints included on function signatures
- [ ] Constants defined at module level, not inline
- [ ] Magic numbers replaced with named constants
- [ ] Code formatted as Databricks notebook with MAGIC cells
- [ ] Widget parameters for environment, load_date, schemas

---

## 3. Testing

- [ ] Unit test file generated (`{pipeline_id}_test.py`)
- [ ] Test fixtures created for SparkSession and sample data
- [ ] Positive test cases cover all transformation rules
- [ ] Negative test cases cover error handling paths
- [ ] Edge cases included (empty DataFrame, nulls, special characters)
- [ ] Code coverage ≥ 80%
- [ ] All tests pass locally (`pytest` exit code 0)
- [ ] Test execution time < 60 seconds
- [ ] No hardcoded file paths in tests
- [ ] Mock/stub for external dependencies (APIs, file systems)

---

## 4. Job Definition

- [ ] Valid JSON format (parseable by Databricks Jobs API)
- [ ] Schedule correctly mapped from legacy system
- [ ] Cluster sizing appropriate for data volume
- [ ] Autoscale configured with min/max workers
- [ ] Spark configuration includes Delta Lake optimizations
- [ ] Job parameters defined with defaults
- [ ] Email notifications configured for success/failure
- [ ] Webhook notifications configured (if applicable)
- [ ] Timeout set appropriately (not unlimited)
- [ ] Retry policy configured (max 2 retries)
- [ ] Job starts in PAUSED status (safety default)
- [ ] Tags include project, agent, and pipeline identifiers
- [ ] Max concurrent runs set to 1 (prevent overlap)

---

## 5. Optimization

- [ ] Spark explain plan analyzed (no cartesian products)
- [ ] Broadcast joins applied for small tables (< 100MB)
- [ ] Partition strategy defined and applied
- [ ] Partition file sizes within target range (100MB–1GB)
- [ ] Z-ORDER configured for frequently queried columns
- [ ] AQE (Adaptive Query Execution) enabled
- [ ] Skew join handling enabled
- [ ] Delta Lake auto-optimize enabled
- [ ] Delta Lake auto-compaction enabled
- [ ] Caching applied only for reused DataFrames (≥ 2 uses)
- [ ] Unpersist called after cache is no longer needed
- [ ] Optimization report generated with rationale

---

## 6. Post-Generation

- [ ] All output artifacts exist in `projects/{project_name}/outputs/midstream/generated-code/`
  - [ ] `generated-code/{pipeline_id}.py`
  - [ ] `generated-tests/{pipeline_id}_test.py`
  - [ ] `job-definitions/{pipeline_id}.json`
  - [ ] `optimization-reports/{pipeline_id}_optimization.md` (if optimized)
- [ ] Code reviewed by human (for autonomy level 2+)
- [ ] Artifacts handed off to Vera ✅ for quality validation
- [ ] Generation metrics logged (lines, time, strategy, coverage)
- [ ] Pipeline status updated in migration tracker
- [ ] Known issues or warnings documented
- [ ] Batch report generated (if batch operation)

---

## Sign-Off

| Role               | Name | Date | Status   |
|--------------------|------|------|----------|
| Code Generator     |      |      | ☐ Done   |
| Human Reviewer     |      |      | ☐ Done   |
| Quality Gate (Vera)|      |      | ☐ Done   |

---

> **Coda ⚙️** — *"Checklist completo. Código pronto para validação."*
