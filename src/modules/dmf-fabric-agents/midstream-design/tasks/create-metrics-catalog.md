# Task: Create Metrics Catalog

**Command:** `*metrics`  
**Output:** `metrics-catalog.md`

---

## Objective

Document all business metrics with formulas, aggregation rules, owners, and SLAs.

---

## Prerequisites

- [ ] KPIs defined (from DataStrategist)
- [ ] Data model complete
- [ ] Business glossary available

---

## Steps

### Step 1: Gather Metrics from KPIs

Review KPIs document and extract:
- Required metrics
- Business definitions
- Expected calculations

### Step 2: Categorize Metrics

Organize metrics by type:

| Type | Description | Example |
|------|-------------|---------|
| **Additive** | Can sum across all dimensions | Revenue, Quantity |
| **Semi-additive** | Sum across some dimensions | Account Balance |
| **Non-additive** | Cannot sum | Ratio, Percentage |

### Step 3: Define Each Metric

For each metric, document:

```yaml
metric:
  id: "MTRC_001"
  name: "total_revenue"
  display_name: "Total Revenue"
  description: "Sum of all sales revenue"
  
  formula:
    expression: "SUM(fact_sales.amount)"
    base_measure: "fact_sales.amount"
    
  type: "additive"
  
  aggregations:
    allowed: [SUM, AVG, MIN, MAX]
    default: SUM
    not_allowed: []
    
  dimensions:
    sliceable_by:
      - dim_date
      - dim_customer
      - dim_product
      - dim_region
      
  filters:
    default: "date >= current_year_start"
    optional:
      - date_range
      - region
      - customer_segment
      
  ownership:
    owner: "Finance Team"
    steward: "data-steward@company.com"
    
  sla:
    freshness: "Daily by 6 AM UTC"
    accuracy: 99.9%
    
  related_metrics:
    - "avg_revenue_per_customer"
    - "revenue_ytd"
```

### Step 4: Map to Data Model

Link metrics to data model:

| Metric | Source Table | Source Column | Calculation |
|--------|--------------|---------------|-------------|
| total_revenue | fact_sales | amount | SUM |
| customer_count | dim_customer | customer_key | COUNT DISTINCT |

### Step 5: Document Derived Metrics

For calculated metrics:

```yaml
derived_metric:
  name: "avg_revenue_per_customer"
  formula: "total_revenue / customer_count"
  components:
    - "total_revenue"
    - "customer_count"
```

### Step 6: Create Catalog Document

Compile all metrics into `metrics-catalog.md`.

---

## Output Template

```markdown
# Metrics Catalog

## Overview
[Summary of metrics in this catalog]

## Metrics by Category

### Financial Metrics
| ID | Name | Formula | Type | Owner |
|----|------|---------|------|-------|
| MTRC_001 | Total Revenue | SUM(amount) | Additive | Finance |

### Operational Metrics
[Table]

### Customer Metrics
[Table]

## Detailed Definitions

### MTRC_001: Total Revenue
[Full YAML definition]

## Aggregation Rules
[Rules table]

## Ownership Matrix
[Owner assignments]
```

---

## Validation

- [ ] All KPI metrics documented
- [ ] Formulas are calculable from model
- [ ] Aggregation rules consistent
- [ ] Owners assigned
- [ ] SLAs defined
