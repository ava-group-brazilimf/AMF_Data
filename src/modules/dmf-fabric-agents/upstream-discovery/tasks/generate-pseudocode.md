# Generate Pseudocode Task

**Task ID:** generate-pseudocode  
**Agent:** Logan (Logic Extractor)  
**Version:** 1.0  
**Command:** `*generate-pseudocode`  
**Phase:** UPSTREAM

---

## Purpose

Convert extracted business logic into platform-agnostic pseudocode using standardized steps: READ, FILTER, JOIN, GROUP, AGGREGATE, TRANSFORM, VALIDATE, WRITE. The pseudocode must be understandable by humans and consumable by the Code Generator agent (Coda).

---

## Prerequisites

- Extraction output available (`projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json`)
- `*extract-logic` completed for the target pipeline(s)

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | Yes | Pipeline identifier |
| extraction_result | object | Yes | Output from extract-logic task |
| output_format | string | No | Format: "json" (default) or "markdown" |

---

## Execution Steps

### Step 1: Load Extraction Results

```
LOAD extraction result from projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json
VALIDATE extraction confidence >= 0.75
IF confidence < 0.75:
  WARN "Low confidence extraction — pseudocode may require SME review"
  SET sme_review_flag = true
LOAD business rules, transformations, inputs, outputs
```

### Step 2: Define Pseudocode Steps

```
INITIALIZE pseudocode_steps = []

FOR EACH input_source:
  ADD step: READ
    source: {table/file/api}
    columns: [selected columns]
    alias: {readable alias}

FOR EACH filter_rule:
  ADD step: FILTER
    condition: {business rule in natural language}
    source_rule: {original code reference}
    confidence: {score}

FOR EACH join_operation:
  ADD step: JOIN
    type: {INNER|LEFT|RIGHT|FULL|CROSS}
    left: {left source alias}
    right: {right source alias}
    on: {join condition in natural language}
    business_reason: {WHY this join exists}

FOR EACH grouping:
  ADD step: GROUP
    by: [grouping columns]
    purpose: {business reason for grouping}

FOR EACH aggregation:
  ADD step: AGGREGATE
    function: {SUM|COUNT|AVG|MIN|MAX|custom}
    column: {source column}
    alias: {output column name}
    business_meaning: {what this metric represents}

FOR EACH transformation:
  ADD step: TRANSFORM
    type: {CASE|CALC|STRING|DATE|CAST|CUSTOM}
    input: {source column(s)}
    output: {target column}
    logic: {transformation in natural language}
    business_rule: {associated business rule}

FOR EACH validation:
  ADD step: VALIDATE
    check: {validation description}
    on_failure: {REJECT|DEFAULT|LOG|SKIP}
    default_value: {if applicable}

FOR EACH output_target:
  ADD step: WRITE
    target: {table/file/api}
    mode: {OVERWRITE|APPEND|MERGE|UPSERT}
    partition_by: [partition columns if applicable]
    business_owner: {data owner if known}
```

### Step 3: Enrich with Business Context

```
FOR EACH step in pseudocode_steps:
  ADD business_context:
    - rule_name: human-readable name for the rule
    - rule_description: plain language explanation
    - source_reference: original code location
    - confidence: extraction confidence score
    - assumptions: any assumptions made
    - sme_notes: notes for SME review if needed
```

### Step 4: Validate Pseudocode Completeness

```
CHECK all inputs from extraction are represented in READ steps
CHECK all outputs from extraction are represented in WRITE steps
CHECK all business rules are mapped to at least one step
CHECK data flow is consistent (no orphan columns)
CHECK step ordering respects dependencies
CALCULATE pseudocode_coverage = mapped_rules / total_rules
IF pseudocode_coverage < 0.90:
  WARN "Incomplete pseudocode — {unmapped_rules} rules not represented"
```

### Step 5: Generate Output

```
BUILD pseudocode document:
  {
    "pipeline_id": pipeline_id,
    "pipeline_name": pipeline_name,
    "generation_date": current_timestamp,
    "confidence": overall_confidence,
    "coverage": pseudocode_coverage,
    "steps": pseudocode_steps,
    "business_rules_summary": [extracted rules with mappings],
    "assumptions": [all documented assumptions],
    "sme_review_required": boolean,
    "metadata": {
      "source_language": original_language,
      "source_files": [file references],
      "total_steps": step_count,
      "total_rules": rule_count
    }
  }

SAVE to projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json
UPDATE extraction log
```

---

## Pseudocode Step Types Reference

| Step | Purpose | Example |
|------|---------|---------|
| `READ` | Load data from source | Read orders table, select order_id, amount, date |
| `FILTER` | Apply business conditions | Keep only orders where status = 'ACTIVE' and amount > 0 |
| `JOIN` | Combine data sources | Join orders with customers on customer_id |
| `GROUP` | Group records | Group by region, product_category |
| `AGGREGATE` | Calculate metrics | Sum(amount) as total_revenue |
| `TRANSFORM` | Apply transformations | If amount > 10000 then 'HIGH' else 'STANDARD' |
| `VALIDATE` | Data quality checks | Reject if order_date is NULL |
| `WRITE` | Output results | Write to target table, partitioned by date |

---

## Output

| Output | Format | Location |
|--------|--------|----------|
| Pseudocode | JSON | `projects/{project_name}/outputs/upstream/logic/pseudocode/{pipeline_id}.json` |

---

## Quality Criteria

- 100% of input sources mapped to READ steps
- 100% of output targets mapped to WRITE steps
- >= 90% business rules mapped to pseudocode steps
- Platform-agnostic language (no HiveQL, SQL, PySpark references)
- Human-readable descriptions for all steps
- Confidence score assigned to each step

---

*Task defined by AI-Agent Migration Factory™ v4.0*
