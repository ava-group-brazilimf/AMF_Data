# Task: Create Agent Contracts

**Command:** `*agent-contracts` / `*AC`  
**Output:** `agent-contracts.md`

---

## Objective

Define formal contracts between agents specifying inputs, outputs, handoffs, and error handling.

---

## Prerequisites

- [ ] Agent blueprint complete
- [ ] Dependencies identified
- [ ] Data flows mapped

---

## Steps

### Step 1: Identify All Interactions

Map every agent-to-agent interaction:

| From Agent | To Agent | Artifact | Purpose |
|------------|----------|----------|---------|
| Strategist | Analyst | problem-statement.md | Context |
| Analyst | Architect | sttm.md | Requirements |

### Step 2: Define Input Contracts

For each agent, document required inputs:

```yaml
agent_id: "{agent}"

inputs:
  required:
    - artifact: "{name}.md"
      from_agent: "{source_agent}"
      description: "{what it contains}"
      validation:
        - rule: "exists"
        - rule: "schema_valid"
        - rule: "sections_present"
          sections: ["overview", "details"]
      freshness: "< 24 hours"
      
  optional:
    - artifact: "{name}.md"
      from_agent: "{source_agent}"
      description: "{what it provides}"
      default_behavior: "proceed without"
```

### Step 3: Define Output Contracts

For each agent, document outputs:

```yaml
outputs:
  - artifact: "{name}.md"
    to_agents: ["{target_1}", "{target_2}"]
    description: "{what it contains}"
    format: "markdown"
    sections:
      required:
        - "Overview"
        - "Details"
      optional:
        - "Appendix"
    quality:
      completeness: 100%
      validation: "checklist_pass"
```

### Step 4: Define Handoff Protocols

Specify how handoffs work:

```yaml
handoff:
  trigger: "{condition}"
  method: "direct|via_orchestrator"
  
  data_transfer:
    format: "markdown|yaml|json"
    location: "docs/{folder}/"
    
  confirmation:
    required: true
    method: "status_update|notification"
    
  rollback:
    enabled: true
    method: "restore_previous"
```

### Step 5: Define Error Handling

Specify error responses:

```yaml
error_handling:
  on_missing_input:
    action: "request|skip|default"
    notify: ["{agent}", "orchestrator"]
    
  on_validation_failure:
    action: "retry|escalate"
    retry_count: 3
    escalate_to: "orchestrator"
    
  on_timeout:
    threshold: "30 minutes"
    action: "notify|escalate"
    
  fallback:
    enabled: true
    strategy: "default_output|human_takeover"
```

### Step 6: Document All Contracts

Create `agent-contracts.md` with all contracts organized by agent.

---

## Output Template

```markdown
# Agent Contracts

## Overview
[Summary of contract system]

## Contract Matrix

| Agent | Inputs From | Outputs To |
|-------|------------|------------|
| {agent} | {sources} | {targets} |

## Detailed Contracts

### {Agent Name}

#### Inputs
[Input contract YAML]

#### Outputs
[Output contract YAML]

#### Handoff Protocol
[Handoff YAML]

#### Error Handling
[Error YAML]

[Repeat for each agent]

## Error Escalation Flow
[Mermaid diagram]
```

---

## Validation

- [ ] All agents have contracts
- [ ] All inputs have sources
- [ ] All outputs have targets
- [ ] Error handling complete
- [ ] No orphan artifacts
