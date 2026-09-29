# 🔒 Security & Compliance — Best Practices

## AI-Agent Migration Factory™ — Reference Guide

---

## 1. PII Detection Patterns

### 1.1 Column Name Heuristics

Use column naming patterns to pre-screen for PII before running data-level scans:

| Pattern (regex)                        | PII Type       | Confidence |
| -------------------------------------- | -------------- | ---------- |
| `email\|e_mail\|email_addr\|correio`  | EMAIL          | 0.70       |
| `cpf\|nr_cpf\|num_cpf\|cd_cpf`       | BR_CPF         | 0.80       |
| `cnpj\|nr_cnpj\|num_cnpj\|cd_cnpj`   | BR_CNPJ        | 0.80       |
| `phone\|telefone\|celular\|fone`      | PHONE_NUMBER   | 0.70       |
| `credit_card\|cartao\|card_number`    | CREDIT_CARD    | 0.75       |
| `passport\|passaporte\|nr_passaporte` | PASSPORT       | 0.75       |
| `address\|endereco\|logradouro\|cep`  | ADDRESS        | 0.65       |
| `iban\|conta_bancaria\|nr_conta`      | IBAN           | 0.70       |
| `name\|nome\|nome_completo`           | PERSON_NAME    | 0.60       |

### 1.2 Presidio Custom Recognizers

```python
from presidio_analyzer import PatternRecognizer, Pattern

# Brazilian CPF Recognizer
cpf_pattern = Pattern(
    name="br_cpf_pattern",
    regex=r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
    score=0.85
)
cpf_recognizer = PatternRecognizer(
    supported_entity="BR_CPF",
    patterns=[cpf_pattern],
    supported_language="pt"
)

# Brazilian CNPJ Recognizer
cnpj_pattern = Pattern(
    name="br_cnpj_pattern",
    regex=r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
    score=0.85
)
cnpj_recognizer = PatternRecognizer(
    supported_entity="BR_CNPJ",
    patterns=[cnpj_pattern],
    supported_language="pt"
)
```

### 1.3 Data Sampling Strategy

- **Sample size**: 100 rows per column (configurable)
- **Sampling method**: Random selection for large tables, full scan for < 100 rows
- **Null handling**: Skip NULL values, report NULL percentage
- **Encoding**: Handle UTF-8 and Latin-1 (common in SAP exports)
- **Performance**: Use TABLESAMPLE for tables > 1M rows

```sql
-- Efficient sampling in Databricks
SELECT column_name
FROM catalog.schema.table
TABLESAMPLE (100 ROWS)
WHERE column_name IS NOT NULL;
```

---

## 2. Data Masking Strategies

### 2.1 SHA-256 Hash

**Use when:** Cross-system joins needed, original value not required.

```python
import hashlib

SALT = "migration-factory-2025-salt"  # Store in Key Vault

def hash_pii(value: str) -> str:
    return hashlib.sha256(f"{value}{SALT}".encode()).hexdigest()
```

**Databricks SQL:**
```sql
CREATE OR REPLACE FUNCTION catalog.schema.hash_pii(value STRING)
RETURNS STRING
RETURN SHA2(CONCAT(value, SECRET('scope', 'pii-salt')), 256);
```

### 2.2 Partial Mask

**Use when:** Display purposes, customer service, partial visibility needed.

| PII Type      | Input                    | Masked Output            |
| ------------- | ------------------------ | ------------------------ |
| EMAIL         | `john.doe@company.com`   | `j***@company.com`       |
| BR_CPF        | `123.456.789-00`         | `***.***.*89-00`         |
| PHONE         | `+55 11 99999-0000`      | `+55 ** ****-0000`       |
| CREDIT_CARD   | `4111-1111-1111-1111`    | `****-****-****-1111`    |

```sql
CREATE OR REPLACE FUNCTION catalog.schema.mask_email(value STRING)
RETURNS STRING
RETURN CASE
  WHEN is_member('compliance_admin') THEN value
  WHEN value IS NULL THEN NULL
  ELSE CONCAT(LEFT(value, 1), '***@', SPLIT_PART(value, '@', 2))
END;
```

### 2.3 Tokenization

**Use when:** Reversible masking needed, operational recovery scenarios.

