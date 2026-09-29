# Create DQ Rules Task

**Task ID:** create-dq-rules  
**Agent:** DataSteward  
**Version:** 1.0

---

## Purpose

Define comprehensive data quality rules for all data layers, specifying validation logic, severity levels, and actions for quality violations.

---

## Prerequisites

- Data model available (from DataArchitect)
- Initial DQ requirements (from BusinessAnalyst)
- Understanding of business criticality

---

## Execution Steps

### Step 1: Review Data Model

Analyze:
- All entities per layer (Bronze, Silver, Gold)
- Column definitions and types
- Relationships and foreign keys
- Business keys

### Step 2: Review Initial DQ Requirements

Load from BusinessAnalyst:
- Critical data elements identified
- Known data quality issues
- Business validation rules

### Step 3: Define Rule Categories

For each layer, define rules in categories:

1. **Completeness**: Missing/null checks
2. **Validity**: Format and range validation
3. **Uniqueness**: Duplicate detection
4. **Referential**: Foreign key integrity
5. **Consistency**: Cross-field validation
6. **Timeliness**: Freshness checks
7. **Accuracy**: Value correctness

### Step 4: Set Severity and Actions

For each rule:
- **CRITICAL**: Reject record, fail pipeline
- **HIGH**: Quarantine for review
- **MEDIUM**: Flag and process
- **LOW**: Log only

### Step 5: Define Quarantine Strategy

Document:
- Quarantine table structure
- Reprocessing workflow
- Retention policy

### Step 6: Generate DQ Rules Document

---

## Output Template

