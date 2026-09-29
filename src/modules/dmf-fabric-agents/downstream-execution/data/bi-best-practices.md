# BI Development Best Practices

## Overview

This document outlines best practices for Power BI development following enterprise standards and ensuring scalable, maintainable BI solutions.

---

## 1. Data Modeling Best Practices

### Star Schema Design
- **Always prefer star schema** over snowflake
- Keep fact tables narrow (only foreign keys and measures)
- Denormalize dimension tables
- One primary grain per fact table

### Naming Conventions
```
Tables:
  - FACT_<EntityName>     → FACT_Sales, FACT_Inventory
  - DIM_<EntityName>      → DIM_Customer, DIM_Product
  - BRIDGE_<Purpose>      → BRIDGE_CustomerProducts

Columns:
  - <Entity>Key           → CustomerKey, ProductKey
  - <Entity>ID            → CustomerID (natural key)
  - <Descriptive Name>    → CustomerName, ProductCategory
  
Measures:
  - <Verb> <Subject>      → Total Sales, Average Price
  - <Subject> <Period>    → Sales YTD, Sales PY
  - <Subject> <Type>      → Sales Growth %, Sales Rank
```

### Date Table Requirements
Every model needs a proper date table:
```dax
Date = 
VAR StartDate = DATE(2020, 1, 1)
VAR EndDate = DATE(2025, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(StartDate, EndDate),
    "Year", YEAR([Date]),
    "Quarter", "Q" & QUARTER([Date]),
    "Month", FORMAT([Date], "MMMM"),
    "MonthNumber", MONTH([Date]),
    "Week", WEEKNUM([Date]),
    "DayOfWeek", FORMAT([Date], "dddd"),
    "YearMonth", FORMAT([Date], "YYYY-MM")
)
```

---

## 2. DAX Best Practices

### Use Variables
```dax
// GOOD: Using variables
Profit Margin % = 
VAR _revenue = [Total Revenue]
VAR _cost = [Total Cost]
VAR _profit = _revenue - _cost
RETURN
    DIVIDE(_profit, _revenue, BLANK())

// BAD: Repeated calculations
Profit Margin % = 
DIVIDE(
    [Total Revenue] - [Total Cost],
    [Total Revenue],
    BLANK()
)
```

### Always Use DIVIDE
```dax
// GOOD
DIVIDE(Numerator, Denominator, BLANK())

// BAD - Can cause errors
Numerator / Denominator
```

### Avoid CALCULATE Abuse
```dax
// BAD - Unnecessary CALCULATE
Total Sales Bad = CALCULATE(SUM(Sales[Amount]))

// GOOD - Simple aggregation
Total Sales Good = SUM(Sales[Amount])
```

### Time Intelligence Patterns
```dax
// Standard Time Intelligence Measures
Sales YTD = CALCULATE([Total Sales], DATESYTD('Date'[Date]))
Sales MTD = CALCULATE([Total Sales], DATESMTD('Date'[Date]))
Sales QTD = CALCULATE([Total Sales], DATESQTD('Date'[Date]))
Sales PY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
Sales PM = CALCULATE([Total Sales], PREVIOUSMONTH('Date'[Date]))
```

---

## 3. Dashboard Design Principles

### Visual Hierarchy
1. **Top**: KPIs and summary metrics
2. **Middle**: Trend and comparison charts
3. **Bottom**: Detail tables and drill-through

### Chart Selection Guide
| Data Type | Recommended Visual |
|-----------|-------------------|
| Single KPI | Card or Gauge |
| Trend over time | Line or Area Chart |
| Comparison | Bar Chart (horizontal) |
| Part-to-whole | Donut or Treemap |
| Geographic | Map |
| Detailed data | Table or Matrix |
| Ranking | Sorted Bar Chart |
| Distribution | Histogram |

### Color Guidelines
- Use corporate brand colors
- Reserve red/green for negative/positive
- Maximum 7 colors per visual
- Ensure accessibility (color-blind safe)

### Performance Guidelines
- Maximum 8 visuals per page
- Limit slicers to essential filters
- Use bookmarks for view switching
- Consider separate detail pages

---

## 4. Security Best Practices

### Row-Level Security Patterns
```dax
// Static RLS - Direct filter
[Region] = "West"

// Dynamic RLS - User lookup
[Email] = USERPRINCIPALNAME()

// Dynamic RLS - Security table
CONTAINS(
    SecurityTable,
    SecurityTable[UserEmail], USERPRINCIPALNAME(),
    SecurityTable[Region], Sales[Region]
)
```

### Testing RLS
- Always test with "View as Role"
- Verify no cross-role data leakage
- Test performance impact

---

## 5. Performance Optimization

### Model Size Reduction
1. Remove unused columns
2. Use appropriate data types
3. Disable auto date/time
4. Minimize cardinality

### DAX Performance
1. Use variables
2. Avoid nested iterators
3. Minimize filter context changes
4. Use TREATAS for virtual relationships

### Query Reduction
1. Limit visuals per page
2. Use aggregation tables
3. Configure incremental refresh
4. Optimize DirectQuery sources

---

## 6. Development Workflow

### Source Control
- Use PBIP format for Git integration
- Separate dataset and report files
- Version control all artifacts

### Environments
- **Development**: Personal workspace
- **Test**: Shared workspace for UAT
- **Production**: Published app

### Deployment Pipeline
1. Develop in Desktop/PBIP
2. Commit to Git
3. Deploy to Test workspace
4. UAT sign-off
5. Deploy to Production
6. Publish/Update App

---

## 7. Documentation Standards

### Required Documentation
1. Data dictionary (all tables/columns)
2. Measure documentation (purpose, logic)
3. Model diagram
4. User guide
5. Refresh schedule

### Measure Comments
```dax
// Measure: Total Revenue
// Purpose: Calculates total sales revenue excluding returns
// Logic: Sum of Amount where TransactionType = 'Sale'
// Author: BI Team
// Created: 2024-01-15
// Dependencies: None

Total Revenue = 
CALCULATE(
    SUM(Sales[Amount]),
    Sales[TransactionType] = "Sale"
)
```

---

## 8. Error Handling

### DAX Error Prevention
```dax
// Handle division by zero
DIVIDE(Numerator, Denominator, BLANK())

// Handle missing relationships
IF(HASONEVALUE(Dim[Column]), VALUES(Dim[Column]), "Multiple")

// Handle blank dates
IF(ISBLANK([Date]), "N/A", FORMAT([Date], "YYYY-MM-DD"))
```

### Data Validation
```dax
// Flag invalid records
Quality Flag = 
SWITCH(
    TRUE(),
    ISBLANK([Amount]), "Missing Amount",
    [Amount] < 0, "Negative Amount",
    [Date] > TODAY(), "Future Date",
    "Valid"
)
```
