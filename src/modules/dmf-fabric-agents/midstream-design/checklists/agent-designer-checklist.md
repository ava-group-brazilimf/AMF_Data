# AgentDesigner Checklist

**Agent:** AgentDesigner (Nova)  
**Phase:** MIDSTREAM  
**Gate:** Gate 2

---

## Pre-Design Checklist

### Prerequisites Verification

- [ ] Project context understood
- [ ] Architecture document available
- [ ] Workflow requirements identified
- [ ] Stakeholders mapped
- [ ] Risk assessment complete

### Context Understanding

- [ ] Business goals clear
- [ ] Automation requirements understood
- [ ] Human oversight needs identified
- [ ] Integration points mapped
- [ ] Constraints documented

---

## Agent Blueprint Checklist

### Agent Identification

- [ ] All required agents identified
- [ ] Agent personas defined
- [ ] Roles and responsibilities clear
- [ ] Boundaries established

### Agent Capabilities

- [ ] Tools specified for each agent
- [ ] Commands documented
- [ ] Input requirements defined
- [ ] Output specifications clear

### Agent Behavior

- [ ] Activation instructions written
- [ ] Greeting behavior defined
- [ ] Error handling specified
- [ ] Escalation triggers identified

---

## Agent Contracts Checklist

### Input Contracts

- [ ] All inputs documented
- [ ] Required vs optional inputs clear
- [ ] Validation rules specified
- [ ] Source agents identified

### Output Contracts

- [ ] All outputs documented
- [ ] Format specifications clear
- [ ] Quality criteria defined
- [ ] Target agents identified

### Handoff Protocols

- [ ] Handoff triggers defined
- [ ] Data transfer format specified
- [ ] Confirmation requirements clear
- [ ] Rollback procedures documented

### Error Handling

- [ ] Error types identified
- [ ] Retry policies defined
- [ ] Fallback strategies documented
- [ ] Escalation paths clear

---

## Guardrails Checklist

### Gate Definitions

- [ ] Gate 1 criteria defined
- [ ] Gate 2 criteria defined
- [ ] Gate 3 criteria defined
- [ ] Validation rules specified

### Autonomy Levels

- [ ] Level 1 (Assisted) tasks identified
- [ ] Level 2 (Supervised) tasks identified
- [ ] Level 3 (Monitored) tasks identified
- [ ] Level 4 (Autonomous) tasks identified

### Human-in-the-Loop

- [ ] Approval triggers defined
- [ ] Review checkpoints identified
- [ ] Override mechanisms documented
- [ ] Audit requirements specified

---

## Orchestration Flow Checklist

### Flow Design

- [ ] Execution sequence documented
- [ ] Parallel paths identified
- [ ] Sequential dependencies mapped
- [ ] Conditional branches defined

### Decision Points

- [ ] Decision criteria clear
- [ ] Branch conditions documented
- [ ] Default paths specified
- [ ] Timeout handling defined

### Escalation Paths

- [ ] Escalation triggers defined
- [ ] Escalation targets identified
- [ ] Communication channels specified
- [ ] Resolution workflows documented

---

## Quality Checklist

### Design Quality

- [ ] No circular dependencies
- [ ] No orphan agents
- [ ] All agents have contracts
- [ ] All contracts have validation

### Documentation Quality

- [ ] All agents described
- [ ] All contracts documented
- [ ] Diagrams included
- [ ] Examples provided

### Alignment

- [ ] Design aligns with architecture
- [ ] Design supports requirements
- [ ] Design enables KPIs
- [ ] Risk mitigations adequate

---

## Gate 2 Readiness

### Required Artifacts

- [ ] agent-blueprint.md complete
- [ ] agent-contracts.md complete
- [ ] orchestration-flow.md complete

### Validation

- [ ] Design reviewed by Architect
- [ ] Contracts reviewed by Engineer
- [ ] Flow reviewed by Orchestrator
- [ ] No critical gaps identified

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| AgentDesigner | Nova | | ⬜ |
| DataArchitect | Winston | | ⬜ |
| Orchestrator | Orion | | ⬜ |
