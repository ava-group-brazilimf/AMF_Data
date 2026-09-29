# Task: Cost Optimization Analysis

**Command:** `*cost-optimization`  
**Agent:** IterationImprovement (Kai)  
**Output:** `cost-optimization.md`

---

## Objective

Analyze current data platform costs and identify optimization opportunities to reduce expenses while maintaining performance and reliability.

---

## Prerequisites

- [ ] Access to cost data (billing, usage metrics)
- [ ] Current architecture documentation
- [ ] Pipeline performance metrics
- [ ] Understanding of SLAs and requirements

---

## Steps

### Step 1: Gather Cost Data

Collect cost information by category:

| Category | Components | Data Source |
|----------|------------|-------------|
| **Compute** | Spark clusters, serverless, VMs | Cloud billing |
| **Storage** | Data lake, warehouse, backup | Cloud billing |
| **Network** | Data transfer, egress | Cloud billing |
| **Licensing** | BI tools, databases, software | Procurement |
| **Support** | Support plans, consultancy | Finance |

### Step 2: Analyze Cost Distribution

Create cost breakdown:

```yaml
cost_analysis:
  period: "{month/quarter}"
  total_cost: "${total}"
  
  by_category:
    compute: "${value}"
    storage: "${value}"
    network: "${value}"
    licensing: "${value}"
    
  by_environment:
    production: "${value}"
    development: "${value}"
    testing: "${value}"
    
  by_project:
    project_a: "${value}"
    project_b: "${value}"
```

### Step 3: Identify Optimization Opportunities

Common optimization areas:

| Area | Opportunity | Typical Savings |
|------|-------------|-----------------|
| **Compute** | Right-sizing clusters | 20-40% |
| **Compute** | Spot/preemptible instances | 60-80% |
| **Compute** | Auto-scaling | 15-30% |
| **Storage** | Lifecycle policies | 20-40% |
| **Storage** | Compression | 30-50% |
| **Storage** | Tiering | 40-60% |
| **Network** | Region optimization | 10-30% |
| **Scheduling** | Off-peak processing | 10-20% |
| **Redundancy** | Eliminate duplicates | 5-15% |

### Step 4: Calculate ROI

For each opportunity:

```yaml
optimization_opportunity:
  name: "{opportunity name}"
  category: "{compute|storage|network|other}"
  
  current_state:
    monthly_cost: "${current}"
    configuration: "{current config}"
    
  proposed_state:
    monthly_cost: "${proposed}"
    configuration: "{proposed config}"
    
  savings:
    monthly: "${savings}"
    annual: "${savings * 12}"
    percentage: "{%}"
    
  implementation:
    effort: "{hours}"
    cost: "${implementation cost}"
    timeline: "{days/weeks}"
    
  roi:
    payback_period: "{months}"
    first_year_net: "${net savings}"
```

### Step 5: Prioritize Recommendations

Use impact/effort matrix:

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1** | High savings, low effort | Do immediately |
| **P2** | High savings, high effort | Plan & execute |
| **P3** | Low savings, low effort | Quick wins |
| **P4** | Low savings, high effort | Defer/skip |

---

## Output Template

```markdown
# Cost Optimization Report

**Project:** {project_name}  
**Period Analyzed:** {start_date} to {end_date}  
**Author:** IterationImprovement  
**Date:** {date}  
**Version:** 1.0

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Current Monthly Cost | ${current} |
| Potential Monthly Savings | ${savings} |
| Savings Percentage | {%}% |
| Implementation Effort | {hours} hours |
| Payback Period | {months} months |

**Key Findings:**
1. {Finding 1}
2. {Finding 2}
3. {Finding 3}

---

## Current Cost Analysis

### Total Cost by Category

```mermaid
pie title Monthly Cost Distribution
    "Compute" : {value}
    "Storage" : {value}
    "Network" : {value}
    "Licensing" : {value}
