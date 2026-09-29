# Orchestration Flow Template

## Flow Overview

**Project:** {project_name}  
**Version:** {version}  
**Last Updated:** {date}  
**Owner:** Nova (AgentDesigner)

---

## Executive Summary

| Aspect | Value |
|--------|-------|
| Total Phases | 4 (UPSTREAM, MIDSTREAM, DOWNSTREAM, CORE) |
| Total Gates | 3 |
| Human Checkpoints | {count} |
| Estimated Duration | {time} |

---

## Main Orchestration Flow

```mermaid
flowchart TB
    START([🚀 Project Start]) --> GATE0{Gate 0<br>Kickoff}
    
    GATE0 -->|Pass| UP1[🎯 Alex<br>Problem Statement]
    UP1 --> UP2[📋 Mary<br>Requirements]
    
    UP2 --> GATE1{Gate 1<br>Discovery Complete}
    
    GATE1 -->|Pass| MID1[🏛️ Winston<br>Architecture]
    GATE1 -->|Fail| UP2
    
    MID1 --> MID2[🧩 Sofia<br>Data Model]
    MID2 --> MID3[🧠 Nova<br>Agent Design]
    
    MID3 --> GATE2{Gate 2<br>Design Complete}
    
    GATE2 -->|Pass| DOWN1[🛠️ Diego<br>Implementation]
    GATE2 -->|Fail| MID1
    
    DOWN1 --> DOWN2[📊 Bianca<br>BI Layer]
    DOWN1 --> DOWN3[🛡️ Gaia<br>Data Quality]
    
    DOWN2 --> GATE3{Gate 3<br>Ready for Prod}
    DOWN3 --> GATE3
    
    GATE3 -->|Pass| PROD([✅ Production])
    GATE3 -->|Fail| DOWN4[🔁 Kai<br>Improvement]
    DOWN4 --> DOWN1
    
    ORCH[🧭 Orion<br>Orchestrator] -.->|monitors| UP1
    ORCH -.->|monitors| MID1
    ORCH -.->|monitors| DOWN1
```

---

## Detailed Phase Flows

### UPSTREAM Phase

```mermaid
flowchart LR
    A[Start] --> B[Alex: Problem Statement]
    B --> C{Approved?}
    C -->|No| B
    C -->|Yes| D[Alex: KPIs]
    D --> E[Mary: Requirements]
    E --> F[Mary: STTM]
    F --> G[Mary: Analytical Questions]
    G --> H{Gate 1}
    H -->|Pass| I[To MIDSTREAM]
    H -->|Fail| E
```

**Checkpoints:**
| Step | Autonomy | Human Action |
|------|----------|--------------|
| Problem Statement | Level 2 | Review & Approve |
| KPIs | Level 2 | Review & Approve |
| Requirements | Level 2 | Validate |
| STTM | Level 3 | Audit |

---

### MIDSTREAM Phase

```mermaid
flowchart LR
    A[From Gate 1] --> B[Winston: Architecture]
    B --> C{ADR Approved?}
    C -->|No| B
    C -->|Yes| D[Sofia: Data Model]
    D --> E[Sofia: Contracts]
    E --> F[Nova: Agent Blueprint]
    F --> G[Nova: Orchestration]
    G --> H{Gate 2}
    H -->|Pass| I[To DOWNSTREAM]
    H -->|Fail| B
```

**Checkpoints:**
| Step | Autonomy | Human Action |
|------|----------|--------------|
| Architecture | Level 2 | Review ADRs |
| Data Model | Level 3 | Audit |
| Agent Blueprint | Level 2 | Approve |

---

### DOWNSTREAM Phase

```mermaid
flowchart TB
    A[From Gate 2] --> B[Diego: DDL Creation]
    B --> C[Diego: ETL Development]
    C --> D[Diego: Unit Tests]
    
    D --> E{Tests Pass?}
    E -->|No| C
    E -->|Yes| F[Parallel Execution]
    
    F --> G[Bianca: Semantic Model]
    F --> H[Gaia: DQ Validation]
    
    G --> I{Gate 3}
    H --> I
    
    I -->|Pass| J[Production]
    I -->|Fail| K[Kai: Improvement]
    K --> C
```

---

## Gate Definitions

### Gate 0: Kickoff

| Criteria | Required | Validator |
|----------|----------|-----------|
| Project charter signed | Yes | PM |
| Resources allocated | Yes | Delivery Lead |
| Access granted | Yes | Admin |

### Gate 1: Discovery Complete

| Criteria | Required | Validator |
|----------|----------|-----------|
| problem-statement.md exists | Yes | Alex |
| kpis.md approved | Yes | Stakeholder |
| sttm.md complete | Yes | Mary |
| analytical-questions.md done | Yes | Mary |
| Checklist 100% | Yes | Orchestrator |

### Gate 2: Design Complete

| Criteria | Required | Validator |
|----------|----------|-----------|
| architecture.md approved | Yes | Winston |
| data-model.md complete | Yes | Sofia |
| agent-blueprint.md done | Yes | Nova |
| All ADRs documented | Yes | Winston |
| Checklist 100% | Yes | Orchestrator |

### Gate 3: Production Ready

| Criteria | Required | Validator |
|----------|----------|-----------|
| All tests passing | Yes | Diego |
| DQ validation > 95% | Yes | Gaia |
| Semantic model working | Yes | Bianca |
| Documentation complete | Yes | All |
| Security review done | Yes | Security |

---

## Decision Points

### Decision Point 1: Architecture Pattern

```mermaid
flowchart TD
    A[Evaluate Data Volume] --> B{Volume?}
    B -->|< 1GB| C[Simple ETL]
    B -->|1-100GB| D[Batch Processing]
    B -->|> 100GB| E[Distributed Processing]
```

**Decision Maker:** Winston (DataArchitect)  
**Escalation:** Human Architect

### Decision Point 2: Error Recovery

```mermaid
flowchart TD
    A[Error Detected] --> B{Severity?}
    B -->|Low| C[Auto-retry]
    B -->|Medium| D[Checkpoint & Notify]
    B -->|High| E[Stop & Escalate]
```

**Decision Maker:** Orchestrator (Orion)  
**Escalation:** Delivery Lead

---

## Escalation Paths

```mermaid
flowchart TD
    A[Issue Detected] --> B{Can Agent Resolve?}
    B -->|Yes| C[Agent Handles]
    B -->|No| D[Escalate to Orchestrator]
    D --> E{Can Orchestrator Resolve?}
    E -->|Yes| F[Orchestrator Handles]
    E -->|No| G[Escalate to Human]
    G --> H{Resolution Type}
    H -->|Technical| I[Tech Lead]
    H -->|Business| J[Product Owner]
    H -->|Process| K[Delivery Lead]
```

---

## Monitoring & Metrics

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Gate Pass Rate | > 90% | < 75% |
| Average Cycle Time | < 2 weeks | > 3 weeks |
| Rework Rate | < 10% | > 20% |
| DQ Score | > 95% | < 90% |

### Health Checks

- [ ] All agents responsive
- [ ] No blocked artifacts
- [ ] Gates functioning
- [ ] Escalation paths clear
- [ ] Metrics collecting
