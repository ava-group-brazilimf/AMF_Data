# DataSteward Checklist

**Agent:** DataSteward  
**Phase:** MIDSTREAM  
**Gate:** Gate 2

---

## Pre-Governance Checklist

### Prerequisites Verification

- [ ] Gate 1 passed (UPSTREAM complete)
- [ ] Data model available from DataArchitect
- [ ] Architecture document available
- [ ] Initial DQ requirements from BusinessAnalyst

### Context Understanding

- [ ] Data domains understood
- [ ] Regulatory requirements identified
- [ ] Stakeholders mapped
- [ ] Existing governance practices reviewed

---

## Data Quality Rules Checklist

### Rule Coverage

- [ ] Bronze layer rules defined
- [ ] Silver layer rules defined
- [ ] Gold layer rules defined
- [ ] Cross-layer validation rules defined

### Rule Categories

- [ ] Completeness rules (NOT NULL checks)
- [ ] Validity rules (format, range, type)
- [ ] Uniqueness rules (duplicate detection)
- [ ] Referential integrity rules (FK validation)
- [ ] Consistency rules (cross-field validation)
- [ ] Timeliness rules (freshness)
- [ ] Business rules (domain-specific)

### Severity and Actions

- [ ] CRITICAL rules identified (pipeline blockers)
- [ ] HIGH rules identified (quarantine triggers)
- [ ] MEDIUM rules identified (flag and process)
- [ ] LOW rules identified (logging only)

### Quarantine Strategy

- [ ] Quarantine table structure defined
- [ ] Quarantine workflow documented
- [ ] Retention policy specified
- [ ] Reprocessing procedure defined

### Thresholds and Alerts

- [ ] Failure thresholds set per severity
- [ ] Alert channels configured
- [ ] Escalation path defined
- [ ] SLAs specified

---

## Governance Framework Checklist

### Roles and Responsibilities

- [ ] Data Owner role defined
- [ ] Data Steward role defined
- [ ] Data Custodian role defined
- [ ] RACI matrix complete

### Policies

- [ ] Data Access Policy documented
- [ ] Data Quality Policy documented
- [ ] Data Retention Policy documented
- [ ] Data Privacy Policy documented
- [ ] Data Security Policy documented

### Standards

- [ ] Naming conventions defined
- [ ] Data type standards specified
- [ ] Metadata requirements documented

### Procedures

- [ ] Change management procedure defined
- [ ] Issue resolution procedure defined
- [ ] Exception handling procedure defined
- [ ] Escalation procedure defined

### Governance Metrics

- [ ] Quality metrics identified
- [ ] Compliance metrics identified
- [ ] Targets set for each metric

### Governance Council

- [ ] Council composition defined
- [ ] Responsibilities specified
- [ ] Meeting cadence established

---

## Data Classification Checklist

### Classification Framework

- [ ] Sensitivity levels defined (Public → Restricted)
- [ ] Data categories identified (PII, PHI, PCI, etc.)
- [ ] Handling requirements per level specified

### Entity Classification

- [ ] All Bronze entities classified
- [ ] All Silver entities classified
- [ ] All Gold entities classified
- [ ] Classification rationale documented

### Column-Level Classification

- [ ] High sensitivity columns identified
- [ ] Confidential columns identified
- [ ] Masking rules defined per column

### Access Controls

- [ ] Access matrix by classification created
- [ ] Role-based access defined
- [ ] Review process established

---

## Optional Deliverables Checklist

### Compliance Mapping (if applicable)

- [ ] Applicable regulations identified
- [ ] Requirements mapped to data
- [ ] Control mapping documented
- [ ] Gap analysis completed

### Lineage Documentation (if applicable)

- [ ] Source-to-target lineage documented
- [ ] Transformation logic captured
- [ ] Impact analysis capability defined

---

## Gate 2 Readiness Checklist

### Required Artifacts

- [ ] `dq-rules.md` complete
- [ ] `governance.md` complete
- [ ] `classification.md` complete

### Quality Criteria

- [ ] DQ rules cover all critical data elements
- [ ] Governance framework is implementable
- [ ] Classification aligns with compliance needs
- [ ] Documentation is actionable

### Documentation Quality

- [ ] All sections completed (no placeholders)
- [ ] Tables properly formatted
- [ ] Version information present
- [ ] Author attributed

---

## Handoff Checklist

### For DataFlow Agent

- [ ] DQ rules ready for ETL implementation
- [ ] Quarantine table DDL available
- [ ] Error handling patterns specified

### For InsightForge Agent

- [ ] Classification for semantic model known
- [ ] RLS requirements documented

### For Orchestrator

- [ ] All Gate 2 governance artifacts complete
- [ ] Validation passed

---

## Sign-off

| Checkpoint | Status | Date | Notes |
|------------|--------|------|-------|
| DQ Rules Complete | ⬜ | | |
| Governance Complete | ⬜ | | |
| Classification Complete | ⬜ | | |
| Gate 2 Ready | ⬜ | | |

---

*Checklist maintained by DataSteward Agent*