```python
import uuid
import json

TOKEN_VAULT = {}  # Replace with Azure Key Vault in production

def tokenize(value: str, pii_type: str) -> str:
    token = f"TOK-{pii_type}-{uuid.uuid4().hex[:12]}"
    TOKEN_VAULT[token] = {"original": value, "type": pii_type}
    return token

def detokenize(token: str) -> str:
    entry = TOKEN_VAULT.get(token)
    return entry["original"] if entry else None
```

### 2.4 Redaction

**Use when:** Complete removal, logs, exports, non-essential fields.

```sql
CREATE OR REPLACE FUNCTION catalog.schema.redact(value STRING)
RETURNS STRING
RETURN CASE
  WHEN is_member('compliance_admin') THEN value
  ELSE '[REDACTED]'
END;
```

---

## 3. LGPD Compliance Checklist

### Legal Bases (Art. 7)
- [ ] Consent obtained and recorded
- [ ] Legitimate interest assessed (LIA documented)
- [ ] Contract performance justified
- [ ] Legal obligation identified
- [ ] Public policy basis documented (if applicable)

### Sensitive Data (Art. 11)
- [ ] Sensitive data categories identified (health, biometric, ethnic, religious)
- [ ] Enhanced protection applied (encryption + masking + access control)
- [ ] Specific consent obtained for sensitive data processing
- [ ] DPO notified of sensitive data handling

### Data Subject Rights (Art. 9)
- [ ] Right to access: Data export mechanism available
- [ ] Right to correction: Update procedures in place
- [ ] Right to deletion: DELETE operations validated on PII tables
- [ ] Right to portability: Standard export format (JSON/CSV) supported
- [ ] Right to information: Processing activities documented

### Data Retention (Art. 16)
- [ ] Retention periods defined per data category
- [ ] Automatic purge mechanisms configured
- [ ] Retention metadata stored as table properties
- [ ] Exception process for extended retention documented

---

## 4. GDPR Requirements

### Core Principles (Art. 5)
| Principle              | Implementation                                  |
| ---------------------- | ----------------------------------------------- |
| Lawfulness             | Legal basis documented for each processing activity |
| Purpose limitation     | Processing purpose metadata on each table         |
| Data minimization      | Only required columns migrated, unused dropped    |
| Accuracy               | Data quality checks at ingestion                  |
| Storage limitation     | TTL policies on Delta tables                      |
| Integrity/Confidentiality | Encryption at rest + in transit, column masking |
| Accountability         | Full audit trail, compliance reports              |

