# Task: Define Initial DQ Requirements

```yaml
task_id: define-dq-initial
agent: business-analyst
version: "1.1"
command: "*dq-initial"
phase: UPSTREAM
gate: 1
output: "dq-initial.md"
output_folder: "projects/{project_name}/outputs/upstream/analysis/"
```

---

## Purpose

Define initial data quality requirements to establish quality expectations early in the project, before detailed DQ rules are created by the DataSteward.

---

## Prerequisites

- STTM document (created or in progress)
- Understanding of critical data fields
- Knowledge of business requirements for data quality

---

## Execution Steps

### Step 1: Identify Data Quality Dimensions

Select relevant DQ dimensions:

| Dimension | Description | Example Rule |
|-----------|-------------|--------------|
| **Completeness** | Data is not missing | NOT NULL checks |
| **Accuracy** | Data is correct | Valid ranges, lookups |
| **Timeliness** | Data is up-to-date | Within SLA |
| **Consistency** | Data is consistent | Cross-source matching |
| **Uniqueness** | No duplicates | Unique key checks |
| **Validity** | Data conforms to rules | Format, domain checks |

### Step 2: Identify Critical Fields

From STTM, identify fields that are:
1. Used in KPI calculations
2. Primary/Foreign keys
3. Business-critical decisions
4. Customer-facing
5. Regulatory/Compliance

### Step 3: Set Thresholds

For each dimension and critical field:
1. Define acceptable threshold (e.g., 99% complete)
2. Define action on failure
3. Assign priority

### Step 4: Define Initial Validation Rules

Create high-level validation rules:
1. Rule description
2. Affected field(s)
3. Dimension addressed
4. Threshold

### Step 5: Generate DQ Initial Document

---

## Output Template

