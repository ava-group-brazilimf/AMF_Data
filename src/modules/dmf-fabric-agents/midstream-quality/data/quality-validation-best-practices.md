# ✅ Quality Validation Best Practices

> **Agent:** Vera | **Reference:** Quality validation standards and guidelines for the AI-Agent Migration Factory™

---

## 1. Code Quality Standards

### 1.1 Syntax Correctness

Every generated code file must be syntactically valid. No exceptions.

```python
# ✅ CORRECT: Always validate before proceeding
import ast

def validate_syntax(code_path: str) -> bool:
    """Validate Python file has zero syntax errors."""
    with open(code_path, 'r') as f:
        source = f.read()
    try:
        ast.parse(source)
        return True
    except SyntaxError as e:
        log_error(f"Syntax error at line {e.lineno}: {e.msg}")
        return False
```

### 1.2 Lint Standards

| Tool   | Threshold          | Config File  | Notes                           |
|--------|--------------------|--------------|---------------------------------|
| Pylint | Score ≥ 8.0/10     | `.pylintrc`  | Disable C0114 for notebooks     |
| Flake8 | ≤ 10 violations    | `.flake8`    | Max line length 120             |
| mypy   | Zero critical errors | `mypy.ini` | Strict mode for public APIs     |

### 1.3 Code Structure Rules

```python
# ✅ CORRECT: Functions under 50 lines, typed, documented
def transform_customer_data(
    df_source: DataFrame,
    df_lookup: DataFrame,
    load_date: str
) -> DataFrame:
    """Transform raw customer data applying business rules.
    
    Args:
        df_source: Raw customer DataFrame.
        df_lookup: Region lookup table.
        load_date: Processing date (YYYY-MM-DD).
    
    Returns:
        Transformed DataFrame ready for Delta Lake.
    """
    # ... implementation under 50 lines ...

# ❌ WRONG: No type hints, no docstring, too long
def transform(df, lkp, dt):
    # 100+ lines of unstructured code
    pass
```

### 1.4 Common Lint Issues to Watch

| Issue                        | Rule     | Remediation                              |
|------------------------------|----------|------------------------------------------|
| Bare `except:`               | E722     | Use specific exception types             |
| Unused imports               | F401     | Remove or use `# noqa: F401`            |
| Undefined variable           | F821     | Define before use, check spelling        |
| Missing docstring            | C0114    | Add Google-style docstring               |
| Too many arguments (> 5)     | R0913    | Use dataclass or config object           |
| Line too long (> 120)        | E501     | Break line or refactor                   |
| Magic number                 | —        | Replace with named constant              |

---

## 2. Semantic Equivalence Testing

### 2.1 Data Flow Preservation

The generated code must maintain exact data flow equivalence with the legacy system.

```
Verification Checklist:
  ✅ Every source table read in legacy → read in generated code
  ✅ Every target table written in legacy → written in generated code
  ✅ Read filters match (WHERE clauses, date ranges)
  ✅ Write modes match (append, overwrite, merge)
  ✅ Column selection matches (no missing, no extra columns)
  ✅ Join conditions match (same keys, same type)
```

### 2.2 Business Rule Verification

Business rules are the highest priority in semantic equivalence — they represent the core logic the migration must preserve.

```
For each business rule:
  1. Extract rule from pseudocode
  2. Locate implementation in generated code
  3. Verify:
     - Conditional logic matches (IF/ELSE/CASE/WHEN)
     - Calculation formulas are equivalent
     - Default values are consistent
     - Null handling is identical
     - Date/time operations produce same results
     - String operations produce same results
  4. Document any deviations with justification
```

### 2.3 Common Semantic Pitfalls

| Pitfall                             | Example                                  | Impact    |
|-------------------------------------|------------------------------------------|-----------|
| Missing NULL handling               | `col("x") == "Y"` vs `col("x").isNull()`| DATA LOSS |
| Different join types                | INNER vs LEFT in source system           | DATA LOSS |
| Missing DISTINCT                    | Source had DISTINCT, generated doesn't   | DUPLICATES|
| Date format mismatch                | `yyyy-MM-dd` vs `dd/MM/yyyy`            | DATA ERROR|
| Case sensitivity                    | `UPPER()` missing in comparison          | MISMATCH  |
| Order of operations                 | Filter before vs after join              | DIFFERENT RESULTS |
| Default value difference            | Legacy uses 0, generated uses NULL       | DATA ERROR|

