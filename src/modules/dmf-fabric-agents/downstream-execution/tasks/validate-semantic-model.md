---
task: validate-semantic-model
version: 1.0
elicit: true
description: Validate a semantic model against best practices and quality standards
---

# Validate Semantic Model

## Purpose
Perform a comprehensive quality check on a Power BI semantic model to ensure it follows best practices.

## Process

### Step 1: Gather Model Information
ASK the user to provide:

1. **Model Location**: Where is the PBIP/SemanticModel or connection?
2. **Model Purpose**: What business area does it serve?
3. **Known Issues**: Any existing concerns?

### Step 2: Execute Validation Checks

**Category: Data Model Structure**
- [ ] Star schema implemented (no snowflaking)
- [ ] Single fact tables at consistent grain
- [ ] Dimension tables properly designed
- [ ] No circular relationships
- [ ] Appropriate cardinality set
- [ ] Cross-filter direction correct

**Category: Naming Conventions**
- [ ] Tables use business-friendly names
- [ ] Columns use business-friendly names
- [ ] No underscores or technical prefixes
- [ ] Consistent capitalization
- [ ] Measures have clear names

**Category: Data Types**
- [ ] Appropriate data types assigned
- [ ] No text columns that should be numeric
- [ ] Dates using Date data type
- [ ] Decimals with appropriate precision

**Category: Relationships**
- [ ] All relationships defined
- [ ] Key columns properly typed
- [ ] No many-to-many without bridge
- [ ] Inactive relationships documented

**Category: Measures**
- [ ] Base measures exist
- [ ] Measures organized in display folders
- [ ] Format strings applied
- [ ] Descriptions provided

**Category: Performance**
- [ ] Auto date/time disabled
- [ ] Unused columns removed
- [ ] High cardinality columns reviewed
- [ ] Calculated columns minimized

### Step 3: Generate Validation Report

```markdown
# Semantic Model Validation Report

**Model**: {Name}
**Date**: {Date}
**Validator**: InsightForge Agent

## Summary
| Category | Pass | Fail | Warning |
|----------|------|------|---------|
| Structure | X | X | X |
| Naming | X | X | X |
| Data Types | X | X | X |
| Relationships | X | X | X |
| Measures | X | X | X |
| Performance | X | X | X |

## Detailed Findings

### Critical Issues (Must Fix)
1. **Issue**: {Description}
   - **Location**: {Table/Column}
   - **Impact**: {Why it matters}
   - **Fix**: {How to resolve}

### Warnings (Should Fix)
1. **Issue**: {Description}
   - **Location**: {Table/Column}
   - **Impact**: {Why it matters}
   - **Fix**: {How to resolve}

### Recommendations (Nice to Have)
1. **Suggestion**: {Description}

## Action Plan
| Priority | Issue | Owner | Due Date |
|----------|-------|-------|----------|
| 1 | | | |
```

## Output Structure

```
validation/
├── validation-report.md
├── findings-detail.md
└── action-plan.md
```
