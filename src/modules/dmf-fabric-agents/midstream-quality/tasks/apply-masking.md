# 🔒 Task: Apply Masking

## AI-Agent Migration Factory™ — Security & Compliance Agent

---

## Task ID
`apply-masking`

## Command
`*apply-masking`

## Purpose
Apply appropriate data masking strategies to detected PII fields. Generate masked column definitions compatible with Delta Lake column masking and dynamic views in Databricks Unity Catalog.

---

## Trigger
- Manual: `*apply-masking --input=pii-findings.json --strategy=<strategy>`
- Automatic: When `*scan-pii` returns verdict `REQUIRES_MASKING`

---

## Inputs

| Input                  | Source              | Format | Required |
| ---------------------- | ------------------- | ------ | -------- |
| `pii-findings.json`   | scan-pii task       | JSON   | Yes      |
| `masking-config.yaml`  | Manual / policy     | YAML   | Optional |
| `table-schemas.json`   | Discovery Scout 🔍  | JSON   | Yes      |

---

## Parameters

| Parameter       | Default    | Description                                          |
| --------------- | ---------- | ---------------------------------------------------- |
| `--input`       | —          | Path to PII findings file                            |
| `--strategy`    | sha256     | Masking strategy: `sha256`, `partial-mask`, `tokenization`, `redaction` |
| `--preview`     | false      | Preview masking without applying                     |
| `--vault`       | —          | Key vault for tokenization (azure-keyvault)          |
| `--scope`       | all        | Apply to `all` findings or specific `table.column`   |

---

## Procedure

### Step 1: Load PII Findings
```
1.1 Read pii-findings.json
1.2 Validate findings structure
1.3 Filter by scope if --scope specified
1.4 Group findings by masking strategy recommendation
1.5 Log: "Processing {N} PII fields for masking"
```

### Step 2: Determine Masking Strategy per Field
```
2.1 Apply strategy selection matrix:
    - EMAIL → partial-mask (j***@example.com)
    - BR_CPF → partial-mask (***456-00) or sha256
    - BR_CNPJ → partial-mask (**345.678/****-00) or sha256
    - PHONE_NUMBER → partial-mask (+55 ** ****-0000)
    - CREDIT_CARD → partial-mask (****-****-****-1111)
    - PASSPORT → redaction
    - ADDRESS → redaction or sha256
    - IBAN → partial-mask
2.2 Override with --strategy if explicitly specified
2.3 If --preview, show proposed masking without executing
```

### Step 3: Generate Delta Lake Column Masking Functions
```
3.1 For each PII field, generate SQL masking function:

    CREATE OR REPLACE FUNCTION mask_email(value STRING)
    RETURNS STRING
    RETURN CASE
      WHEN is_member('compliance_admin') THEN value
      ELSE CONCAT(LEFT(value, 1), '***@', SPLIT(value, '@')[1])
    END;

3.2 Generate ALTER TABLE statements:
    ALTER TABLE catalog.schema.table
    ALTER COLUMN email_addr
    SET MASK mask_email;

3.3 For SHA-256:
    CREATE OR REPLACE FUNCTION hash_pii(value STRING)
    RETURNS STRING
    RETURN SHA2(CONCAT(value, '<salt>'), 256);
```

### Step 4: Generate Dynamic Views (Alternative)
```
4.1 For row-level filtering + column masking:

    CREATE OR REPLACE VIEW catalog.schema.table_masked AS
    SELECT
      id,
      mask_email(email_addr) AS email_addr,
      mask_cpf(nr_cpf) AS nr_cpf,
      -- non-PII columns pass through
      material_number,
      description
    FROM catalog.schema.table_raw
    WHERE region IN (SELECT allowed_region FROM user_permissions);
```

### Step 5: Validate Masking
```
5.1 Verify masked output:
    - SHA-256 produces consistent 64-char hex string
    - Partial mask preserves expected visible characters
    - Tokenization generates valid token and vault entry
    - Redaction replaces with [REDACTED]
5.2 Run reverse-detection scan on masked values
    - Confirm Presidio no longer detects PII in masked output
5.3 Verify masking function grants:
    - Only compliance_admin can see unmasked values
```

### Step 6: Generate Masking Report
```
6.1 For each masked field:
    - table_name, column_name
    - original_pii_type
    - masking_strategy applied
    - sql_function_name
    - before_sample → after_sample
    - verification_status (PASS | FAIL)
6.2 Write to masking-reports/{pipeline_id}.json
6.3 Log audit entry: MASKING_APPLIED
```

---

## Output

### Primary: `masking-reports/{pipeline_id}.json`

```json
{
  "masking_id": "MASK-2025-001",
  "timestamp": "2025-01-15T11:00:00Z",
  "pipeline_id": "MM_MDG_001",
  "strategy_applied": "mixed",
  "fields_masked": 8,
  "masking_actions": [
    {
      "table": "MARA_PARTNERS",
      "column": "EMAIL_ADDR",
      "pii_type": "EMAIL",
      "strategy": "partial-mask",
      "function_name": "mask_email",
      "sample_before": "john.doe@company.com",
      "sample_after": "j***@company.com",
      "sql_ddl": "ALTER TABLE migration.staging.mara_partners ALTER COLUMN email_addr SET MASK mask_email;",
      "verification": "PASS",
      "reverse_scan": "NO_PII_DETECTED"
    }
  ],
  "sql_scripts": [
    "masking-reports/sql/create-masking-functions.sql",
    "masking-reports/sql/alter-table-masks.sql",
    "masking-reports/sql/create-masked-views.sql"
  ],
  "verdict": "MASKING_COMPLETE"
}
```

---

## Masking Strategy Matrix

| PII Type       | Default Strategy | Reversible | Visible Chars    |
| -------------- | ---------------- | ---------- | ---------------- |
| EMAIL          | partial-mask     | No         | First char + domain |
| BR_CPF         | partial-mask     | No         | Last 5 digits    |
| BR_CNPJ        | partial-mask     | No         | Middle segment   |
| PHONE_NUMBER   | partial-mask     | No         | Last 4 digits    |
| CREDIT_CARD    | partial-mask     | No         | Last 4 digits    |
| PASSPORT       | redaction        | No         | None             |
| ADDRESS        | sha256           | No         | None             |
| IBAN           | partial-mask     | No         | Last 4 chars     |

---

## Acceptance Criteria

- [ ] All PII fields from findings receive appropriate masking
- [ ] SQL masking functions are valid and executable in Databricks
- [ ] Reverse PII scan confirms no PII detectable in masked output
- [ ] Masking report includes before/after samples
- [ ] Audit log entry generated for each masking action
- [ ] Human approval obtained before applying to production tables
- [ ] Compliance admin bypass verified (can see unmasked values)
