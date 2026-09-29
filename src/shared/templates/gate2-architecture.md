---
artifact: architecture
gate: 2
version: "1.0.0"
owner: DataArchitect
status: DRAFT
required_by: orchestrator.gate_criteria.gate_2
---

# Gate 2: Architecture

## Architecture Decision Summary

<!-- Diagram URL or embedded Mermaid block. -->

```mermaid
flowchart LR
    SRC[Source System] --> ING[Ingestion Layer]
    ING --> BRZ[Bronze / Raw]
    BRZ --> SLV[Silver / Standardized]
    SLV --> GLD[Gold / Curated]
    GLD --> CNS[Consumption Layer]
```

## Technology Stack

| Layer | Technology | Version | Justification |
| --- | --- | --- | --- |
| Orchestration | | | |
| Ingestion | | | |
| Storage | | | |
| Transformation | | | |
| Quality | | | |
| Serving | | | |

## Non-Functional Requirements

| NFR | Requirement | Design Response |
| --- | --- | --- |
| Scalability | | |
| Availability | | |
| Security | | |
| Recoverability | | |

## Integration Points

| System | Direction | Protocol | Auth |
| --- | --- | --- | --- |
| | | | |

## Approval

| Reviewer | Date | Status |
| --- | --- | --- |
| | | PENDING |