```markdown
# Initial Data Quality Requirements

**Project:** {project_name}  
**Date:** {date}  
**Author:** BusinessAnalyst  
**Version:** 1.0

---

## Executive Summary

This document defines initial data quality requirements to be validated throughout the data pipeline. Detailed DQ rules will be elaborated by the DataSteward during the MIDSTREAM phase.

---

## Data Quality Dimensions

### Applicable Dimensions

| Dimension | Applicable | Priority | Default Threshold |
|-----------|------------|----------|-------------------|
| Completeness | ✅ | High | ≥ 95% |
| Accuracy | ✅ | High | ≥ 98% |
| Timeliness | ✅ | Medium | Within SLA |
| Consistency | ✅ | Medium | ≥ 99% |
| Uniqueness | ✅ | High | 100% |
| Validity | ✅ | High | ≥ 99% |

### Dimension Definitions

**Completeness**
- Required fields are not NULL
- Optional fields have expected fill rate
- Records are not missing

**Accuracy**
- Values are within expected ranges
- Lookups match reference data
- Calculations are correct

**Timeliness**
- Data arrives within SLA
- Data is not stale
- Timestamps are valid

**Consistency**
- Same data across sources matches
- Related fields are consistent
- Historical data is stable

**Uniqueness**
- Primary keys are unique
- No duplicate records
- Entity resolution is correct

**Validity**
- Values conform to data types
- Formats are correct
- Business rules are satisfied

---

## Critical Fields Identification

### High Priority (Must Pass)

| # | Field | Table | Dimension | Threshold | Justification |
|---|-------|-------|-----------|-----------|---------------|
| 1 | {field_name} | {table} | Completeness | 100% | Primary Key |
| 2 | {field_name} | {table} | Uniqueness | 100% | Primary Key |
| 3 | {field_name} | {table} | Accuracy | 99% | KPI calculation |
| 4 | {field_name} | {table} | Validity | 100% | Date field |

### Medium Priority (Should Pass)

| # | Field | Table | Dimension | Threshold | Justification |
|---|-------|-------|-----------|-----------|---------------|
| 5 | {field_name} | {table} | Completeness | 95% | Reporting field |
| 6 | {field_name} | {table} | Consistency | 98% | Cross-source field |

### Low Priority (Monitor)

| # | Field | Table | Dimension | Threshold | Justification |
|---|-------|-------|-----------|-----------|---------------|
| 7 | {field_name} | {table} | Completeness | 80% | Optional field |

---

## Initial Validation Rules

### Rule DQ-001: Primary Key Completeness

| Attribute | Value |
|-----------|-------|
| **Description** | Primary key fields must not be NULL |
| **Dimension** | Completeness |
| **Fields** | {list of PK fields} |
| **Threshold** | 100% |
| **Priority** | High |
| **Action on Failure** | Reject record |

### Rule DQ-002: Primary Key Uniqueness

| Attribute | Value |
|-----------|-------|
| **Description** | Primary key values must be unique |
| **Dimension** | Uniqueness |
| **Fields** | {list of PK fields} |
| **Threshold** | 100% |
| **Priority** | High |
| **Action on Failure** | Reject duplicate |

### Rule DQ-003: Reference Data Validity

| Attribute | Value |
|-----------|-------|
| **Description** | Lookup fields must match reference data |
| **Dimension** | Validity |
| **Fields** | {lookup fields} |
| **Threshold** | 99% |
| **Priority** | High |
| **Action on Failure** | Flag for review |

### Rule DQ-004: Date Field Validity

| Attribute | Value |
|-----------|-------|
| **Description** | Date fields must be valid dates |
| **Dimension** | Validity |
| **Fields** | {date fields} |
| **Threshold** | 100% |
| **Priority** | High |
| **Action on Failure** | Reject record |

### Rule DQ-005: Numeric Range Check

| Attribute | Value |
|-----------|-------|
| **Description** | Numeric values must be within expected ranges |
| **Dimension** | Accuracy |
| **Fields** | {numeric fields} |
| **Ranges** | {field: [min, max]} |
| **Threshold** | 99% |
| **Priority** | Medium |
| **Action on Failure** | Flag for review |

### Rule DQ-006: Timeliness SLA

| Attribute | Value |
|-----------|-------|
| **Description** | Data must arrive within defined SLA |
| **Dimension** | Timeliness |
| **SLA** | {e.g., Data available by 6:00 AM} |
| **Threshold** | 99% |
| **Priority** | Medium |
| **Action on Failure** | Alert operations |

---

## DQ Thresholds by Layer

| Layer | Completeness | Accuracy | Uniqueness | Validity |
|-------|--------------|----------|------------|----------|
| Landing | N/A | N/A | N/A | N/A |
| Bronze | ≥ 95% | ≥ 95% | 100% | ≥ 95% |
| Silver | ≥ 98% | ≥ 98% | 100% | ≥ 99% |
| Gold | ≥ 99% | ≥ 99% | 100% | 100% |

---

## Actions on DQ Failure

| Severity | Action | Description |
|----------|--------|-------------|
| Critical | Reject | Record not processed, logged to error table |
| Major | Quarantine | Record moved to quarantine for review |
| Minor | Flag | Record processed with DQ flag |
| Warning | Log | Issue logged, record processed normally |

---

## DQ Monitoring Requirements

### Dashboards Needed
- [ ] DQ Summary Dashboard (overall pass rates)
- [ ] DQ Trend Dashboard (quality over time)
- [ ] DQ Exception Dashboard (failed records)

### Alerts Needed
- [ ] Alert on critical DQ failure
- [ ] Alert on threshold breach
- [ ] Alert on SLA miss

---

## Open Questions

| # | Question | Impact | Owner |
|---|----------|--------|-------|
| 1 | {question about DQ thresholds} | {impact} | {owner} |

---

## Next Steps

1. Review DQ requirements with stakeholders
2. Proceed to Gate 1 validation
3. DataSteward will elaborate detailed DQ rules in MIDSTREAM

---

*Document generated by BusinessAnalyst Agent*
```

---

## DQ Dimension Reference

### Completeness Rules
```sql
-- NULL check
SELECT COUNT(*) WHERE field IS NULL

-- Fill rate
SELECT COUNT(field) / COUNT(*) * 100 AS fill_rate
```

### Uniqueness Rules
```sql
-- Duplicate check
SELECT pk_field, COUNT(*) 
GROUP BY pk_field 
HAVING COUNT(*) > 1
```

### Validity Rules
```sql
-- Date format
WHERE TRY_CAST(date_field AS DATE) IS NULL

-- Lookup match
WHERE code NOT IN (SELECT code FROM reference_table)
```

---

## Validation Checklist

Before completing, verify:

- [ ] Relevant DQ dimensions identified
- [ ] Critical fields identified with justification
- [ ] Thresholds set for each dimension
- [ ] Initial validation rules documented
- [ ] Actions on failure defined
- [ ] Priority assigned to each rule
- [ ] Monitoring requirements stated
