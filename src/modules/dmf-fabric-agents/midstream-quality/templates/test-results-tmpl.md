# ✅ Template: Test Execution Results

> **Template ID:** test-results-tmpl
> **Agent:** Vera (Quality Gate)
> **Output:** `projects/{project_name}/outputs/midstream/quality/test-results/{pipeline_id}_test_results.json`

---

## Template

```json
{
  "report_metadata": {
    "template": "test-results-tmpl",
    "version": "1.0.0",
    "generated_by": "Vera ✅ — Quality Gate Agent",
    "factory": "AI-Agent Migration Factory™"
  },
  "pipeline": {
    "pipeline_id": "{{pipeline_id}}",
    "pipeline_name": "{{pipeline_name}}",
    "test_timestamp": "{{timestamp}}"
  },
  "test_file": {
    "path": "projects/{project_name}/outputs/midstream/generated-tests/{{pipeline_id}}_test.py",
    "valid": {{test_file_valid}},
    "total_test_functions": {{total_test_functions}},
    "has_fixtures": {{has_fixtures}},
    "has_spark_session": {{has_spark_session}}
  },
  "execution": {
    "command": "pytest {{test_file}} --cov={{module}} --cov-report=json -v --tb=long",
    "exit_code": {{exit_code}},
    "duration_seconds": {{total_duration}},
    "environment": {
      "python_version": "{{python_version}}",
      "pytest_version": "{{pytest_version}}",
      "spark_version": "{{spark_version}}",
      "spark_master": "local[2]",
      "shuffle_partitions": 2
    }
  },
  "summary": {
    "total": {{total_tests}},
    "passed": {{passed}},
    "failed": {{failed}},
    "errors": {{errors}},
    "skipped": {{skipped}},
    "pass_rate": {{pass_rate}},
    "result": "{{overall_result}}"
  },
  "tests": [
    {{#tests}}
    {
      "name": "{{test_name}}",
      "full_name": "{{test_full_name}}",
      "outcome": "{{outcome}}",
      "duration_seconds": {{duration}},
      "category": "{{category}}",
      "message": "{{message}}",
      "traceback": "{{traceback}}",
      "stdout": "{{stdout}}",
      "stderr": "{{stderr}}"
    }
    {{/tests}}
  ],
  "coverage": {
    "overall": {
      "line_rate": {{line_rate}},
      "branch_rate": {{branch_rate}},
      "lines_covered": {{lines_covered}},
      "lines_total": {{lines_total}},
      "lines_missed": {{lines_missed}},
      "branches_covered": {{branches_covered}},
      "branches_total": {{branches_total}},
      "branches_missed": {{branches_missed}}
    },
    "per_function": [
      {{#functions}}
      {
        "function_name": "{{function_name}}",
        "line_rate": {{fn_line_rate}},
        "lines_covered": {{fn_lines_covered}},
        "lines_total": {{fn_lines_total}},
        "missing_lines": [{{fn_missing_lines}}],
        "branch_rate": {{fn_branch_rate}}
      }
      {{/functions}}
    ],
    "uncovered_lines": [{{uncovered_lines}}],
    "uncovered_branches": [
      {{#uncovered_branches}}
      {
        "line": {{branch_line}},
        "branch": "{{branch_desc}}"
      }
      {{/uncovered_branches}}
    ]
  },
  "quality_analysis": {
    "test_categories": {
      "positive_tests": {{positive_count}},
      "negative_tests": {{negative_count}},
      "edge_case_tests": {{edge_case_count}},
      "positive_pct": {{positive_pct}},
      "negative_pct": {{negative_pct}},
      "edge_case_pct": {{edge_case_pct}}
    },
    "assertion_quality": {
      "total_assertions": {{total_assertions}},
      "schema_assertions": {{schema_assertions}},
      "row_count_assertions": {{row_count_assertions}},
      "value_assertions": {{value_assertions}},
      "generic_assertions": {{generic_assertions}}
    },
    "fixture_quality": {
      "spark_session_scoped": "{{spark_scope}}",
      "sample_data_representative": {{sample_representative}},
      "proper_cleanup": {{proper_cleanup}}
    },
    "quality_notes": [
      {{#quality_notes}}
      {
        "type": "{{note_type}}",
        "message": "{{note_message}}",
        "recommendation": "{{note_recommendation}}"
      }
      {{/quality_notes}}
    ]
  },
  "failures": [
    {{#failures}}
    {
      "test_name": "{{fail_test_name}}",
      "failure_type": "{{failure_type}}",
      "message": "{{fail_message}}",
      "traceback": "{{fail_traceback}}",
      "line_number": {{fail_line}},
      "suggestion": "{{fail_suggestion}}"
    }
    {{/failures}}
  ],
  "score": {
    "test_score": {{test_score}},
    "pass_rate_component": {{pass_rate_score}},
    "coverage_component": {{coverage_score}},
    "quality_component": {{quality_score}},
    "deductions": [
      {{#deductions}}
      {
        "reason": "{{deduction_reason}}",
        "amount": {{deduction_amount}}
      }
      {{/deductions}}
    ]
  }
}
```

