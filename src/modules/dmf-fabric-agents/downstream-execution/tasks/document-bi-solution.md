---
task: document-bi-solution
version: 1.0
elicit: true
description: Create comprehensive documentation for BI solutions including data dictionary, user guides, and technical specs
---

# Document BI Solution

## Purpose
Generate comprehensive documentation for a BI solution covering technical specifications, user guides, and maintenance procedures.

## Process

### Step 1: Gather Context
ASK the user for:

1. **Solution Name**: What is the BI solution called?
2. **Scope**: What does it include? (Datasets, reports, dashboards)
3. **Audience**: Who needs documentation? (Users, admins, developers)
4. **Existing Docs**: Any current documentation to reference?

### Step 2: Generate Documentation

PRODUCE the following documents:

**1. Executive Summary**
```markdown
# {Solution Name} - BI Solution

## Overview
{Brief description of the solution and its business value}

## Key Features
- Feature 1
- Feature 2

## Stakeholders
| Role | Name | Responsibility |
|------|------|----------------|
| Owner | | |
| Admin | | |
```

**2. Data Dictionary**
```markdown
# Data Dictionary

## Tables

### {Table Name}
| Column | Data Type | Description | Source |
|--------|-----------|-------------|--------|
| col1 | INT | Description | Source.table |

## Measures

### {Measure Name}
- **Purpose**: What it calculates
- **Formula**: `SUM(Table[Column])`
- **Format**: Currency
- **Used In**: Dashboard 1, Report 2
```

**3. User Guide**
```markdown
# User Guide

## Getting Started
{How to access the solution}

## Navigation
{How to navigate dashboards/reports}

## Common Tasks
### Filtering Data
{Instructions}

### Exporting Data
{Instructions}

## FAQ
{Common questions and answers}
```

**4. Technical Specification**
```markdown
# Technical Specification

## Architecture
{Diagram and description}

## Data Sources
| Source | Type | Refresh | Gateway |
|--------|------|---------|---------|
| SQL Server | DirectQuery | Real-time | On-prem |

## Security
{RLS roles and assignments}

## Performance
{Optimization notes}
```

**5. Maintenance Guide**
```markdown
# Maintenance Guide

## Refresh Schedule
| Dataset | Schedule | Owner |
|---------|----------|-------|
| Sales | Daily 6AM | |

## Monitoring
{What to monitor and how}

## Troubleshooting
{Common issues and solutions}
```

## Output Structure

```
documentation/
├── executive-summary.md
├── data-dictionary.md
├── user-guide.md
├── technical-spec.md
├── maintenance-guide.md
├── release-notes.md
└── README.md
```

## Quality Criteria

- [ ] All components documented
- [ ] Screenshots included where helpful
- [ ] Version history maintained
- [ ] Contact information included
- [ ] Search-friendly formatting
