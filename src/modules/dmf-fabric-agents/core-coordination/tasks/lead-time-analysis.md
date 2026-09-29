# Task: Lead Time Analysis

**Command:** `*lead-time-analysis`  
**Agent:** IterationImprovement (Kai)  
**Output:** `lead-time-analysis.md`

---

## Objective

Analyze and optimize the lead time from request to delivery across the data development lifecycle, identifying bottlenecks and improvement opportunities.

---

## Prerequisites

- [ ] Historical data on project timelines
- [ ] Access to work tracking system (Jira, Azure DevOps)
- [ ] Understanding of current processes
- [ ] Baseline measurements established

---

## Steps

### Step 1: Define Lead Time Scope

Lead time segments in data projects:

| Segment | Start | End | What's Measured |
|---------|-------|-----|-----------------|
| **Discovery** | Request received | Requirements approved | Understanding needs |
| **Design** | Requirements approved | Design approved | Architecture & modeling |
| **Development** | Design approved | Code complete | Building the solution |
| **Testing** | Code complete | Tests passed | Validation |
| **Deployment** | Tests passed | Production live | Release |
| **Total** | Request received | Production live | End-to-end |

### Step 2: Collect Lead Time Data

For each project/feature:

```yaml
lead_time_record:
  item_id: "{ticket/story ID}"
  item_type: "{feature|bug|enhancement}"
  complexity: "{small|medium|large}"
  
  timestamps:
    request_date: "{YYYY-MM-DD}"
    requirements_approved: "{YYYY-MM-DD}"
    design_approved: "{YYYY-MM-DD}"
    code_complete: "{YYYY-MM-DD}"
    tests_passed: "{YYYY-MM-DD}"
    production_date: "{YYYY-MM-DD}"
    
  calculated:
    discovery_days: {number}
    design_days: {number}
    development_days: {number}
    testing_days: {number}
    deployment_days: {number}
    total_lead_time: {number}
    
  wait_times:
    waiting_for_approval: {days}
    waiting_for_review: {days}
    waiting_for_environment: {days}
    blocked_by_dependency: {days}
```

### Step 3: Analyze Patterns

Calculate metrics:
- Average lead time by complexity
- Lead time percentiles (50th, 75th, 95th)
- Trend over time
- Wait time vs. work time ratio

### Step 4: Identify Bottlenecks

Common bottlenecks:

| Bottleneck | Symptoms | Impact |
|------------|----------|--------|
| Approval delays | Long wait between phases | +X days |
| Review backlog | Code sitting in review | +X days |
| Environment issues | Can't test/deploy | +X days |
| Dependencies | Waiting for other teams | +X days |
| Rework | Failed tests, design changes | +X days |

### Step 5: Propose Improvements

For each bottleneck:
- Root cause analysis
- Proposed solution
- Expected improvement
- Implementation effort

---

## Output Template

```markdown
# Lead Time Analysis Report

**Project:** {project_name}  
**Period Analyzed:** {start_date} to {end_date}  
**Author:** IterationImprovement  
**Date:** {date}  
**Version:** 1.0

---

## Executive Summary

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Average Lead Time | {X} days | {Y} days | {Z} days |
| 95th Percentile | {X} days | {Y} days | {Z} days |
| Wait Time Ratio | {X}% | {Y}% | {Z}% |

**Key Findings:**
1. {Finding 1}
2. {Finding 2}
3. {Finding 3}

---

## Lead Time Overview

### End-to-End Lead Time

```mermaid
flowchart LR
    A[Request] -->|{X} days| B[Requirements]
    B -->|{X} days| C[Design]
    C -->|{X} days| D[Development]
    D -->|{X} days| E[Testing]
    E -->|{X} days| F[Production]
    
    style A fill:#f9f
    style F fill:#9f9
```

**Total Average Lead Time:** {X} days

### Lead Time by Phase

| Phase | Average | Median | 95th %ile | % of Total |
|-------|---------|--------|-----------|------------|
| Discovery | {X} days | {X} days | {X} days | {%}% |
| Design | {X} days | {X} days | {X} days | {%}% |
| Development | {X} days | {X} days | {X} days | {%}% |
| Testing | {X} days | {X} days | {X} days | {%}% |
| Deployment | {X} days | {X} days | {X} days | {%}% |
| **Total** | **{X} days** | **{X} days** | **{X} days** | **100%** |

### Work Time vs. Wait Time

```mermaid
pie title Time Distribution
    "Active Work" : {value}
    "Waiting/Blocked" : {value}
