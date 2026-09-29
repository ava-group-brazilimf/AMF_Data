# Create Governance Framework Task

**Task ID:** create-governance  
**Agent:** DataSteward  
**Version:** 1.0

---

## Purpose

Define a comprehensive data governance framework including policies, roles, standards, and procedures for managing data as a strategic asset.

---

## Prerequisites

- Architecture document available
- Understanding of organizational structure
- Compliance requirements known

---

## Execution Steps

### Step 1: Define Governance Scope

Determine:
- Data domains covered
- Systems in scope
- Stakeholders involved
- Regulatory context

### Step 2: Define Roles and Responsibilities

Establish:
- Data Owner responsibilities
- Data Steward responsibilities
- Data Custodian responsibilities
- RACI matrix

### Step 3: Define Policies

Create policies for:
- Data access
- Data quality
- Data privacy
- Data retention
- Data security

### Step 4: Define Standards

Document standards for:
- Naming conventions
- Data types
- Metadata requirements
- Documentation

### Step 5: Define Procedures

Create procedures for:
- Change management
- Issue resolution
- Exception handling
- Escalation

### Step 6: Generate Governance Document

---

## Output Template

```markdown
# Data Governance Framework

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataSteward  
**Version:** 1.0

---

## Executive Summary

This document establishes the data governance framework for {project_name}, defining roles, policies, standards, and procedures for managing data as a strategic asset.

---

## Governance Scope

### In Scope

| Domain | Description | Systems |
|--------|-------------|---------|
| {domain_1} | {description} | {systems} |
| {domain_2} | {description} | {systems} |

### Out of Scope

- {exclusion_1}
- {exclusion_2}

### Regulatory Context

| Regulation | Applicability | Key Requirements |
|------------|---------------|------------------|
| {regulation_1} | {scope} | {requirements} |
| {regulation_2} | {scope} | {requirements} |

---

## Roles and Responsibilities

### Role Definitions

#### Data Owner

| Attribute | Description |
|-----------|-------------|
| **Definition** | Business accountable for data quality and appropriate use |
| **Scope** | Specific data domain or subject area |
| **Authority** | Approve access, define business rules, prioritize issues |

**Responsibilities:**
- Define data quality requirements
- Approve data access requests
- Establish data retention policies
- Resolve escalated data issues
- Sign off on data quality reports

#### Data Steward

| Attribute | Description |
|-----------|-------------|
| **Definition** | Operational responsibility for data quality and governance |
| **Scope** | Data domain or system |
| **Authority** | Implement policies, manage quality, resolve issues |

**Responsibilities:**
- Implement data quality rules
- Monitor data quality metrics
- Investigate and resolve data issues
- Maintain data documentation
- Train users on data standards

#### Data Custodian

| Attribute | Description |
|-----------|-------------|
| **Definition** | Technical responsibility for data systems |
| **Scope** | Technical systems and infrastructure |
| **Authority** | Implement access controls, manage systems |

**Responsibilities:**
- Implement security controls
- Manage backup and recovery
- Maintain system performance
- Apply technical changes
- Support audit requirements

### RACI Matrix

| Activity | Data Owner | Data Steward | Data Custodian | IT |
|----------|------------|--------------|----------------|-----|
| Define business rules | A | R | C | I |
| Implement DQ rules | I | A | R | C |
| Approve access | A | R | C | I |
| Implement access | I | C | A | R |
| Resolve DQ issues | A | R | C | I |
| System maintenance | I | I | A | R |
| Audit compliance | A | R | R | C |

*A = Accountable, R = Responsible, C = Consulted, I = Informed*

---

## Data Governance Policies

### Policy 1: Data Access Policy

**Purpose:** Control access to data based on classification and need

**Policy Statement:**
- All data access requires authorization
- Access granted on least-privilege principle
- Access reviewed quarterly
- Privileged access requires additional approval

**Procedures:**
1. User submits access request
2. Data Steward reviews classification
3. Data Owner approves/rejects
4. Data Custodian implements access
5. Access logged for audit

### Policy 2: Data Quality Policy

**Purpose:** Ensure data meets defined quality standards

**Policy Statement:**
- All data must meet defined quality rules
- Quality issues must be tracked and resolved
- Quality metrics reported regularly
- Source systems responsible for initial quality

**Procedures:**
1. DQ rules defined per data element
2. Automated quality checks on ingestion
3. Quarantine for failed records
4. Investigation within SLA
5. Root cause resolution

### Policy 3: Data Retention Policy

**Purpose:** Define data lifecycle and retention periods

**Policy Statement:**
- Data retained per regulatory and business requirements
- Retention periods documented per data class
- Expired data archived or deleted
- Retention audited annually

**Retention Schedule:**

| Data Class | Active | Archive | Destroy |
|------------|--------|---------|---------|
| Transactional | 2 years | 5 years | 7 years |
| Reference | Indefinite | N/A | N/A |
| Audit/Compliance | 7 years | 3 years | 10 years |
| Temporary/Staging | 30 days | N/A | 30 days |

### Policy 4: Data Privacy Policy

**Purpose:** Protect personal and sensitive data

**Policy Statement:**
- Personal data handled per privacy regulations
- Consent tracked for data use
- Privacy impact assessments for new uses
- Data subject rights supported

**Privacy Controls:**
- Data minimization
- Purpose limitation
- Access restriction
- Encryption and masking
- Audit logging

### Policy 5: Data Security Policy

**Purpose:** Protect data from unauthorized access and threats

**Policy Statement:**
- Data encrypted at rest and in transit
- Access authenticated and authorized
- Security events monitored
- Incidents responded to promptly

---

## Data Standards

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Database | `{env}_{project}` | prd_analytics |
| Schema | `{layer}` | silver |
| Table | `{layer}_{domain}_{entity}` | slv_sales_orders |
| Column | `{descriptor}_{type}` | order_date, is_active |
| PK | `{entity}_sk` | order_sk |
| FK | `{ref_entity}_sk` | customer_sk |

### Data Type Standards

| Logical Type | Physical Type | Usage |
|--------------|---------------|-------|
| Identifier | BIGINT | Surrogate keys |
| Code | STRING(10) | Short codes |
| Name | STRING(255) | Names, descriptions |
| Amount | DECIMAL(18,4) | Currency values |
| Quantity | INT | Counts |
| Flag | BOOLEAN | Yes/No indicators |
| Date | DATE | Calendar dates |
| Timestamp | TIMESTAMP | Point in time (UTC) |

### Metadata Requirements

All data assets must have:
- Business name
- Technical name
- Description
- Data Owner
- Classification
- Source system
- Update frequency
- Last updated date

---

## Governance Procedures

### Change Management

**Purpose:** Control changes to data structures and rules

**Process:**
1. Change request submitted
2. Impact assessment performed
3. Stakeholders consulted
4. Data Owner approval
5. Change implemented in non-prod
6. Testing and validation
7. Production deployment
8. Documentation updated

### Issue Resolution

**Purpose:** Resolve data quality and governance issues

**SLA by Severity:**

| Severity | Response | Resolution |
|----------|----------|------------|
| Critical | 1 hour | 4 hours |
| High | 4 hours | 24 hours |
| Medium | 1 day | 1 week |
| Low | 1 week | 1 month |

**Escalation Path:**
1. Data Steward (initial)
2. Data Owner (if unresolved)
3. Governance Council (if cross-domain)

### Exception Handling

**Purpose:** Manage approved deviations from standards

**Process:**
1. Exception request with justification
2. Risk assessment
3. Data Owner approval
4. Time-limited approval
5. Regular review
6. Remediation plan

---

## Governance Metrics

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data Completeness | > 99% | % non-null required fields |
| Data Validity | > 99% | % passing validation rules |
| Data Timeliness | < SLA | Time from source to consumption |
| Issue Resolution | < SLA | Time to resolve issues |

### Compliance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Access Review Completion | 100% | Quarterly reviews completed |
| Policy Acknowledgment | 100% | Users acknowledged policies |
| Audit Findings Resolved | 100% | Open audit items |

---

## Governance Council

### Purpose

Provide strategic oversight of data governance program

### Composition

- Executive Sponsor
- Data Owners (domain representatives)
- Lead Data Steward
- IT Representative
- Compliance Representative

### Responsibilities

- Approve governance policies
- Resolve cross-domain issues
- Prioritize governance initiatives
- Review governance metrics
- Sponsor governance improvements

### Meeting Cadence

- Monthly governance review
- Quarterly metrics review
- Annual policy review

---

## Next Steps

1. Classify data - `*classify-data`
2. Map compliance - `*map-compliance`
3. Proceed to Gate 2 validation

---

*Document generated by DataSteward Agent*
```

---

## Validation Checklist

Before completing, verify:

- [ ] Roles clearly defined
- [ ] RACI matrix complete
- [ ] All policies documented
- [ ] Standards specified
- [ ] Procedures defined
- [ ] Metrics identified
- [ ] Governance council established
