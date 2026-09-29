# 🔒 Security & Compliance Checklist

## AI-Agent Migration Factory™ — Security & Compliance Agent

---

> **Instructions:** Complete each section sequentially. Every item must be checked before the pipeline advances past Gate 2.  
> **Verdict:** ALL sections must pass for COMPLIANT status.

---

## 1. PII Detection

- [ ] PII scan executed on all table schemas (`*scan-pii`)
- [ ] All columns scanned (100% coverage confirmed)
- [ ] Presidio analyzer initialized with pt and en language support
- [ ] Custom BR recognizers registered (CPF, CNPJ)
- [ ] Column name heuristic scan completed
- [ ] Data sample scan completed (100 rows per column)
- [ ] Confidence threshold applied (≥ 0.85)
- [ ] PII findings report generated (`pii-findings.json`)
- [ ] Findings classified by severity (CRITICAL, HIGH, MEDIUM, LOW)
- [ ] All PII types covered: EMAIL, PHONE, CPF, CNPJ, CREDIT_CARD, IBAN, PASSPORT, ADDRESS
- [ ] Code scan completed for generated Python files (if applicable)
- [ ] No hardcoded credentials or API keys in generated code

---

## 2. Data Masking

- [ ] Masking strategy determined for each PII field
- [ ] Strategy selection follows the masking matrix:
  - [ ] EMAIL → partial-mask
  - [ ] BR_CPF → partial-mask or SHA-256
  - [ ] BR_CNPJ → partial-mask or SHA-256
  - [ ] PHONE_NUMBER → partial-mask
  - [ ] CREDIT_CARD → partial-mask
  - [ ] PASSPORT → redaction
  - [ ] ADDRESS → SHA-256 or redaction
  - [ ] IBAN → partial-mask
- [ ] SQL masking functions created and validated in Databricks
- [ ] ALTER TABLE SET MASK applied to all PII columns
- [ ] Reverse PII scan confirms no PII in masked output
- [ ] Compliance admin bypass tested (can view unmasked values)
- [ ] Masking report generated (`masking-reports/{pipeline_id}.json`)
- [ ] Human approval obtained before production masking

---

## 3. Regulatory Compliance — LGPD

- [ ] **LGPD-01**: Legal basis documented for data processing (Art. 7)
- [ ] **LGPD-02**: Sensitive data (CPF, health) has enhanced protection (Art. 11)
- [ ] **LGPD-03**: Data subject export/delete capability verified (Art. 9)
- [ ] **LGPD-04**: Data retention policy defined and enforced (Art. 16)
- [ ] **LGPD-05**: Consent management verified (Art. 8)

---

## 4. Regulatory Compliance — GDPR

- [ ] **GDPR-01**: Data minimization — only necessary data migrated (Art. 5(1)(c))
- [ ] **GDPR-02**: Purpose limitation — processing purpose documented (Art. 5(1)(b))
- [ ] **GDPR-03**: Storage limitation — retention periods defined (Art. 5(1)(e))
- [ ] **GDPR-04**: Integrity & confidentiality — encryption verified (Art. 5(1)(f))
- [ ] **GDPR-05**: Right to erasure — DELETE capability confirmed (Art. 17)
- [ ] **GDPR-06**: Data protection by design — masking at ingestion (Art. 25)

---

## 5. Regulatory Compliance — SOX

- [ ] **SOX-01**: Access controls on financial data tables (Section 404)
- [ ] **SOX-02**: Complete audit trail for data modifications (Section 302)
- [ ] **SOX-03**: Data integrity — checksums and row counts verified (Section 404)
- [ ] **SOX-04**: Segregation of duties — no single-user full access (Section 302)
- [ ] **SOX-05**: Financial records retention ≥ 7 years (Section 802)

---

## 6. Access Control

- [ ] Unity Catalog enabled and configured
- [ ] All principals validated against role matrix
- [ ] No ALL PRIVILEGES grants at catalog level
- [ ] PII columns protected with masking functions
- [ ] Row-level security configured where applicable
- [ ] Individual user grants replaced with group-based grants
- [ ] Service principals scoped to minimum required permissions
- [ ] Segregation of duties enforced (no write + admin on same principal)
- [ ] No public or anonymous access to data tables
- [ ] Over-privileged access report generated and reviewed

---

## 7. Encryption

- [ ] Azure Storage Service Encryption enabled (at rest)
- [ ] Databricks workspace encryption enabled
- [ ] Azure Key Vault configured for key management
- [ ] TLS 1.2+ enforced on all connections (in transit)
- [ ] JDBC/ODBC connections use encrypted channels
- [ ] Tokenization vault secured (if tokenization strategy used)
- [ ] No plaintext credentials in connection strings
- [ ] Certificate rotation schedule documented

---

## 8. Audit Trail

- [ ] Audit log generated for all compliance activities
- [ ] Entries are append-only (immutable)
- [ ] Each entry has unique event_id
- [ ] Timestamps are ISO 8601 with timezone
- [ ] Human approvals recorded with actor identification
- [ ] JSONL format validated
- [ ] Elasticsearch-compatible format available
- [ ] Retention policy set to 7 years (2555 days) — SOX requirement
- [ ] Audit trail accessible for regulatory inquiries

---

## 9. Post-Compliance Review

- [ ] Compliance report generated (`compliance-reports/{pipeline_id}.json`)
- [ ] Compliance score calculated (target ≥ 95%)
- [ ] Verdict issued: COMPLIANT / NON-COMPLIANT / REVIEW_REQUIRED
- [ ] All CRITICAL findings addressed and resolved
- [ ] Remediation actions documented for any failures
- [ ] Report shared with downstream agents:
  - [ ] If COMPLIANT → forwarded to Balance ⚖️
  - [ ] If NON-COMPLIANT → forwarded to Phoenix 🔧
- [ ] Final audit log entry generated: PIPELINE_CLEARED or PIPELINE_BLOCKED
- [ ] Stakeholder sign-off obtained (if required by policy)

---

## Sign-Off

| Role                  | Name | Date | Status     |
| --------------------- | ---- | ---- | ---------- |
| Security Agent (Shield) |    |      | ☐ Approved |
| Data Protection Officer |    |      | ☐ Approved |
| Migration Coordinator   |    |      | ☐ Approved |

---

**Compliance Verdict:** ☐ COMPLIANT | ☐ NON-COMPLIANT | ☐ REVIEW_REQUIRED

**Pipeline Status:** ☐ CLEARED for Gate 2 | ☐ BLOCKED — remediation required
