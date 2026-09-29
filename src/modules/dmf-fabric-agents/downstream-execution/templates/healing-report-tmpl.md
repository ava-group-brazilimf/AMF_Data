---
report:
  report_id: "{report_id}"
  schema_version: "1.3"
  generated_at: "{report_date}"

context:
  scope: "{scope}"
  scope_id: "{scope_id}"
  migration_id: "{migration_id}"
  wave_id: "{wave_id}"

timing:
  start_time: "{start_time_iso8601}"
  end_time: "{end_time_iso8601}"
  duration_seconds: {duration_seconds}

status:
  pipeline_status: "{pipeline_status}" 
  # COMPLETED_SUCCESSFUL | COMPLETED_WITH_ESCALATIONS | FAILED | IN_PROGRESS
  recommended_action: "{recommended_action}" 
  # CONTINUE | MONITOR | ESCALATE
  overall_confidence: "{confidence_level}" 
  # HIGH | MEDIUM | LOW

artifacts:
  diff_files:
    - "artifacts/fix-{report_id}.diff"
  logs:
    - "artifacts/healing-{report_id}.log"
---
# 🔧 Healing Report
# Template ID: healing-report-tmpl
# Agent: Phoenix (Self-Healing)
# Version: 1.3


---

## 📊 Summary (Machine-Readable)

```yaml
summary:
  processing:
    total_pipelines_processed: {total_pipelines}
    healed: {healed_count}
    partial: {partial_count}
    escalated: {escalated_count}
    in_progress: {in_progress_count}

  rates:
    healing_rate: {healing_rate}
    success_rate: {success_rate}
    escalation_rate: {escalation_rate}

  performance:
    avg_attempts_per_fix: {avg_attempts}
    median_attempts_per_fix: {median_attempts}
    avg_time_per_fix_seconds: {avg_time_seconds}
    median_time_per_fix_seconds: {median_time_seconds}
    min_time_per_fix_seconds: {min_time_seconds}
    max_time_per_fix_seconds: {max_time_seconds}

  learning:
    patterns_discovered: {patterns_learned}
    patterns_promoted_to_rules: {patterns_promoted}

  impact:
    estimated_manual_hours_saved: {hours_saved}
    cost_savings_usd: {cost_savings}
```

---
## 🧾 Executive Summary

| Metric | Value |
|--------|-------|
| Total Pipelines Processed | {total_pipelines} |
| ✅ Healed | {healed_count} ({healing_rate}%) |
| ⚠️ Partial | {partial_count} |
| ❌ Escalated | {escalated_count} |
| 🔄 In Progress | {in_progress_count} |
| Avg Attempts to Fix | {avg_attempts} |
| Avg Time to Fix | {avg_time_seconds}s |
| Patterns Learned | {patterns_learned} |
| Cost Savings | ~{hours_saved} human hours saved |



**Overall Assessment:** {overall_assessment}

## 🚦 Pipeline Decision

| Metric | Value |
|--------|-------|
| Success Rate | {success_rate}% |
| Escalation Rate | {escalation_rate}% |
| Recommended Action | {recommended_action} |

### Decision Rules
- ≥ 95% success → Continue
- 70–94% success → Monitor
- < 70% success → Escalate



## Error Distribution

| Error Type | Count | % of Total | Auto-Fix Rate |
|------------|------|------------|---------------|
{{ERROR_DISTRIBUTION_ROWS}}


## Fix Attempts Detail
{{FIX_ATTEMPTS_BLOCK}}

### Pipeline: {pipeline_id}

**Error:** {error_description}  
**Classification:** {error_classification} ({pattern_id})  
**Root Cause:** {root_cause}


## Strategy Effectiveness

| Strategy | Attempts | Successes | Success Rate | Avg Time |
|----------|---------|-----------|-------------|----------|
| Rule-based | {rb_attempts} | {rb_success} | {rb_rate}% | {rb_time}s |
| LLM Alt Prompt | {la_attempts} | {la_success} | {la_rate}% | {la_time}s |
| LLM Diff Model | {ld_attempts} | {ld_success} | {ld_rate}% | {ld_time}s |

---

## Patterns Learned

| # | Pattern ID | Category | Source Pipeline | Fix Template | Success Rate |
|---|-----------|----------|----------------|-------------|-------------|
| 1 | {pattern_id} | {category} | {pipeline} | {template} | {rate}% |
| 2 | {pattern_id} | {category} | {pipeline} | {template} | {rate}% |

### Patterns Promoted to Rule-Based

| Pattern | Previous Strategy | Cumulative Success | Occurrences |
|---------|------------------|-------------------|-------------|
| {pattern} | {strategy} | {success_rate}% | {count} |

---

## Escalations

| Pipeline | Error | Attempts | Reason for Escalation | Priority |
|----------|-------|---------|----------------------|----------|
| {pipeline_id} | {error} | {attempts}/3 | {reason} | {priority} |

---

## Regressions Detected

| Pipeline | Attempt | Dimension | Before | After | Action Taken |
|----------|---------|----------|--------|-------|-------------|
| {pipeline_id} | #{attempt} | {dimension} | {before} | {after} | {action} |

---

## Time Analysis

| Pipeline | Diagnosis | Fix Attempts | Verification | Total |
|----------|----------|-------------|-------------|-------|
| {pipeline_id} | {diag_time} | {fix_time} | {verify_time} | {total_time} |

**Total Healing Time:** {total_healing_time}  
**Estimated Manual Time:** {manual_estimate}  
**Time Saved:** {time_saved} ({savings_percent}%)

---

## ✅ Recommendations

| Type | Recommendation | Priority | Owner |
|------|---------------|----------|-------|
{{RECOMMENDATIONS_ROWS}}
``

---

## Appendix: Code Diffs

{code_diffs_if_included}
