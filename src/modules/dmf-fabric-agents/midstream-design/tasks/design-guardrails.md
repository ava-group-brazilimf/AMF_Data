# Task: Design Guardrails

**Command:** `*guardrails`  
**Output:** Updates to orchestration-flow.md, autonomy-matrix section

---

## Objective

Design comprehensive guardrails including gates, autonomy levels, and human-in-the-loop triggers to ensure safe and effective agent operation.

---

## Prerequisites

- [ ] Agent blueprint complete
- [ ] Agent contracts defined
- [ ] Risk assessment done

---

## Steps

### Step 1: Define Gate Criteria

For each gate, define:

```yaml
gate:
  id: "gate-{number}"
  name: "{Gate Name}"
  phase_transition: "{from_phase} → {to_phase}"
  
  criteria:
    required:
      - artifact: "{artifact}.md"
        owner: "{agent}"
        validation: "{validation_type}"
        
    quality:
      - metric: "completeness"
        threshold: 100%
        
      - metric: "validation_score"
        threshold: 90%
        
  validators:
    - agent: "{validating_agent}"
    - human: "{human_role}"  # if required
    
  on_fail:
    action: "return_to_previous"
    notify: ["{agents}"]
```

### Step 2: Create Autonomy Matrix

Map tasks to autonomy levels:

| Task | Risk Level | Autonomy | Human Role |
|------|------------|----------|------------|
| Generate PRD | Medium | Level 2 | Approve |
| Create DDL | Medium | Level 2 | Review |
| Run tests | Low | Level 3 | Audit |
| Deploy | High | Level 1 | Decide |

### Step 3: Define Human-in-the-Loop Triggers

Specify when human intervention is required:

```yaml
hitl_triggers:
  confidence:
    threshold: 80%
    action: "require_approval"
    
  critical_decisions:
    - type: "schema_change"
      action: "require_approval"
      approver: "tech_lead"
      
    - type: "production_deploy"
      action: "require_approval"
      approver: "release_manager"
      
  errors:
    - type: "repeated_failure"
      count: 3
      action: "escalate"
      
  scheduled:
    - event: "gate_transition"
      action: "checkpoint_review"
```

### Step 4: Design Override Mechanisms

Define how humans can override agents:

```yaml
overrides:
  abort:
    command: "*abort"
    effect: "stop_all_agents"
    cleanup: true
    
  pause:
    command: "*pause"
    effect: "suspend_processing"
    resume: "*resume"
    
  skip:
    command: "*skip {step}"
    effect: "bypass_step"
    require_reason: true
    
  force:
    command: "*force {action}"
    effect: "override_validation"
    audit_log: true
```

### Step 5: Document Guardrails

Add to orchestration-flow.md:
- Gate definitions with criteria
- Autonomy matrix
- HITL triggers
- Override mechanisms

---

## Validation

- [ ] All gates have clear criteria
- [ ] All tasks have autonomy levels
- [ ] HITL triggers cover risks
- [ ] Override mechanisms documented
- [ ] Audit trail enabled
