# Governance Framework Template

# Data Governance Framework

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataSteward  
**Version:** 1.0

---

## Governance Scope

### In Scope

| Domain | Description | Systems |
|--------|-------------|---------|
| {domain} | {description} | {systems} |

### Regulatory Context

| Regulation | Applicability | Key Requirements |
|------------|---------------|------------------|
| {regulation} | {scope} | {requirements} |

---

## Roles and Responsibilities

### Role Definitions

#### Data Owner
- Define data quality requirements
- Approve data access requests
- Establish data retention policies
- Resolve escalated data issues

#### Data Steward
- Implement data quality rules
- Monitor data quality metrics
- Investigate and resolve data issues
- Maintain data documentation

#### Data Custodian
- Implement security controls
- Manage backup and recovery
- Maintain system performance

### RACI Matrix

| Activity | Data Owner | Data Steward | Data Custodian | IT |
|----------|------------|--------------|----------------|-----|
| Define business rules | A | R | C | I |
| Implement DQ rules | I | A | R | C |
| Approve access | A | R | C | I |
| System maintenance | I | I | A | R |

---

## Data Governance Policies

### Policy 1: Data Access Policy

**Purpose:** Control access to data based on classification and need

**Policy Statement:**
- All data access requires authorization
- Access granted on least-privilege principle
- Access reviewed quarterly

### Policy 2: Data Quality Policy

**Purpose:** Ensure data meets defined quality standards

**Policy Statement:**
- All data must meet defined quality rules
- Quality issues must be tracked and resolved
- Quality metrics reported regularly

### Policy 3: Data Retention Policy

**Retention Schedule:**

| Data Class | Active | Archive | Destroy |
|------------|--------|---------|---------|
| Transactional | 2 years | 5 years | 7 years |
| Reference | Indefinite | N/A | N/A |
| Audit | 7 years | 3 years | 10 years |

---

## Data Standards

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Schema | `{layer}` | silver |
| Table | `{layer}_{domain}_{entity}` | slv_sales_orders |
| Column | `{descriptor}_{type}` | order_date |

### Data Type Standards

| Logical Type | Physical Type |
|--------------|---------------|
| Identifier | BIGINT |
| Amount | DECIMAL(18,4) |
| Flag | BOOLEAN |
| Date | DATE |
| Timestamp | TIMESTAMP |

---

## Governance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data Completeness | > 99% | % non-null required fields |
| Data Validity | > 99% | % passing validation rules |
| Issue Resolution | < SLA | Time to resolve issues |

---

## Governance Council

### Composition
- Executive Sponsor
- Data Owners
- Lead Data Steward
- IT Representative

### Meeting Cadence
- Monthly governance review
- Quarterly metrics review
- Annual policy review

---

*Template provided by DataSteward Agent*
