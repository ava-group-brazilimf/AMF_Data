# Define Success Criteria Task

**Task ID:** define-success-criteria  
**Agent:** DataStrategist  
**Version:** 1.0

---

## Purpose

Define clear, measurable success criteria that will determine when the data initiative has achieved its goals.

---

## Prerequisites

- Problem statement completed
- KPIs defined
- Understanding of stakeholder expectations

---

## Execution Steps

### Step 1: Review Existing Artifacts

Load and review:
- Problem Statement (success vision)
- KPIs (targets and baselines)

### Step 2: Categorize Success Criteria

Group criteria into:
1. **Must Have** - Required for project to be considered successful
2. **Should Have** - Important but not critical
3. **Nice to Have** - Additional value if achieved

### Step 3: Define Each Criterion

For each criterion, specify:
1. Description of what success looks like
2. Measurable threshold
3. How it will be validated
4. Who needs to approve

### Step 4: Align with KPIs

Map each criterion to relevant KPIs to ensure measurability.

### Step 5: Define Acceptance Process

Document:
1. Who signs off on success
2. What evidence is required
3. When validation occurs

### Step 6: Generate Success Criteria Document

---

## Output Template

```markdown
# Success Criteria

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataStrategist  
**Version:** 1.0

---

## Executive Summary

This document defines the measurable criteria that will determine project success. All "Must Have" criteria must be met for the project to be considered successful.

---

## Success Criteria Overview

| # | Criterion | Priority | KPI Link | Status |
|---|-----------|----------|----------|--------|
| 1 | {criterion_1} | Must Have | KPI-1 | ⏳ Pending |
| 2 | {criterion_2} | Must Have | KPI-2 | ⏳ Pending |
| 3 | {criterion_3} | Should Have | KPI-3 | ⏳ Pending |
| 4 | {criterion_4} | Nice to Have | - | ⏳ Pending |

---

## Must Have Criteria

These criteria are **required** for project success.

### Criterion 1: {criterion_name}

| Attribute | Value |
|-----------|-------|
| **Description** | {what success looks like} |
| **Threshold** | {specific measurable value} |
| **Linked KPI** | {kpi_name} |
| **Validation Method** | {how we will verify} |
| **Approver** | {who signs off} |

**Acceptance Evidence:**
- {evidence item 1}
- {evidence item 2}

---

### Criterion 2: {criterion_name}

| Attribute | Value |
|-----------|-------|
| **Description** | {what success looks like} |
| **Threshold** | {specific measurable value} |
| **Linked KPI** | {kpi_name} |
| **Validation Method** | {how we will verify} |
| **Approver** | {who signs off} |

**Acceptance Evidence:**
- {evidence item 1}
- {evidence item 2}

---

## Should Have Criteria

These criteria are **important** but not critical for initial success.

### Criterion 3: {criterion_name}

| Attribute | Value |
|-----------|-------|
| **Description** | {description} |
| **Threshold** | {threshold} |
| **Linked KPI** | {kpi} |
| **Validation Method** | {method} |
| **Approver** | {approver} |

---

## Nice to Have Criteria

These criteria provide **additional value** if achieved.

### Criterion 4: {criterion_name}

| Attribute | Value |
|-----------|-------|
| **Description** | {description} |
| **Target** | {target} |
| **Benefit** | {additional value provided} |

---

## Acceptance Process

### Sign-Off Authority

| Role | Authority | Criteria Scope |
|------|-----------|----------------|
| Business Owner | Final approval | All criteria |
| Technical Lead | Technical validation | Technical criteria |
| Data Owner | Data quality validation | DQ criteria |

### Validation Timeline

| Phase | Validation | Criteria Reviewed |
|-------|------------|-------------------|
| Gate 1 | Discovery complete | Problem/KPI definition |
| Gate 2 | Design complete | Technical feasibility |
| Gate 3 | Implementation complete | All criteria |
| Post-Deploy | 30 days after go-live | Business value |

### Evidence Requirements

For each criterion to be marked as "Met", provide:
1. Measurement data showing threshold achieved
2. Date of measurement
3. Source of data
4. Sign-off from approver

---

## Criteria Tracking

### Status Definitions

| Status | Icon | Meaning |
|--------|------|---------|
| Pending | ⏳ | Not yet evaluated |
| In Progress | 🔄 | Being measured/validated |
| Met | ✅ | Criterion achieved |
| Partial | ⚠️ | Partially achieved |
| Not Met | ❌ | Failed to achieve |

### Current Status

| Criterion | Target | Current | Status | Notes |
|-----------|--------|---------|--------|-------|
| {criterion_1} | {target} | {current} | ⏳ | {notes} |
| {criterion_2} | {target} | {current} | ⏳ | {notes} |
| {criterion_3} | {target} | {current} | ⏳ | {notes} |

---

## Dependencies and Risks

### Dependencies

| Criterion | Depends On | Risk if Not Met |
|-----------|------------|-----------------|
| {criterion} | {dependency} | {risk} |

### Risks to Success

| Risk | Impact | Mitigation |
|------|--------|------------|
| {risk_description} | {impact} | {mitigation} |

---

## Review History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| {date} | 1.0 | Initial version | DataStrategist |

---

## Next Steps

1. Review and validate with stakeholders
2. Obtain sign-off on criteria
3. Complete UPSTREAM artifacts for Gate 1

---

*Document generated by DataStrategist Agent*
```

---

## Success Criteria Types

### Quantitative Criteria
| Type | Example |
|------|---------|
| Threshold | "Error rate below 1%" |
| Improvement | "Processing time reduced by 50%" |
| Target | "95% data completeness" |

### Qualitative Criteria
| Type | Example |
|------|---------|
| Capability | "Users can self-serve reports" |
| Compliance | "Meets GDPR requirements" |
| Adoption | "All departments using new system" |

---

## Validation Checklist

Before completing, verify:

- [ ] At least 2 "Must Have" criteria defined
- [ ] Each criterion has measurable threshold
- [ ] Criteria link to KPIs where applicable
- [ ] Validation method specified
- [ ] Approvers identified
- [ ] Evidence requirements clear
- [ ] Stakeholders agree on criteria
