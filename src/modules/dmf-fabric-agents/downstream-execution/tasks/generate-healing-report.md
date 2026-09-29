# Generate Healing Report Task

**Task ID:** generate-healing-report  
**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0  
**Command:** `*healing-report`  
**Phase:** DOWNSTREAM


---

## Purpose

Generate a comprehensive healing report with all diagnosis attempts, fix strategies used, success/failure outcomes, patterns learned, time spent, and escalations needed. Provides actionable summary for stakeholders and audit trail.

---

## Prerequisites

- At least one healing cycle completed for the pipeline(s)
- Healing logs available in `healing-logs/`

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | No | Specific pipeline (omit for full report) |
| scope | string | No | "pipeline", "wave", or "project" (default: "pipeline") |
| wave_id | string | No | Wave identifier (for wave-level reports) |
| include_diffs | bool | No | Include code diffs in report (default: false) |

---

## Execution Steps

### Step 1: Collect Healing Data

```
IF pipeline_id provided:
  LOAD healing-logs/{pipeline_id}.json
  LOAD healing-logs/{pipeline_id}_attempts.json
  LOAD healing-logs/{pipeline_id}_diagnosis.json
  SET scope = "pipeline"
ELSE IF wave_id provided:
  LOAD ALL healing-logs/*.json for pipelines in wave
  SET scope = "wave"
ELSE:
  LOAD ALL healing-logs/*.json
  SET scope = "project"

LOG "📊 Coletando dados de healing ({scope}): {count} pipelines"
```

### Step 2: Calculate Metrics

```
CALCULATE aggregate metrics:
  total_pipelines: count(status IN ["HEALED", "ESCALATED", "PARTIAL", "IN_PROGRESS"])
  healed_count: count(status == "HEALED")
  escalated_count: count(status == "ESCALATED")
  partial_count: count(status == "PARTIAL")
  in_progress_count: count(status == "IN_PROGRESS")
  
  healing_rate: healed_count / (healed_count + escalated_count + partial_count) * 100
  success_rate: healed_count / total_pipelines * 100
  escalation_rate: escalated_count / total_pipelines * 100
  
  avg_attempts: mean(successful_attempt_number)
  median_attempts: median(successful_attempt_number)
  avg_time_seconds: mean(fix_duration_minutes) * 60
  median_time_seconds: median(fix_duration_minutes) * 60
  min_time_seconds: min(fix_duration_minutes) * 60
  max_time_seconds: max(fix_duration_minutes) * 60
  
  strategy_breakdown:
    rule_based_success: count(strategy == "rule_based" AND success)
    llm_alt_prompt_success: count(strategy == "llm_alternative_prompt" AND success)
    llm_diff_model_success: count(strategy == "llm_different_model" AND success)
  
  error_distribution:
    FOR EACH pattern_id:
      count, success_rate, avg_attempts
  
  patterns_learned: count(new patterns added to MLflow)
  patterns_promoted: count(patterns promoted to rule-based)
  regressions_detected: count(regression events)
  
  hours_saved: estimated_human_hours_saved
  cost_savings: estimated_human_hours_saved * hourly_rate

  GENERATE:
  report_id: unique ID
  report_date: current timestamp

DETERMINE:
  pipeline_status:
    IF no escalations → COMPLETED_SUCCESSFUL
    IF escalations exist → COMPLETED_WITH_ESCALATIONS
    IF running → IN_PROGRESS

  recommended_action:
    IF success_rate >= 95 → CONTINUE
    IF success_rate between 70–94 → MONITOR
    IF success_rate < 70 → ESCALATE

  confidence_level:
    based on consistency of fixes / variance of results

LOG "📈 Healing rate: {healing_rate}% ({healed_count}/{total_pipelines})"
```

### Step 3: Generate Report

```
LOAD template FROM templates/healing-report-tmpl.md

POPULATE template with:
  - Header (pipeline/wave/project info, report_id, report_date, agent)
  - Executive Summary (healing rate, key metrics)
  - Error Distribution rows in `{{ERROR_DISTRIBUTION_ROWS}}`
  - Attempt Details in `{{FIX_ATTEMPTS_BLOCK}}`
  - Strategy Effectiveness (which strategies work best)
  - Patterns Learned (new patterns from this cycle)
  - Escalations (details of what couldn't be fixed)
  - Recommendations (improvements, new patterns to create)
  - Appendix (diffs if include_diffs == true)

SAVE report to:
  IF scope == "pipeline":
    projects/{project_name}/outputs/downstream/healing/error-analysis/{pipeline_id}_healing-report.md
  ELSE IF scope == "wave":
    projects/{project_name}/outputs/downstream/healing/error-analysis/{wave_id}_healing-report.md
  ELSE:
    projects/{project_name}/outputs/downstream/healing/error-analysis/project-healing-report.md
```

### Step 4: Generate Summary Table

```
DISPLAY summary:

┌────────────────────────────────────────────────────────┐
│              🔧 HEALING REPORT SUMMARY                 │
├────────────────────────────────────────────────────────┤
│  Scope: {scope}           Date: {report_date}          │
│  Pipelines Processed: {total_pipelines}                │
│                                                        │
│  ✅ Healed:      {healed_count}  ({healing_rate}%)     │
│  ⚠️ Partial:     {partial_count}                       │
│  ❌ Escalated:   {escalated_count}                     │
│  🔄 In Progress: {in_progress_count}                   │
│                                                        │
│  Avg Attempts:   {avg_attempts}                        │
│  Avg Fix Time:   {avg_time_seconds}s                   │
│  Patterns Learned: {patterns_learned}                  │
│  Cost Savings:   ~{hours_saved} hours saved            │
└────────────────────────────────────────────────────────┘
```

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `projects/{project_name}/outputs/downstream/healing/error-analysis/{id}_healing-report.md` | Markdown | Full healing report |
| Console summary | Text | Quick summary table |

---

## Report Sections

1. **Executive Summary** — High-level healing rate and key takeaways
2. **Error Distribution** — Breakdown by error type/pattern
3. **Fix Attempt Details** — Per-pipeline, per-attempt breakdown
4. **Strategy Effectiveness** — Success rates by strategy (rule/LLM/model)
5. **Patterns Learned** — New patterns added to knowledge base
6. **Regressions** — Any regressions detected and how handled
7. **Escalations** — What was escalated and why
8. **Time Analysis** — Time spent per pipeline, per attempt
9. **Recommendations** — Suggested improvements for next cycle
10. **Appendix** — Code diffs (optional)
