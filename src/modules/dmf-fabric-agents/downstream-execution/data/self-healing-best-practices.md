# Self-Healing Best Practices

**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0

---

## 1. Error Classification Taxonomy

### Hierarchy

```
Migration Errors
├── Syntax Errors (deterministic, always auto-fixable)
│   ├── Python syntax (SyntaxError)
│   ├── PySpark API misuse (AttributeError)
│   └── SQL syntax (AnalysisException — parse)
│
├── Semantic Errors (context-dependent, may need LLM)
│   ├── Business logic deviation
│   ├── Transformation correctness
│   ├── Data type mismatches (TypeMismatch)
│   └── Join condition errors
│
├── Runtime Errors (environment-dependent)
│   ├── Null handling (NullPointerException)
│   ├── Column not found (AnalysisException — resolve)
│   ├── Partition errors
│   ├── Schema evolution / drift
│   ├── Encoding errors (UnicodeDecodeError)
│   ├── Date format mismatches (ValueError)
│   └── Memory / resource errors (OutOfMemoryError)
│
└── Compliance Errors (policy-based)
    ├── PII exposure (LGPD / GDPR)
    ├── SOX audit trail missing
    ├── Data masking incomplete
    └── Access control violations
```

### Severity Mapping

| Severity | Auto-Fix Likelihood | Max Attempt | Examples |
|----------|-------------------|-------------|----------|
| Low | ≥ 90% | 1 (rule-based) | import_missing, encoding_error |
| Medium | 75–90% | 2 (rule + LLM) | type_mismatch, null_handling, date_format |
| High | 50–75% | 3 (all strategies) | schema_evolution, sql_syntax, join_condition |
| Critical | < 50% | Escalate fast | compliance violations, data loss risk |

---

## 2. Root Cause Analysis

### The 5-Whys Technique for Migration Errors

1. **Why** did the pipeline fail? → Column `CUST_DATE` not found
2. **Why** was the column not found? → Source schema has `CUSTOMER_DATE`
3. **Why** was the wrong name used? → BODS job used alias `CUST_DATE`
4. **Why** wasn't the alias mapped? → Column mapping didn't cover aliases
5. **Why** wasn't alias handling included? → Logic extractor didn't parse BODS aliases

**Root Cause:** Logic extraction gap — BODS alias handling not implemented.

### Fault Tree Template

```
Pipeline Failure
├── Error in generated code?
│   ├── Yes → Code generation issue (Coda)
│   │   ├── Missing transformation?
│   │   ├── Wrong API usage?
│   │   └── Template error?
│   └── No → Environment issue
│       ├── Schema drift?
│       ├── Missing dependency?
│       └── Configuration error?
├── Error in business logic?
│   ├── Yes → Logic extraction issue (Logan)
│   └── No → Translation issue
└── Error in compliance?
    └── Yes → Security issue (Shield)
```

---

## 3. Fix Strategy Selection

### Decision Matrix

| Error Type | Pattern Known? | Confidence | Strategy |
|-----------|---------------|------------|----------|
| Any | Yes (≥ 0.85) | High | Rule-based (Attempt 1) |
| Any | Partial (0.5–0.84) | Medium | Rule-based then LLM (Attempts 1→2) |
| Any | No (< 0.5) | Low | LLM from start (Attempts 2→3) |
| Compliance | Any | Any | Always rule-based + human review |

### Strategy Characteristics

| Strategy | Speed | Determinism | Risk | Best For |
|----------|-------|-------------|------|----------|
| Rule-based | Fast (< 30s) | 100% | Low | Known patterns, simple fixes |
| LLM Alt Prompt | Medium (1–2 min) | Variable | Medium | Novel errors with clear context |
| LLM Diff Model | Slow (2–3 min) | Variable | Higher | Complex errors, creative solutions |

### Minimal Diff Principle

**Always prefer the smallest possible change:**

```python
# BAD: Rewriting entire function
def process_data(df):
    # ... completely rewritten 50 lines ...

# GOOD: Surgical fix
def process_data(df):
    # ... original code ...
    result = df.withColumn("date",
-       col("date_str")                          # ← removed
+       to_date(col("date_str"), "yyyy-MM-dd")   # ← added
    )
    # ... rest of original code unchanged ...
```

---

## 4. Common Migration Error Patterns

### Pattern 1: Type Mismatch

```python
# Error: AnalysisException: cannot resolve 'date_col' due to data type mismatch
# Root Cause: Source has STRING, target expects DATE

# Fix:
df = df.withColumn("date_col", to_date(col("date_col"), "yyyy-MM-dd"))
```

### Pattern 2: Null Handling

```python
# Error: NullPointerException / NoneType has no attribute
# Root Cause: Missing null check on nullable column

# Fix:
df = df.filter(col("field").isNotNull())
# OR
df = df.withColumn("field", coalesce(col("field"), lit("")))
```

### Pattern 3: SQL Syntax (BODS → Spark)

```python
# Error: BODS SQL functions not available in Spark SQL
# Common translations:
# NVL(a, b)         → coalesce(a, b)
# DECODE(a,b,c,d)   → CASE WHEN a=b THEN c ELSE d END
# SYSDATE            → current_timestamp()
# SUBSTR(s,p,l)      → substring(s, p, l)
# TO_CHAR(d, 'fmt')  → date_format(d, 'fmt')
```

