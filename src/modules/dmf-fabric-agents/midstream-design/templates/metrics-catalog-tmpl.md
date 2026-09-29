# Metrics Catalog Template

## Catalog Overview

**Project:** {project_name}  
**Version:** {version}  
**Last Updated:** {date}  
**Owner:** Sofia (DataModeler)

---

## Metrics Summary

| Category | Count | Owner |
|----------|-------|-------|
| Financial | {n} | Finance Team |
| Operational | {n} | Operations Team |
| Customer | {n} | Customer Success |
| Total | {N} | - |

---

## Financial Metrics

### MTRC_FIN_001: Total Revenue

| Attribute | Value |
|-----------|-------|
| **ID** | MTRC_FIN_001 |
| **Name** | total_revenue |
| **Display Name** | Total Revenue |
| **Description** | Sum of all sales revenue |
| **Type** | Additive |

**Formula:**
```
SUM(fact_sales.amount)
```

**Source:**
| Table | Column | Transformation |
|-------|--------|----------------|
| fact_sales | amount | SUM |

**Aggregations:**
| Aggregation | Allowed | Notes |
|-------------|---------|-------|
| SUM | ✅ | Default |
| AVG | ✅ | Average per period |
| MIN | ✅ | |
| MAX | ✅ | |
| COUNT | ❌ | Use order_count instead |

**Sliceable By:**
- dim_date (Year, Quarter, Month, Day)
- dim_customer (Segment, Region)
- dim_product (Category, Subcategory)

**Filters:**
| Filter | Default | Optional |
|--------|---------|----------|
| Date Range | Current Year | ✅ |
| Region | All | ✅ |
| Customer Segment | All | ✅ |

**Ownership:**
| Role | Contact |
|------|---------|
| Owner | Finance Team |
| Steward | data-steward@company.com |

**SLA:**
| Metric | Target |
|--------|--------|
| Freshness | Daily by 6 AM UTC |
| Accuracy | 99.9% |

---

### MTRC_FIN_002: Revenue YTD

| Attribute | Value |
|-----------|-------|
| **ID** | MTRC_FIN_002 |
| **Name** | revenue_ytd |
| **Display Name** | Revenue Year to Date |
| **Description** | Total revenue from start of current year |
| **Type** | Additive (Time-scoped) |

**Formula:**
```
SUM(fact_sales.amount) 
WHERE fact_sales.date_key >= year_start_key
```

---

## Operational Metrics

### MTRC_OPS_001: Order Count

| Attribute | Value |
|-----------|-------|
| **ID** | MTRC_OPS_001 |
| **Name** | order_count |
| **Display Name** | Total Orders |
| **Description** | Count of distinct orders |
| **Type** | Additive |

**Formula:**
```
COUNT(DISTINCT fact_sales.order_id)
```

---

## Customer Metrics

### MTRC_CUS_001: Customer Count

| Attribute | Value |
|-----------|-------|
| **ID** | MTRC_CUS_001 |
| **Name** | customer_count |
| **Display Name** | Active Customers |
| **Description** | Count of distinct customers with transactions |
| **Type** | Semi-Additive |

**Formula:**
```
COUNT(DISTINCT fact_sales.customer_key)
```

**Note:** Semi-additive - cannot sum across time periods.

---

## Derived Metrics

### MTRC_DER_001: Average Revenue per Customer

| Attribute | Value |
|-----------|-------|
| **ID** | MTRC_DER_001 |
| **Name** | avg_revenue_per_customer |
| **Display Name** | Average Revenue per Customer |
| **Description** | Average revenue generated per customer |
| **Type** | Non-Additive (Ratio) |

**Formula:**
```
total_revenue / customer_count
```

**Components:**
| Component | Reference |
|-----------|-----------|
| total_revenue | MTRC_FIN_001 |
| customer_count | MTRC_CUS_001 |

**Warning:** Cannot be summed or averaged directly.

---

## Aggregation Rules Summary

| Metric Type | SUM | AVG | MIN | MAX | COUNT |
|-------------|-----|-----|-----|-----|-------|
| Additive | ✅ | ✅ | ✅ | ✅ | ✅ |
| Semi-Additive | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| Non-Additive | ❌ | ❌ | ✅ | ✅ | ✅ |

⚠️ = Allowed only for certain dimensions (not time)

---

## Ownership Matrix

| Metric Category | Owner | Steward | Approver |
|-----------------|-------|---------|----------|
| Financial | Finance | data-steward | CFO |
| Operational | Operations | data-steward | COO |
| Customer | Customer Success | data-steward | CCO |

---

## Glossary

| Term | Definition |
|------|------------|
| Additive | Metric that can be summed across all dimensions |
| Semi-Additive | Metric that can be summed across some dimensions |
| Non-Additive | Metric that cannot be summed (ratios, percentages) |
| Grain | The level of detail represented by one row |
| Conformed | Metric definition shared across multiple facts |
