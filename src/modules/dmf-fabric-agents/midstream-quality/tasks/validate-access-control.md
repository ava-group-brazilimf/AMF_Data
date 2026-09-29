# 🔒 Task: Validate Access Control

## AI-Agent Migration Factory™ — Security & Compliance Agent

---

## Task ID
`validate-access-control`

## Command
`*validate-access`

## Purpose
Validate Unity Catalog permissions to ensure least privilege enforcement. Check table-level and column-level grants, verify role assignments, identify over-privileged access, and confirm row-level security configurations.

---

## Trigger
- Manual: `*validate-access --catalog=<name> --schema=<name>`
- Automatic: As part of `*check-compliance --scope=access-only`

---

## Inputs

| Input                    | Source               | Format | Required |
| ------------------------ | -------------------- | ------ | -------- |
| `table-schemas.json`     | Discovery Scout 🔍   | JSON   | Yes      |
| `pii-findings.json`     | scan-pii task        | JSON   | Optional |
| `access-grants.json`     | Unity Catalog export | JSON   | Optional |
| `role-definitions.yaml`  | Manual / policy      | YAML   | Optional |

---

## Parameters

| Parameter              | Default               | Description                                  |
| ---------------------- | --------------------- | -------------------------------------------- |
| `--catalog`            | —                     | Unity Catalog name to validate               |
| `--schema`             | —                     | Schema name to scope validation              |
| `--check-roles`        | false                 | Include role assignment validation            |
| `--report-overprivileged` | false              | Generate report of over-privileged principals |
| `--enforce`            | false                 | Generate REVOKE statements for violations    |

---

## Procedure

### Step 1: Discover Access Configuration
```
1.1 Connect to Unity Catalog metadata
1.2 List all catalogs, schemas, tables in scope
1.3 Extract current grants:
    SHOW GRANTS ON CATALOG <catalog>;
    SHOW GRANTS ON SCHEMA <catalog>.<schema>;
    SHOW GRANTS ON TABLE <catalog>.<schema>.<table>;
1.4 Extract column masking functions:
    DESCRIBE TABLE EXTENDED <catalog>.<schema>.<table>;
1.5 Log: "Validating access for {N} tables in {catalog}.{schema}"
```

### Step 2: Validate Least Privilege
```
2.1 For each principal (user, group, service principal):
    a. List all granted privileges
    b. Compare against expected role matrix:
       - data_reader: SELECT only
       - data_writer: SELECT, INSERT, UPDATE
       - data_admin: SELECT, INSERT, UPDATE, DELETE, ALTER
       - compliance_admin: ALL PRIVILEGES (limited scope)
    c. Flag grants exceeding expected role

2.2 Check for dangerous patterns:
    - ALL PRIVILEGES on catalog level → CRITICAL
    - MODIFY on PII tables without column masking → HIGH
    - SELECT on PII columns without masking function → HIGH
    - CREATE TABLE in production schema → MEDIUM
    - Any public/anonymous access → CRITICAL
```

### Step 3: Validate PII Column Protections
```
3.1 Cross-reference pii-findings.json with column grants:
    - Every PII column MUST have a masking function applied
    - Every PII table MUST have row-level security (if applicable)
3.2 Check masking function assignments:
    - Verify masking function exists and is active
    - Verify unmasked access limited to compliance_admin group
3.3 Flag unprotected PII columns as CRITICAL violations
```

### Step 4: Validate Role Assignments
```
4.1 Check group memberships:
    - No individual user grants (use groups only)
    - Groups follow naming convention: {project}_{role}_{scope}
    - Service principals use dedicated groups
4.2 Validate segregation of duties:
    - No user in both data_writer and compliance_admin
    - No single user with full CRUD + admin access
    - Separate principals for ETL execution and data access
4.3 Check service principal scoping:
    - ETL service principal: write access to staging only
    - BI service principal: read access to curated only
    - Admin service principal: limited to metadata operations
```

### Step 5: Validate Row-Level Security
```
5.1 For tables with row-level security requirements:
    - Verify RLS function exists
    - Verify RLS function references user attributes correctly
    - Test RLS with sample user contexts
5.2 Common RLS patterns:
    - Regional filtering: WHERE region IN (user.allowed_regions)
    - Department filtering: WHERE dept = user.department
    - Client filtering: WHERE client_id IN (user.client_ids)
```

### Step 6: Generate Remediation Scripts (if --enforce)
```
6.1 For each violation, generate corrective SQL:
    - REVOKE excessive privileges
    - GRANT appropriate reduced privileges
    - ALTER COLUMN to add masking function
    - CREATE FUNCTION for missing masking functions
6.2 Scripts require human approval before execution
6.3 Output to compliance-reports/access-remediation.sql
```

### Step 7: Generate Access Validation Report
```
7.1 Summarize findings:
    - Total principals validated
    - Total grants checked
    - Violations by severity
    - Over-privileged principals list
7.2 Write to compliance-reports/access-validation.json
7.3 Log audit entry: ACCESS_VALIDATED
```

---

## Output

### Primary: `compliance-reports/access-validation.json`

```json
{
  "validation_id": "ACC-2025-001",
  "timestamp": "2025-01-15T13:00:00Z",
  "pipeline_id": "MM_MDG_001",
  "scope": {
    "catalog": "migration_catalog",
    "schema": "staging",
    "tables": 45
  },
  "summary": {
    "principals_validated": 12,
    "grants_checked": 156,
    "violations": 3,
    "by_severity": {
      "CRITICAL": 1,
      "HIGH": 1,
      "MEDIUM": 1
    }
  },
  "violations": [
    {
      "id": "ACC-V-001",
      "severity": "CRITICAL",
      "principal": "etl_service_principal",
      "type": "OVER_PRIVILEGED",
      "description": "ALL PRIVILEGES granted at catalog level",
      "current_grant": "ALL PRIVILEGES ON CATALOG migration_catalog",
      "recommended_grant": "SELECT, INSERT ON SCHEMA migration_catalog.staging",
      "remediation_sql": "REVOKE ALL PRIVILEGES ON CATALOG migration_catalog FROM etl_service_principal; GRANT SELECT, INSERT ON SCHEMA migration_catalog.staging TO etl_service_principal;"
    }
  ],
  "pii_protection_status": {
    "pii_columns_total": 8,
    "pii_columns_masked": 8,
    "pii_columns_unprotected": 0
  },
  "verdict": "REVIEW_REQUIRED"
}
```

---

## Severity Classification

| Severity   | Criteria                                                  |
| ---------- | --------------------------------------------------------- |
| CRITICAL   | ALL PRIVILEGES at catalog/schema level, unmasked PII access, public access |
| HIGH       | Write access to PII tables without masking, excessive scope |
| MEDIUM     | Individual user grants (should use groups), unnecessary CREATE |
| LOW        | Minor naming convention violations, informational          |

---

## Acceptance Criteria

- [ ] All principals in scope are validated against expected role matrix
- [ ] PII columns are cross-referenced with masking function assignments
- [ ] Over-privileged access is flagged with specific remediation SQL
- [ ] Segregation of duties is validated
- [ ] Row-level security is verified where applicable
- [ ] Remediation scripts are generated but NOT auto-executed
- [ ] Audit log entry generated for access validation
- [ ] Report includes clear verdict: PASS, REVIEW_REQUIRED, or FAIL