### Pattern 4: Import Missing

```python
# Error: ModuleNotFoundError: No module named 'pyspark.sql.functions'
# Fix: Add missing import at top of file
from pyspark.sql.functions import col, lit, when, coalesce, to_date
from pyspark.sql.types import StringType, IntegerType, DateType
```

### Pattern 5: Column Not Found

```python
# Error: AnalysisException: cannot resolve 'CUST_ID'
# Root Cause: Column renamed in target schema

# Fix: Use correct column mapping
df = df.withColumnRenamed("CUST_ID", "customer_id")
# OR
column_mapping = {"CUST_ID": "customer_id", "CUST_NAME": "customer_name"}
for old, new in column_mapping.items():
    df = df.withColumnRenamed(old, new)
```

### Pattern 6: Partition Error

```python
# Error: Incorrect partitioning causing skew or missing partitions

# Fix: Explicit repartition with appropriate key
df = df.repartition(200, col("partition_key"))
# OR for output:
df.write.partitionBy("year", "month").format("delta").save(path)
```

### Pattern 7: Schema Evolution

```python
# Error: Schema mismatch when reading/writing Delta tables

# Fix:
df.write \
    .format("delta") \
    .option("mergeSchema", "true") \
    .mode("overwrite") \
    .save(path)
```

### Pattern 8: Encoding Error

```python
# Error: UnicodeDecodeError: 'utf-8' codec can't decode byte

# Fix:
df = spark.read \
    .option("encoding", "ISO-8859-1") \
    .option("charset", "ISO-8859-1") \
    .csv(path)
```

### Pattern 9: Date Format

```python
# Error: ValueError: time data does not match format

# Fix:
df = df.withColumn("date_col",
    to_date(col("date_col"), "dd/MM/yyyy"))  # Match source format

# Multi-format handling:
df = df.withColumn("date_col",
    coalesce(
        to_date(col("date_col"), "yyyy-MM-dd"),
        to_date(col("date_col"), "dd/MM/yyyy"),
        to_date(col("date_col"), "MM-dd-yyyy")
    ))
```

### Pattern 10: Join Condition

```python
# Error: Join key type mismatch (INT vs STRING)

# Fix: Cast join keys to same type
df_result = df_a.join(
    df_b,
    df_a["key_col"].cast("string") == df_b["key_col"].cast("string"),
    "left"
)
```

---

## 5. Learning System

### MLflow Integration

```
Experiment: self-healing-patterns
│
├── Run: learn_PL_CUSTOMER_001_20260213
│   ├── Parameters: pattern=type_mismatch, strategy=rule_based
│   ├── Metrics: success=1.0, time=12s, lines_changed=2
│   └── Artifacts: signature.json, template.json, diff.patch
│
├── Run: learn_PL_ORDER_045_20260213
│   ├── Parameters: pattern=novel_join_skew, strategy=llm_alt_prompt
│   ├── Metrics: success=1.0, time=95s, lines_changed=8
│   └── Artifacts: signature.json, template.json, diff.patch
│
└── Registry: Known Patterns (auto-updated)
    ├── type_mismatch (95% success, rule-based)
    ├── null_handling (90% success, rule-based)
    └── novel_join_skew (80% success, LLM — pending promotion)
```

### Pattern Lifecycle

```
Discovery → Validation → Tracking → Promotion → Rule-Based
   │            │            │           │            │
   New error    First fix    MLflow      ≥90% rate    Deterministic
   encountered  succeeds     tracking    ≥5 occurs    template
```

---

## 6. Circuit Breaker Pattern

### When to Activate

| Condition | Action |
|-----------|--------|
| 5 consecutive pipeline failures | PAUSE all healing, alert team |
| Regression detected in 3+ fixes | PAUSE, review fix templates |
| Novel error rate > 60% | PAUSE, update pattern registry |
| Fix time > 10 min per pipeline | WARN, investigate bottleneck |

### Recovery Protocol

1. **Identify** — root cause of consecutive failures
2. **Analyze** — common thread across failures
3. **Update** — patterns/templates based on findings
4. **Test** — with one pipeline before resuming
5. **Resume** — with monitoring on higher alert

---

## 7. Escalation Guidelines

### When to Escalate

- After 3 fix attempts with no improvement
- Regression detected that can't be reverted cleanly
- Compliance error with security implications
- Schema-breaking change required
- Business logic ambiguity (can't determine correct behavior)
- Error in upstream agent output (logic extraction or code generation)

### Escalation Content

Every escalation to Orion 🧭 must include:

1. **Pipeline ID and context**
2. **Error description and classification**
3. **Root cause analysis** (even if incomplete)
4. **All 3 attempts** — what was tried and why it failed
5. **Blast radius** — what else might be affected
6. **Specific help needed** — what human expertise is required
7. **Suggested next steps** — Phoenix's recommendation
8. **Time invested** — how long was spent on healing

### Escalation Priority

| Priority | Criteria | SLA |
|----------|----------|-----|
| P1 - Critical | Compliance violation, data loss risk | 1 hour |
| P2 - High | Blocking other pipelines, wave blocker | 4 hours |
| P3 - Medium | Single pipeline issue, workaround exists | 1 business day |
| P4 - Low | Enhancement, pattern improvement | Next sprint |
