# Error Analysis Template
# Template ID: error-analysis-tmpl
# Agent: Phoenix (Self-Healing)
# Version: 1.0

---

# 🔍 Deep Error Analysis

**Pipeline:** {pipeline_id}  
**Date:** {analysis_date}  
**Analyst:** Phoenix (Self-Healing Agent)  
**Severity:** {severity_icon} {severity}

---

## Error Summary

| Field | Value |
|-------|-------|
| Error Class | {error_class} |
| Error Message | {error_message} |
| File | {file_name} |
| Line | {line_number} |
| Function | {function_name} |
| Pattern ID | {pattern_id} — {pattern_description} |
| Classification | {known_or_novel} |
| Confidence | {confidence}% |

---

## Stack Trace

```
{full_stack_trace}
```

---

## Code Context

```python
# Lines {start_line}–{end_line} of {file_name}
{code_snippet_with_error_highlighted}
```

---

## Root Cause Tree

```
{pipeline_id} Pipeline Failure
│
├── Immediate Cause
│   └── {immediate_cause}
│       └── Evidence: {evidence_1}
│
├── Intermediate Cause
│   └── {intermediate_cause}
│       └── Evidence: {evidence_2}
│
└── Root Cause
    └── {root_cause}
        └── Evidence: {evidence_3}
```

### 5-Whys Analysis

| # | Question | Answer |
|---|----------|--------|
| 1 | Why did the pipeline fail? | {answer_1} |
| 2 | Why did {cause_1} happen? | {answer_2} |
| 3 | Why did {cause_2} happen? | {answer_3} |
| 4 | Why did {cause_3} happen? | {answer_4} |
| 5 | Why did {cause_4} happen? | {answer_5} |

**Root Cause:** {definitive_root_cause}

---

## Blast Radius Assessment

### Direct Impact

| Component | Affected? | Description |
|-----------|:---------:|-------------|
| Current pipeline | ✅ | {direct_impact} |
| Downstream pipelines | {icon} | {downstream_impact} |
| Data consumers | {icon} | {consumer_impact} |
| Other waves | {icon} | {wave_impact} |

### Indirect Impact

| Area | Risk Level | Description |
|------|:----------:|-------------|
| Data quality | {risk_icon} | {dq_impact} |
| Performance | {risk_icon} | {perf_impact} |
| Compliance | {risk_icon} | {compliance_impact} |
| Schedule | {risk_icon} | {schedule_impact} |

**Overall Blast Radius:** {blast_radius_level} — {blast_radius_summary}

---

## Recommended Fix

### Primary Recommendation

**Strategy:** {recommended_strategy}  
**Confidence:** {fix_confidence}%  
**Estimated Time:** {estimated_time}

```python
# Recommended code change:
{recommended_fix_code}
```

**Rationale:** {fix_rationale}

### Alternative Approaches

| # | Approach | Pros | Cons | Risk |
|---|---------|------|------|------|
| 1 | {approach_1} | {pros} | {cons} | {risk} |
| 2 | {approach_2} | {pros} | {cons} | {risk} |

---

## Prevention

### How to Prevent This Error in Future

| # | Prevention Measure | Applied To | Description |
|---|-------------------|-----------|-------------|
| 1 | {measure_1} | {target} | {description} |
| 2 | {measure_2} | {target} | {description} |
| 3 | {measure_3} | {target} | {description} |

### Upstream Agent Feedback

| Agent | Feedback | Action |
|-------|----------|--------|
| {agent_name} | {feedback} | {suggested_action} |

---

## Related Errors

| Pipeline | Error | Similarity | Same Root Cause? |
|----------|-------|-----------|:----------------:|
| {pipeline_id} | {error} | {similarity}% | {icon} |

---

## Metadata

| Field | Value |
|-------|-------|
| Analysis Duration | {duration_minutes} min |
| LLM Calls Made | {llm_calls} |
| Patterns Consulted | {patterns_checked} |
| Analysis Revision | {revision} |
