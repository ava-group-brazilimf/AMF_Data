# DAX Patterns Reference

## Overview

This reference document provides common DAX patterns for Power BI development. Each pattern includes the formula, explanation, and usage context.

---

## 1. Basic Aggregation Patterns

### Simple Sum
```dax
Total Sales = SUM(Sales[Amount])
```

### Conditional Sum
```dax
Online Sales = 
CALCULATE(
    SUM(Sales[Amount]),
    Sales[Channel] = "Online"
)
```

### Distinct Count
```dax
Customer Count = DISTINCTCOUNT(Sales[CustomerID])
```

### Average with Blanks Handled
```dax
Average Price = 
AVERAGEX(
    FILTER(Products, NOT(ISBLANK(Products[Price]))),
    Products[Price]
)
```

---

## 2. Time Intelligence Patterns

### Year-to-Date
```dax
Sales YTD = 
CALCULATE(
    [Total Sales],
    DATESYTD('Date'[Date])
)
```

### Month-to-Date
```dax
Sales MTD = 
CALCULATE(
    [Total Sales],
    DATESMTD('Date'[Date])
)
```

### Quarter-to-Date
```dax
Sales QTD = 
CALCULATE(
    [Total Sales],
    DATESQTD('Date'[Date])
)
```

### Same Period Last Year
```dax
Sales PY = 
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)
```

### Year-over-Year Growth
```dax
YoY Growth = 
VAR CurrentYear = [Total Sales]
VAR PriorYear = [Sales PY]
RETURN
    CurrentYear - PriorYear
```

### Year-over-Year Growth %
```dax
YoY Growth % = 
DIVIDE(
    [YoY Growth],
    [Sales PY],
    BLANK()
)
```

### Previous Month
```dax
Sales PM = 
CALCULATE(
    [Total Sales],
    PREVIOUSMONTH('Date'[Date])
)
```

### Previous Quarter
```dax
Sales PQ = 
CALCULATE(
    [Total Sales],
    PREVIOUSQUARTER('Date'[Date])
)
```

### Rolling 12 Months
```dax
Sales Rolling 12M = 
CALCULATE(
    [Total Sales],
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    )
)
```

### Moving Average (3 Month)
```dax
Sales 3M Avg = 
AVERAGEX(
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -3,
        MONTH
    ),
    CALCULATE([Total Sales])
)
```

---

## 3. Comparison Patterns

### Variance to Budget
```dax
Variance = [Actual] - [Budget]
```

### Variance Percentage
```dax
Variance % = 
DIVIDE(
    [Variance],
    [Budget],
    BLANK()
)
```

### Target Achievement
```dax
Achievement % = 
DIVIDE(
    [Actual],
    [Target],
    BLANK()
)
```

### Status Indicator
```dax
Status = 
VAR Achievement = [Achievement %]
RETURN
SWITCH(
    TRUE(),
    Achievement >= 1, "🟢",
    Achievement >= 0.8, "🟡",
    "🔴"
)
```

---

## 4. Ranking Patterns

