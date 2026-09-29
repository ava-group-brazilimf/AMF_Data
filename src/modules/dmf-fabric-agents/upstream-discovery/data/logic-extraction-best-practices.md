# Logic Extraction Best Practices

**Reference:** Logan (Logic Extractor) Agent  
**Version:** 1.0

---

## Multi-Language Parsing

### Choosing the Right Parser

| Language | Primary Parser | Fallback | Notes |
|----------|---------------|----------|-------|
| HiveQL | `sqlglot` + `sqlparse` | Regex | Handle Hive-specific: LATERAL VIEW, TRANSFORM, SerDe |
| PySpark | `python-ast` + `spark-analyzer` | Regex | Track DataFrame API chains, resolve lazy evaluation |
| SQL (ANSI) | `sqlglot` | `sqlparse` | Normalize dialects before parsing |
| Scala | `scala-ast-parser` | LLM | Focus on Spark Scala patterns, case classes |
| Java | `java-ast-parser` | LLM | MapReduce patterns, custom InputFormats |
| Python | `python-ast` | Regex | Watch for dynamic SQL generation, exec() |
| Shell/Bash | `bash-parser` + Regex | LLM only | Shell often wraps other languages — identify inner code |

### Multi-Language Pipeline Strategy

```
WHEN pipeline spans multiple languages:
  1. Identify the "orchestrator" (usually Shell/Bash or Airflow DAG)
  2. Extract the execution order from the orchestrator
  3. Parse each inner language separately
  4. Merge results maintaining execution order
  5. Validate data flow across language boundaries
  6. Flag cross-language parameter passing for special attention
```

❌ **Never do this:**
- Parse all languages with a single generic parser
- Ignore shell wrapper scripts (they contain critical flow logic)
- Assume SQL dialect without validation
- Skip config files (Oozie XML, Airflow DAG definitions)

✅ **Always do this:**
- Validate parser output against original code structure
- Test parser with sample code before full extraction
- Log parse failures with line numbers for manual review
- Use dialect-aware SQL parsers (Hive SQL ≠ ANSI SQL)

---

## LLM Prompt Engineering

### Extraction Prompts

**Rule 1: Be Specific About Output Format**
```
❌ Bad:  "Analyze this code and tell me what it does"
✅ Good: "Analyze this HiveQL query and extract:
          1. All business rules (WHERE/HAVING conditions)
          2. All transformations (CASE/WHEN, calculations)
          3. Data quality checks (NULL handling, validations)
          Return as JSON with fields: rule_name, rule_type, 
          confidence, description, source_line"
```

**Rule 2: Provide Context**
```
❌ Bad:  Just sending the code
✅ Good: Sending code + table descriptions + pipeline purpose +
         upstream dependencies + known business domain
```

**Rule 3: Chain Prompts for Complex Code**
```
Step 1: "What are the input sources and output targets?"
Step 2: "For each transformation, what is the business intent?"
Step 3: "What assumptions does this code make about data quality?"
Step 4: "Generate platform-agnostic pseudocode for this logic"
```

**Rule 4: Cross-Validate LLM Output**
```
ALWAYS compare LLM extraction with AST extraction:
  - Rules found by AST but missed by LLM → flag for review
  - Rules found by LLM but not in AST → validate against source
  - Conflicting interpretations → reduce confidence, flag for SME
```

### Temperature Settings

| Task | Temperature | Rationale |
|------|:-----------:|-----------|
| Code analysis | 0.0 | Deterministic — same code should yield same analysis |
| Business intent | 0.1 | Slight creativity for interpreting intent |
| Pseudocode generation | 0.1 | Structured but needs natural language |
| Confidence scoring | 0.0 | Strictly deterministic |
| SME question generation | 0.3 | Creative for asking the right questions |

---

## Confidence Scoring

### Score Components

```
confidence = weighted_average(
  ast_parse_success    * 0.15,  # Did AST parse without errors?
  rule_extraction      * 0.25,  # Were business rules found?
  pseudocode_coverage  * 0.25,  # Is pseudocode complete?
  udf_resolution       * 0.15,  # Are UDFs understood?
  llm_agreement        * 0.10,  # Do AST and LLM agree?
  cross_reference      * 0.10   # Do dependencies check out?
)
```

### Confidence Thresholds

| Score | Classification | Action |
|:-----:|:-------------:|--------|
| >= 0.90 | 🟢 READY | Auto-approve for code generation |
| 0.75-0.89 | 🟡 REVIEW | SME spot-check recommended (10% sample) |
| 0.50-0.74 | 🟠 ATTENTION | SME full review required |
| < 0.50 | 🔴 BLOCKED | Re-extraction or manual intervention |