```

| Category | Time | % of Total |
|----------|------|------------|
| Active Work | {X} days | {%}% |
| Waiting for Approval | {X} days | {%}% |
| Waiting for Review | {X} days | {%}% |
| Waiting for Environment | {X} days | {%}% |
| Blocked by Dependencies | {X} days | {%}% |

---

## Lead Time by Complexity

| Complexity | Count | Avg Lead Time | Std Dev |
|------------|-------|---------------|---------|
| Small | {n} | {X} days | {X} days |
| Medium | {n} | {X} days | {X} days |
| Large | {n} | {X} days | {X} days |

### Small Items (Expected: 1-3 days)

| Item ID | Type | Lead Time | Status |
|---------|------|-----------|--------|
| {id} | {type} | {X} days | ✅/⚠️/❌ |

### Medium Items (Expected: 5-10 days)

| Item ID | Type | Lead Time | Status |
|---------|------|-----------|--------|
| {id} | {type} | {X} days | ✅/⚠️/❌ |

### Large Items (Expected: 15-30 days)

| Item ID | Type | Lead Time | Status |
|---------|------|-----------|--------|
| {id} | {type} | {X} days | ✅/⚠️/❌ |

---

## Lead Time Trend

| Period | Avg Lead Time | Items Delivered | Notes |
|--------|---------------|-----------------|-------|
| {period-4} | {X} days | {n} | Baseline |
| {period-3} | {X} days | {n} | {note} |
| {period-2} | {X} days | {n} | {note} |
| {period-1} | {X} days | {n} | {note} |
| Current | {X} days | {n} | {note} |

**Trend:** ↑ Increasing / ↓ Decreasing / → Stable

---

## Bottleneck Analysis

### Identified Bottlenecks

| # | Bottleneck | Phase | Avg Delay | Frequency | Impact |
|---|------------|-------|-----------|-----------|--------|
| 1 | {bottleneck} | {phase} | {X} days | {%}% of items | High |
| 2 | {bottleneck} | {phase} | {X} days | {%}% of items | Medium |
| 3 | {bottleneck} | {phase} | {X} days | {%}% of items | Medium |

### Bottleneck 1: {Name}

**Current State:**
{Description of the bottleneck}

**Root Causes:**
1. {Cause 1}
2. {Cause 2}

**Impact:**
- Average delay: {X} days
- Affects {%}% of items
- Estimated cost: ${value}/month

**Proposed Solution:**
{Description of solution}

**Expected Improvement:**
- Reduce delay by {X} days ({%}%)
- Implementation effort: {hours} hours

---

## Improvement Recommendations

### Quick Wins (Implement This Week)

| # | Improvement | Expected Reduction | Effort |
|---|-------------|-------------------|--------|
| 1 | {improvement} | {X} days | {hours}h |
| 2 | {improvement} | {X} days | {hours}h |

### Process Changes (Implement This Month)

| # | Improvement | Expected Reduction | Effort |
|---|-------------|-------------------|--------|
| 1 | {improvement} | {X} days | {days} days |
| 2 | {improvement} | {X} days | {days} days |

### Automation Opportunities (Implement This Quarter)

| # | Improvement | Expected Reduction | Effort |
|---|-------------|-------------------|--------|
| 1 | {automation} | {X} days | {days} days |
| 2 | {automation} | {X} days | {days} days |

---

## Projected Lead Time After Improvements

### Baseline vs. Target

| Phase | Current | After Quick Wins | After All Improvements |
|-------|---------|------------------|------------------------|
| Discovery | {X} days | {X} days | {X} days |
| Design | {X} days | {X} days | {X} days |
| Development | {X} days | {X} days | {X} days |
| Testing | {X} days | {X} days | {X} days |
| Deployment | {X} days | {X} days | {X} days |
| **Total** | **{X} days** | **{X} days** | **{X} days** |

### Improvement Timeline

```mermaid
gantt
    title Lead Time Improvement Plan
    dateFormat  YYYY-MM-DD
    section Quick Wins
    Implement improvement 1    :a1, {date}, 3d
    Implement improvement 2    :a2, after a1, 2d
    section Process Changes
    Process improvement 1      :b1, after a2, 14d
    section Automation
    Automation project         :c1, after b1, 30d
    section Validation
    Measure results           :d1, after c1, 14d
```

---

## Metrics & Monitoring

### KPIs to Track

| KPI | Current | Target | Frequency |
|-----|---------|--------|-----------|
| Average Lead Time | {X} days | {Y} days | Weekly |
| 95th Percentile | {X} days | {Y} days | Weekly |
| Wait Time Ratio | {%}% | {%}% | Weekly |
| Throughput | {n} items/week | {n} items/week | Weekly |

### Success Criteria

- [ ] Average lead time reduced by {%}%
- [ ] 95th percentile reduced by {%}%
- [ ] Wait time ratio below {%}%
- [ ] No regression in quality metrics

---

## Appendix: Raw Data

{Detailed lead time data for each item analyzed}
```

---

## Handoff

After completing lead time analysis:
- **Continue improvement:** Review incidents → `*incident-review`
- **Create backlog:** Add to improvement backlog → `*improvement-backlog`
- **Check status:** View progress → `@orchestrator *status`
