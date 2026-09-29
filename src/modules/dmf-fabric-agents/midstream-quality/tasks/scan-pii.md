# 🔒 Task: Scan PII

## AI-Agent Migration Factory™ — Security & Compliance Agent

---

## Task ID
`scan-pii`

## Command
`*scan-pii`

## Purpose
Detect Personally Identifiable Information (PII) in table schemas and data samples using the Presidio analyzer engine, supplemented by custom regex patterns and NLP-based Named Entity Recognition.

---

## Trigger
- Manual: `*scan-pii --source=<file>`
- Automatic: When new table schemas or generated code arrive from upstream agents (Coda ⚙️, Scout 🔍)

---

## Inputs

| Input                    | Source Agent       | Format   | Required |
| ------------------------ | ------------------ | -------- | -------- |
| `table-schemas.json`     | Discovery Scout 🔍 | JSON     | Yes      |
| `generated-code/*.py`    | Code Generator ⚙️  | Python   | Optional |
| `data-samples/*.csv`     | Manual upload      | CSV      | Optional |

---

## Parameters

| Parameter       | Default   | Description                                          |
| --------------- | --------- | ---------------------------------------------------- |
| `--source`      | —         | Path to schema file or code directory                |
| `--types`       | ALL       | Comma-separated PII types to scan (EMAIL, BR_CPF, etc.) |
| `--confidence`  | 0.85      | Minimum confidence threshold to flag a finding        |
| `--sample-rows` | 100       | Number of rows to sample per column for data scanning |
| `--language`    | pt,en     | Languages for NLP-based detection                    |
| `--mode`        | schema    | `schema` for schema scan, `code-scan` for code scanning |

---

## Procedure

### Step 1: Load and Parse Input
```
1.1 Read source file (table-schemas.json or code files)
1.2 Parse schema structure: catalog → schema → table → columns
1.3 Extract column names, data types, sample values (if available)
1.4 Log: "Scanning {N} tables, {M} columns across {K} schemas"
```

### Step 2: Column Name Heuristic Scan
```
2.1 Match column names against PII indicator patterns:
    - email|e_mail|email_addr → EMAIL
    - cpf|nr_cpf|num_cpf → BR_CPF
    - cnpj|nr_cnpj|num_cnpj → BR_CNPJ
    - phone|telefone|celular → PHONE_NUMBER
    - credit_card|cartao → CREDIT_CARD
    - passport|passaporte → PASSPORT
    - address|endereco|logradouro → ADDRESS
    - iban|conta_bancaria → IBAN
2.2 Flag matches with confidence=0.70 (heuristic)
2.3 Mark for Presidio confirmation
```

### Step 3: Presidio Analyzer Scan
```
3.1 Initialize Presidio AnalyzerEngine with pt and en recognizers
3.2 Register custom recognizers:
    - BRCPFRecognizer (validates check digits)
    - BRCNPJRecognizer (validates check digits)
3.3 For each column with sample data:
    a. Sample up to 100 rows
    b. Run Presidio analyze() on each value
    c. Aggregate results by PII type
    d. Calculate column-level confidence score
3.4 Merge with heuristic findings (take higher confidence)
```

### Step 4: Code Scan (if mode=code-scan)
```
4.1 Parse Python files for string literals containing PII patterns
4.2 Check for hardcoded credentials, connection strings, API keys
4.3 Detect PII in logging statements, print statements, comments
4.4 Flag insecure patterns: eval(), exec(), SQL injection vectors
```

### Step 5: Generate Findings Report
```
5.1 For each detected PII field:
    - table_name, column_name
    - pii_type (EMAIL, BR_CPF, etc.)
    - confidence_score (0.0 – 1.0)
    - detection_method (presidio | regex | heuristic | nlp)
    - sample_count (how many samples matched)
    - recommended_action (mask | redact | tokenize | review)
    - severity (CRITICAL | HIGH | MEDIUM | LOW)
5.2 Sort findings by severity DESC, confidence DESC
5.3 Write to pii-findings/pii-findings.json
```

### Step 6: Summary and Audit
```
6.1 Generate summary:
    - Total columns scanned
    - Total PII fields detected
    - Breakdown by PII type
    - Breakdown by severity
6.2 Log audit entry: PII_SCAN_COMPLETED
6.3 If PII found → set pipeline status = REQUIRES_MASKING
6.4 If no PII found → set pipeline status = PII_CLEAR
```

---

## Output

### Primary: `pii-findings/pii-findings.json`

```json
{
  "scan_id": "PII-SCAN-2025-001",
  "timestamp": "2025-01-15T10:30:00Z",
  "pipeline_id": "MM_MDG_001",
  "scan_config": {
    "confidence_threshold": 0.85,
    "sample_rows": 100,
    "languages": ["pt", "en"],
    "pii_types": "ALL"
  },
  "summary": {
    "tables_scanned": 45,
    "columns_scanned": 312,
    "pii_fields_detected": 8,
    "by_type": {
      "EMAIL": 2,
      "BR_CPF": 3,
      "PHONE_NUMBER": 2,
      "ADDRESS": 1
    },
    "by_severity": {
      "CRITICAL": 3,
      "HIGH": 3,
      "MEDIUM": 2
    }
  },
  "findings": [
    {
      "table": "MARA_PARTNERS",
      "column": "EMAIL_ADDR",
      "pii_type": "EMAIL",
      "confidence": 0.97,
      "detection_method": "presidio",
      "sample_matches": 94,
      "severity": "CRITICAL",
      "recommended_action": "mask",
      "recommended_strategy": "partial-mask",
      "regulatory_reference": "LGPD Art. 11, GDPR Art. 9"
    }
  ],
  "verdict": "REQUIRES_MASKING"
}
```

---

## Severity Classification

| Severity   | Criteria                                            |
| ---------- | --------------------------------------------------- |
| CRITICAL   | Direct identifier (CPF, email) with confidence > 0.90 |
| HIGH       | Direct identifier with confidence 0.85–0.90          |
| MEDIUM     | Indirect identifier (address, phone) or confidence 0.70–0.85 |
| LOW        | Heuristic match only, no sample confirmation          |

---

## Acceptance Criteria

- [ ] All columns in provided schemas are scanned (100% coverage)
- [ ] Presidio analyzer runs with custom BR recognizers (CPF, CNPJ)
- [ ] Findings include confidence scores ≥ threshold
- [ ] Output JSON is valid and parseable
- [ ] Audit log entry generated for scan completion
- [ ] At least column-name heuristic works even without data samples
