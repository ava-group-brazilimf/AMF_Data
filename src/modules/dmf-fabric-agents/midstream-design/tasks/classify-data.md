# Classify Data Task

**Task ID:** classify-data  
**Agent:** DataSteward  
**Version:** 1.0

---

## Purpose

Classify all data elements by sensitivity level to ensure appropriate handling, protection, and access controls.

---

## Prerequisites

- Data model available
- Understanding of regulatory requirements
- Business context of data usage

---

## Execution Steps

### Step 1: Review Classification Framework

Standard classification levels:
- **PUBLIC**: Non-sensitive, freely shareable
- **INTERNAL**: Business use only
- **CONFIDENTIAL**: Sensitive business data
- **RESTRICTED**: PII/PHI/PCI, maximum protection

### Step 2: Identify Data Categories

Common categories:
- Personal Identifiable Information (PII)
- Protected Health Information (PHI)
- Payment Card Industry (PCI)
- Financial data
- Business sensitive
- Operational data
- Public data

### Step 3: Classify Each Entity

For each table:
- Review column definitions
- Identify sensitive columns
- Assign classification level
- Document rationale

### Step 4: Define Handling Requirements

Per classification:
- Access controls
- Encryption requirements
- Masking requirements
- Audit requirements
- Retention requirements

### Step 5: Generate Classification Document

---

## Output Template

