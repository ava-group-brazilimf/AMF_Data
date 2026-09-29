# Extract Logic Task

**Task ID:** extract-logic  
**Agent:** Logan (Logic Extractor)  
**Version:** 1.0  
**Command:** `*extract-logic`  
**Phase:** UPSTREAM

---

## Purpose

Parse legacy source code, use LLM to extract business intent, identify business rules, data quality checks, transformations, and generate a structured representation of the business logic for each pipeline.

---

## Prerequisites

- `inventory.json` available from Discovery Scout
- `dependency-graph.json` available from Discovery Scout
- Source code files accessible in the workspace
- LLM API keys configured (GPT-4 or Claude 3.5)

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | Yes | Pipeline identifier from inventory |
| source_files | list | Yes | List of source code files to analyze |
| language | string | Yes | Source language (HiveQL, PySpark, SQL, etc.) |
| context | object | No | Additional context (comments, documentation) |

---

## Execution Steps

### Step 1: Load Pipeline Context

```
LOAD inventory.json
FIND pipeline by pipeline_id
EXTRACT metadata: name, type, language, complexity
LOAD dependency-graph.json
FIND pipeline dependencies (upstream/downstream)
SET extraction_context = {metadata, dependencies}
```

### Step 2: Parse Source Code (AST Analysis)

```
FOR EACH source_file in pipeline:
  DETECT language (HiveQL, PySpark, SQL, Scala, Python, Shell,
                   InformaticaPowerCenterXML, SynapsePipelineJSON)
  SELECT appropriate parser:
    - HiveQL                   → hive-ast-parser
    - PySpark / Python         → python-ast + spark-analyzer
    - SQL                      → sqlglot + sqlparse
        IF source platform = synapse:
          USE dialect=tsql
          CAPTURE: CTAS structure, DISTRIBUTION hint (+ hash column),
                   EXTERNAL TABLE definitions, OPENROWSET lake paths
          RECORD each hint in pseudocode metadata (target platform decisions
          depend on them)
    - Scala                    → scala-ast-parser
    - Shell/Bash               → bash-parser + regex
    - InformaticaPowerCenterXML →
        LOAD powercenter-extraction-patterns.md
        FOR EACH <TRANSFORMATION> in Mapping:
          MAP transformation type to pseudocode pattern (see patterns file)
          EXTRACT input ports, output ports, derivation expressions
          EXTRACT filter conditions, join conditions, aggregation expressions
          EXTRACT SQL Override from Source Qualifier if present
          IF JavaTransformation OR ExternalProcedure:
            SET confidence = LOW
            SET manual_migration_required = true
            LOG "Requires manual migration — Java/External code not parseable"
            ADD to manual_review_queue
            SKIP to next transformation
        CONTINUE to Step 3 with extracted structure
    - SynapsePipelineJSON →
        LOAD synapse-extraction-patterns.md
        FOR EACH pipeline JSON:
          FOR EACH activity in activities[]:
            MAP activity type to pseudocode pattern (see patterns file)
            EXTRACT inputs, outputs, dependsOn conditions
            IF activity type in (WebActivity, Custom, AzureFunctionActivity):
              SET confidence = LOW
              SET manual_migration_required = true
              ADD to manual_review_queue
          RESOLVE ExecutePipeline references → nested pseudocode
        FOR EACH dataflow JSON:
          MAP each transformation to pseudocode pattern
          EXTRACT expressions from derivedColumn/aggregate/filter
          TRANSLATE Data Flow expression language to neutral pseudocode
        CONTINUE to Step 3 with extracted structure
  PARSE source code using selected parser
  EXTRACT:
    - Input sources (tables, files, APIs)
    - Output targets (tables, files, APIs)
    - Transformations (joins, filters, aggregations, pivots)
    - Control flow (IF/ELSE, CASE, loops)
    - UDF calls (mark for separate analysis)
    - Data quality checks (NULL handling, range validations)
  IF parse_error:
    LOG warning with line number and context
    REDUCE confidence by 0.1 per error
    ATTEMPT fallback: regex-based extraction
```

### Step 3: Extract Business Intent (LLM Analysis)

```
CONSTRUCT prompt with:
  - Parsed AST summary
  - Original source code
  - Pipeline metadata from inventory
  - Dependency context
  
SEND to primary LLM (GPT-4-Turbo):
  "Analyze the following code and extract:
   1. Business intent — WHY does this code exist?
   2. Business rules — WHAT conditions govern the logic?
   3. Data quality rules — WHAT validations are applied?
   4. Edge cases — WHAT happens with NULLs, empty sets, duplicates?
   5. Assumptions — WHAT implicit assumptions are made?"

PARSE LLM response into structured format
VALIDATE extracted rules against AST findings
CROSS-REFERENCE with dependency graph for consistency
```

### Step 4: Identify Business Rules

```
FOR EACH rule extracted:
  CLASSIFY rule type:
    - FILTER: WHERE clauses, HAVING conditions
    - TRANSFORM: CASE/WHEN, string manipulations, calculations
    - VALIDATION: NULL checks, range checks, format checks
    - AGGREGATION: GROUP BY logic, window functions
    - LOOKUP: JOIN conditions, reference data lookups
    - SCD: Slowly Changing Dimension patterns (Type 1/2/3)
    - DEDUP: Deduplication logic
  ASSIGN confidence score (0.0-1.0)
  DOCUMENT source location (file, line number)
  MARK if SME review required (confidence < 0.75)
```

### Step 5: Generate Extraction Output

```
BUILD extraction result:
  {
    "pipeline_id": pipeline_id,
    "extraction_date": current_timestamp,
    "language": detected_language,
    "confidence": overall_confidence,
    "inputs": [list of input sources],
    "outputs": [list of output targets],
    "business_rules": [list of extracted rules],
    "transformations": [list of transformations],
    "data_quality_checks": [list of quality checks],
    "udfs_referenced": [list of UDF calls],
    "assumptions": [list of documented assumptions],
    "warnings": [list of extraction warnings],
    "sme_review_required": boolean
  }

SAVE to projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json
LOG extraction in audit trail
```

---

## Output

| Output | Format | Location |
|--------|--------|----------|
| Extraction result | JSON | `projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json` |
| Extraction log | LOG | `projects/{project_name}/outputs/upstream/logic/reports/extraction-log.md` |

---

## Quality Criteria

- All input sources identified (100% coverage)
- All output targets identified (100% coverage)
- Business rules extracted with confidence >= 0.75
- Data quality checks documented
- UDF references flagged for separate analysis
- Assumptions explicitly documented
- Warnings logged for low-confidence extractions

---

*Task defined by AI-Agent Migration Factory™ v4.0*
