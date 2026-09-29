# Parse UDF Task

**Task ID:** parse-udf  
**Agent:** Logan (Logic Extractor)  
**Version:** 1.0  
**Command:** `*parse-udf`  
**Phase:** UPSTREAM

---

## Purpose

Decompile and document User Defined Functions (UDFs) found in legacy code. UDFs are critical risk areas in migration — they contain embedded business logic, custom transformations, and platform-specific implementations that must be understood before migration.

---

## Prerequisites

- UDFs identified during `*extract-logic` execution
- Source code for UDFs accessible
- Language identified (Java, Python, Scala, HiveQL)

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| udf_name | string | Yes | Name of the UDF to analyze |
| source_file | string | Yes | Path to UDF source code |
| language | string | Yes | Implementation language |
| calling_pipelines | list | No | Pipelines that reference this UDF |

---

## Execution Steps

### Step 1: Identify UDF Type and Scope

```
LOAD UDF source code
CLASSIFY UDF type:
  - SCALAR: Takes single row, returns single value
  - TABULAR (UDTF): Takes input, returns table
  - AGGREGATE (UDAF): Aggregates multiple rows into single value
  - WINDOW: Operates within a window partition

IDENTIFY:
  - Input parameters (types, defaults)
  - Return type(s)
  - Side effects (file I/O, external calls, state)
  - Dependencies (imports, libraries, other UDFs)
  - Platform-specific APIs used
```

### Step 2: Decompile UDF Logic

```
PARSE UDF into AST
EXTRACT control flow:
  - Conditional branches (IF/ELSE, CASE/WHEN, try/catch)
  - Loops (FOR, WHILE, recursive calls)
  - Early returns and edge case handling

EXTRACT data transformations:
  - String manipulations
  - Date/time calculations
  - Numeric computations
  - Type conversions
  - Regex patterns

USE LLM to interpret complex logic:
  "Given this UDF implementation in {language}:
   {source_code}
   
   Explain:
   1. What business function does this UDF serve?
   2. What are the edge cases handled?
   3. What assumptions does it make about input data?
   4. Can this be replaced by a built-in function?
   5. What is the equivalent logic in plain pseudocode?"
```

### Step 3: Assess Replaceability

```
EVALUATE if UDF can be replaced by built-in functions:
  CHECK against known built-in equivalents:
    - String functions: CONCAT, SUBSTRING, TRIM, REGEXP
    - Date functions: DATEADD, DATEDIFF, FORMAT
    - Math functions: ROUND, CEIL, FLOOR, ABS
    - Aggregate functions: SUM, COUNT, AVG with conditions
    - Window functions: ROW_NUMBER, RANK, LAG, LEAD

CLASSIFY replaceability:
  - DIRECT_REPLACE: Built-in function exists on target platform
  - PARTIAL_REPLACE: Logic can be split into built-in + simple transform
  - REWRITE_REQUIRED: No equivalent — must be rewritten as target UDF
  - COMPLEX: Requires significant refactoring or architectural change

ESTIMATE migration effort:
  - DIRECT_REPLACE: 0.5 hours
  - PARTIAL_REPLACE: 2.0 hours
  - REWRITE_REQUIRED: 4.0 hours
  - COMPLEX: 8.0+ hours (flag for SME)
```

### Step 4: Document UDF

```
BUILD UDF documentation:
  {
    "udf_name": udf_name,
    "udf_type": SCALAR|TABULAR|AGGREGATE|WINDOW,
    "source_language": language,
    "source_file": file_path,
    "analysis_date": current_timestamp,
    "signature": {
      "input_params": [name, type, default],
      "return_type": type,
      "throws": [exception types]
    },
    "business_purpose": LLM_extracted_purpose,
    "logic_pseudocode": [pseudocode steps],
    "edge_cases": [identified edge cases],
    "assumptions": [documented assumptions],
    "dependencies": {
      "imports": [required libraries],
      "other_udfs": [called UDFs],
      "platform_apis": [platform-specific APIs]
    },
    "replaceability": {
      "classification": DIRECT_REPLACE|PARTIAL|REWRITE|COMPLEX,
      "built_in_equivalent": equivalent_function or null,
      "migration_strategy": recommended_approach,
      "estimated_effort_hours": number
    },
    "calling_pipelines": [list of pipelines using this UDF],
    "confidence": extraction_confidence,
    "sme_review_required": boolean
  }

SAVE to projects/{project_name}/outputs/upstream/logic/udf-analysis/{udf_name}.json
```

### Step 5: Update Pipeline References

```
FOR EACH pipeline that references this UDF:
  UPDATE pseudocode to include UDF resolution:
    - If DIRECT_REPLACE: note the built-in replacement
    - If REWRITE_REQUIRED: embed UDF pseudocode inline
    - If COMPLEX: mark as "requires SME resolution"
  
LOG UDF analysis in extraction report
```

---

## Output

| Output | Format | Location |
|--------|--------|----------|
| UDF Analysis | JSON | `projects/{project_name}/outputs/upstream/logic/udf-analysis/{udf_name}.json` |
| Updated Pseudocode | JSON | `projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json` (updated) |

---

## Quality Criteria

- UDF type correctly classified
- All input/output parameters documented
- Business purpose clearly explained
- Edge cases identified
- Replaceability assessed with rationale
- Migration effort estimated
- Calling pipelines identified and cross-referenced
- Confidence score >= 0.70 for each UDF

---

*Task defined by AI-Agent Migration Factory™ v4.0*
