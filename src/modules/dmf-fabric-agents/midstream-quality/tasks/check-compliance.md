# 🔒 Task: Check Compliance

## AI-Agent Migration Factory™ — Security & Compliance Agent

---

## Task ID
`check-compliance`

## Command
`*check-compliance`

## Purpose
Validate the migration pipeline against selected compliance frameworks (LGPD, GDPR, SOX, HIPAA). Checks data retention policies, consent management, audit trail enablement, encryption at rest and in transit, and access control configurations.

Semantic contract used by this task (must match template):
- Decision Result: `APPROVED`, `BLOCKED`, `REVIEW_REQUIRED`
- Process Status: `READY`, `IN_PROGRESS`, `FAILED`
- Boolean flags: `Yes/No` in Markdown views, `true/false` in JSON

---

## Trigger
- Manual: `*check-compliance --frameworks=LGPD,GDPR --pipeline=<id>`
- Automatic: After `*apply-masking` completes successfully

---

## Inputs

| Input                         | Source                | Format | Required |
| ----------------------------- | --------------------- | ------ | -------- |
| `pii-findings.json`          | scan-pii task         | JSON   | Yes      |
| `masking-report.json`        | apply-masking task    | JSON   | Optional |
| `table-schemas.json`          | Discovery Scout 🔍    | JSON   | Yes      |
| `compliance-requirements.yaml`| Migration Coordinator 🎯 | YAML | Optional |
| `access-grants.json`          | Unity Catalog export  | JSON   | Optional |

---

## Parameters

| Parameter       | Default     | Description                                    |
| --------------- | ----------- | ---------------------------------------------- |
| `--frameworks`  | LGPD,GDPR   | Comma-separated frameworks to validate against |
| `--pipeline`    | —           | Pipeline ID for scoped validation              |
| `--scope`       | all         | `all`, `pii-only`, `access-only`, `encryption-only` |
| `--full-report` | false       | Generate detailed report with all checks       |

---

## Procedure

### Step 1: Initialize Compliance Check
```
1.1 Load selected frameworks and their rules
1.2 Load pipeline artifacts (PII findings, masking reports, schemas)
1.3 Initialize checklist with all applicable checks
1.4 Log: "Starting compliance validation for {pipeline_id} against {frameworks}"
```

### Step 2: LGPD Compliance Checks
```
LGPD-01: Legal Basis Documentation
  - Verify legal basis is documented for each data processing activity
  - Check: compliance-requirements.yaml contains legal_basis field
  - Reference: Art. 7

LGPD-02: Sensitive Data Protection
  - Verify sensitive data (CPF, health, biometric) has enhanced protection
  - Check: All BR_CPF fields are masked or tokenized
  - Reference: Art. 11

LGPD-03: Data Subject Rights
  - Verify capability to export/delete individual data subject records
  - Check: DELETE and EXPORT procedures exist for PII tables
  - Reference: Art. 9

LGPD-04: Data Retention Policy
  - Verify retention periods are defined and enforced
  - Check: Table properties include retention_days metadata
  - Reference: Art. 16

LGPD-05: Consent Management
  - Verify consent records exist for personal data processing
  - Check: Consent tracking table/column exists in schema
  - Reference: Art. 8
```

### Step 3: GDPR Compliance Checks
```
GDPR-01: Data Minimization
  - Verify only necessary data is collected and migrated
  - Check: No unused PII columns in target schema
  - Reference: Art. 5(1)(c)

GDPR-02: Purpose Limitation
  - Verify data processing purpose is documented
  - Check: Processing purpose metadata exists
  - Reference: Art. 5(1)(b)

GDPR-03: Storage Limitation
  - Verify data retention periods are defined
  - Check: TTL or retention policies on Delta tables
  - Reference: Art. 5(1)(e)

GDPR-04: Integrity & Confidentiality
  - Verify encryption at rest and in transit
  - Check: Workspace encryption enabled, TLS enforced
  - Reference: Art. 5(1)(f)

GDPR-05: Right to Erasure
  - Verify capability for data deletion (Delta DELETE support)
  - Check: DELETE operations tested on PII tables
  - Reference: Art. 17

GDPR-06: Data Protection by Design
  - Verify masking applied before data lands in target
  - Check: Masking functions applied at ingestion, not post-hoc
  - Reference: Art. 25
```