### Basic Rank
```dax
Rank = 
RANKX(
    ALL(Products[ProductName]),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

### Rank within Category
```dax
Rank in Category = 
RANKX(
    ALLSELECTED(Products[ProductName]),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

### Top N Filter
```dax
Is Top 10 = 
IF([Rank] <= 10, 1, 0)
```

### Top N with Others
```dax
Top 5 + Others = 
VAR CurrentRank = [Rank]
VAR CurrentProduct = SELECTEDVALUE(Products[ProductName])
RETURN
IF(
    CurrentRank <= 5,
    CurrentProduct,
    "Others"
)
```

---

## 5. Ratio and Percentage Patterns

### Percentage of Total
```dax
% of Total = 
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(Products)),
    BLANK()
)
```

### Percentage of Parent
```dax
% of Category = 
DIVIDE(
    [Total Sales],
    CALCULATE(
        [Total Sales],
        ALLEXCEPT(Products, Products[Category])
    ),
    BLANK()
)
```

### Margin Percentage
```dax
Margin % = 
DIVIDE(
    [Total Sales] - [Total Cost],
    [Total Sales],
    BLANK()
)
```

### Mix Analysis
```dax
Product Mix % = 
DIVIDE(
    [Total Quantity],
    CALCULATE([Total Quantity], ALL(Products[ProductName])),
    BLANK()
)
```

---

## 6. Running Total Patterns

### Running Total
```dax
Running Total = 
CALCULATE(
    [Total Sales],
    FILTER(
        ALLSELECTED('Date'[Date]),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

### Running Total within Year
```dax
Running Total YTD = 
CALCULATE(
    [Total Sales],
    FILTER(
        ALLSELECTED('Date'),
        'Date'[Date] <= MAX('Date'[Date]) &&
        'Date'[Year] = MAX('Date'[Year])
    )
)
```

---

## 7. Filter Context Patterns

### Remove Specific Filter
```dax
All Regions Sales = 
CALCULATE(
    [Total Sales],
    ALL(Geography[Region])
)
```

### Keep Only Specific Filters
```dax
Sales by Category Only = 
CALCULATE(
    [Total Sales],
    ALLEXCEPT(Products, Products[Category])
)
```

### Override Filter
```dax
Sales for ProductA = 
CALCULATE(
    [Total Sales],
    Products[ProductName] = "Product A"
)
```

### TREATAS (Virtual Relationship)
```dax
Budget from Separate Table = 
CALCULATE(
    SUM(Budget[Amount]),
    TREATAS(
        VALUES('Date'[Year]),
        Budget[Year]
    )
)
```

---

## 8. Conditional Patterns

### IF Pattern
```dax
Category Display = 
IF(
    HASONEVALUE(Products[Category]),
    VALUES(Products[Category]),
    "Multiple Categories"
)
```

### SWITCH Pattern
```dax
Quarter Name = 
SWITCH(
    QUARTER('Date'[Date]),
    1, "Q1",
    2, "Q2",
    3, "Q3",
    4, "Q4",
    "Unknown"
)
```

### SWITCH TRUE Pattern
```dax
Performance Band = 
VAR Sales = [Total Sales]
RETURN
SWITCH(
    TRUE(),
    Sales >= 1000000, "Platinum",
    Sales >= 500000, "Gold",
    Sales >= 100000, "Silver",
    "Bronze"
)
```

---

## 9. Dynamic Patterns

### Dynamic Measure Selection
```dax
Selected Metric = 
VAR Selection = SELECTEDVALUE(MetricSlicer[Metric], "Sales")
RETURN
SWITCH(
    Selection,
    "Sales", [Total Sales],
    "Quantity", [Total Quantity],
    "Margin", [Total Margin],
    "Customers", [Customer Count],
    [Total Sales]
)
```

### What-If Parameter
```dax
Scenario Sales = 
[Total Sales] * (1 + 'Growth Assumption'[Growth Assumption Value])
```

---

## 10. Error Handling Patterns

### Safe Division
```dax
Safe Ratio = DIVIDE(Numerator, Denominator, 0)
```

### Blank Handling
```dax
Sales or Zero = 
IF(ISBLANK([Total Sales]), 0, [Total Sales])
```

### Error Handling
```dax
Safe Calculation = 
IFERROR([Complex Calculation], BLANK())
```

---

## 11. Parent-Child Hierarchy Patterns

### Path Function
```dax
Employee Path = 
PATH(Employees[EmployeeID], Employees[ManagerID])
```

### Path Contains
```dax
Reports to Manager = 
PATHCONTAINS(
    [Employee Path],
    SELECTEDVALUE(Managers[ManagerID])
)
```

### Path Length (Level)
```dax
Hierarchy Level = 
PATHLENGTH([Employee Path])
```

---

## Quick Reference Card

| Pattern | Primary Function |
|---------|-----------------|
| YTD | DATESYTD |
| Prior Year | SAMEPERIODLASTYEAR |
| Rolling Period | DATESINPERIOD |
| Ranking | RANKX |
| % of Total | ALL + DIVIDE |
| Running Total | FILTER + ALLSELECTED |
| Remove Filter | ALL / ALLEXCEPT |
| Override Filter | CALCULATE + condition |
| Virtual Relationship | TREATAS |
| Safe Division | DIVIDE |