```markdown
# Data Quality Rules Specification

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataSteward  
**Version:** 1.0

---

## Overview

This document defines comprehensive data quality rules for all data layers.

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
| CRITICAL | REJECT | Record rejected, pipeline may fail |
| HIGH | QUARANTINE | Record sent to quarantine for review |
| MEDIUM | FLAG | Record flagged but processed |
| LOW | LOG | Issue logged only |

---

## Bronze Layer Rules

### Entity: brz_{entity_name}

#### Completeness Rules

| Rule ID | Column | Check | Severity | Action | Message |
|---------|--------|-------|----------|--------|---------|
| BRZ_{ENT}_001 | {column} | NOT NULL | CRITICAL | REJECT | {column} is required |
| BRZ_{ENT}_002 | {column} | NOT NULL | HIGH | QUARANTINE | {column} should not be null |

#### Validity Rules

| Rule ID | Column | Check | Parameters | Severity | Action | Message |
|---------|--------|-------|------------|----------|--------|---------|
| BRZ_{ENT}_010 | {column} | DATA_TYPE | {expected_type} | CRITICAL | REJECT | Invalid data type |
| BRZ_{ENT}_011 | {column} | REGEX | {pattern} | HIGH | QUARANTINE | Invalid format |
| BRZ_{ENT}_012 | {column} | RANGE | min={x}, max={y} | MEDIUM | FLAG | Value out of range |

#### Uniqueness Rules

| Rule ID | Columns | Check | Severity | Action | Message |
|---------|---------|-------|----------|--------|---------|
| BRZ_{ENT}_020 | {key_column} | UNIQUE | CRITICAL | REJECT | Duplicate key found |

---

## Silver Layer Rules

### Entity: slv_{domain}_{entity_name}

#### Completeness Rules

| Rule ID | Column | Check | Severity | Action | Message |
|---------|--------|-------|----------|--------|---------|
| SLV_{ENT}_001 | {column} | NOT NULL | CRITICAL | REJECT | {column} is required |

#### Referential Integrity Rules

| Rule ID | Source Column | Target Table | Target Column | Severity | Action | Default |
|---------|---------------|--------------|---------------|----------|--------|---------|
| SLV_{ENT}_030 | {fk_column} | {dim_table} | {pk_column} | HIGH | DEFAULT | -1 |

#### Consistency Rules

| Rule ID | Expression | Description | Severity | Action | Message |
|---------|------------|-------------|----------|--------|---------|
| SLV_{ENT}_040 | `start_date <= end_date` | Date order | HIGH | QUARANTINE | Invalid date range |
| SLV_{ENT}_041 | `amount >= 0` | Positive amount | MEDIUM | FLAG | Negative amount |

#### Business Rules

| Rule ID | Rule Name | Expression | Severity | Action | Message |
|---------|-----------|------------|----------|--------|---------|
| SLV_{ENT}_050 | {rule_name} | {expression} | {severity} | {action} | {message} |

---

## Gold Layer Rules

### Entity: gld_fact_{name}

#### Completeness Rules

| Rule ID | Column | Check | Severity | Action | Message |
|---------|--------|-------|----------|--------|---------|
| GLD_FACT_{NAME}_001 | {dim_sk} | NOT NULL | CRITICAL | REJECT | Dimension key required |

#### Referential Integrity Rules

| Rule ID | Source Column | Target Table | Target Column | Severity | Action |
|---------|---------------|--------------|---------------|----------|--------|
| GLD_FACT_{NAME}_030 | date_sk | gld_dim_date | date_sk | CRITICAL | REJECT |
| GLD_FACT_{NAME}_031 | {dim}_sk | gld_dim_{dim} | {dim}_sk | CRITICAL | REJECT |

#### Aggregation Validation Rules

| Rule ID | Check | Expected | Tolerance | Severity | Action |
|---------|-------|----------|-----------|----------|--------|
| GLD_FACT_{NAME}_060 | ROW_COUNT | > previous_count | 0% | HIGH | ALERT |
| GLD_FACT_{NAME}_061 | SUM({measure}) | reconciles_to_source | 0.01% | HIGH | ALERT |

---

## Cross-Layer Rules

### Data Lineage Validation

| Rule ID | Source | Target | Check | Severity |
|---------|--------|--------|-------|----------|
| XLAY_001 | brz_{entity} | slv_{entity} | COUNT_MATCH | MEDIUM |
| XLAY_002 | slv_{entity} | gld_fact | SUM_MATCH | HIGH |

### Freshness Rules

| Rule ID | Entity | Max Age | Severity | Action |
|---------|--------|---------|----------|--------|
| FRESH_001 | brz_{entity} | 24 hours | HIGH | ALERT |
| FRESH_002 | gld_fact_{name} | 4 hours | CRITICAL | ALERT |

---

## Quarantine Strategy

### Quarantine Table Schema

```sql
CREATE TABLE quarantine.{layer}_{entity}_quarantine (
    quarantine_id BIGINT GENERATED ALWAYS AS IDENTITY,
    original_record STRING,  -- JSON of original record
    rule_id STRING,
    rule_message STRING,
    severity STRING,
    quarantine_timestamp TIMESTAMP,
    reviewed_by STRING,
    reviewed_at TIMESTAMP,
    resolution STRING,  -- REPROCESS, IGNORE, FIXED
    reprocessed_at TIMESTAMP
);
```

### Quarantine Workflow

1. **Capture**: Failed records written to quarantine
2. **Alert**: Notification sent if threshold exceeded
3. **Review**: Data steward reviews quarantined records
4. **Resolution**: Fix source, manual correction, or ignore
5. **Reprocess**: Fixed records reprocessed through pipeline

### Retention Policy

| Severity | Retention | Auto-Archive |
|----------|-----------|--------------|
| CRITICAL | 90 days | No |
| HIGH | 60 days | After 30 days |
| MEDIUM | 30 days | After 14 days |
| LOW | 7 days | Yes |

---

## Threshold Alerts

### Pipeline Failure Thresholds

| Severity | Threshold | Action |
|----------|-----------|--------|
| CRITICAL | > 0 records | Fail pipeline |
| HIGH | > 1% of batch | Fail pipeline |
| MEDIUM | > 5% of batch | Alert only |
| LOW | N/A | Log only |

### Alert Configuration

| Alert | Condition | Channel | Recipients |
|-------|-----------|---------|------------|
| Critical Failure | Any CRITICAL | PagerDuty | On-call |
| High Threshold | HIGH > 1% | Teams | Data Team |
| Daily Summary | All | Email | Data Steward |

---

## Implementation Notes

### DQ Framework Integration

Rules should be implemented using:
- {DQ tool/framework}
- Check configuration location: {path}

### Execution Order

1. Schema validation (Bronze)
2. Completeness checks
3. Validity checks
4. Uniqueness checks
5. Referential integrity
6. Business rules
7. Cross-layer validation

---

## Next Steps

1. Create governance framework - `*create-governance`
2. Classify data - `*classify-data`
3. Proceed to Gate 2 validation

---

*Document generated by DataSteward Agent*
```

---

## Validation Checklist

Before completing, verify:

- [ ] All entities have rules defined
- [ ] Critical columns have NOT NULL rules
- [ ] Foreign keys have referential integrity rules
- [ ] Business rules from STTM included
- [ ] Quarantine strategy defined
- [ ] Thresholds appropriate
- [ ] Severity levels balanced