### 2.4 LLM Comparison Guidelines

When using LLM for semantic comparison:

```
Best Practices:
  ✅ Provide full pseudocode + full generated code (no truncation)
  ✅ Ask for structured JSON response with confidence scores
  ✅ Request specific discrepancy list, not just overall assessment
  ✅ Include schema context (column types, constraints)
  ✅ Ask about edge cases explicitly (nulls, empty, boundaries)
  
  ❌ Don't rely on single LLM call — cross-validate with structural analysis
  ❌ Don't accept confidence < 0.80 without human review
  ❌ Don't skip comparison for "simple" pipelines
```

---

## 3. Test Coverage Guidelines

### 3.1 Minimum Coverage Requirements

| Coverage Type | Minimum | Target  | Notes                            |
|---------------|---------|---------|----------------------------------|
| Line Coverage | 80%     | 90%+    | Must cover all transformation logic |
| Branch Coverage| 70%    | 85%+    | Every IF/ELSE path tested        |
| Function Coverage | 100% | 100%   | Every function must be called     |

### 3.2 Test Categories

```
Test Distribution (minimum):
  ├── Positive Tests (Happy Path):  60% of total
  │   ├── Basic transformation with valid data
  │   ├── All business rules with expected inputs
  │   └── End-to-end pipeline execution
  │
  ├── Negative Tests (Error Handling): 20% of total
  │   ├── Invalid input data
  │   ├── Missing required columns
  │   ├── Type mismatches
  │   └── Connection failures (mocked)
  │
  └── Edge Case Tests: 10% of total
      ├── Empty DataFrame
      ├── All NULLs in column
      ├── Duplicate keys
      ├── Boundary values (MAX_INT, empty string)
      └── Special characters in string columns
```

### 3.3 Test Quality Indicators

```python
# ✅ GOOD TEST: Specific assertions, clear naming, documented
def test_transform_customer_applies_uppercase(spark_session, sample_data):
    """Verify customer_name is uppercased per business rule BR-001."""
    result = transform_customer_data(sample_data, load_date="2025-01-15")
    
    assert result.count() == 3
    assert result.schema == expected_schema
    assert result.filter(col("customer_name") == "JOHN DOE").count() == 1
    assert result.filter(col("region").isNull()).count() == 0

# ❌ BAD TEST: Vague assertion, no documentation
def test_transform(spark):
    result = transform(spark.createDataFrame([]))
    assert result is not None  # This tells us nothing
```

### 3.4 Mandatory Test Scenarios

Every pipeline test suite must include:

| Scenario                       | Purpose                                      |
|--------------------------------|----------------------------------------------|
| Valid input → expected output  | Verify core transformation logic             |
| Empty input DataFrame          | Verify graceful handling of no data          |
| NULL values in key columns     | Verify null handling per business rules      |
| Duplicate keys                 | Verify deduplication or expected behavior    |
| Schema validation              | Verify output schema matches specification   |
| Row count validation           | Verify no unexpected row gain/loss           |
| Delta merge behavior           | Verify insert/update/delete handling         |

---

## 4. Performance Benchmarking

### 4.1 EXPLAIN Plan Analysis

```
Key Indicators:
  ✅ BroadcastHashJoin for small tables (< 100MB)
  ✅ Predicate pushdown (filters at scan level)
  ✅ Partition pruning (partition column in WHERE)
  ✅ AQE enabled for runtime optimization
  ✅ Reasonable number of stages/shuffles
  
  ❌ CartesianProduct (CRITICAL — always reject)
  ❌ SortMergeJoin on small table (use broadcast)
  ❌ Full scan on partitioned table without filter
  ❌ collect()/toPandas() on large dataset
  ❌ Coalesce(1) before write on large dataset
```

### 4.2 Performance Regression Thresholds

