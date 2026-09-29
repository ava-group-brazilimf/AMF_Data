---
task: create-dax-measures
version: 1.0
elicit: true
description: Generate DAX measures with proper patterns, formatting, and documentation
---

# Create DAX Measures

## Purpose
Generate optimized, well-documented DAX measures following best practices for performance and maintainability.

## Process

### Step 1: Gather Requirements
ASK the user for the following information:

1. **Measure Purpose**: What business question does this measure answer?
2. **Calculation Type**: Sum, Average, Count, Ratio, Time Intelligence, etc.
3. **Context**: What filters should affect this measure?
4. **Format**: Currency, Percentage, Number, Date?
5. **Comparison Needed**: YoY, MoM, vs Target, vs Budget?
6. **Related Measures**: Dependencies on existing measures?

### Step 2: Design Measure Logic

ANALYZE requirements to determine:

**Pattern Selection**
- Simple aggregation (SUM, AVERAGE, COUNT)
- CALCULATE with filters
- Time intelligence (YTD, MTD, QTD)
- Iterator functions (SUMX, AVERAGEX)
- Ratio/percentage calculations
- Ranking functions
- Moving averages/running totals

**Performance Considerations**
- Avoid nested iterators when possible
- Use variables for repeated calculations
- Consider measure branching
- Optimize filter context

### Step 3: Generate DAX Code

PRODUCE formatted DAX with:

```dax
// Measure: [Measure Name]
// Purpose: Brief description of what this measure calculates
// Author: InsightForge Agent
// Created: {DATE}
// Dependencies: [List any measures this depends on]

Measure Name = 
VAR _variableName = <calculation>
VAR _anotherVariable = <calculation>
RETURN
    <final calculation using variables>
```

### Step 4: Document Measure

CREATE documentation including:
- Business definition
- Technical specification
- Usage examples
- Known limitations

## DAX Pattern Library

### Time Intelligence Patterns

```dax
// Year-to-Date
Sales YTD = 
CALCULATE(
    [Total Sales],
    DATESYTD('Date'[Date])
)

// Previous Year Same Period
Sales PY = 
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)

// Year-over-Year Growth %
Sales YoY % = 
VAR _currentYear = [Total Sales]
VAR _previousYear = [Sales PY]
RETURN
    DIVIDE(
        _currentYear - _previousYear,
        _previousYear,
        BLANK()
    )
```

### Comparison Patterns

```dax
// Variance to Budget
Variance to Budget = 
[Actual Sales] - [Budget Sales]

// Variance % to Budget
Variance % = 
DIVIDE(
    [Variance to Budget],
    [Budget Sales],
    BLANK()
)
```

### Ranking Patterns

```dax
// Product Rank by Sales
Product Rank = 
RANKX(
    ALL('Product'[Product Name]),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

## Output Structure

```
dax-measures/
├── measures/
│   ├── base-measures.dax
│   ├── time-intelligence.dax
│   ├── comparisons.dax
│   └── kpis.dax
├── docs/
│   ├── measure-dictionary.md
│   └── calculation-logic.md
└── README.md
```

## Quality Criteria

- [ ] Uses variables for readability
- [ ] Proper formatting and indentation
- [ ] DIVIDE function instead of / operator
- [ ] BLANK() for error handling where appropriate
- [ ] No unnecessary CALCULATE wrappers
- [ ] Comments explaining complex logic
- [ ] Tested with sample data
