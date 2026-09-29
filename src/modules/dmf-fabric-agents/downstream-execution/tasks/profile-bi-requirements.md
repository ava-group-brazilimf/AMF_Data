---
task: profile-bi-requirements
version: 1.0
elicit: true
description: Systematically gather and document BI requirements from stakeholders
---

# Profile BI Requirements

## Purpose
Conduct a structured requirements gathering session to understand business needs, user personas, and success criteria for BI solutions.

## Process

### Step 1: Stakeholder Identification
ASK about the stakeholders:

1. **Primary Sponsor**: Who owns this initiative?
2. **Key Users**: Who will use the solution daily?
3. **Data Owners**: Who controls the source data?
4. **IT Contacts**: Who supports infrastructure?

### Step 2: Business Context
GATHER business understanding:

1. **Business Objectives**: What strategic goals does this support?
2. **Pain Points**: What current reporting challenges exist?
3. **Decision Making**: What decisions will this data support?
4. **Success Metrics**: How will we measure success?

### Step 3: User Personas
DOCUMENT for each user type:

```yaml
persona:
  name: "{Role Name}"
  department: "{Department}"
  frequency: Daily/Weekly/Monthly
  technical_level: Low/Medium/High
  primary_questions:
    - "Question 1 they need answered"
    - "Question 2 they need answered"
  key_metrics:
    - Metric 1
    - Metric 2
  preferred_format: Dashboard/Report/Alert
  mobile_access: Yes/No
```

### Step 4: Data Requirements
IDENTIFY data needs:

1. **Source Systems**: Where does the data live?
2. **Key Entities**: What are the main data subjects?
3. **Time Periods**: Historical depth and comparison needs?
4. **Granularity**: What level of detail?
5. **Refresh Needs**: How current must data be?

### Step 5: Generate Requirements Document

PRODUCE structured requirements:

```markdown
# BI Requirements Document

## Executive Summary
{Brief overview of the solution}

## Stakeholders
| Role | Name | Department | Involvement |
|------|------|------------|-------------|
| Sponsor | | | |
| User | | | |

## User Personas
{Detailed persona descriptions}

## Functional Requirements
| ID | Requirement | Priority | Persona |
|----|-------------|----------|---------|
| FR-001 | | Must Have | |
| FR-002 | | Should Have | |

## Non-Functional Requirements
- Performance: <X seconds load time
- Availability: <X% uptime
- Security: {requirements}

## Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2
```

## Output Structure

```
requirements/
├── stakeholder-map.md
├── user-personas.md
├── requirements-document.md
├── data-requirements.md
└── success-criteria.md
```
