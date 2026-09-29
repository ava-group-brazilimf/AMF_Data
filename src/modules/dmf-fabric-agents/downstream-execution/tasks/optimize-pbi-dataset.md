---
task: optimize-pbi-dataset
version: 1.0
elicit: true
description: Analyze and optimize Power BI dataset for improved performance
---

# Optimize Power BI Dataset

## Purpose
Analyze an existing Power BI semantic model and provide recommendations for performance optimization, reduced memory consumption, and improved query times.

## Process

### Step 1: Gather Current State
ASK the user for:

1. **Current Issues**: What performance problems exist?
2. **Dataset Size**: Approximate rows in fact tables?
3. **User Complaints**: Slow visuals, slow refresh, both?
4. **Storage Mode**: Import, DirectQuery, Composite?
5. **Refresh Duration**: How long does refresh take?

### Step 2: Analyze Model

REVIEW these areas:

**Data Model Analysis**
- [ ] Cardinality of columns (high cardinality issues)
- [ ] Unused columns that can be removed
- [ ] Data types (using appropriate types?)
- [ ] Calculated columns vs measures
- [ ] Relationship efficiency

**DAX Analysis**
- [ ] Complex measures causing slow queries
- [ ] Nested iterators
- [ ] Row-by-row calculations
- [ ] Filter context issues

**Query Analysis**
- [ ] Visuals generating inefficient queries
- [ ] Too many visuals per page
- [ ] Cross-filtering performance

### Step 3: Generate Optimization Plan

PRODUCE recommendations in priority order:

**Quick Wins (High Impact, Low Effort)**
```
1. Remove unused columns
2. Change data types (Text to Whole Number where appropriate)
3. Disable auto date/time
4. Remove unnecessary bi-directional relationships
```

**Model Improvements (High Impact, Medium Effort)**
```
1. Create aggregation tables
2. Implement incremental refresh
3. Optimize star schema
4. Add proper indexes to source
```

**DAX Optimization (Variable Effort)**
```
1. Convert calculated columns to measures
2. Use variables in complex measures
3. Optimize CALCULATE patterns
4. Implement measure branching
```

### Step 4: Provide Specific Recommendations

FOR each issue found, provide:

```yaml
issue:
  description: "{What the problem is}"
  impact: High/Medium/Low
  current_state: "{Current DAX or model state}"
  recommended_fix: "{Optimized version}"
  expected_improvement: "{Estimated improvement}"
```

## Common Optimizations

### High Cardinality Columns
```
Problem: Text columns with many unique values increase model size
Solution: 
- Remove if not needed for filtering/display
- Convert to numeric codes with lookup
- Use star schema with dimension tables
```

### Calculated Columns
```
Problem: Calculated columns are computed at refresh and stored
Solution:
- Convert to measures where possible
- Move calculation to source/Power Query
- Use only when filtering/sorting required
```

### Inefficient DAX
```
Before (Slow):
Sales Amount = 
SUMX(
    Sales,
    Sales[Quantity] * RELATED(Product[Price])
)

After (Fast):
Sales Amount = 
SUM(Sales[Sales Amount])
-- Pre-calculate in source or Power Query
```

### Aggregation Tables
```yaml
aggregation_table:
  name: Sales_Daily_Agg
  grain: Date, Product Category
  measures:
    - SUM(Sales Amount)
    - COUNT(Transactions)
  source_detail_table: Sales
  expected_speedup: "10-100x for summary visuals"
```

## Output Structure

```
optimization/
├── analysis/
│   ├── model-analysis.md
│   ├── dax-analysis.md
│   └── query-analysis.md
├── recommendations/
│   ├── quick-wins.md
│   ├── model-improvements.md
│   └── dax-optimizations.md
├── implementation/
│   ├── aggregation-tables.sql
│   └── optimized-measures.dax
└── README.md
```

## Quality Criteria

- [ ] All high-impact issues identified
- [ ] Recommendations prioritized by effort/impact
- [ ] Before/after code provided
- [ ] Expected improvements quantified
- [ ] Implementation steps clear
