# Learn Pattern Task

**Task ID:** learn-pattern  
**Agent:** Phoenix (Self-Healing)  
**Version:** 1.0  
**Command:** `*learn-pattern`  
**Phase:** DOWNSTREAM

---

## Purpose

After a successful fix: extract the error signature, generate a reusable fix pattern, and store it in the MLflow registry. Update the known patterns list so future occurrences of the same error can be fixed automatically via rule-based approach (Attempt 1).

---

## Prerequisites

- Fix successfully verified (`healing-logs/{pipeline_id}.json` with status = HEALED)
- Attempt history with diff details (`healing-logs/{pipeline_id}_attempts.json`)
- MLflow experiment configured (`self-healing-patterns`)

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| pipeline_id | string | Yes | Pipeline identifier |
| force_learn | bool | No | Learn even from partial fixes (default: false) |

---

## Execution Steps

### Step 1: Load Successful Fix Context

```
LOAD healing_log FROM healing-logs/{pipeline_id}.json
LOAD attempt_history FROM healing-logs/{pipeline_id}_attempts.json

FIND successful_attempt = attempt WHERE status == "HEALED"
IF NOT found AND NOT force_learn:
  LOG "⚠️ Nenhum fix bem-sucedido encontrado. Use --force-learn para forçar."
  RETURN

EXTRACT:
  error_signature = {
    error_class: diagnosis.error_class,
    error_message_pattern: regex_from(diagnosis.error_message),
    code_context_hash: hash(diagnosis.code_snippet),
    pipeline_type: diagnosis.pipeline_type
  }
  
  fix_pattern = {
    strategy_used: successful_attempt.strategy,
    diff: successful_attempt.diff,
    lines_changed: successful_attempt.lines_changed,
    fix_description: successful_attempt.explanation
  }

LOG "📚 Extraindo padrão do fix bem-sucedido (Tentativa #{successful_attempt.number})"
```

### Step 2: Generate Error Signature

```
CREATE error_signature:
  id: auto_generate (e.g., "pattern_2026_0213_001")
  category: diagnosis.pattern_id OR "novel_{error_class}"
  
  matching_criteria:
    error_class: {exact_match}
    message_regex: {extracted_regex_pattern}
    code_context:
      - function_type: {e.g., "join", "filter", "groupBy"}
      - data_types_involved: {e.g., ["StringType", "DateType"]}
      - spark_api: {e.g., "DataFrame.join"}
  
  severity: {original_severity}
  frequency: 1  # first occurrence
  
LOG "🔑 Signature gerada: {error_signature.id}"
```

### Step 3: Generate Fix Template

```
ANALYZE successful diff:
  EXTRACT transformation_type:
    - addition (new code added)
    - replacement (code swapped)
    - deletion (code removed)
    - wrapping (code wrapped in new construct)
  
  GENERALIZE fix:
    REPLACE specific column names → {column_placeholder}
    REPLACE specific data types → {source_type}, {target_type}
    REPLACE specific values → {default_value}
    KEEP structural pattern intact

CREATE fix_template:
  id: {error_signature.id}_fix
  transformation: {transformation_type}
  template: |
    # Generalized fix template
    {generalized_code_pattern}
  parameters:
    - name: {param_1}
      type: {type}
      description: {desc}
  
  applicability:
    min_confidence: 0.85
    pre_conditions: [{conditions_for_template_to_apply}]
    contraindications: [{when_NOT_to_apply}]

LOG "📝 Template de fix gerado: {fix_template.id}"
```

### Step 4: Store in MLflow

```
CONNECT to MLflow experiment "self-healing-patterns"

LOG experiment run:
  run_name: "learn_{pipeline_id}_{timestamp}"
  
  parameters:
    pattern_id: {error_signature.id}
    error_class: {error_class}
    strategy_used: {strategy}
    attempt_number: {successful_attempt.number}
  
  metrics:
    fix_success: 1.0
    time_to_fix_seconds: {elapsed}
    lines_changed: {count}
    score_improvement: {score_delta}
    regression_detected: 0
  
  artifacts:
    - error_signature.json
    - fix_template.json
    - diff.patch
    - before_code.py
    - after_code.py
  
  tags:
    agent: "phoenix"
    phase: "downstream"
    pipeline: {pipeline_id}
    category: {error_category}

LOG "📦 Padrão armazenado no MLflow (run: {run_id})"
```

### Step 5: Update Known Patterns Registry

```
LOAD current known_patterns FROM core-config.yaml

IF error_signature.category NOT IN known_patterns:
  # New pattern discovered!
  APPEND to known_patterns:
    - id: {error_signature.category}
      description: {auto_generated_description}
      severity: {severity}
      auto_fix_rate: {initial_rate}  # starts at 1.0 for first success
      fix_template: {fix_template.id}
  
  LOG "🆕 Novo padrão adicionado ao registry: {category}"
ELSE:
  # Existing pattern — update success rate
  UPDATE known_patterns[category]:
    auto_fix_rate = recalculate(total_successes / total_attempts)
    last_updated: {now}
  
  LOG "📊 Padrão existente atualizado: {category} (taxa: {auto_fix_rate})"

# Check for auto-promotion
IF pattern was LLM-fixed AND cumulative_success_rate >= 0.90:
  PROMOTE pattern to rule_based:
    CREATE deterministic fix template from generalized LLM fixes
  LOG "⬆️ Padrão promovido para rule-based! (taxa: {success_rate})"
```

### Step 6: Save Learning Summary

```
SAVE to learned-patterns/{error_signature.id}.json:
  signature: {error_signature}
  template: {fix_template}
  mlflow_run_id: {run_id}
  learned_from: {pipeline_id}
  learned_at: {timestamp}
  promoted_to_rule: {boolean}

LOG "✅ Aprendizado concluído. Padrão disponível para futuros fixes."
```

### Step 7: Automatic Pattern Mining via Headroom (if available)

```
7.1  CHECK if headroom is available: headroom --version
7.2  IF available:
     RUN headroom learn --dry-run --config .headroom/learn-config.yaml
     REVIEW suggested corrections
     IF corrections are relevant to current failure:
       RUN headroom learn --apply --config .headroom/learn-config.yaml
       LOG "headroom learn applied N corrections to agent files"
7.3  ALWAYS: write manual learnings to learn-patterns.md as per existing steps
```

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `learned-patterns/{pattern_id}.json` | JSON | Error signature + fix template |
| MLflow experiment run | MLflow | Tracked metrics, parameters, artifacts |
| Updated known patterns | Config | Core config updated with new/improved patterns |

---

## Auto-Promotion Criteria

| Metric | Threshold | Action |
|--------|-----------|--------|
| Cumulative success rate | ≥ 90% | Promote LLM fix → rule-based |
| Minimum occurrences | ≥ 5 | Required before promotion evaluation |
| Zero regressions | 0 | No regressions in any application |
| Consistent fix template | ≥ 80% similarity | Fix approach is stable across occurrences |
