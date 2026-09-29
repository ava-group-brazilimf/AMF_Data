# Task: Define Analytical Questions

```yaml
task_id: define-analytical-questions
agent: business-analyst
version: "1.1"
command: "*analytical-questions"
phase: UPSTREAM
gate: 1
output: "analytical-questions.md"
output_folder: "projects/{project_name}/outputs/upstream/analysis/"
```

---

## Purpose

Define the specific analytical questions that the data solution must be able to answer, linking them to KPIs and identifying the data required.

---

## Prerequisites

- KPIs document from DataStrategist
- Understanding of business objectives
- Knowledge of available data sources

---

## Execution Steps

### Step 1: Review KPIs and Objectives

Load and review:
- KPIs document
- Problem statement
- Success criteria (if available)

### Step 2: Formulate Questions

For each KPI or objective, ask:
- "What questions need to be answered to track this KPI?"
- "What trends do stakeholders want to see?"
- "What comparisons are needed?"
- "What drill-downs are required?"

### Step 3: Prioritize Questions

For each question, assign:
1. Priority (High/Medium/Low)
2. Business value
3. Data complexity
4. Stakeholder requesting

### Step 4: Define Data Requirements

For each question, identify:
1. Dimensions needed (e.g., time, geography, product)
2. Measures needed (e.g., sales, count, average)
3. Filters required
4. Grain/granularity
5. Data sources

### Step 5: Link to KPIs

Map each question to relevant KPIs.

### Step 6: Generate Document

---

## Output Template

```markdown
# Analytical Questions

**Project:** {project_name}  
**Date:** {date}  
**Author:** BusinessAnalyst  
**Version:** 1.0

---

## Executive Summary

This document defines the analytical questions that the data solution must answer. These questions are derived from business KPIs and stakeholder needs.

**Total Questions:** {n}  
**High Priority:** {n}  
**Medium Priority:** {n}  
**Low Priority:** {n}

---

## Questions Summary

| ID | Question | Priority | Linked KPI | Complexity |
|----|----------|----------|------------|------------|
| AQ-001 | {question_short} | High | {kpi} | {High/Med/Low} |
| AQ-002 | {question_short} | Medium | {kpi} | {High/Med/Low} |
| AQ-003 | {question_short} | Medium | {kpi} | {High/Med/Low} |
| AQ-004 | {question_short} | Low | {kpi} | {High/Med/Low} |
| AQ-005 | {question_short} | Low | - | {High/Med/Low} |

---

## High Priority Questions

### AQ-001: {question_full}

| Attribute | Value |
|-----------|-------|
| **Priority** | High |
| **Business Context** | {why this question is important} |
| **Linked KPI** | {kpi_name} |
| **Requested By** | {stakeholder} |

**Data Requirements:**

| Aspect | Details |
|--------|---------|
| **Dimensions** | {time, geography, product, customer, etc.} |
| **Measures** | {sales, count, average, etc.} |
| **Grain** | {daily, monthly, per transaction, etc.} |
| **Filters** | {date range, region, category, etc.} |
| **Time Range** | {last 12 months, YTD, etc.} |

**Data Sources:**
- Source 1: {source_name} - {table/entity}
- Source 2: {source_name} - {table/entity}

**Expected Output:**
{description of expected answer format - chart, table, single value}

**Example Answer:**
```
{example of what the answer might look like}
```

---

### AQ-002: {question_full}

{same format}

---

## Medium Priority Questions

### AQ-003: {question_full}

| Attribute | Value |
|-----------|-------|
| **Priority** | Medium |
| **Business Context** | {context} |
| **Linked KPI** | {kpi_name} |
| **Requested By** | {stakeholder} |

**Data Requirements:**

| Aspect | Details |
|--------|---------|
| **Dimensions** | {dimensions} |
| **Measures** | {measures} |
| **Grain** | {grain} |
| **Filters** | {filters} |

**Data Sources:**
- {sources}

---

### AQ-004: {question_full}

{same format}

---

## Low Priority Questions

### AQ-005: {question_full}

{abbreviated format for lower priority}

---

## Question Categories

| Category | Count | Questions |
|----------|-------|-----------|
| Financial Performance | {n} | AQ-001, AQ-003 |
| Operational Efficiency | {n} | AQ-002, AQ-004 |
| Customer Insights | {n} | AQ-005 |
| Compliance/Risk | {n} | - |

---

## Data Coverage Matrix

| Question | Source 1 | Source 2 | Source 3 | Coverage |
|----------|----------|----------|----------|----------|
| AQ-001 | ✅ | ✅ | - | 100% |
| AQ-002 | ✅ | ⚠️ | - | 90% |
| AQ-003 | ✅ | ✅ | ✅ | 100% |
| AQ-004 | ⚠️ | - | - | 70% |
| AQ-005 | ✅ | - | - | 100% |

**Legend:** ✅ = Available, ⚠️ = Partial, ❌ = Not Available

---

## Dimension Requirements Summary

| Dimension | Questions Using | Source | Status |
|-----------|-----------------|--------|--------|
| Time (Date) | All | Multiple | ✅ Available |
| Geography | AQ-001, AQ-003 | {source} | ✅ Available |
| Product | AQ-002, AQ-004 | {source} | ⚠️ Partial |
| Customer | AQ-001, AQ-005 | {source} | ✅ Available |

---

## Measure Requirements Summary

| Measure | Questions Using | Calculation | Source |
|---------|-----------------|-------------|--------|
| Sales Amount | AQ-001, AQ-003 | SUM(amount) | {source} |
| Order Count | AQ-002 | COUNT(*) | {source} |
| Average Value | AQ-004 | AVG(amount) | Derived |

---

## Open Questions

| # | Question | Impact | Owner |
|---|----------|--------|-------|
| 1 | {open question about data} | {impact} | {owner} |

---

## Next Steps

1. Review questions with stakeholders
2. Define initial DQ requirements - `*dq-initial`
3. Proceed to Gate 1 validation

---

*Document generated by BusinessAnalyst Agent*
```

---

## Question Formulation Guide

### Good Question Characteristics

| Characteristic | Good Example | Bad Example |
|----------------|--------------|-------------|
| Specific | "What is the monthly revenue by product category for the last 12 months?" | "How is revenue doing?" |
| Measurable | "How many orders are processed within SLA by region?" | "Is order processing good?" |
| Actionable | "Which products have declining sales trend over 3 months?" | "What's the data like?" |
| Time-bound | "What was the YoY growth rate for Q4?" | "What is the growth?" |

### Question Starters

| Type | Starters |
|------|----------|
| Trend | "How has X changed over time?" |
| Comparison | "How does X compare to Y?" |
| Distribution | "What is the breakdown of X by Y?" |
| Ranking | "What are the top/bottom N by X?" |
| Threshold | "What percentage of X meets threshold Y?" |
| Correlation | "Is there a relationship between X and Y?" |

---

## Validation Checklist

Before completing, verify:

- [ ] At least 5 analytical questions defined
- [ ] Each question is specific and measurable
- [ ] Priority assigned to each question
- [ ] Linked to KPIs where applicable
- [ ] Dimensions identified per question
- [ ] Measures identified per question
- [ ] Data sources identified
- [ ] Grain/granularity specified
- [ ] Questions cover different stakeholder needs
