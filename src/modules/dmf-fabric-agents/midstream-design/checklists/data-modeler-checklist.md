# DataModeler Checklist

**Agent:** DataModeler (Sofia)  
**Phase:** MIDSTREAM  
**Gate:** Gate 2

---

## Pre-Modeling Checklist

### Prerequisites Verification

- [ ] Gate 1 passed (UPSTREAM complete)
- [ ] STTM document available
- [ ] Architecture document available
- [ ] KPIs and success criteria available
- [ ] Analytical questions defined

### Context Understanding

- [ ] Business requirements understood
- [ ] Source entities identified
- [ ] Target entities clear
- [ ] Metrics requirements known
- [ ] Data granularity requirements clear

---

## Data Model Checklist

### Entity Identification

- [ ] All fact tables identified
- [ ] All dimension tables identified
- [ ] Bridge tables identified (if needed)
- [ ] Reference tables identified

### Granularity Definition

- [ ] Fact table grain defined
- [ ] Dimension grain defined
- [ ] Landing layer grain defined
- [ ] Silver layer grain defined
- [ ] Gold layer grain defined

### Key Management

- [ ] Primary keys defined for all tables
- [ ] Foreign keys defined
- [ ] Surrogate keys strategy defined
- [ ] Natural keys documented

### Relationships

- [ ] All relationships mapped
- [ ] Cardinality specified (1:1, 1:N, N:M)
- [ ] Relationship type defined (identifying/non-identifying)
- [ ] Bridge tables for M:N relationships

### SCD Types

- [ ] SCD Type 1 tables identified
- [ ] SCD Type 2 tables identified
- [ ] SCD Type 3 tables identified (if any)
- [ ] Historical tracking requirements met

### Naming Conventions

- [ ] Fact tables follow `fact_{subject}` pattern
- [ ] Dimensions follow `dim_{entity}` pattern
- [ ] Bridges follow `bridge_{relationship}` pattern
- [ ] Columns follow consistent naming

---

## Data Contracts Checklist

### Input Contracts

- [ ] All source systems documented
- [ ] Schema for each source defined
- [ ] Data types specified
- [ ] Nullable fields identified
- [ ] Primary keys documented

### Output Contracts

- [ ] All consumers identified
- [ ] Schema for each output defined
- [ ] SLAs documented
- [ ] Quality thresholds defined

### Schema Evolution

- [ ] Breaking changes policy defined
- [ ] Non-breaking changes policy defined
- [ ] Versioning strategy documented
- [ ] Deprecation policy defined

---

## Metrics Catalog Checklist

### Metric Definitions

- [ ] All business metrics documented
- [ ] Formulas clearly defined
- [ ] Base measures identified
- [ ] Calculated measures documented

### Aggregation Rules

- [ ] Allowed aggregations specified
- [ ] Non-additive measures identified
- [ ] Semi-additive measures identified
- [ ] Aggregation paths documented

### Ownership

- [ ] Metric owners assigned
- [ ] SLAs defined
- [ ] Update frequency specified
- [ ] Data source documented

---

## Quality Checklist

### Model Quality

- [ ] No circular dependencies
- [ ] No orphan entities
- [ ] All relationships validated
- [ ] Granularity consistent

### Documentation Quality

- [ ] All entities described
- [ ] All columns documented
- [ ] Business glossary updated
- [ ] Diagrams included

### Alignment

- [ ] Model aligns with STTM
- [ ] Model supports analytical questions
- [ ] Model enables KPI calculation
- [ ] Model follows architecture guidelines

---

## Gate 2 Readiness

### Required Artifacts

- [ ] `data-model.json` (canonical) complete — no `{{...}}` placeholders, `_template_metadata` removed
- [ ] `data-model.md` (derived) complete and consistent with JSON
- [ ] `data-model-er.html` (derived) complete and renders without missing placeholders
- [ ] `data-contracts.md` complete
- [ ] `metrics-catalog.md` complete

### Multi-Format Consistency

- [ ] Naming follows `brz_` / `slv_` / `gld_fact_` / `gld_dim_` conventions in all three formats
- [ ] KPIs in JSON `kpis` block recomputed from `layers[*]` arrays
- [ ] Every `relationships[].from` / `.to` resolves to an existing entity name
- [ ] `pk_fk` ∈ { PK, FK, NK, '-' }; PK unique per entity
- [ ] `scd_type` ∈ { 1, 2, 3 } for dimensions; null for facts
- [ ] HTML ER SVG block renders entities grouped by layer with relationship lines

### Validation

- [ ] Model reviewed by DataArchitect
- [ ] Contracts reviewed by DataEngineer
- [ ] Metrics reviewed by BusinessAnalyst
- [ ] No critical gaps identified

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| DataModeler | Sofia | | ⬜ |
| DataArchitect | Winston | | ⬜ |
| Orchestrator | Orion | | ⬜ |
