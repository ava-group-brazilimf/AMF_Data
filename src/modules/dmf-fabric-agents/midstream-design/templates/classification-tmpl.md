# Data Classification Template

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
| **PUBLIC** | Non-sensitive, can be shared externally | Product catalogs |
| **INTERNAL** | Business use, not for external sharing | Internal metrics |
| **CONFIDENTIAL** | Sensitive business, restricted access | Financial data |
| **RESTRICTED** | Highest sensitivity, regulatory protection | PII, PHI, PCI |

### Data Categories

| Category | Classification | Regulations |
|----------|----------------|-------------|
| PII | RESTRICTED | GDPR, LGPD |
| PHI | RESTRICTED | HIPAA |
| PCI | RESTRICTED | PCI-DSS |
| Financial | CONFIDENTIAL | SOX |
| Operational | INTERNAL | Internal policy |
| Public | PUBLIC | N/A |

---

## Handling Requirements

### By Classification Level

| Control | PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED |
|---------|--------|----------|--------------|------------|
| Access | Open | Authenticated | Role-based | Named individuals |
| Encryption Rest | Optional | Recommended | Required | Required |
| Encryption Transit | Recommended | Required | Required | Required |
| Masking | Not required | Not required | Non-prod | Required non-prod |
| Audit | Basic | Access logging | Full trail | Comprehensive |

---

## Entity Classification

### Bronze Layer

| Entity | Classification | Categories | Rationale |
|--------|----------------|------------|-----------|
| brz_{entity} | {level} | {categories} | {rationale} |

### Silver Layer

| Entity | Classification | Categories | Rationale |
|--------|----------------|------------|-----------|
| slv_{entity} | {level} | {categories} | {rationale} |

### Gold Layer

| Entity | Classification | Categories | Rationale |
|--------|----------------|------------|-----------|
| gld_{entity} | {level} | {categories} | {rationale} |

---

## Column-Level Classification

### High Sensitivity Columns

| Entity | Column | Category | Classification | Masking Rule |
|--------|--------|----------|----------------|--------------|
| {entity} | customer_name | PII | RESTRICTED | Partial redact |
| {entity} | email | PII | RESTRICTED | Hash |
| {entity} | phone | PII | RESTRICTED | Partial mask |

---

## Masking Rules

| Technique | Description | Example |
|-----------|-------------|---------|
| Redaction | Replace with fixed | John → XXXXX |
| Partial Mask | Show partial | 555-1234 → XXX-1234 |
| Hashing | One-way hash | sha256(value) |
| Tokenization | Reversible token | TOKEN_ABC |
| Generalization | Reduce precision | Age 35 → 30-40 |

---

## Access Matrix

| Role | PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED |
|------|--------|----------|--------------|------------|
| Employee | ✅ | ✅ | ❌ | ❌ |
| Analyst | ✅ | ✅ | ✅ (masked) | ❌ |
| Manager | ✅ | ✅ | ✅ | ❌ |
| Data Steward | ✅ | ✅ | ✅ | ✅ (audit) |

---

## Review Process

- **Frequency**: Quarterly
- **Reviewer**: Data Steward
- **Approver**: Data Owner
- **Trigger**: New data, regulatory change, incident

---

*Template provided by DataSteward Agent*