```markdown
# Data Classification Document

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataSteward  
**Version:** 1.0

---

## Classification Framework

### Sensitivity Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **PUBLIC** | Non-sensitive, can be shared externally | Product catalogs, public reports |
| **INTERNAL** | Business use, not for external sharing | Internal metrics, operational data |
| **CONFIDENTIAL** | Sensitive business, restricted access | Financial data, contracts, strategies |
| **RESTRICTED** | Highest sensitivity, regulatory protection | PII, PHI, PCI, credentials |

### Data Categories

| Category | Abbreviation | Typical Classification | Regulations |
|----------|--------------|------------------------|-------------|
| Personal Identifiable Information | PII | RESTRICTED | GDPR, LGPD |
| Protected Health Information | PHI | RESTRICTED | HIPAA |
| Payment Card Industry | PCI | RESTRICTED | PCI-DSS |
| Financial Business | FIN | CONFIDENTIAL | SOX |
| Intellectual Property | IP | CONFIDENTIAL | Trade secret |
| Operational | OPS | INTERNAL | Internal policy |
| Public | PUB | PUBLIC | N/A |

---

## Handling Requirements by Classification

### PUBLIC

| Control | Requirement |
|---------|-------------|
| **Access** | Open access |
| **Encryption at Rest** | Optional |
| **Encryption in Transit** | Recommended |
| **Masking** | Not required |
| **Audit** | Basic logging |
| **Retention** | Per business need |

### INTERNAL

| Control | Requirement |
|---------|-------------|
| **Access** | Authenticated users |
| **Encryption at Rest** | Recommended |
| **Encryption in Transit** | Required |
| **Masking** | Not required |
| **Audit** | Access logging |
| **Retention** | Per business policy |

### CONFIDENTIAL

| Control | Requirement |
|---------|-------------|
| **Access** | Role-based, need-to-know |
| **Encryption at Rest** | Required |
| **Encryption in Transit** | Required |
| **Masking** | In non-production |
| **Audit** | Full audit trail |
| **Retention** | Per policy, secure deletion |

### RESTRICTED

| Control | Requirement |
|---------|-------------|
| **Access** | Named individuals, MFA |
| **Encryption at Rest** | Required, managed keys |
| **Encryption in Transit** | Required, TLS 1.2+ |
| **Masking** | Required in non-prod, optional in prod |
| **Audit** | Comprehensive, tamper-proof |
| **Retention** | Per regulation, certified deletion |
| **Additional** | DLP monitoring, access reviews |

---

## Entity Classification

### Bronze Layer

| Entity | Classification | Categories | Rationale |
|--------|----------------|------------|-----------|
| brz_{entity_1} | {level} | {categories} | {rationale} |
| brz_{entity_2} | {level} | {categories} | {rationale} |

### Silver Layer

| Entity | Classification | Categories | Rationale |
|--------|----------------|------------|-----------|
| slv_{domain}_{entity_1} | {level} | {categories} | {rationale} |
| slv_{domain}_{entity_2} | {level} | {categories} | {rationale} |

### Gold Layer

| Entity | Classification | Categories | Rationale |
|--------|----------------|------------|-----------|
| gld_dim_{entity_1} | {level} | {categories} | {rationale} |
| gld_fact_{name} | {level} | {categories} | {rationale} |

---

## Column-Level Classification

### High Sensitivity Columns (RESTRICTED)

| Entity | Column | Category | Classification | Masking Rule |
|--------|--------|----------|----------------|--------------|
| {entity} | customer_name | PII | RESTRICTED | Partial redact |
| {entity} | email_address | PII | RESTRICTED | Hash |
| {entity} | phone_number | PII | RESTRICTED | Partial mask |
| {entity} | ssn | PII | RESTRICTED | Token |
| {entity} | credit_card | PCI | RESTRICTED | Last 4 only |

### Confidential Columns

| Entity | Column | Category | Classification | Notes |
|--------|--------|----------|----------------|-------|
| {entity} | salary | FIN | CONFIDENTIAL | Aggregate only |
| {entity} | contract_value | FIN | CONFIDENTIAL | Need-to-know |

### Internal Columns

| Entity | Column | Category | Classification | Notes |
|--------|--------|----------|----------------|-------|
| {entity} | order_id | OPS | INTERNAL | Business reference |
| {entity} | status | OPS | INTERNAL | Operational |

---

## Masking Rules

### Masking Techniques

| Technique | Description | Use Case | Example |
|-----------|-------------|----------|---------|
| **Redaction** | Replace with fixed value | Testing | John Doe → XXXXX |
| **Partial Mask** | Show partial value | Support | 555-123-4567 → XXX-XXX-4567 |
| **Hashing** | One-way hash | Analytics | email → sha256(email) |
| **Tokenization** | Reversible token | Production | 1234-5678 → TOKEN_ABC123 |
| **Generalization** | Reduce precision | Analytics | Age 35 → Age 30-40 |
| **Nullification** | Set to null | Minimal | Value → NULL |
| **Shuffling** | Swap between records | Testing | Real values, wrong rows |
| **Synthetic** | Generate fake data | Testing | Random realistic values |

### Masking Configuration

| Column Type | Production | Non-Production |
|-------------|------------|----------------|
| Full Name | None | Partial redact |
| Email | None | Hash |
| Phone | None | Partial mask |
| SSN/ID | None | Full redact |
| Address | None | Synthetic |
| DOB | None | Generalize (year only) |

---

## Access Matrix by Classification

| Role | PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED |
|------|--------|----------|--------------|------------|
| Public | ✅ | ❌ | ❌ | ❌ |
| Employee | ✅ | ✅ | ❌ | ❌ |
| Analyst | ✅ | ✅ | ✅ (masked) | ❌ |
| Manager | ✅ | ✅ | ✅ | ❌ |
| Data Steward | ✅ | ✅ | ✅ | ✅ (audit) |
| Data Owner | ✅ | ✅ | ✅ | ✅ |

---

## Classification Review Process

### Initial Classification

1. Data Steward reviews data model
2. Identifies sensitive columns
3. Applies classification framework
4. Documents rationale
5. Data Owner approves

### Periodic Review

- **Frequency**: Quarterly
- **Trigger**: New data, regulatory change, incident
- **Reviewer**: Data Steward
- **Approver**: Data Owner

### Classification Change

1. Change request submitted
2. Impact assessment
3. Control update plan
4. Approval obtained
5. Controls implemented
6. Documentation updated

---

## Implementation Checklist

### Immediate Actions

- [ ] Implement encryption for CONFIDENTIAL/RESTRICTED
- [ ] Configure access controls per classification
- [ ] Set up masking for non-production
- [ ] Enable audit logging

### Ongoing Actions

- [ ] Quarterly classification review
- [ ] Access review per classification
- [ ] Incident response for data exposure
- [ ] Training on classification handling

---

## Next Steps

1. Map compliance requirements - `*map-compliance`
2. Document lineage - `*document-lineage`
3. Proceed to Gate 2 validation

---

*Document generated by DataSteward Agent*
```

---

## Validation Checklist

Before completing, verify:

- [ ] All entities classified
- [ ] Sensitive columns identified
- [ ] Handling requirements defined
- [ ] Masking rules specified
- [ ] Access matrix created
- [ ] Review process defined
