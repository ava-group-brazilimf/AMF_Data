# DQ Rules Document Template

## Data Quality Rules Specification


| Field | Value |
|-------|-------|
| **Project:** | {project_name} |
| **Domain:** | {domain} |
| **Date:** | {date} |
| **Author:** | DataSteward |
| **Version:** | 1.0 |

---

## Overview

This document defines the data quality rules across all processing layers (Bronze, Silver, and Gold), ensuring data consistency, integrity, and reliability throughout the data pipeline.

The rules provide standardized validation controls to detect and manage data quality issues, supporting accurate reporting and reliable analytics.


### Rule Statistics

| Layer | Rules | Critical | High | Medium | Low |
|-------|-------|----------|------|--------|-----|
| Bronze | {n} | {n} | {n} | {n} | {n} |
| Silver | {n} | {n} | {n} | {n} | {n} |
| Gold | {n} | {n} | {n} | {n} | {n} |
| **Total** | {n} | {n} | {n} | {n} | {n} |

### Severity Definitions

| Severity | Action | Description |
|----------|--------|-------------|
| CRITICAL | REJECT | Record is rejected; pipeline may fail based on threshold policy |
| HIGH | QUARANTINE (data issue) / ALERT (monitoring) / DEFAULT (fallback FK) | QUARANTINE → data issue; ALERT → monitoring only; DEFAULT → fallback value (e.g., FK = -1) |
| MEDIUM | FLAG / ALERT | FLAG → processed with quality indicator; ALERT → monitoring only |
| LOW | LOG | Rule violation is logged for monitoring and trend analysis |

---

## Bronze Layer Rules

### Entity: brz_{entity_name}

| Item | Value |
|------|-------|
| Entity | brz_{entity_name} |
| Description | Bronze rules validate raw ingestion quality with a focus on mandatory fields, type conformance, and duplicate prevention. |

#### Completeness Rules

| Rule ID | Column | Check | Severity | Action | Message |
|---------|--------|-------|----------|--------|---------|
| BRZ_{ENT}_001 | {column} | NOT NULL | CRITICAL | REJECT | Column {column} must not be null |

#### Validity Rules

| Rule ID | Column | Check | Parameters | Severity | Action | Message |
|---------|--------|-------|------------|----------|--------|---------|
| BRZ_{ENT}_010 | {column} | DATA_TYPE | {type} | CRITICAL | REJECT | Column {column} must match data type {type} |

#### Uniqueness Rules

| Rule ID | Key Columns | Check | Severity | Action | Message |
|---------|---------|-------|----------|--------|---------|
| BRZ_{ENT}_020 | {key} | UNIQUE | CRITICAL | REJECT | Duplicate value detected for key {key} |

---

## Silver Layer Rules

### Entity: slv_{domain}_{entity_name}

| Item | Value |
|------|-------|
| Entity | slv_{domain}_{entity_name} |
| Description | Silver rules enforce conformed business semantics, referential integrity, and cross-field consistency. |

#### Referential Integrity Rules

| Rule ID | Source Column | Target Table | Target Column | Severity | Action | Default |
|---------|---------------|--------------|---------------|----------|--------|---------|
| SLV_{ENT}_030 | {fk_column} | {dim_table} | {pk_column} | HIGH | DEFAULT | -1 |

#### Consistency Rules

| Rule ID | Rule Expression | Description | Severity | Action | Message |
|---------|------------|-------------|----------|--------|---------|
| SLV_{ENT}_040 | `{expression}` | {description} | HIGH | QUARANTINE | {message} |

---

## Gold Layer Rules

### Entity: gld_fact_{name}

| Item | Value |
|------|-------|
| Entity | gld_fact_{name} |
| Description | Gold rules validate analytical readiness and aggregate-level stability for reporting and KPIs. |

#### Aggregation Validation Rules

| Rule ID | Check | Expected | Tolerance | Severity | Action |
|---------|-------|----------|-----------|----------|--------|
| GLD_FACT_{NAME}_060 | ROW_COUNT | > previous_batch | 0% | HIGH | ALERT |

---

## Quarantine Strategy

### Quarantine Table Schema

```sql
CREATE TABLE quarantine.{layer}_{entity}_quarantine (
    quarantine_id BIGINT GENERATED ALWAYS AS IDENTITY,
    original_record STRING,
    rule_id STRING,
    rule_message STRING,
    severity STRING,
    quarantine_timestamp TIMESTAMP,
    reviewed_by STRING,
    resolution STRING
);
```
---

### Threshold Alerts

| Severity | Threshold | Action |
|----------|-----------|--------|
| CRITICAL | > 0 records | Fail pipeline |
| HIGH | > 1% of batch | Fail pipeline |
| MEDIUM | > 5% of batch | Raise alert only |

---

## Quick Fill Example

Use one line per rule and keep fields objective.

| Rule ID | Layer | Check | Main Field |
|---------|-------|-------|------------|
| BRZ_CUSTOMER_001 | BRZ | NOT NULL | customer_id |
| BRZ_CUSTOMER_002 | BRZ | DATA_TYPE | birth_date:date |
| BRZ_CUSTOMER_003 | BRZ | UNIQUE | customer_id |
| SLV_ORDER_030 | SLV | FK | customer_id -> dim_customer.customer_id |
| SLV_ORDER_040 | SLV | BUSINESS_RULE | order_total = subtotal + tax |
| GLD_SALES_060 | GLD | KPI_RECONCILIATION | revenue_daily |

---
*Template provided by DataSteward Agent*