### Data Protection by Design (Art. 25)
- Apply masking **at ingestion**, not post-hoc
- Use column masking in Unity Catalog (data never stored unmasked)
- Implement row-level security at table creation
- Default to deny access (grant only what's needed)

### Data Protection Impact Assessment (DPIA)
- Required when processing PII at scale (migration qualifies)
- Document: data types, purposes, risks, safeguards
- Submit to DPO before migration execution

---

## 5. SOX Audit Controls

### Section 302 — Corporate Responsibility
- [ ] Management certification process defined
- [ ] Internal controls documented and tested
- [ ] Deficiencies reported and remediated
- [ ] Segregation of duties enforced

### Section 404 — Internal Controls Assessment
- [ ] IT General Controls (ITGC) documented:
  - [ ] Access management controls
  - [ ] Change management controls
  - [ ] Computer operations controls
  - [ ] Program development controls
- [ ] Application controls documented:
  - [ ] Input validation controls
  - [ ] Processing controls (checksums, row counts)
  - [ ] Output controls (reconciliation)
- [ ] Control testing evidence maintained for 7 years

### Audit Trail Requirements
```
Required fields for SOX-compliant audit log:
- Timestamp (UTC, millisecond precision)
- Actor (user or service principal)
- Action type (CREATE, READ, UPDATE, DELETE)
- Object affected (catalog.schema.table.column)
- Old value hash (for UPDATE)
- New value hash (for UPDATE)
- Source system
- Transaction ID
- Approval reference (if applicable)
```

---

## 6. Access Control Patterns

### Unity Catalog Permission Model

```
CATALOG (migration_catalog)
├── SCHEMA (staging)
│   ├── TABLE (mara_raw)         → data_writer: INSERT, SELECT
│   ├── TABLE (mara_partners)    → data_reader: SELECT (masked)
│   └── TABLE (financial_data)   → compliance_admin only
├── SCHEMA (curated)
│   ├── TABLE (material_master)  → data_reader: SELECT
│   └── VIEW (material_masked)   → bi_users: SELECT
└── SCHEMA (audit)
    └── TABLE (audit_trail)      → compliance_admin: INSERT, SELECT
```

### Role Matrix

| Role               | Catalog | Schema   | Table     | Column  |
| ------------------ | ------- | -------- | --------- | ------- |
| `data_reader`      | USAGE   | USAGE    | SELECT    | Masked  |
| `data_writer`      | USAGE   | USAGE    | SELECT, INSERT, UPDATE | Masked |
| `data_admin`       | USAGE   | ALL      | ALL       | Masked  |
| `compliance_admin` | USAGE   | USAGE    | SELECT    | Unmasked|
| `etl_service`      | USAGE   | USAGE    | INSERT    | N/A     |
| `bi_service`       | USAGE   | USAGE    | SELECT    | Masked  |

### Least Privilege SQL Templates

```sql
-- Create groups
CREATE GROUP IF NOT EXISTS data_readers;
CREATE GROUP IF NOT EXISTS data_writers;
CREATE GROUP IF NOT EXISTS compliance_admins;

-- Grant minimal access
GRANT USAGE ON CATALOG migration_catalog TO data_readers;
GRANT USAGE ON SCHEMA migration_catalog.curated TO data_readers;
GRANT SELECT ON TABLE migration_catalog.curated.material_master TO data_readers;

-- Service principal scoped access
GRANT USAGE ON CATALOG migration_catalog TO etl_service_principal;
GRANT USAGE ON SCHEMA migration_catalog.staging TO etl_service_principal;
GRANT INSERT ON SCHEMA migration_catalog.staging TO etl_service_principal;
```

---

## 7. Encryption Standards

### At Rest
| Component              | Standard          | Implementation                  |
| ---------------------- | ----------------- | ------------------------------- |
| Azure Storage          | AES-256           | Azure SSE (automatic)           |
| Databricks DBFS        | AES-256           | Workspace encryption key         |
| Delta Lake files       | AES-256           | Inherited from storage           |
| Key Vault              | RSA-2048 / HSM    | Customer-managed keys (CMK)     |
| Tokenization vault     | AES-256           | Azure Key Vault Secrets          |

### In Transit
| Connection             | Standard          | Configuration                    |
| ---------------------- | ----------------- | -------------------------------- |
| HTTPS API calls        | TLS 1.2+          | Enforce minimum version           |
| JDBC/ODBC              | TLS 1.2+          | `ssl=true` in connection string   |
| Cluster communication  | TLS 1.2+          | Databricks managed                |
| Key Vault access       | TLS 1.2+          | Azure enforced                    |

### Key Management Best Practices
- Use Azure Key Vault for all cryptographic keys
- Rotate encryption keys every 90 days
- Use separate keys for different environments (dev/staging/prod)
- Enable soft-delete and purge protection on Key Vault
- Log all key access in Azure Monitor

### Certificate Rotation Schedule
| Certificate            | Rotation Period | Responsible           |
| ---------------------- | --------------- | --------------------- |
| TLS certificates       | 90 days         | Azure App Service     |
| Service principal keys | 90 days         | Azure AD              |
| Encryption keys        | 90 days         | Key Vault policy      |
| Token signing keys     | 180 days        | Identity provider     |

---

## Quick Reference Card

| Topic              | Key Rule                                           |
| ------------------ | -------------------------------------------------- |
| PII Detection      | Scan 100% of columns, confidence ≥ 0.85            |
| Masking            | Zero unmasked PII in target, verify with reverse scan |
| LGPD               | Document legal basis, enable data subject rights    |
| GDPR               | Protection by design, mask at ingestion             |
| SOX                | Audit trail 7 years, segregation of duties          |
| Access Control     | Least privilege, groups not users, column masking   |
| Encryption         | AES-256 at rest, TLS 1.2+ in transit                |
| Audit              | Immutable, append-only, structured JSON             |
