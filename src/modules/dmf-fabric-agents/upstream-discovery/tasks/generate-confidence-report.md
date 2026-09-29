# Generate Confidence Report Task

**Task ID:** generate-confidence-report  
**Agent:** Logan (Logic Extractor)  
**Version:** 1.0  
**Command:** `*confidence-report`  
**Phase:** UPSTREAM

---

## Purpose

Generate a comprehensive confidence report with per-pipeline extraction quality metrics. This report is used by the Migration Coordinator (Orion) for Gate 1 validation and by the Code Generator (Coda) to prioritize generation work.

---

## Prerequisites

- `*extract-logic` completed for target pipelines
- `*generate-pseudocode` completed for target pipelines
- `*parse-udf` completed for all referenced UDFs (if applicable)

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| scope | string | Yes | "all" or specific pipeline_ids |
| threshold | float | No | Minimum confidence threshold (default: 0.75) |
| include_details | boolean | No | Include per-rule breakdown (default: true) |

---

## Execution Steps

### Step 1: Collect Extraction Results

```
LOAD all pseudocode files from projects/{project_name}/outputs/upstream/logic/pseudocode/
LOAD all UDF analyses from projects/{project_name}/outputs/upstream/logic/udf-analysis/
LOAD inventory.json for pipeline metadata
BUILD comprehensive extraction inventory
```

### Step 2: Calculate Per-Pipeline Confidence

```
FOR EACH pipeline:
  CALCULATE component scores:
    - ast_parse_score: Percentage of code successfully parsed by AST
    - rule_extraction_score: Business rules extracted / expected rules
    - pseudocode_coverage: Pseudocode steps / total operations
    - udf_resolution_score: UDFs resolved / UDFs referenced
    - llm_confidence: Average LLM confidence across extractions
    - cross_reference_score: Dependencies verified / total dependencies
  
  CALCULATE weighted confidence:
    overall = (
      ast_parse_score * 0.15 +
      rule_extraction_score * 0.25 +
      pseudocode_coverage * 0.25 +
      udf_resolution_score * 0.15 +
      llm_confidence * 0.10 +
      cross_reference_score * 0.10
    )
  
  CLASSIFY pipeline readiness:
    IF overall >= 0.90: "READY" (green) — auto-approve for code generation
    IF overall >= 0.75: "REVIEW" (yellow) — SME spot-check recommended
    IF overall >= 0.50: "ATTENTION" (orange) — SME review required
    IF overall < 0.50: "BLOCKED" (red) — re-extraction or manual intervention
```

### Step 3: Identify Risk Areas

```
FOR EACH pipeline with confidence < threshold:
  IDENTIFY specific gaps:
    - Unparsed code sections (AST failures)
    - Low-confidence business rules
    - Unresolved UDFs
    - Missing dependency mappings
    - Ambiguous transformations

  GENERATE recommendation:
    - "Re-run extraction with additional context"
    - "Request SME review for rules X, Y, Z"
    - "Provide UDF source code for {udf_name}"
    - "Clarify business intent for transformation at line {n}"
```

### Step 4: Generate Aggregate Metrics

```
CALCULATE overall extraction quality:
  - total_pipelines: count in scope
  - ready_count: pipelines with confidence >= 0.90
  - review_count: pipelines with 0.75 <= confidence < 0.90
  - attention_count: pipelines with 0.50 <= confidence < 0.75
  - blocked_count: pipelines with confidence < 0.50
  - average_confidence: mean across all pipelines
  - median_confidence: median across all pipelines
  - total_business_rules: sum of all extracted rules
  - total_udfs_analyzed: count of UDFs processed
  - sme_review_items: count of items flagged for SME
  - gate_1_readiness: ready_percentage >= 80% threshold
```

### Step 5: Generate Report

```
BUILD confidence report using logic-report-tmpl.md:

  HEADER: Logic Extraction Confidence Report
  DATE: current_timestamp
  AGENT: Logan (Logic Extractor)
  SCOPE: {scope description}

  EXECUTIVE SUMMARY:
    - Overall readiness: {percentage}
    - Gate 1 status: {PASS/CONDITIONAL/FAIL}
    - Key risks: {top 3 risk areas}

  PER-PIPELINE TABLE:
    | Pipeline | Confidence | Status | Rules | UDFs | Action Required |
    |----------|-----------|--------|-------|------|-----------------|
    | {id}     | {score}   | {icon} | {n}   | {n}  | {action}        |

  RISK ANALYSIS:
    - Blocked pipelines with root causes
    - Low-confidence rules requiring SME review
    - Unresolved UDFs

  RECOMMENDATIONS:
    - Prioritized list of actions to improve confidence
    - Estimated effort for each action

SAVE to projects/{project_name}/outputs/upstream/logic/reports/logic-extraction-report.md
```

---

## Output

| Output | Format | Location |
|--------|--------|----------|
| Confidence Report | MD | `projects/{project_name}/outputs/upstream/logic/reports/logic-extraction-report.md` |
| Metrics JSON | JSON | `projects/{project_name}/outputs/upstream/logic/reports/extraction-metrics.json` |

---

## Quality Criteria

- All in-scope pipelines included in the report
- Per-pipeline confidence calculated with all 6 components
- Risk areas identified with actionable recommendations
- Gate 1 readiness assessment clearly stated
- SME review items explicitly listed
- Report follows the logic-report-tmpl.md template

---

*Task defined by AI-Agent Migration Factory™ v4.0*
