# Apply Fix Task

**Task ID:** apply-fix  
**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0  
**Command:** `*fix`  
**Phase:** DOWNSTREAM

---

## Purpose

Apply a fix to rejected pipeline code based on the diagnosis. Uses a progressive strategy: Attempt 1 = rule-based, Attempt 2 = LLM with alternative prompt, Attempt 3 = LLM with different model. Always applies the minimal diff approach (smallest possible change).

---

## Prerequisites

- Diagnosis report completed (`healing-logs/{pipeline_id}_diagnosis.json`)
- Original generated code available (`generated-code/{pipeline_id}.py`)
- Known pattern registry loaded from MLflow

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | Yes | Pipeline identifier |
| attempt_number | int | No | Current attempt (1–3, default: auto-detect) |
| force_strategy | string | No | Override strategy: rule_based, llm_alternative_prompt, llm_different_model |
| dry_run | bool | No | Preview fix without applying (default: false) |

---

## Execution Steps

### Step 1: Load Context

```
LOAD diagnosis FROM healing-logs/{pipeline_id}_diagnosis.json
LOAD original_code FROM generated-code/{pipeline_id}.py
LOAD attempt_history FROM healing-logs/{pipeline_id}_attempts.json (if exists)

DETERMINE current_attempt:
  IF attempt_history exists:
    current_attempt = len(attempt_history) + 1
  ELSE:
    current_attempt = 1

IF current_attempt > 3:
  LOG "❌ Máximo de 3 tentativas atingido. Escalando para Orion 🧭"
  TRIGGER escalation to migration-coordinator
  RETURN escalation_report
```

### Step 2: Select Fix Strategy

```
MATCH current_attempt:
  CASE 1 → strategy = "rule_based"
    LOG "🔧 Tentativa #1: Fix baseado em regras"
    LOAD fix_template FROM known_patterns[diagnosis.pattern_id]
    
  CASE 2 → strategy = "llm_alternative_prompt"
    LOG "🔧 Tentativa #2: LLM com prompt alternativo"
    PREPARE repair_prompt with:
      - Original code
      - Error details from diagnosis
      - Previous attempt #1 result (why it failed)
      - Specific repair instructions
    
  CASE 3 → strategy = "llm_different_model"
    LOG "🔧 Tentativa #3: LLM com modelo diferente"
    PREPARE repair_prompt with:
      - Full context (code + errors + previous attempts)
      - Request for creative/alternative approach
    SELECT stronger_model (e.g., GPT-4o if prior was GPT-4-mini)
```

### Step 3: Apply Fix (Rule-Based — Attempt 1)

```
IF strategy == "rule_based":
  MATCH diagnosis.pattern_id:
    
    CASE "type_mismatch":
      IDENTIFY source_type, target_type from error
      INSERT appropriate cast/conversion:
        col(field).cast(target_type)
      
    CASE "null_handling":
      IDENTIFY affected_columns
      ADD null checks:
        .filter(col(field).isNotNull())
        OR coalesce(col(field), lit(default_value))
      
    CASE "sql_syntax":
      IDENTIFY BODS-specific SQL constructs
      REWRITE to Spark SQL equivalent
      
    CASE "import_missing":
      IDENTIFY missing_module from error
      ADD import statement at file top
      
    CASE "column_not_found":
      LOAD schema mapping
      REPLACE incorrect column name with correct mapping
      
    CASE "partition_error":
      ANALYZE partition strategy
      FIX repartition/coalesce parameters
      
    CASE "schema_evolution":
      ADD .option("mergeSchema", "true")
      OR ADD explicit schema definition
      
    CASE "encoding_error":
      ADD .option("encoding", "UTF-8")
      OR ADD explicit encoding conversion
      
    CASE "date_format":
      INSERT to_date/to_timestamp with correct format
      
    CASE "join_condition":
      ADD explicit cast on join keys to match types

  GENERATE diff (original vs fixed)
  VALIDATE diff is minimal (≤ 20 lines changed)
```