### Step 4: SOX Compliance Checks
```
SOX-01: Internal Controls
  - Verify access controls on financial data tables
  - Check: Row-level and column-level security on financial tables
  - Reference: Section 404

SOX-02: Audit Trail
  - Verify complete audit trail for all data modifications
  - Check: Change Data Capture (CDC) enabled, audit log present
  - Reference: Section 302

SOX-03: Data Integrity
  - Verify checksums and row counts match between source and target
  - Check: Reconciliation report available
  - Reference: Section 404

SOX-04: Segregation of Duties
  - Verify no single user has full read/write/admin access
  - Check: Role assignments show proper separation
  - Reference: Section 302

SOX-05: Retention Compliance
  - Verify financial records retained for 7+ years
  - Check: Retention policy >= 2555 days on financial tables
  - Reference: Section 802
```

### Step 5: HIPAA Compliance Checks (if enabled)
```
HIPAA-01: Access Control
  - Verify access controls are enforced for PHI datasets
  - Check: Role and policy controls in place for PHI resources
  - Reference: 45 CFR 164.312(a)(1)

HIPAA-02: Audit Controls
  - Verify all PHI access and changes are logged
  - Check: Audit trail enabled and queryable for PHI tables
  - Reference: 45 CFR 164.312(b)

HIPAA-03: Integrity
  - Verify controls to protect PHI from improper alteration or destruction
  - Check: Integrity controls and reconciliation evidence present
  - Reference: 45 CFR 164.312(c)(1)

HIPAA-04: Transmission Security
  - Verify PHI is protected in transit
  - Check: TLS 1.2+ enforced for all PHI data paths
  - Reference: 45 CFR 164.312(e)(1)

HIPAA-05: Minimum Necessary
  - Verify only minimum necessary PHI is exposed and processed
  - Check: Column-level restrictions and least-privilege access on PHI
  - Reference: 45 CFR 164.502(b)
```

### Step 6: Cross-Framework Checks
```
CROSS-01: Encryption at Rest
  - Verify: Azure Storage Service Encryption enabled
  - Verify: Databricks workspace encryption enabled
  - Verify: Key management (Azure Key Vault) configured

CROSS-02: Encryption in Transit
  - Verify: TLS 1.2+ enforced on all connections
  - Verify: JDBC/ODBC connections use encrypted channels

CROSS-03: Access Control Validation
  - Verify: Unity Catalog enabled and configured
  - Verify: No public access to data tables
  - Verify: Service principals use least privilege

CROSS-04: Audit Trail Completeness
  - Verify: All compliance activities have audit entries
  - Verify: Audit log is immutable (append-only)
  - Verify: Retention meets strictest framework requirement
```

### Step 7: Generate Compliance Report
```
7.1 Aggregate all check results:
  - APPROVED: Check satisfied with evidence
  - BLOCKED: Check not satisfied, requires remediation
  - REVIEW_REQUIRED: Check partially satisfied or requires human validation
  - Applicable flag recorded as true/false per framework
7.2 Calculate compliance score:
  - compliance_score_weighted_percent = (approved_checks / total_applicable_checks) * 100
  - gatescore_total = compliance_score_weighted_percent / 100
7.3 Determine decision result (`gate2_decision_result`):
  - gatescore_total >= 0.85 and no CRITICAL check BLOCKED -> APPROVED
  - gatescore_total >= 0.70 and no unresolved CRITICAL blocker -> REVIEW_REQUIRED
  - gatescore_total < 0.70 or any CRITICAL check BLOCKED -> BLOCKED
7.4 Render Markdown report from template:
  - Use templates/compliance-report-tmpl.md placeholders and canonical semantic dictionary
  - Write to compliance-reports/{pipeline_id}.md
7.5 Export machine-readable JSON using canonical schema
  - Write to compliance-reports/{pipeline_id}.json
7.6 Log audit entry: COMPLIANCE_CHECK_COMPLETED
```

---

## Output

### Primary: `compliance-reports/{pipeline_id}.md`

Generated from template: `templates/compliance-report-tmpl.md`

### Secondary (Machine-Readable): `compliance-reports/{pipeline_id}.json`

Canonical contract: this task MUST emit the same top-level JSON structure used by the compliance template (`metadata`, `decision`, `kpis`, `gatescore`, `execution_trace`, `pii`, `compliance`, `reconciliation`, `risk`, `access_control`, `governance`, `audit`).

