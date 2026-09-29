# Data Governance Best Practices

**Reference:** DataSteward Agent  
**Version:** 1.0

---

## Data Quality Principles

### 1. Quality at the Source

- Enforce quality rules as early as possible
- Fix issues at source systems when feasible
- Document known source quality issues
- Establish SLAs with source system owners

### 2. Defense in Depth

Apply quality checks at multiple layers:

| Layer | Primary Checks |
|-------|----------------|
| Landing | Schema, completeness |
| Bronze | Type validation, deduplication |
| Silver | Business rules, referential integrity |
| Gold | Aggregation validation, reconciliation |

### 3. Fail Fast, Fail Safe

- Critical issues should stop the pipeline
- Non-critical issues should be captured, not dropped
- Always quarantine bad data for investigation
- Never silently discard records

### 4. Measurable Quality

Define and track quality metrics:
- Completeness: % of required fields populated
- Validity: % passing validation rules
- Uniqueness: % of records with unique keys
- Timeliness: data freshness vs SLA
- Consistency: % matching across sources

---

## Data Quality Rule Design

### Rule Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Completeness** | Check for missing data | NOT NULL, required fields |
| **Validity** | Verify format and values | Range, regex, lookup |
| **Uniqueness** | Prevent duplicates | PK uniqueness, business key |
| **Referential** | Validate relationships | FK exists, parent-child |
| **Consistency** | Cross-field validation | Date order, sum checks |
| **Timeliness** | Data freshness | Max age, SLA compliance |
| **Accuracy** | Correctness | Reconciliation, spot checks |

### Severity Assignment

| Severity | When to Use | Examples |
|----------|-------------|----------|
| **CRITICAL** | Breaks downstream, violates constraints | Missing PK, invalid FK |
| **HIGH** | Significant business impact | Missing required business data |
| **MEDIUM** | Moderate impact, can process | Suspicious values, minor format |
| **LOW** | Minimal impact, informational | Preferred format, best practice |

### Rule Writing Best Practices

1. **Be Specific**: Rule should be unambiguous
2. **Be Testable**: Rule should have clear pass/fail
3. **Be Documented**: Include business context
4. **Be Maintainable**: Avoid hardcoded values
5. **Be Efficient**: Consider performance impact

---

## Quarantine Management

### Quarantine Design

```sql
-- Recommended quarantine table structure
CREATE TABLE quarantine.{entity}_quarantine (
    quarantine_id BIGINT GENERATED ALWAYS AS IDENTITY,
    original_record STRING,      -- JSON of full record
    rule_id STRING,              -- Which rule failed
    rule_message STRING,         -- Failure message
    severity STRING,             -- CRITICAL/HIGH/MEDIUM/LOW
    quarantine_timestamp TIMESTAMP,
    source_batch_id STRING,      -- Source batch reference
    reviewed_by STRING,          -- Who reviewed
    reviewed_at TIMESTAMP,
    resolution STRING,           -- REPROCESS/IGNORE/FIXED/DUPLICATE
    resolution_notes STRING,
    reprocessed_at TIMESTAMP
);
```

### Quarantine Workflow

1. **Capture**: Write failed record with context
2. **Alert**: Notify based on severity and threshold
3. **Triage**: Classify issue type (source, transform, data)
4. **Investigate**: Determine root cause
5. **Resolve**: Fix source, manual fix, or ignore
6. **Reprocess**: Re-run through pipeline if fixed
7. **Archive**: Move to archive after retention

### Retention Guidelines

| Severity | Active Retention | Archive Retention |
|----------|------------------|-------------------|
| CRITICAL | 90 days | 1 year |
| HIGH | 60 days | 6 months |
| MEDIUM | 30 days | 3 months |
| LOW | 7 days | 1 month |

---

## Governance Framework Principles

### 1. Clear Ownership

Every data asset needs:
- **Data Owner**: Business accountability
- **Data Steward**: Operational responsibility
- **Data Custodian**: Technical management

### 2. Documented Policies

Essential policies:
- Data Access Policy
- Data Quality Policy
- Data Retention Policy
- Data Privacy Policy
- Data Security Policy

### 3. Enforced Standards

Standards should cover:
- Naming conventions
- Data types
- Metadata requirements
- Documentation standards