### Common Confidence Reducers

| Factor | Penalty | Mitigation |
|--------|:-------:|------------|
| AST parse failure | -0.10 per section | Use regex fallback, request cleaner source |
| Unresolved UDF | -0.15 per UDF | Request UDF source code from SME |
| Dynamic SQL (exec/eval) | -0.20 | Log all dynamic patterns, request runtime examples |
| Undocumented magic numbers | -0.05 per instance | Flag for SME, document assumption |
| Circular dependencies | -0.10 | Map cycle, flag for architecture review |
| Missing table schema | -0.05 per table | Request DDL or sample data |

---

## Pseudocode Generation

### Step Type Standards

Use ONLY these standardized step types:

| Step | Syntax | Example |
|------|--------|---------|
| READ | `READ {source} SELECT {columns}` | `READ orders_table SELECT order_id, amount, status` |
| FILTER | `FILTER WHERE {condition}` | `FILTER WHERE status = 'ACTIVE' AND amount > 0` |
| JOIN | `JOIN {type} {right} ON {condition}` | `JOIN LEFT customers ON order.cust_id = customer.id` |
| GROUP | `GROUP BY {columns}` | `GROUP BY region, product_category` |
| AGGREGATE | `AGGREGATE {function}({column}) AS {alias}` | `AGGREGATE SUM(amount) AS total_revenue` |
| TRANSFORM | `TRANSFORM {input} → {output}: {logic}` | `TRANSFORM amount → tier: IF > 10000 THEN 'HIGH' ELSE 'STD'` |
| VALIDATE | `VALIDATE {check} ON_FAIL {action}` | `VALIDATE order_date IS NOT NULL ON_FAIL REJECT` |
| WRITE | `WRITE {target} MODE {mode}` | `WRITE fact_orders MODE UPSERT PARTITION BY order_date` |

### Avoiding Platform Leakage

```
❌ "Use spark.read.parquet() to load the file"
✅ "READ sales_data from file source (format: columnar)"

❌ "Apply Hive LATERAL VIEW EXPLODE on tags column"  
✅ "TRANSFORM tags → tag: UNNEST array into individual rows"

❌ "Use Delta Lake MERGE INTO for upsert"
✅ "WRITE target_table MODE UPSERT ON key_columns"
```

---

## Business Rule Documentation

### Rule Naming Convention

```
Format: {DOMAIN}_{TYPE}_{SEQUENCE}
Examples:
  - SALES_FILTER_001: "Exclude cancelled orders"
  - FINANCE_CALC_001: "Calculate net revenue after tax"
  - CUSTOMER_VALID_001: "Reject records with NULL customer_id"
  - INVENTORY_SCD_001: "Track product price changes (Type 2)"
```

### Rule Documentation Template

```
Rule ID: {DOMAIN}_{TYPE}_{SEQ}
Rule Name: {human-readable name}
Rule Type: FILTER | TRANSFORM | VALIDATE | AGGREGATE | LOOKUP | SCD | DEDUP
Business Intent: {WHY this rule exists}
Logic: {WHAT the rule does in plain language}
Source Reference: {file}:{line_number}
Confidence: {0.0-1.0}
Assumptions: {any assumptions made}
Edge Cases: {known edge cases}
SME Verified: {true/false}
```

---

## Digital Twin Creation

### Layer Mapping Guidelines

**Physical Layer — "What exists"**
- Map every object from the inventory without exception
- Include deprecated and orphan objects (mark status)
- Preserve exact schema information
- Document physical location and access patterns

**Semantic Layer — "What it means"**
- Assign business-friendly names (not technical names)
- Classify by business domain (Sales, Finance, Customer, etc.)
- Apply data sensitivity classification (PII, financial, public)
- Document data quality rules
- Map end-to-end lineage

**Target Layer — "Where it's going"**
- Follow the Medallion Architecture (Bronze → Silver → Gold)
- Bronze: raw ingestion, schema-on-read
- Silver: cleansed, conformed, business rules applied
- Gold: aggregated, business-ready, consumption-optimized
- Map migration strategy per object (lift-shift vs refactor vs rebuild)

### Common Mistakes

❌ **Never do this:**
- Skip the semantic layer (jumping physical → target)
- Map 1:1 without considering target platform best practices
- Ignore partitioning and storage format decisions
- Leave gaps without documenting them

✅ **Always do this:**
- Complete all three layers before moving to code generation
- Validate cross-layer consistency
- Document gaps and unknowns explicitly
- Get SME buy-in on semantic naming before proceeding

---

*Best practices defined by AI-Agent Migration Factory™ v4.0*