---

## Rendered Example — All Tests Passing

```
╔══════════════════════════════════════════════════════════╗
║ ✅ TEST EXECUTION RESULTS                               ║
╠══════════════════════════════════════════════════════════╣
║ Pipeline: PL_CUSTOMER_MASTER                            ║
║ Date:     2025-01-15 14:30:22 UTC                       ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║ Summary:                                                ║
║   Total Tests:  5                                       ║
║   Passed:       5 ✅                                    ║
║   Failed:       0                                       ║
║   Errors:       0                                       ║
║   Skipped:      0                                       ║
║   Pass Rate:    100%                                    ║
║   Duration:     12.4s                                   ║
║                                                          ║
║ Tests:                                                  ║
║   ✅ test_transform_customer_data         (2.1s)        ║
║   ✅ test_null_handling                   (1.8s)        ║
║   ✅ test_empty_dataframe                 (1.2s)        ║
║   ✅ test_delta_merge                     (4.5s)        ║
║   ✅ test_schema_validation               (2.8s)        ║
║                                                          ║
║ Coverage:                                               ║
║   Line Coverage:   92% (46/50 lines)                    ║
║   Branch Coverage: 88% (22/25 branches)                 ║
║   Uncovered Lines: 23, 45, 67, 89                       ║
║                                                          ║
║ Score: 9.5/10                                           ║
╚══════════════════════════════════════════════════════════╝
```

---

## Rendered Example — With Failures

```
╔══════════════════════════════════════════════════════════╗
║ ❌ TEST EXECUTION RESULTS                               ║
╠══════════════════════════════════════════════════════════╣
║ Pipeline: PL_ORDER_HISTORY                              ║
║ Date:     2025-01-15 15:10:45 UTC                       ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║ Summary:                                                ║
║   Total Tests:  6                                       ║
║   Passed:       4 ✅                                    ║
║   Failed:       2 ❌                                    ║
║   Errors:       0                                       ║
║   Skipped:      0                                       ║
║   Pass Rate:    66.7%                                   ║
║   Duration:     18.2s                                   ║
║                                                          ║
║ Tests:                                                  ║
║   ✅ test_read_source_data                (1.5s)        ║
║   ✅ test_transform_orders                (3.2s)        ║
║   ❌ test_null_handling                   (2.1s)        ║
║   ✅ test_delta_merge                     (5.8s)        ║
║   ❌ test_edge_case_duplicates            (3.0s)        ║
║   ✅ test_schema_validation               (2.6s)        ║
║                                                          ║
║ Failures:                                               ║
║                                                          ║
║ ❌ test_null_handling:                                   ║
║   Type: AssertionError                                  ║
║   Message: Expected 0 nulls in 'region', found 3       ║
║   Line: 45                                              ║
║   Suggestion: Add COALESCE for 'region' column          ║
║                                                          ║
║ ❌ test_edge_case_duplicates:                            ║
║   Type: AssertionError                                  ║
║   Message: Expected 100 rows, got 103 (duplicates)      ║
║   Line: 78                                              ║
║   Suggestion: Add DISTINCT or dedup logic               ║
║                                                          ║
║ Coverage:                                               ║
║   Line Coverage:   72% (36/50 lines)                    ║
║   Branch Coverage: 65% (13/20 branches)                 ║
║                                                          ║
║ Score: 3.0/10                                           ║
╚══════════════════════════════════════════════════════════╝
```

---

## Usage Notes

- Template uses Mustache-style placeholders (`{{variable}}`)
- `outcome` values: `passed`, `failed`, `error`, `skipped`
- `category` values: `positive`, `negative`, `edge_case`
- `overall_result` values: `PASS` (100% pass rate), `FAIL` (any failure)
- `failure_type` values: `AssertionError`, `TypeError`, `ValueError`, `RuntimeError`, etc.
- `spark_scope` values: `session` (recommended), `function`, `module`
- Score deductions track specific reasons for point reduction
- Coverage `line_rate` and `branch_rate` are 0.0–1.0 (multiply by 100 for percentage)