### 4. Defined Processes

Key processes:
- Change management
- Issue resolution
- Exception handling
- Escalation procedures

---

## Data Classification Best Practices

### Classification Framework

Standard levels:

| Level | Description | Key Indicator |
|-------|-------------|---------------|
| **PUBLIC** | No impact if disclosed | Published externally |
| **INTERNAL** | Minor business impact | Internal communications |
| **CONFIDENTIAL** | Significant business impact | Competitive advantage |
| **RESTRICTED** | Legal/regulatory impact | PII, PHI, PCI |

### Classification Process

1. **Inventory**: List all data assets
2. **Analyze**: Review content and usage
3. **Classify**: Apply classification level
4. **Document**: Record classification and rationale
5. **Implement**: Apply appropriate controls
6. **Review**: Periodic reassessment

### PII Identification Checklist

Common PII elements:
- [ ] Full name
- [ ] Email address
- [ ] Phone number
- [ ] Physical address
- [ ] Date of birth
- [ ] Social security / national ID
- [ ] Driver's license
- [ ] Passport number
- [ ] Financial account numbers
- [ ] Biometric data
- [ ] Medical information
- [ ] Geolocation data
- [ ] IP address (in context)

---

## Compliance Mapping

### Common Regulations

| Regulation | Scope | Key Requirements |
|------------|-------|------------------|
| **GDPR** | EU personal data | Consent, erasure, portability |
| **LGPD** | Brazil personal data | Similar to GDPR |
| **HIPAA** | US health data | Access controls, encryption, audit |
| **PCI-DSS** | Payment card data | Encryption, segmentation, testing |
| **SOX** | US public company financials | Controls, audit trail |
| **CCPA** | California consumer data | Disclosure, opt-out |

### Compliance Control Mapping

| Control Type | Example Requirements |
|--------------|---------------------|
| **Access Control** | Least privilege, authentication |
| **Encryption** | At rest, in transit |
| **Audit** | Access logging, change tracking |
| **Retention** | Defined periods, secure deletion |
| **Privacy** | Consent, anonymization |
| **Security** | Vulnerability management, incidents |

---

## Data Lineage Best Practices

### Lineage Levels

| Level | What to Capture |
|-------|-----------------|
| **System** | Source → Target systems |
| **Dataset** | Table → Table relationships |
| **Column** | Column → Column mappings |
| **Business** | Business entity relationships |

### Lineage Metadata

For each transformation:
- Source (system, table, column)
- Target (system, table, column)
- Transformation logic
- Business rule applied
- Owner/responsible party
- Last updated

### Lineage Use Cases

1. **Impact Analysis**: What breaks if X changes?
2. **Root Cause**: Where did bad data originate?
3. **Compliance**: Prove data handling to auditors
4. **Documentation**: Understand data flow
5. **Change Management**: Assess change impact

---

## Governance Metrics

### Quality Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| DQ Score | Weighted average of all rules | > 95% |
| Completeness | % required fields populated | > 99% |
| Validity | % passing validation | > 99% |
| Timeliness | % within SLA | > 99% |
| Issue Resolution | % resolved within SLA | > 95% |

### Governance Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Classification Coverage | % assets classified | 100% |
| Access Review | % reviews completed on time | 100% |
| Policy Compliance | % assets meeting policy | > 95% |
| Metadata Completeness | % with required metadata | > 90% |

---

## Anti-Patterns to Avoid

### Data Quality Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Silent Drop** | Bad data discarded without trace | Always quarantine |
| **One-Size-Fits-All** | Same severity for all issues | Context-based severity |
| **Over-Engineering** | Too many rules, too strict | Balance strictness with practicality |
| **No Thresholds** | Any failure stops everything | Define acceptable thresholds |

### Governance Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **No Owner** | Unclear accountability | Assign explicit owners |
| **Paper Policy** | Policy exists but not enforced | Implement technical controls |
| **Over-Governance** | Too much process, slow delivery | Right-size governance |
| **Under-Governance** | No controls, compliance risk | Minimum viable governance |

---

## References

- Data Management Body of Knowledge (DAMA-DMBOK)
- ISO 8000 Data Quality
- NIST Privacy Framework
- GDPR Official Text
- PCI-DSS Standards

---

*Reference maintained by DataSteward Agent*
