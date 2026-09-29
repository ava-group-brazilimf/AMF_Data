# ⚙️ Task: Batch Generate

> **Command:** `*batch-generate`
> **Agent:** Coda (Code Generator)
> **Phase:** MIDSTREAM | **Gate:** 2

---

## Objective

Generate code, tests, and job definitions for multiple pipelines in a single batch operation. Parallelizes generation across pipeline entries and produces an aggregated summary report.

---

## Prerequisites

- [ ] Batch definition file available (JSON)
- [ ] All referenced pseudocode files exist in `pseudocode/`
- [ ] Target platform configuration available: `target-config.yaml`
- [ ] Sufficient compute resources for parallel generation

---

## Batch Definition Format

```json
{
  "batch_id": "batch_wave1",
  "description": "Wave 1 — Core Master Data Pipelines",
  "created_by": "migration-coordinator",
  "created_at": "2026-02-13T10:00:00Z",
  "target_platform": "databricks",
  "pipelines": [
    {
      "pipeline_id": "PL_CUSTOMER_MASTER",
      "priority": 1,
      "complexity": "medium",
      "generate_tests": true,
      "generate_job": true,
      "optimize": true
    },
    {
      "pipeline_id": "PL_MATERIAL_BASIC",
      "priority": 2,
      "complexity": "low",
      "generate_tests": true,
      "generate_job": true,
      "optimize": false
    }
  ],
  "options": {
    "parallel_threads": 4,
    "stop_on_error": false,
    "yolo_for_low_complexity": true
  }
}
```

---

## Steps

### Step 1: Load and Validate Batch File

Parse the batch definition and validate all pipeline references.

```
Load:     batch_file.json
Validate:
  - All pipeline_ids have corresponding pseudocode files
  - Target platform is supported
  - No duplicate pipeline_ids
  - Priority ordering is consistent
```

**Output:** Validated batch manifest with pipeline count and estimated time.

---

### Step 2: Plan Parallel Execution

Organize pipelines into parallel execution groups based on priority and dependencies.

```
Execution Plan:
  Thread 1: PL_CUSTOMER_MASTER (medium) → PL_ORDER_HEADER (high)
  Thread 2: PL_MATERIAL_BASIC (low)     → PL_PRICE_LIST (low)
  Thread 3: PL_VENDOR_MASTER (medium)   → PL_PLANT_DATA (low)
  Thread 4: PL_BOM_EXPLOSION (high)     → PL_ROUTING (medium)

Estimated Total: ~45 seconds (parallel) vs ~180 seconds (sequential)
```

**Parallelization Rules:**
- Independent pipelines can run in parallel
- Dependent pipelines run sequentially within a thread
- Low-complexity pipelines are candidates for `*yolo` mode
- High-complexity pipelines get dedicated threads

---

### Step 3: Execute Generation Pipeline

For each pipeline in the batch, execute the full generation workflow.

```
FOR EACH pipeline IN batch.pipelines (parallel):
    1. *generate-code --pipeline={pipeline_id}
    2. IF pipeline.generate_tests:
         *generate-tests --pipeline={pipeline_id}
    3. IF pipeline.generate_job:
         *generate-job --pipeline={pipeline_id}
    4. IF pipeline.optimize:
         *optimize --pipeline={pipeline_id}
    5. Record results (status, metrics, errors)
```

**Status Tracking:**

| Status     | Description                                     |
|-----------|--------------------------------------------------|
| ✅ SUCCESS | All artifacts generated successfully             |
| ⚠️ WARNING | Generated with warnings (review recommended)    |
| ❌ FAILED  | Generation failed (see error details)            |
| ⏭️ SKIPPED | Skipped (dependency failed, stop_on_error=true) |

---

### Step 4: Aggregate Results

Collect results from all threads and compute batch-level metrics.

```
Metrics:
  - Total pipelines: N
  - Successful: X
  - Warnings: Y
  - Failed: Z
  - Total lines of code: LLL
  - Total test cases: TTT
  - Total generation time: SS seconds
  - Average time per pipeline: SS/N seconds
```

---

### Step 5: Generate Summary Report

Produce a comprehensive batch generation report.

```markdown
# Batch Generation Report: {batch_id}
## Summary
- Date: 2026-02-13
- Pipelines: 12
- Success: 11 | Warnings: 1 | Failed: 0
- Total code: 1,247 lines
- Total tests: 89 test cases
- Duration: 42.3 seconds

## Pipeline Details
| Pipeline           | Pattern     | Lines | Tests | Status | Time  |
|--------------------|-------------|-------|-------|--------|-------|
| PL_CUSTOMER_MASTER | SCD2        | 127   | 12    | ✅     | 4.2s  |
| PL_MATERIAL_BASIC  | Simple ETL  | 45    | 6     | ✅     | 1.8s  |
| PL_BOM_EXPLOSION   | Complex     | 210   | 15    | ⚠️     | 8.1s  |
| ...                | ...         | ...   | ...   | ...    | ...   |
```

---

## Output

| Artifact                                                        | Description                       |
|-----------------------------------------------------------------|-----------------------------------|
| `projects/{project_name}/outputs/midstream/generated-code/*.py`                           | Generated code for all pipelines  |
| `projects/{project_name}/outputs/midstream/generated-tests/*_test.py`                     | Tests for all pipelines           |
| `projects/{project_name}/outputs/midstream/job-definitions/*.json`                        | Job definitions for all pipelines |
| `projects/{project_name}/outputs/midstream/optimization-reports/*.md`                     | Optimization reports (if enabled) |
| `projects/{project_name}/outputs/midstream/generated-code/batch-report-{batch_id}.md`                    | Batch summary report              |

---

## Quality Gates

- [ ] All pipelines in batch attempted
- [ ] Success rate ≥ 90%
- [ ] No CRITICAL failures (data loss risk)
- [ ] All generated code compiles
- [ ] All tests pass
- [ ] Summary report generated with full details
- [ ] Failed pipelines have actionable error messages

---

## Error Handling

| Error Type               | Action                                     |
|--------------------------|---------------------------------------------|
| Missing pseudocode       | Skip pipeline, log error, continue batch    |
| Template not found       | Fall back to LLM generation                 |
| LLM timeout              | Retry once, then skip with error            |
| Schema validation fail   | Log warning, generate with best effort      |
| Out of memory            | Reduce parallelism, retry                   |

---

## Next Steps

After batch generation:
1. Review ⚠️ WARNING pipelines manually
2. Submit entire batch to Vera ✅ for validation
3. Re-run failed pipelines individually with `*generate-code`
