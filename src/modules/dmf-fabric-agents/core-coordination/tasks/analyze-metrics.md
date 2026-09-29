# Task: Analyze Metrics

**Command:** `*metrics` / `*MA`  
**Output:** `metrics-analysis.md`

---

## Objective

Analyze pipeline and quality metrics to identify trends, patterns, and opportunities for improvement.

---

## Prerequisites

- [ ] Metrics collection enabled
- [ ] Baseline established
- [ ] Sufficient data points (at least 2-3 iterations)
- [ ] Access to metric sources

---

## Steps

### Step 1: Collect Metrics

Gather metrics from all sources:

| Metric Category | Source | Metrics |
|-----------------|--------|---------|
| Pipeline | Orchestrator logs | Cycle time, throughput |
| Quality | DQ validation | DQ score, error rate |
| Agents | Agent logs | Accuracy, response time |
| Gates | Gate results | Pass rate, rework |

### Step 2: Calculate Metrics

Compute key metrics:

```yaml
pipeline_metrics:
  cycle_time:
    formula: "end_date - start_date"
    unit: "days"
    
  throughput:
    formula: "artifacts_completed / time_period"
    unit: "artifacts/week"
    
  gate_pass_rate:
    formula: "(passes / attempts) * 100"
    unit: "%"
    
  rework_rate:
    formula: "(rework_items / total_items) * 100"
    unit: "%"

quality_metrics:
  dq_score:
    formula: "quality_checks_passed / total_checks"
    unit: "%"
    
  defect_rate:
    formula: "defects_found / total_outputs"
    unit: "defects/output"
```

### Step 3: Analyze Trends

Compare against baselines and targets:

| Metric | Baseline | Current | Target | Trend | Status |
|--------|----------|---------|--------|-------|--------|
| Cycle Time | 14 days | 12 days | 10 days | ↓ | 🟡 |
| DQ Score | 92% | 96% | 95% | ↑ | 🟢 |
| Pass Rate | 80% | 85% | 90% | ↑ | 🟡 |

### Step 4: Identify Patterns

Look for:
- **Correlations** - Metrics that move together
- **Anomalies** - Unexpected spikes or drops
- **Bottlenecks** - Steps causing delays
- **Root causes** - Why metrics are off target

### Step 5: Create Visualizations

Generate charts:
- Trend lines over time
- Distribution histograms
- Comparison bar charts
- Heat maps for patterns

### Step 6: Develop Recommendations

Based on analysis:

```yaml
recommendation:
  issue: "{metric issue identified}"
  analysis: "{what the data shows}"
  recommendation: "{specific action}"
  expected_impact: "{predicted improvement}"
  effort: "{implementation effort}"
  priority: "high|medium|low"
```

### Step 7: Document Analysis

Create metrics-analysis.md with full report.

---

## Output Template

```markdown
# Metrics Analysis

**Period:** {start_date} to {end_date}  
**Analyst:** Kai (IterationImprovement)

## Executive Summary

### Overall Health: 🟢/🟡/🔴

| Category | Score | Trend | Status |
|----------|-------|-------|--------|
| Pipeline | {score} | ↑/↓/→ | 🟢/🟡/🔴 |
| Quality | {score} | ↑/↓/→ | 🟢/🟡/🔴 |
| Agents | {score} | ↑/↓/→ | 🟢/🟡/🔴 |

### Key Findings
1. {finding}
2. {finding}
3. {finding}

## Pipeline Metrics

### Cycle Time
[Chart showing trend]

| Period | Value | Target | Status |
|--------|-------|--------|--------|
| {period} | {value} | {target} | 🟢/🟡/🔴 |

**Analysis:** {interpretation}

### Gate Pass Rate
[Similar structure]

## Quality Metrics

### Data Quality Score
[Chart and table]

### Defect Rate
[Chart and table]

## Agent Metrics

### Agent Performance Summary
| Agent | Accuracy | Response Time | Escalations |
|-------|----------|---------------|-------------|
| {agent} | {%} | {seconds} | {count} |

## Trend Analysis

### Improving Metrics 📈
- {metric}: {details}

### Declining Metrics 📉
- {metric}: {details}

### Stable Metrics ➡️
- {metric}: {details}

## Recommendations

### High Priority
| # | Recommendation | Expected Impact | Effort |
|---|----------------|-----------------|--------|
| 1 | {rec} | {impact} | {effort} |

### Medium Priority
[Similar table]

## Next Steps
1. {action}
2. {action}

## Appendix
### Data Sources
### Methodology
### Raw Data
```

---

## Validation

- [ ] All metrics collected
- [ ] Calculations verified
- [ ] Trends identified
- [ ] Visualizations clear
- [ ] Recommendations actionable
- [ ] Document complete
