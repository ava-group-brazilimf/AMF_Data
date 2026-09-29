# Diagnose Error Task

**Task ID:** diagnose-error  
**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0  
**Command:** `*diagnose`  
**Phase:** DOWNSTREAM

---

## Purpose

Classify the error type from a validation report, parse the stack trace, match against known patterns in the MLflow registry, and perform root cause analysis using LLM if the error is novel.

---

## Prerequisites

- Validation report from Vera ✅ (`validation-report/{pipeline_id}.json`) or compliance report from Shield 🔒
- Original generated code from Coda ⚙️ (`generated-code/{pipeline_id}.py`)
- Access to MLflow known patterns registry

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | Yes | Pipeline identifier (e.g., PL_CUSTOMER_MASTER) |
| report_path | string | Yes | Path to validation or compliance report |
| code_path | string | Yes | Path to original generated code |
| error_type_hint | string | No | Optional hint about expected error category |

---

## Execution Steps

### Step 1: Load Error Context

```
LOAD validation-report/{pipeline_id}.json FROM Vera
LOAD generated-code/{pipeline_id}.py FROM Coda
EXTRACT error_messages, stack_traces, failed_checks
EXTRACT quality_score_before (baseline for comparison)
LOG "Contexto carregado: {n} erros, score baseline: {score}"
```

### Step 2: Parse Stack Trace

```
FOR EACH error IN error_messages:
  PARSE stack_trace to extract:
    - file_name
    - line_number
    - function_name
    - error_class (e.g., TypeError, ValueError, AnalysisException)
    - error_message_text
  EXTRACT code_snippet around error location (±5 lines)
  LOG "Erro #{i}: {error_class} em {file_name}:{line_number}"
```

### Step 3: Match Against Known Patterns

```
LOAD known_patterns FROM core-config.yaml
LOAD learned_patterns FROM MLflow registry

FOR EACH parsed_error:
  CALCULATE similarity_score against each known pattern:
    - error_class match (exact)
    - error_message pattern match (regex)
    - code context similarity (embedding)
  
  IF best_match.similarity >= 0.85:
    CLASSIFY as "KNOWN" pattern
    SET pattern_id = best_match.id
    SET confidence = best_match.similarity
    SET recommended_fix = best_match.fix_template
    LOG "✅ Pattern conhecido: {pattern_id} (confiança: {confidence})"
  ELSE:
    CLASSIFY as "NOVEL" error
    LOG "⚠️ Erro novo detectado — acionando LLM para análise"
```

### Step 4: Root Cause Analysis (LLM for Novel Errors)

```
IF error.classification == "NOVEL":
  PREPARE context:
    - Full error message and stack trace
    - Code snippet around error (±20 lines)
    - Pipeline purpose and business logic (from pseudocode if available)
    - Target platform constraints (Databricks/PySpark)
  
  PROMPT LLM:
    "Analyze this migration error. Identify:
     1. Root cause (why this error occurs)
     2. Error category (type_mismatch|null_handling|sql_syntax|etc.)
     3. Blast radius (what else might be affected)
     4. Recommended fix approach
     5. Confidence level (0.0–1.0)"
  
  PARSE LLM response
  SET root_cause = llm.root_cause
  SET blast_radius = llm.blast_radius
  LOG "🔍 Root cause (LLM): {root_cause}"
```

### Step 5: Generate Diagnosis Report

```
CREATE diagnosis_report:
  pipeline_id: {pipeline_id}
  timestamp: {now}
  total_errors: {count}
  errors:
    - id: error_{i}
      classification: KNOWN | NOVEL
      pattern_id: {pattern_id} | null
      error_class: {error_class}
      root_cause: {root_cause}
      blast_radius: {blast_radius}
      confidence: {confidence}
      recommended_strategy: rule_based | llm_repair
      recommended_fix: {fix_template} | {llm_suggestion}
  
  overall_assessment:
    complexity: LOW | MEDIUM | HIGH
    estimated_fix_time: {minutes}
    auto_fixable: true | false
    recommended_first_attempt: {strategy}

SAVE diagnosis to healing-logs/{pipeline_id}_diagnosis.json
LOG "📋 Diagnóstico completo: {total_errors} erros, {known_count} conhecidos, {novel_count} novos"
```

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `healing-logs/{pipeline_id}_diagnosis.json` | JSON | Complete diagnosis with classifications and recommendations |
| Console summary | Text | Summary of findings for user review |

---

## Error Classification Reference

| Pattern ID | Error Class | Regex Pattern | Example |
|------------|------------|---------------|---------|
| type_mismatch | TypeError, AnalysisException | `cannot resolve.*due to data type mismatch` | DATE vs STRING |
| null_handling | NullPointerException | `NoneType.*has no attribute` | Missing .isNotNull() |
| sql_syntax | AnalysisException | `syntax error in SQL` | BODS SQL → Spark SQL |
| import_missing | ModuleNotFoundError | `No module named` | Missing pyspark.sql.functions |
| column_not_found | AnalysisException | `cannot resolve.*column` | Column name typo |
| partition_error | AnalysisException | `partition.*not found\|repartition` | Bad partition key |
| schema_evolution | AnalysisException | `schema.*mismatch\|merge.*schema` | Added/removed column |
| encoding_error | UnicodeDecodeError | `codec can't decode` | Latin-1 vs UTF-8 |
| date_format | ValueError | `time data.*does not match format` | DD/MM/YYYY vs YYYY-MM-DD |
| join_condition | AnalysisException | `join.*condition.*type` | INT join STRING key |

---

## Decision Tree

```
Error Received
├── Parse stack trace
├── Match known patterns (≥ 0.85 similarity)?
│   ├── YES → KNOWN classification
│   │   └── Recommend rule_based fix (Attempt 1)
│   └── NO → NOVEL classification
│       └── LLM root cause analysis
│           ├── LLM confidence ≥ 0.7?
│           │   ├── YES → Recommend llm_repair (Attempt 2 strategy)
│           │   └── NO → Flag as HIGH complexity, recommend escalation watch
│           └── Assess blast radius
└── Generate diagnosis report
```
