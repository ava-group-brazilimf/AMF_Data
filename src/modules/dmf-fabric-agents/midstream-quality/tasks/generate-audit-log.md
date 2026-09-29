# 🔒 Task: Generate Audit Log

## AI-Agent Migration Factory™ — Security & Compliance Agent

---

## Task ID
`generate-audit-log`

## Command
`*audit-log`

## Purpose
Generate structured audit log entries for all compliance activities performed by the Security & Compliance Agent. Entries are formatted for Elasticsearch ingestion and maintained as an immutable, append-only trail.

---

## Trigger
- Manual: `*audit-log --pipeline=<id>`
- Automatic: After every compliance action (scan, mask, check, validate)

---

## Inputs

| Input                        | Source              | Format | Required |
| ---------------------------- | ------------------- | ------ | -------- |
| `pii-findings.json`         | scan-pii task       | JSON   | Optional |
| `masking-report.json`       | apply-masking task  | JSON   | Optional |
| `compliance-report.json`    | check-compliance    | JSON   | Optional |
| `access-validation.json`    | validate-access     | JSON   | Optional |

---

## Parameters

| Parameter     | Default        | Description                                      |
| ------------- | -------------- | ------------------------------------------------ |
| `--pipeline`  | —              | Pipeline ID to scope audit entries                |
| `--format`    | jsonl          | Output format: `jsonl`, `elasticsearch`, `csv`    |
| `--since`     | —              | Filter events since ISO datetime                  |
| `--events`    | ALL            | Comma-separated event types to include            |
| `--output`    | audit-trail.log| Output file path                                  |

---

## Procedure

### Step 1: Collect Compliance Events
```
1.1 Scan projects/{project_name}/outputs/midstream/compliance/ for completed task artifacts
1.2 Extract events from each artifact:
    - pii-findings.json → PII_SCAN_COMPLETED events
    - masking-report.json → MASKING_APPLIED events
    - compliance-report.json → COMPLIANCE_CHECK events
    - access-validation.json → ACCESS_VALIDATED events
1.3 Filter by --pipeline and --since if specified
1.4 Sort events chronologically
```

### Step 2: Structure Audit Entries
```
2.1 For each event, create structured entry:
    - event_id: Unique identifier (AUD-YYYY-NNN-XXXX)
    - timestamp: ISO 8601 with timezone
    - event_type: Standard event classification
    - pipeline_id: Migration pipeline reference
    - agent: "security-compliance"
    - actor: Agent persona or human approver
    - action: Specific action performed
    - target: Object/table/column affected
    - result: Outcome (SUCCESS, FAILURE, BLOCKED)
    - evidence: Supporting data or reference
    - severity: INFO, WARNING, CRITICAL
    - metadata: Additional context
```

### Step 3: Event Type Definitions
```
PII_SCAN_STARTED       - PII scan initiated
PII_SCAN_COMPLETED     - PII scan finished with results
PII_DETECTED           - Individual PII field detection
MASKING_REQUESTED      - Masking action requested (awaiting approval)
MASKING_APPROVED       - Human approved masking action
MASKING_APPLIED        - Masking strategy applied to field
MASKING_VERIFIED       - Masked output verified (reverse scan passed)
COMPLIANCE_CHECK_STARTED   - Compliance validation initiated
COMPLIANCE_CHECK_COMPLETED - Compliance check finished with verdict
COMPLIANCE_VIOLATION       - Individual compliance violation detected
ACCESS_VALIDATION_STARTED  - Access control validation initiated
ACCESS_VALIDATED           - Access control check completed
ACCESS_VIOLATION           - Over-privileged access detected
POLICY_VIOLATION           - Security policy violation detected
PIPELINE_BLOCKED           - Pipeline blocked due to non-compliance
PIPELINE_CLEARED           - Pipeline cleared for next phase
```

### Step 4: Format for Target System
```
4.1 JSONL format (default):
    One JSON object per line, newline-delimited

4.2 Elasticsearch format:
    Include _index, _type metadata for bulk API
    Add @timestamp field for Kibana compatibility

4.3 CSV format:
    Header row + comma-separated values
    Suitable for spreadsheet analysis
```

