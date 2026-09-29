# ✅ Template: Validation Report

> **Template ID:** validation-report-tmpl
> **Agent:** Vera (Quality Gate)
> **Output:** `projects/{project_name}/outputs/midstream/quality/validation-reports/{pipeline_id}.md`
>
> **Source of truth:** This Markdown report is *derived* from the canonical
> [`quality-scores-tmpl.json`](./quality-scores-tmpl.json) scorecard. The visual
> stakeholder rendering is [`validation-scorecard-tmpl.html`](./validation-scorecard-tmpl.html).
> All three artifacts must agree — the JSON is the only file read by
> `validate_gate2_artifacts.py` for Gate 2 promotion.

---

## Template

```json
{
  "report_metadata": {
    "template": "validation-report-tmpl",
    "version": "1.0.0",
    "generated_by": "Vera ✅ — Quality Gate Agent",
    "factory": "AI-Agent Migration Factory™"
  },
  "pipeline": {
    "pipeline_id": "{{pipeline_id}}",
    "pipeline_name": "{{pipeline_name}}",
    "complexity_class": "{{complexity_class}}",
    "validation_timestamp": "{{timestamp}}",
    "validation_iteration": {{iteration_number}}
  },
  "input_artifacts": {
    "code_file": "projects/{project_name}/outputs/midstream/generated-code/{{pipeline_id}}.py",
    "test_file": "projects/{project_name}/outputs/midstream/generated-tests/{{pipeline_id}}_test.py",
    "pseudocode_file": "projects/{project_name}/outputs/upstream/logic/pseudocode/{{pipeline_id}}.json"
  },
  "dimension_results": {
    "syntax": {
      "score": {{syntax_score}},
      "weight": 0.15,
      "weighted_score": {{syntax_weighted}},
      "status": "{{syntax_status}}",
      "details": {
        "ast_parse": "{{ast_result}}",
        "py_compile": "{{compile_result}}",
        "import_resolution": "{{import_result}}",
        "errors": [
          {{#syntax_errors}}
          {
            "line": {{line}},
            "column": {{column}},
            "message": "{{message}}",
            "severity": "{{severity}}"
          }
          {{/syntax_errors}}
        ]
      }
    },
    "lint": {
      "score": {{lint_score}},
      "weight": 0.10,
      "weighted_score": {{lint_weighted}},
      "status": "{{lint_status}}",
      "details": {
        "pylint_score": {{pylint_score}},
        "flake8_violations": {{flake8_count}},
        "mypy_errors": {{mypy_errors}},
        "total_warnings": {{total_warnings}},
        "threshold": 10,
        "violations": [
          {{#lint_violations}}
          {
            "tool": "{{tool}}",
            "code": "{{code}}",
            "line": {{line}},
            "message": "{{message}}",
            "severity": "{{severity}}"
          }
          {{/lint_violations}}
        ]
      }
    },
    "semantic": {
      "score": {{semantic_score}},
      "weight": 0.30,
      "weighted_score": {{semantic_weighted}},
      "status": "{{semantic_status}}",
      "details": {
        "confidence": {{semantic_confidence}},
        "threshold": 0.90,
        "data_flow": {
          "score": {{data_flow_score}},
          "sources_expected": {{sources_expected}},
          "sources_found": {{sources_found}},
          "targets_expected": {{targets_expected}},
          "targets_found": {{targets_found}}
        },
        "business_rules": {
          "score": {{business_rules_score}},
          "total_rules": {{total_rules}},
          "exact_match": {{exact_match}},
          "partial_match": {{partial_match}},
          "missing": {{missing_rules}},
          "divergent": {{divergent_rules}}
        },
        "completeness": {
          "score": {{completeness_score}},
          "transformations_expected": {{transforms_expected}},
          "transformations_found": {{transforms_found}},
          "completeness_pct": {{completeness_pct}}
        },
        "llm_holistic": {
          "score": {{llm_score}},
          "confidence": {{llm_confidence}},
          "discrepancies": [
            {{#discrepancies}}
            {
              "type": "{{type}}",
              "description": "{{description}}",
              "severity": "{{severity}}",
              "pseudocode_ref": "{{pseudocode_ref}}",
              "code_ref": "{{code_ref}}"
            }
            {{/discrepancies}}
          ]
        }
      }
    },
    "tests": {
      "score": {{test_score}},
      "weight": 0.25,
      "weighted_score": {{test_weighted}},
      "status": "{{test_status}}",
      "details": {
        "total_tests": {{total_tests}},
        "passed": {{tests_passed}},
        "failed": {{tests_failed}},
        "errors": {{tests_errors}},
        "skipped": {{tests_skipped}},
        "pass_rate": {{pass_rate}},
        "duration_seconds": {{test_duration}},
        "coverage": {
          "line_rate": {{line_coverage}},
          "branch_rate": {{branch_coverage}},
          "lines_covered": {{lines_covered}},
          "lines_total": {{lines_total}},
          "uncovered_lines": [{{uncovered_lines}}]
        },
        "failures": [
          {{#test_failures}}
          {
            "test_name": "{{test_name}}",
            "reason": "{{reason}}",
            "traceback": "{{traceback}}"
          }
          {{/test_failures}}
        ]
      }
    },
    "performance": {
      "score": {{perf_score}},
      "weight": 0.10,
      "weighted_score": {{perf_weighted}},
      "status": "{{perf_status}}",
      "details": {
        "stages": {{stages}},
        "shuffles": {{shuffles}},
        "joins": [
          {{#joins}}
          {
            "type": "{{join_type}}",
            "strategy": "{{join_strategy}}",
            "optimal": {{is_optimal}}
          }
          {{/joins}}
        ],
        "anti_patterns": [
          {{#anti_patterns}}
          {
            "pattern": "{{pattern_name}}",
            "severity": "{{severity}}",
            "location": "{{location}}",
            "recommendation": "{{recommendation}}"
          }
          {{/anti_patterns}}
        ],
        "estimated_runtime_minutes": {{estimated_runtime}},
        "baseline_comparison": {
          "available": {{baseline_available}},
          "legacy_runtime": {{legacy_runtime}},
          "delta_pct": {{delta_pct}},
          "status": "{{baseline_status}}"
        },
        "recommendations": [
          {{#perf_recommendations}}
          {
            "finding": "{{finding}}",
            "recommendation": "{{recommendation}}",
            "estimated_improvement": "{{improvement}}",
            "priority": "{{priority}}"
          }
          {{/perf_recommendations}}
        ]
      }
    },
    "security": {
      "score": {{security_score}},
      "weight": 0.10,
      "weighted_score": {{security_weighted}},
      "status": "{{security_status}}",
      "details": {
        "total_findings": {{total_findings}},
        "high_critical": {{high_critical}},
        "medium": {{medium_findings}},
        "low": {{low_findings}},
        "findings": [
          {{#security_findings}}
          {
            "rule": "{{rule}}",
            "severity": "{{severity}}",
            "line": {{line}},
            "message": "{{message}}",
            "cwe": "{{cwe}}"
          }
          {{/security_findings}}
        ]
      }
    }
  },
  "scoring": {
    "final_score": {{final_score}},
    "decision": "{{decision}}",
    "route_to": "{{route_to}}",
    "hard_blockers": [
      {{#hard_blockers}}
      {
        "dimension": "{{dimension}}",
        "reason": "{{reason}}"
      }
      {{/hard_blockers}}
    ]
  },
  "feedback": {
    "summary": "{{feedback_summary}}",
    "failing_dimensions": [
      {{#failing_dimensions}}
      {
        "dimension": "{{dimension}}",
        "score": {{score}},
        "threshold": {{threshold}},
        "issues": [{{issues}}],
        "remediation": [{{remediation}}]
      }
      {{/failing_dimensions}}
    ],
    "re_validation_eligible": {{re_validation_eligible}},
    "max_iterations": 3,
    "current_iteration": {{current_iteration}}
  }
}
```

