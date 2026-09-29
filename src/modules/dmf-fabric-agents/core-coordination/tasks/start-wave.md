# Start Wave Task

**Task ID:** start-wave  
**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0  
**Command:** `*start-wave`  
**Phase:** CORE

---

## Purpose

Initialize and execute a migration wave, selecting pipelines, resolving dependencies, configuring parallelism, and triggering the agent pipeline.

---

## Prerequisites

- Migration plan (migration-plan.md) approved by PM
- Source and target connections validated
- All agents operational and configured
- `wave-config.yaml` validated by `validate_wave_config.py`
- `project_name` identifies the canonical folder below `projects/`
- `context/project-config.yaml` and `context/agent-task-config.yaml` exist in that project

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| wave_id | string | Yes | Wave identifier (e.g., wave_1_pilot) |
| pipeline_ids | list | Yes | Pipeline IDs to include in this wave |
| strategy | string | Yes | Execution strategy: sequential, parallel, hybrid |
| parallelism | int | No | Max parallel workers (default: 5) |
| wave_config_path | path | Yes | Explicit path to the wave config selected by the user/coordinator |

---

## Execution Steps

### Step 1: Validate Wave Configuration

```
REQUIRE wave_config_path; never discover wave-config.yaml by filename alone
RUN .\.venv\Scripts\python.exe -m src.shared.scripts.validate_wave_config <wave_config_path>
ABORT if validation fails
LOAD project_name from wave-config.yaml
RESOLVE project_root = <repository_root>/projects/{project_name}
RESOLVE context_root from context_base_path (default: {project_root}/context)
RESOLVE outputs_root from outputs_base_path (default: {project_root}/outputs)
LOAD context_root/project-config.yaml
LOAD context_root/agent-task-config.yaml
VERIFY project_name matches in all three configuration files
PROPAGATE project_root, context_root, outputs_root, wave_id and trace_id to every delegated agent
FORBID writes outside outputs_root during this wave
CHECK wave_id is unique (not previously executed)
CHECK all pipeline_ids exist in inventory.json
CHECK no pipeline_id is in another active wave
LOAD complexity classification for each pipeline
CALCULATE estimated execution time
```

### Step 2: Resolve Dependencies

```
LOAD dependency-graph.json from Scout
FOR EACH pipeline in wave:
  RESOLVE upstream dependencies
  VERIFY all dependencies are either:
    - Already migrated (in previous wave)
    - Included in this wave (will be processed first)
  IF unresolved dependencies:
    WARN and ask for confirmation
BUILD execution DAG (topological sort)
```

### Step 3: Configure Execution

```
SET parallelism based on strategy
CONFIGURE Celery workers
INITIALIZE Redis state for wave tracking
CREATE wave entry in Migration Control DB
SET wave status = "initialized"
```

### Step 4: Execute Pipeline Loop

```
FOR EACH pipeline in execution_order:
  1. Trigger Scout 🔍 → scan pipeline metadata
  2. Trigger Logan 🧠 → extract business logic
  3. Trigger Coda ⚙️ → generate target code
  4. Trigger Vera ✅ → validate code quality
  5. IF Vera rejects:
     Trigger Phoenix 🔧 → attempt fix (max 3x)
     Re-trigger Vera ✅
  6. Trigger Shield 🔒 → check compliance
  7. IF Shield rejects:
     Trigger Phoenix 🔧 → apply masking/fix
  8. Deploy to target platform
  9. UPDATE pipeline status in Control DB
```

### Step 5: Post-Wave Actions

```
Trigger Balance ⚖️ → reconcile wave data
Trigger Scribe 📚 → generate wave documentation
GENERATE wave-status-report using template
UPDATE wave status = "completed" or "completed_with_issues"
NOTIFY stakeholders
```

---

## Output

Generate the wave execution report under `{outputs_root}/summary/` using
`wave-status-report-tmpl.md`. All delegated tasks must read inputs from
`{context_root}` and write artifacts below `{outputs_root}`.