### Step 4: Apply Fix (LLM-Based — Attempts 2 & 3)

```
IF strategy IN ["llm_alternative_prompt", "llm_different_model"]:
  
  CONSTRUCT prompt:
    "You are a PySpark migration expert. Fix the following code error.
     
     ORIGINAL CODE:
     {original_code}
     
     ERROR:
     {diagnosis.error_details}
     
     ROOT CAUSE:
     {diagnosis.root_cause}
     
     PREVIOUS ATTEMPTS (if any):
     {attempt_history}
     
     CONSTRAINTS:
     - Apply MINIMAL changes only
     - Do NOT refactor unrelated code
     - Preserve all business logic
     - Maintain code style consistency
     - Return ONLY the fixed code section (not full file)
     
     RETURN FORMAT:
     ```python
     # Fixed code section
     ```
     EXPLANATION: Brief explanation of what was changed and why"
  
  IF strategy == "llm_different_model":
    USE model = "gpt-4o" (or stronger available model)
  ELSE:
    USE model = default_model
  
  CALL LLM with prompt
  PARSE response → fixed_code_section, explanation
  
  APPLY fixed_code_section to original_code:
    - Identify exact location in original code
    - Replace only the affected section
    - Preserve indentation and formatting
  
  GENERATE diff (original vs fixed)
  VALIDATE diff is reasonable (≤ 50 lines changed for LLM)
```

### Step 5: Create Backup & Save Fix

```
BACKUP original_code to healing-logs/{pipeline_id}_backup_attempt{n}.py
SAVE fixed_code to fixed-code/{pipeline_id}.py

LOG attempt record:
  attempt_number: {current_attempt}
  strategy: {strategy}
  pattern_id: {pattern_id}
  changes_made: {diff_summary}
  lines_changed: {count}
  timestamp: {now}

APPEND to healing-logs/{pipeline_id}_attempts.json

IF dry_run:
  DISPLAY diff for user review
  LOG "🔍 Dry run — nenhuma alteração aplicada. Revise o diff acima."
ELSE:
  LOG "✅ Fix aplicado (Tentativa #{current_attempt}). Execute *verify para re-validar."
```

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `fixed-code/{pipeline_id}.py` | Python | Fixed pipeline code |
| `healing-logs/{pipeline_id}_attempts.json` | JSON | Attempt history with diffs |
| `healing-logs/{pipeline_id}_backup_attempt{n}.py` | Python | Backup of code before fix |

---

## Fix Templates Reference

| Pattern | Fix Template | Example |
|---------|-------------|---------|
| type_mismatch | `col(f).cast(StringType())` | DATE → STRING |
| null_handling | `coalesce(col(f), lit(""))` | Add null safety |
| sql_syntax | Spark SQL rewrite | `NVL()` → `coalesce()` |
| import_missing | `from pyspark.sql.functions import X` | Add missing import |
| column_not_found | Column name mapping | `CUST_ID` → `customer_id` |
| partition_error | `.repartition(n, col(key))` | Fix partition strategy |
| schema_evolution | `.option("mergeSchema", "true")` | Handle schema drift |
| encoding_error | `.option("encoding", "UTF-8")` | Fix encoding |
| date_format | `to_date(col(f), "yyyy-MM-dd")` | Fix date parsing |
| join_condition | `col(a).cast(IntegerType()) == col(b)` | Match join key types |

---

## Guardrails

1. **Max diff size:** Rule-based ≤ 20 lines, LLM ≤ 50 lines. Larger diffs require human review.
2. **No business logic changes:** Fixes must NOT alter transformation semantics.
3. **Backup always:** Original code is always backed up before any modification.
4. **3-attempt limit:** After 3 attempts, mandatory escalation to Orion 🧭.
5. **Circuit breaker:** If 5 consecutive pipelines fail, pause and alert team.