```json
{
  "metadata": {
    "report_id": "COMP-2025-001",
    "version": "3.0-enterprise",
    "pipeline_id": "MM_MDG_001",
    "pipeline_run_id": "run-2025-01-15-001",
    "environment": "prod",
    "regions": ["brazilsouth"],
    "frameworks": ["LGPD", "GDPR", "SOX"],
    "generated_at": "2025-01-15T12:00:00Z",
    "expires_at": "2025-01-22T12:00:00Z",
    "agent": "shield",
    "agent_version": "3.0.0"
  },
  "decision": {
    "gate2_decision_result": "APPROVED",
    "decision_timestamp": "2025-01-15T12:00:00Z",
    "primary_blocker_reason": "",
    "gatescore_total": 0.975,
    "threshold": 0.85,
    "recommended_action": "proceed_to_balance",
    "escalation_required": false,
    "escalation_contact": "",
    "next_agent_id": "balance"
  },
  "kpis": {
    "pii_coverage_percent": 100.0,
    "compliance_score_weighted_percent": 97.5
  },
  "gatescore": {
    "completude": {
      "score": 1.0,
      "weight": 0.35,
      "weighted": 0.35,
      "result": "APPROVED"
    },
    "qualidade": {
      "score": 0.95,
      "weight": 0.25,
      "weighted": 0.2375,
      "result": "APPROVED"
    },
    "risco_residual": {
      "score": 0.95,
      "weight": 0.2,
      "weighted": 0.19,
      "result": "APPROVED"
    },
    "reconciliacao": {
      "score": 0.9875,
      "weight": 0.2,
      "weighted": 0.1975,
      "result": "APPROVED"
    }
  },
  "execution_trace": [
    {
      "step": "pii_scan",
      "execution_id": "PII-2025-0001",
      "owner": "shield",
      "timestamp": "2025-01-15T11:45:00Z",
      "process_status": "READY",
      "evidence_link": "https://storage/reports/pii-scan.json"
    }
  ],
  "pii": {
    "scan_stats": {
      "tables_scanned": 24,
      "columns_scanned": 486
    },
    "detection": {
      "total_detected": 132,
      "total_masked": 132,
      "total_unmasked": 0,
      "coverage_percent": 100,
      "masking_coverage_result": "APPROVED"
    }
  },
  "compliance": {
    "score_weighted_percent": 97.5,
    "by_framework": [
      {
        "framework": "LGPD",
        "applicable": true,
        "checks": 5,
        "passed": 5,
        "failed": 0,
        "coverage_percent": 100,
        "result": "APPROVED"
      }
    ]
  },
  "reconciliation": {
    "row_count": {
      "expected": 1023456,
      "actual": 1023456,
      "match": true,
      "result": "APPROVED"
    },
    "checksum": {
      "expected": "ab12...",
      "actual": "ab12...",
      "match": true,
      "result": "APPROVED"
    },
    "schema": {
      "expected_columns": 148,
      "actual_columns": 148,
      "match": true,
      "result": "APPROVED"
    },
    "dtype": {
      "match": true,
      "result": "APPROVED"
    },
    "pii_masking_verify": {
      "match": true,
      "result": "APPROVED"
    },
    "score_percent": 100
  },
  "risk": {
    "critical_count": 0,
    "medium_count": 1,
    "low_count": 2,
    "residual_score": 0.95
  },
  "access_control": {
    "principals_validated": 18,
    "grants_checked": 124,
    "over_privileged_count": 0,
    "pii_protected_columns": 132,
    "pii_total_columns": 132,
    "encryption_at_rest_result": "APPROVED",
    "encryption_in_transit_result": "APPROVED"
  },
  "governance": {
    "approval_chain_result": "APPROVED",
    "approvals": [
      {
        "role": "data_steward",
        "owner": "steward@company.com",
        "timestamp": "2025-01-15T12:02:00Z",
        "decision_result": "APPROVED"
      }
    ]
  },
  "audit": {
    "audit_entry_id": "AUD-2025-0001-ABCD",
    "pii_scan_id": "PII-2025-0001",
    "masking_id": "MASK-2025-0001",
    "reconciliation_id": "RECON-2025-0001",
    "report_content_hash": "sha256:...",
    "generated_at": "2025-01-15T12:00:00Z",
    "expires_at": "2025-01-22T12:00:00Z",
    "event": "COMPLIANCE_CHECK_COMPLETED"
  }
}
```

---

## Compliance Score Thresholds

| GateScore (`gatescore_total`) | Verdict         | Action                                          |
| ----------------------------- | --------------- | ----------------------------------------------- |
| >= 0.85                       | APPROVED        | Forward to Balance ⚖️ for reconciliation         |
| 0.70 - 0.84                   | REVIEW_REQUIRED | Flag for human review, list remediation items    |
| < 0.70                        | BLOCKED         | Block pipeline, notify Phoenix 🔧 for remediation |

Critical override: any `CRITICAL` check with `decision_result=BLOCKED` forces final verdict `BLOCKED`.

---

## Acceptance Criteria

- [ ] All selected framework checks are executed
- [ ] Each detailed check includes decision_result, evidence, confidence, and regulatory reference
- [ ] Compliance score is calculated correctly
- [ ] Verdict follows the score threshold matrix
- [ ] Blocked or review-required checks include specific remediation guidance
- [ ] Audit log entry generated for compliance check completion
- [ ] BLOCKED decision result blocks pipeline progression
