# DataArchitect Checklist

**Agent:** DataArchitect  
**Phase:** MIDSTREAM  
**Gate:** Gate 2

---

## Pre-Architecture Checklist

### Prerequisites Verification

- [ ] Gate 1 passed (UPSTREAM complete)
- [ ] STTM document available
- [ ] Analytical questions defined
- [ ] KPIs and success criteria available
- [ ] Problem statement reviewed

### Context Understanding

- [ ] Business requirements understood
- [ ] Source systems identified
- [ ] Data volumes estimated
- [ ] Performance requirements clear
- [ ] Security/compliance requirements known

---

## Architecture Design Checklist

### Architecture Pattern

- [ ] Architecture pattern selected (Lakehouse/DW/Hybrid)
- [ ] Pattern selection justified
- [ ] Alternatives documented

### Data Layers

- [ ] Landing layer defined
- [ ] Bronze layer defined
- [ ] Silver layer defined
- [ ] Gold layer defined
- [ ] Layer transitions documented

### Technology Stack

- [ ] Storage technology selected
- [ ] Processing technology selected
- [ ] Orchestration technology selected
- [ ] Serving technology selected
- [ ] All selections justified

### Data Flow

- [ ] Ingestion patterns defined
- [ ] Transformation pipeline designed
- [ ] Serving patterns defined
- [ ] Refresh schedules specified

### Cross-Cutting Concerns

- [ ] Security approach documented
- [ ] Scalability strategy defined
- [ ] Monitoring approach specified
- [ ] DR/backup strategy defined

---

## Data Model Checklist

### Entity Design

- [ ] All required entities identified
- [ ] Entity relationships defined
- [ ] Cardinality specified
- [ ] SCD types determined

### Key Management

- [ ] Primary keys defined
- [ ] Business keys identified
- [ ] Foreign keys mapped
- [ ] Surrogate key strategy set

### Column Definitions

- [ ] All columns documented
- [ ] Data types appropriate
- [ ] Nullability specified
- [ ] Descriptions provided
- [ ] Source mappings complete

### Naming Conventions

- [ ] Table naming consistent
- [ ] Column naming consistent
- [ ] Convention documented

### Model Types

- [ ] Bronze tables defined
- [ ] Silver tables defined
- [ ] Gold fact tables defined
- [ ] Gold dimension tables defined
- [ ] Standard dimensions included (date, time)

---

## Decisions Checklist

### ADR Quality

- [ ] All major decisions documented
- [ ] Context clearly explained
- [ ] Alternatives listed
- [ ] Consequences stated (positive/negative)
- [ ] Status appropriate

### Coverage

- [ ] Technology selection ADRs
- [ ] Modeling approach ADR
- [ ] Processing strategy ADR
- [ ] Security model ADR
- [ ] Data quality approach ADR

### Governance

- [ ] ADRs numbered sequentially
- [ ] Related decisions linked
- [ ] Review schedule set

---

## Gate 2 Readiness Checklist

### Required Artifacts

- [ ] `architecture.md` complete
- [ ] `data-model.md` complete
- [ ] `decisions.md` complete
- [ ] `tobe-target-architecture.html` generated and saved to `projects/{project_name}/outputs/midstream/`
  - [ ] Opens in browser with no console errors
  - [ ] All 7 sections present (Header, Principles, Medallion, Tech Stack, SLAs, ADRs, Footer)
  - [ ] Light theme `#F7F8FA` rendered; Playfair Display + JetBrains Mono + Plus Jakarta Sans fonts loaded
  - [ ] Gradient header top border present (fabric → silver → gold → green)
  - [ ] Fabric blue `TO-BE Architecture` badge visible
  - [ ] All `{{PLACEHOLDER}}` tokens replaced with project decisions (none remaining)
  - [ ] Hover effects working on cards and table rows
  - [ ] Content consistent with `architecture.md`

### Quality Criteria

- [ ] Architecture supports all analytical questions
- [ ] Data model implements STTM requirements
- [ ] Decisions align with constraints
- [ ] Security requirements addressed
- [ ] Scalability requirements addressed

### Documentation Quality

- [ ] Diagrams included
- [ ] Tables formatted correctly
- [ ] No placeholder text remaining
- [ ] Version information present
- [ ] Author attributed

---

## Handoff Checklist

### For DataSteward

- [ ] Data quality checkpoints identified
- [ ] Governance requirements documented
- [ ] Data classification noted

### For DataFlow Agent

- [ ] DDL requirements clear
- [ ] ETL logic derivable from model
- [ ] Processing patterns specified

### For InsightForge Agent

- [ ] Semantic model requirements clear
- [ ] Measure definitions implied
- [ ] Hierarchy structures defined

---

## Sign-off

| Checkpoint | Status | Date | Notes |
|------------|--------|------|-------|
| Architecture Complete | ⬜ | | |
| Data Model Complete | ⬜ | | |
| Decisions Documented | ⬜ | | |
| Gate 2 Ready | ⬜ | | |

---

*Checklist maintained by DataArchitect Agent*
