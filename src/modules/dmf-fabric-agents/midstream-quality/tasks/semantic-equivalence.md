# ✅ Task: Semantic Equivalence Check

> **Command:** `*semantic-check`
> **Agent:** Vera (Quality Gate)
> **Phase:** MIDSTREAM | **Gate:** 2

---

## Objective

Compare generated code against the original pseudocode produced by Logan 🧠 to verify semantic equivalence. The generated code must do exactly what the legacy system did — no missing transformations, no altered business logic, and no data flow deviations.

---

## Prerequisites

- [ ] Generated code available: `generated-code/{pipeline_id}.py`
- [ ] Pseudocode available: `pseudocode/{pipeline_id}.json`
- [ ] LLM access configured (GPT-4 for comparison)
- [ ] Minimum confidence threshold loaded (default: 0.90)

---

## Steps

### Step 1: Parse Pseudocode Structure

Extract the logical structure from Logan's pseudocode output.

```
Load: pseudocode/{pipeline_id}.json

Extract:
  sources: [
    { name, type, schema, filters, description }
  ]
  transformations: [
    { step_id, type, logic, input_columns, output_columns, business_rule }
  ]
  targets: [
    { name, type, schema, write_mode, partition_columns }
  ]
  mappings: [
    { source_column, target_column, transformation_applied }
  ]
  business_rules: [
    { rule_id, description, implementation_notes }
  ]
```

**Validation:**
- All `step_id` values are unique
- All referenced columns exist in source/target schemas
- No orphan transformations (all connected to source or target)

---

### Step 2: Parse Generated Code Structure

Analyze the generated code's AST to extract its logical operations.

```
Parse: generated-code/{pipeline_id}.py

Extract:
  read_operations: [
    { source_name, read_method, filters_applied, columns_selected }
  ]
  transformation_operations: [
    { function_name, input_df, output_df, operations_applied, columns_modified }
  ]
  write_operations: [
    { target_name, write_method, mode, partition_columns }
  ]
  column_mappings: [
    { source_column, target_column, transformation_chain }
  ]
```

**Validation:**
- Code is syntactically valid (AST parseable)
- All read/write operations are identifiable
- Transformation chain is traceable

---

### Step 3: Data Flow Preservation Check

Verify that all data flows from the pseudocode are preserved in the generated code.

```
Check 3a: Source Coverage
  FOR each source in pseudocode.sources:
    VERIFY source is read in generated code
    VERIFY read filters match pseudocode filters
    VERIFY selected columns match or superset

Check 3b: Target Coverage
  FOR each target in pseudocode.targets:
    VERIFY target is written in generated code
    VERIFY write mode matches (append/overwrite/merge)
    VERIFY partition columns match

Check 3c: No Extra Sources/Targets
  VERIFY no sources read that aren't in pseudocode
  VERIFY no targets written that aren't in pseudocode
  (Allow temp views and intermediate DataFrames)
```

**Scoring:**
| Source Coverage | Target Coverage | Score |
|-----------------|-----------------|-------|
| 100%            | 100%            | 10.0  |
| ≥ 90%           | 100%            | 8.0   |
| ≥ 90%           | ≥ 90%           | 6.0   |
| < 90%           | any             | 3.0   |

---

### Step 4: Business Rule Alignment

Verify that business rules from the pseudocode are correctly implemented in the generated code.

```
FOR each business_rule in pseudocode.business_rules:
  1. Identify the corresponding code section
  2. Extract the implementation logic
  3. Compare against the pseudocode specification:
     - Conditional logic preserved (IF/ELSE/CASE)
     - Calculation formulas match
     - Default values align
     - Null handling consistent
     - Date/time logic correct
  4. Score alignment: exact_match | partial_match | missing | divergent
```

**LLM Comparison Prompt:**

```
Given the following pseudocode business rule:
{business_rule.description}

And the following generated code implementation:
{code_section}

Evaluate:
1. Does the code correctly implement the business rule? (yes/partial/no)
2. Are there any missing edge cases?
3. Is the null handling consistent with the pseudocode?
4. Confidence score (0.0–1.0)

Respond in JSON format.
```

**Scoring:**
| Alignment          | Score |
|--------------------|-------|
| All exact_match    | 10.0  |
| ≥ 90% exact_match  | 9.0   |
| Some partial_match | 7.0   |
| Any missing rule   | 4.0   |
| Any divergent rule | 2.0   |

---

### Step 5: Transformation Completeness

Verify that all transformations from the pseudocode are implemented and none are missing.

```
FOR each transformation in pseudocode.transformations:
  1. Map to corresponding code operation
  2. Verify:
     - Input columns match
     - Output columns match
     - Transformation type matches (filter/join/aggregate/map/etc.)
     - Order of operations preserved where relevant
  3. Mark as: implemented | missing | modified

Completeness = count(implemented) / count(total_transformations) * 100
```

**Scoring:**
| Completeness | Score |
|--------------|-------|
| 100%         | 10.0  |
| 95–99%       | 8.5   |
| 90–94%       | 7.0   |
| 80–89%       | 5.0   |
| < 80%        | 2.0   |

---

### Step 6: LLM Holistic Comparison

Use GPT-4 to perform a holistic comparison of pseudocode vs. generated code.

```
Prompt:
  "You are a senior data engineer reviewing a code migration.
   
   ORIGINAL PSEUDOCODE:
   {pseudocode_json}
   
   GENERATED CODE:
   {generated_code}
   
   Evaluate semantic equivalence across these dimensions:
   1. Data flow: Are all sources read and all targets written correctly?
   2. Business logic: Are all business rules correctly implemented?
   3. Transformations: Are all transformations present and correctly ordered?
   4. Edge cases: Are nulls, empty sets, and type mismatches handled?
   5. Completeness: Is anything from the pseudocode missing in the code?
   
   Provide:
   - Overall confidence score (0.0–1.0)
   - Per-dimension scores
   - List of discrepancies (if any)
   - Critical issues (if any)
   
   Respond in JSON format."
```

---

### Step 7: Calculate Semantic Score

Combine all sub-scores into a final semantic equivalence score.

```python
semantic_score = (
    data_flow_score     * 0.25 +
    business_rule_score * 0.30 +
    completeness_score  * 0.25 +
    llm_holistic_score  * 0.20
)

confidence = min(data_flow_confidence, business_rule_confidence, llm_confidence)
```

**Decision:**
| Confidence | Action                                |
|------------|---------------------------------------|
| ≥ 0.90     | PASS — Semantic equivalence confirmed |
| 0.80–0.89  | FLAG — Review recommended             |
| < 0.80     | FAIL — Semantic divergence detected   |

---

## Output

```json
{
  "pipeline_id": "{pipeline_id}",
  "check": "semantic_equivalence",
  "timestamp": "2025-01-15T14:30:22Z",
  "confidence": 0.94,
  "score": 9.1,
  "result": "PASS",
  "details": {
    "data_flow": { "score": 10.0, "sources_matched": 3, "targets_matched": 1 },
    "business_rules": { "score": 9.0, "exact": 8, "partial": 1, "missing": 0 },
    "completeness": { "score": 9.5, "implemented": 12, "total": 12 },
    "llm_holistic": { "score": 8.5, "confidence": 0.92 }
  },
  "discrepancies": [],
  "critical_issues": []
}
```