---

## Rendered Example

```
╔══════════════════════════════════════════════════════════╗
║ ✅ QUALITY GATE — VALIDATION REPORT                     ║
╠══════════════════════════════════════════════════════════╣
║ Pipeline:   PL_CUSTOMER_MASTER                          ║
║ Complexity: MEDIUM                                      ║
║ Iteration:  1                                           ║
║ Date:       2025-01-15 14:30:22 UTC                     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║ ┌──────────────┬───────┬────────┬──────────┬──────────┐ ║
║ │ Dimension    │ Score │ Weight │ Weighted │ Status   │ ║
║ ├──────────────┼───────┼────────┼──────────┼──────────┤ ║
║ │ Syntax       │ 10.0  │ 15%    │ 1.50     │ ✅ PASS  │ ║
║ │ Lint         │  8.5  │ 10%    │ 0.85     │ ✅ PASS  │ ║
║ │ Semantic     │  9.1  │ 30%    │ 2.73     │ ✅ PASS  │ ║
║ │ Tests        │  9.5  │ 25%    │ 2.38     │ ✅ PASS  │ ║
║ │ Performance  │  8.0  │ 10%    │ 0.80     │ ✅ PASS  │ ║
║ │ Security     │ 10.0  │ 10%    │ 1.00     │ ✅ PASS  │ ║
║ ├──────────────┼───────┼────────┼──────────┼──────────┤ ║
║ │ TOTAL        │       │ 100%   │ 9.26     │          │ ║
║ └──────────────┴───────┴────────┴──────────┴──────────┘ ║
║                                                          ║
║ FINAL SCORE: 9.3/10                                     ║
║ DECISION:    ✅ APPROVED                                ║
║ ROUTE TO:    Balance ⚖️                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## Usage Notes

- Template uses Mustache-style placeholders (`{{variable}}`)
- Array sections use `{{#array}}...{{/array}}` syntax
- All scores are on a 0.0–10.0 scale
- Weights must sum to 1.0 (100%)
- `decision` values: `APPROVED`, `NEEDS_REVIEW`, `REJECTED`
- `route_to` values: `Balance ⚖️`, `Human Reviewer`, `Phoenix 🔧`
- `re_validation_eligible` is `false` after 3 iterations