### Step 5: Write and Validate
```
5.1 Append entries to audit-logs/audit-trail.log
5.2 Verify file integrity (no truncation, valid JSON per line)
5.3 Calculate summary statistics
5.4 Log meta-entry: AUDIT_LOG_GENERATED
```

---

## Output

### Primary: `audit-logs/audit-trail.log` (JSONL)

```jsonl
{"event_id":"AUD-2025-001-0001","timestamp":"2025-01-15T10:00:00Z","event_type":"PII_SCAN_STARTED","pipeline_id":"MM_MDG_001","agent":"security-compliance","actor":"Shield","action":"Initiated PII scan on table-schemas.json","target":"table-schemas.json","result":"SUCCESS","evidence":"45 tables, 312 columns queued for scanning","severity":"INFO"}
{"event_id":"AUD-2025-001-0002","timestamp":"2025-01-15T10:15:00Z","event_type":"PII_DETECTED","pipeline_id":"MM_MDG_001","agent":"security-compliance","actor":"Shield","action":"Detected EMAIL in MARA_PARTNERS.EMAIL_ADDR","target":"MARA_PARTNERS.EMAIL_ADDR","result":"SUCCESS","evidence":"confidence=0.97, method=presidio, samples=94/100","severity":"CRITICAL"}
{"event_id":"AUD-2025-001-0003","timestamp":"2025-01-15T10:30:00Z","event_type":"PII_SCAN_COMPLETED","pipeline_id":"MM_MDG_001","agent":"security-compliance","actor":"Shield","action":"PII scan completed: 8 fields detected across 45 tables","target":"pipeline:MM_MDG_001","result":"SUCCESS","evidence":"scan_id=PII-SCAN-2025-001, verdict=REQUIRES_MASKING","severity":"WARNING"}
{"event_id":"AUD-2025-001-0004","timestamp":"2025-01-15T11:00:00Z","event_type":"MASKING_APPROVED","pipeline_id":"MM_MDG_001","agent":"security-compliance","actor":"human:joao.costa","action":"Approved masking strategy for 8 PII fields","target":"pipeline:MM_MDG_001","result":"SUCCESS","evidence":"approval_ticket=APR-2025-042","severity":"INFO"}
{"event_id":"AUD-2025-001-0005","timestamp":"2025-01-15T11:05:00Z","event_type":"MASKING_APPLIED","pipeline_id":"MM_MDG_001","agent":"security-compliance","actor":"Shield","action":"Applied partial-mask to MARA_PARTNERS.EMAIL_ADDR","target":"MARA_PARTNERS.EMAIL_ADDR","result":"SUCCESS","evidence":"strategy=partial-mask, function=mask_email, verification=PASS","severity":"INFO"}
```

### Elasticsearch Bulk Format

```json
{"index":{"_index":"migration-audit-2025","_id":"AUD-2025-001-0001"}}
{"@timestamp":"2025-01-15T10:00:00Z","event_type":"PII_SCAN_STARTED","pipeline_id":"MM_MDG_001","agent":"security-compliance","actor":"Shield","action":"Initiated PII scan","severity":"INFO"}
```

---

## Retention Policy

| Framework | Minimum Retention | Applied Policy |
| --------- | ----------------- | -------------- |
| LGPD      | Not specified     | 5 years        |
| GDPR      | Duration of purpose| 5 years       |
| SOX       | 7 years           | 7 years        |
| HIPAA     | 6 years           | 7 years        |
| **Applied**| —                | **7 years (2555 days)** |

---

## Acceptance Criteria

- [ ] All compliance activities generate corresponding audit entries
- [ ] Entries are append-only (never modified or deleted)
- [ ] Each entry has a unique event_id
- [ ] Timestamps are ISO 8601 with timezone
- [ ] JSONL format validates (one valid JSON per line)
- [ ] Elasticsearch format includes required metadata fields
- [ ] Retention policy meets the strictest framework requirement (7 years)
- [ ] Human approvals are recorded with actor identification
