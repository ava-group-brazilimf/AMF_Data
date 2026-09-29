# Metrics Analysis Template

**Project:** {project_name}  
**Period:** {start_date} to {end_date}  
**Analyst:** Kai (IterationImprovement)  
**Version:** {version}

---

## Executive Summary

### Overall Health Score: 🟢 / 🟡 / 🔴

| Category | Score | Trend | Status | Notes |
|----------|-------|-------|--------|-------|
| Pipeline Performance | {0-100} | ↑↓→ | 🟢/🟡/🔴 | {brief note} |
| Data Quality | {0-100} | ↑↓→ | 🟢/🟡/🔴 | {brief note} |
| Agent Performance | {0-100} | ↑↓→ | 🟢/🟡/🔴 | {brief note} |
| Process Efficiency | {0-100} | ↑↓→ | 🟢/🟡/🔴 | {brief note} |

### Top 3 Findings

1. **{Finding}**: {one-sentence summary}
2. **{Finding}**: {one-sentence summary}
3. **{Finding}**: {one-sentence summary}

### Top 3 Recommendations

1. **{Recommendation}**: Expected impact {X}%
2. **{Recommendation}**: Expected impact {X}%
3. **{Recommendation}**: Expected impact {X}%

---

## Pipeline Performance Metrics

### Cycle Time

```
Target: ──────────────────────────── 10 days
        │
Current: ████████████████░░░░░░░░░░ 12 days
        │
Baseline: ████████████████████░░░░░░ 14 days
```

| Period | Cycle Time | vs Target | vs Baseline | Trend |
|--------|------------|-----------|-------------|-------|
| {period 1} | {days} | +{n}% | -{n}% | ↓ |
| {period 2} | {days} | +{n}% | -{n}% | ↓ |
| {period 3} | {days} | +{n}% | -{n}% | → |

**Analysis:** {interpretation of the data}

**Bottlenecks Identified:**
- {stage}: {avg time} ({% of total})
- {stage}: {avg time} ({% of total})

### Throughput

| Period | Artifacts Completed | Rate | Trend |
|--------|---------------------|------|-------|
| {period} | {count} | {n}/week | ↑ |

### Gate Pass Rate

| Gate | Attempts | Passes | Pass Rate | Target | Status |
|------|----------|--------|-----------|--------|--------|
| Gate 1 | {n} | {n} | {%} | 90% | 🟢/🟡/🔴 |
| Gate 2 | {n} | {n} | {%} | 90% | 🟢/🟡/🔴 |
| Gate 3 | {n} | {n} | {%} | 90% | 🟢/🟡/🔴 |

### Rework Rate

| Category | Rework Items | Total Items | Rate | Target | Status |
|----------|--------------|-------------|------|--------|--------|
| {category} | {n} | {n} | {%} | <10% | 🟢/🟡/🔴 |

---

## Data Quality Metrics

### DQ Score Trend

```
100% ┤                    ╭──●
 95% ┤        ╭───────────╯
 90% ┼───────╯
 85% ┤
     └────┬────┬────┬────┬────
       W1   W2   W3   W4   W5
```

| Period | DQ Score | Target | Status | Issues |
|--------|----------|--------|--------|--------|
| {period} | {%} | 95% | 🟢/🟡/🔴 | {count} |

### Quality Issues by Type

| Issue Type | Count | % of Total | Trend |
|------------|-------|------------|-------|
| Schema violations | {n} | {%} | ↓ |
| Null values | {n} | {%} | ↓ |
| Duplicates | {n} | {%} | → |
| Range violations | {n} | {%} | ↑ |

### Defect Escape Rate

| Stage Found | Count | % of Total |
|-------------|-------|------------|
| Development | {n} | {%} |
| Testing | {n} | {%} |
| Production | {n} | {%} |

---

## Agent Performance Metrics

### Agent Summary

| Agent | Accuracy | Response Time | Escalations | Interventions |
|-------|----------|---------------|-------------|---------------|
| Alex | {%} | {s} | {n} | {n} |
| Mary | {%} | {s} | {n} | {n} |
| Winston | {%} | {s} | {n} | {n} |
| Sofia | {%} | {s} | {n} | {n} |
| Nova | {%} | {s} | {n} | {n} |
| Diego | {%} | {s} | {n} | {n} |
| Bianca | {%} | {s} | {n} | {n} |
| Gaia | {%} | {s} | {n} | {n} |
| Orion | {%} | {s} | {n} | {n} |

### Agent Performance Details

#### {Agent Name}

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Accuracy | {%} | 95% | 🟢/🟡/🔴 |
| Response Time | {s} | <5s | 🟢/🟡/🔴 |
| Escalation Rate | {%} | <5% | 🟢/🟡/🔴 |

**Top Issues:**
1. {issue}
2. {issue}

---

## Trend Analysis

### Improving Metrics 📈

| Metric | Baseline | Current | Improvement |
|--------|----------|---------|-------------|
| {metric} | {value} | {value} | +{%} |

**Contributing Factors:**
- {factor}
- {factor}

### Declining Metrics 📉

| Metric | Baseline | Current | Decline |
|--------|----------|---------|---------|
| {metric} | {value} | {value} | -{%} |

**Root Causes:**
- {cause}
- {cause}

### Stable Metrics ➡️

| Metric | Value | Target | Notes |
|--------|-------|--------|-------|
| {metric} | {value} | {target} | {notes} |

---

## Correlations & Patterns

### Identified Correlations

| Metric A | Metric B | Correlation | Insight |
|----------|----------|-------------|---------|
| {metric} | {metric} | Strong + | {insight} |
| {metric} | {metric} | Moderate - | {insight} |

### Recurring Patterns

1. **{Pattern}**: {description}
2. **{Pattern}**: {description}

---

## Recommendations

### High Priority 🔴

| # | Recommendation | Expected Impact | Effort | Timeline |
|---|----------------|-----------------|--------|----------|
| 1 | {recommendation} | {%} improvement in {metric} | {effort} | {time} |

### Medium Priority 🟡

| # | Recommendation | Expected Impact | Effort | Timeline |
|---|----------------|-----------------|--------|----------|
| 2 | {recommendation} | {%} improvement in {metric} | {effort} | {time} |

### Low Priority 🟢

| # | Recommendation | Expected Impact | Effort | Timeline |
|---|----------------|-----------------|--------|----------|
| 3 | {recommendation} | {%} improvement in {metric} | {effort} | {time} |

---

## Next Steps

1. **Immediate (This Week):**
   - {action}
   
2. **Short-term (This Month):**
   - {action}
   
3. **Long-term (This Quarter):**
   - {action}

---

## Appendix

### Data Sources

| Source | Description | Refresh Rate |
|--------|-------------|--------------|
| {source} | {description} | {rate} |

### Methodology

- {methodology notes}

### Glossary

| Term | Definition |
|------|------------|
| {term} | {definition} |