| Regression Level | Threshold         | Action                              |
|------------------|-------------------|-------------------------------------|
| Acceptable       | ≤ 10% slower      | PASS — note in report               |
| Warning          | 10–20% slower     | FLAG — include optimization hints   |
| Regression       | 20–50% slower     | REVIEW — human must approve         |
| Critical         | > 50% slower      | REJECT — must be optimized          |
| Improvement      | Any % faster      | Positive note in report             |

### 4.3 Common Performance Issues

| Issue                          | Detection                       | Fix                                |
|--------------------------------|---------------------------------|------------------------------------|
| Missing broadcast hint         | SortMergeJoin on small table    | `F.broadcast(df_small)`           |
| No partition pruning           | FileScan without partition filter| Add partition column to WHERE     |
| UDF instead of native          | PythonUDF in plan               | Replace with built-in functions   |
| Repeated scan                  | Same table read multiple times  | Cache intermediate DataFrame      |
| Too many small files           | Delta table DESCRIBE DETAIL     | Run OPTIMIZE + VACUUM             |
| Skewed join                    | One task much slower than others| Enable AQE skew join handling     |

---

## 5. Security Scanning

### 5.1 Security Rules

| Rule                           | Severity | Detection                         |
|--------------------------------|----------|-----------------------------------|
| Hardcoded password             | CRITICAL | String patterns: `password=`, `secret=` |
| Hardcoded connection string    | HIGH     | JDBC/ODBC patterns in code        |
| Use of eval/exec               | HIGH     | AST node check                    |
| SQL injection risk             | HIGH     | String concatenation in SQL       |
| Insecure deserialization       | MEDIUM   | `pickle.load()`, `yaml.load()`   |
| Insecure file operations       | MEDIUM   | Path traversal patterns           |
| Missing input validation       | LOW      | Parameters used without validation|
| Debug code left in             | LOW      | `print()`, `TODO`, `FIXME`       |

### 5.2 Acceptable Patterns

```python
# ✅ CORRECT: Credentials from secrets manager
connection_string = dbutils.secrets.get(scope="migration", key="db_connection")

# ✅ CORRECT: Parameterized SQL
spark.sql(f"SELECT * FROM {catalog}.{schema}.{table} WHERE load_date = '{date}'")

# ❌ WRONG: Hardcoded credentials
connection_string = "jdbc:sqlserver://host;user=admin;password=P@ssw0rd"

# ❌ WRONG: eval() usage
result = eval(user_input)
```

---

## 6. Handling Edge Cases

### 6.1 When to Override Thresholds

Override thresholds only in documented, justified scenarios:

| Scenario                       | Allowed Override          | Approval Required |
|--------------------------------|---------------------------|-------------------|
| Legacy has known performance issues | Regression threshold | Human PM          |
| Legacy code has no unit tests  | Coverage threshold (50%)  | Tech Lead         |
| Complex custom business logic  | LLM confidence (0.80)    | Architect         |
| Time-critical hotfix           | None — no shortcuts       | —                 |

### 6.2 Handling Flaky Tests

```
IF test fails intermittently:
  1. Run 3 times — pass if 3/3 succeed
  2. If flaky, identify root cause:
     - Timing dependency → Add explicit waits
     - Order dependency → Isolate test state
     - Resource contention → Use session-scoped fixtures
  3. Never skip flaky tests — fix them
```

### 6.3 Handling Missing Baselines

```
IF no legacy baseline exists:
  1. Skip regression comparison
  2. Use absolute thresholds:
     - Max runtime: based on data volume heuristic
     - Max stages: complexity_class → threshold mapping
     - Max shuffles: number_of_joins + 1
  3. Note in report: "No baseline available — absolute thresholds applied"
  4. Generate baseline from first successful run for future comparisons
```

### 6.4 Re-Validation Rules

```
After rejection and remediation by Phoenix 🔧:
  1. Re-run full validation pipeline (no shortcuts)
  2. Compare against previous validation report
  3. Verify all previously failing checks now pass
  4. Maximum 3 validation iterations per pipeline
  5. After 3 rejections → escalate to human
  6. Track iteration history in validation report
```