```

| Category | Monthly Cost | % of Total | Trend |
|----------|--------------|------------|-------|
| Compute | ${value} | {%}% | ↑/↓/→ |
| Storage | ${value} | {%}% | ↑/↓/→ |
| Network | ${value} | {%}% | ↑/↓/→ |
| Licensing | ${value} | {%}% | ↑/↓/→ |
| **Total** | **${total}** | **100%** | |

### Cost by Environment

| Environment | Monthly Cost | % of Total | Notes |
|-------------|--------------|------------|-------|
| Production | ${value} | {%}% | Business critical |
| Development | ${value} | {%}% | Optimization target |
| Testing | ${value} | {%}% | Optimization target |

### Cost Trend (6 months)

| Month | Cost | Change | Notes |
|-------|------|--------|-------|
| {month-5} | ${value} | - | Baseline |
| {month-4} | ${value} | +/-{%}% | {note} |
| {month-3} | ${value} | +/-{%}% | {note} |
| {month-2} | ${value} | +/-{%}% | {note} |
| {month-1} | ${value} | +/-{%}% | {note} |
| {current} | ${value} | +/-{%}% | {note} |

---

## Optimization Opportunities

### Priority 1: Quick Wins (High Impact, Low Effort)

#### 1.1 {Opportunity Name}

| Attribute | Value |
|-----------|-------|
| **Category** | Compute/Storage/Network |
| **Current Cost** | ${current}/month |
| **Projected Cost** | ${projected}/month |
| **Monthly Savings** | ${savings} ({%}%) |
| **Implementation Effort** | {hours} hours |
| **Risk Level** | Low/Medium/High |

**Current State:**
{Description of current configuration}

**Proposed Change:**
{Description of proposed optimization}

**Implementation Steps:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

**Risk Mitigation:**
- {Risk 1}: {Mitigation}

---

### Priority 2: Strategic Optimizations (High Impact, High Effort)

#### 2.1 {Opportunity Name}

| Attribute | Value |
|-----------|-------|
| **Category** | Compute/Storage/Network |
| **Current Cost** | ${current}/month |
| **Projected Cost** | ${projected}/month |
| **Monthly Savings** | ${savings} ({%}%) |
| **Implementation Effort** | {hours} hours |
| **Risk Level** | Low/Medium/High |

**Current State:**
{Description}

**Proposed Change:**
{Description}

**Implementation Plan:**
| Phase | Activities | Duration | Owner |
|-------|------------|----------|-------|
| 1 | {activities} | {days} | {owner} |
| 2 | {activities} | {days} | {owner} |

---

### Priority 3: Minor Optimizations (Low Impact, Low Effort)

| # | Opportunity | Savings/Month | Effort | Action |
|---|-------------|---------------|--------|--------|
| 1 | {opportunity} | ${value} | {hours}h | {action} |
| 2 | {opportunity} | ${value} | {hours}h | {action} |

---

## Savings Summary

### By Category

| Category | Current | Optimized | Savings | % |
|----------|---------|-----------|---------|---|
| Compute | ${value} | ${value} | ${value} | {%}% |
| Storage | ${value} | ${value} | ${value} | {%}% |
| Network | ${value} | ${value} | ${value} | {%}% |
| **Total** | **${total}** | **${total}** | **${total}** | **{%}%** |

### Implementation Timeline

```mermaid
gantt
    title Cost Optimization Implementation
    dateFormat  YYYY-MM-DD
    section Priority 1
    Quick Win 1           :a1, {date}, 3d
    Quick Win 2           :a2, after a1, 2d
    section Priority 2
    Strategic Opt 1       :b1, after a2, 14d
    section Monitoring
    Validate savings      :c1, after b1, 7d
```

### Projected Savings Over Time

| Month | Baseline | Optimized | Cumulative Savings |
|-------|----------|-----------|-------------------|
| Month 1 | ${baseline} | ${optimized} | ${cumulative} |
| Month 2 | ${baseline} | ${optimized} | ${cumulative} |
| Month 3 | ${baseline} | ${optimized} | ${cumulative} |
| **Annual** | **${baseline*12}** | **${optimized*12}** | **${total_savings}** |

---

## Recommendations

### Immediate Actions (This Week)
1. {Action 1} - Expected savings: ${value}/month
2. {Action 2} - Expected savings: ${value}/month

### Short-Term (This Month)
1. {Action 1} - Expected savings: ${value}/month
2. {Action 2} - Expected savings: ${value}/month

### Medium-Term (This Quarter)
1. {Action 1} - Expected savings: ${value}/month
2. {Action 2} - Expected savings: ${value}/month

---

## Monitoring Plan

| Metric | Current | Target | Check Frequency |
|--------|---------|--------|-----------------|
| Total monthly cost | ${current} | ${target} | Weekly |
| Compute utilization | {%}% | {%}% | Daily |
| Storage growth rate | {%}%/month | {%}%/month | Weekly |
| Cost per pipeline | ${value} | ${target} | Weekly |

---

## Appendix: Cost Data Details

{Detailed breakdown of costs by resource, if needed}
```

---

## Handoff

After completing cost optimization analysis:
- **Continue improvement:** Analyze lead time → `*lead-time-analysis`
- **Create backlog:** Add to improvement backlog → `*improvement-backlog`
- **Check status:** View progress → `@orchestrator *status`
