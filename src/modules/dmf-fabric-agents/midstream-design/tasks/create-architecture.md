# Create Architecture Task

```yaml
task_id: create-architecture
agent: data-architect
version: "1.1"
command: "*create-architecture"
phase: MIDSTREAM
gate: 2
outputs:
  - file: "architecture-spec.json"
    format: json
    path: "projects/{project_name}/outputs/midstream/"
    description: "Machine-readable architecture specification (layers, stack, SLAs, ADRs)"
  - file: "architecture.md"
    format: markdown
    path: "projects/{project_name}/outputs/midstream/"
    description: "Human-readable architecture document for downstream agents"
  - file: "tobe-target-architecture.html"
    format: html
    path: "projects/{project_name}/outputs/midstream/"
    description: "Executive visual presentation for Gate 2 stakeholder review"
output_folder: "projects/{project_name}/outputs/midstream/"
```

---

## Reference Template

Before executing **Step 9**, load the HTML template as visual reference:

```
src/modules/dmf-fabric-agents/midstream-design/templates/tobe-target-architecture-tmpl.html
```

Reproduce its structure, gradient header border, CSS variables, fonts, medallion flow and hover patterns exactly. Replace every `{{PLACEHOLDER}}` with decisions made in this task — never leave placeholders in the final HTML. If a value is unavailable, render `—` or `N/A`.

---

## Purpose

Design and document a comprehensive data architecture that supports the business requirements defined in UPSTREAM phase.

---

## Prerequisites

- Gate 1 passed
- STTM available
- Analytical questions defined
- Understanding of technology constraints

---

## Execution Steps

### Step 1: Review Upstream Artifacts

Load and review:
- STTM (source systems, target tables, transformations)
- Analytical questions (data requirements)
- Problem statement (business context)
- KPIs (success metrics)

### Step 2: Define Architecture Pattern

Select appropriate pattern:
- **Lakehouse**: Unified analytics with Delta Lake
- **Data Warehouse**: Traditional DW/DM approach
- **Hybrid**: Combination based on needs

### Step 3: Design Data Layers

Define each layer:
1. **Landing/Raw**: Ingestion strategy
2. **Bronze**: Cleansing approach
3. **Silver**: Business logic layer
4. **Gold**: Aggregation/serving layer

### Step 4: Select Technology Stack

For each component, document:
1. Technology choice
2. Justification
3. Alternatives considered

### Step 5: Design Data Flow

Document:
1. Ingestion patterns (batch, streaming, hybrid)
2. Transformation pipeline
3. Serving patterns
4. Refresh schedules

### Step 6: Address Cross-Cutting Concerns

Document:
1. Security (access, encryption)
2. Scalability (growth strategy)
3. Monitoring (observability)
4. Disaster recovery

### Step 7: Persist Architecture JSON

Before generating any text output, consolidate all architectural decisions
made in Steps 1–6 into a single structured JSON file.

- **File:** `architecture-spec.json`
- **Path:** `projects/{project_name}/outputs/midstream/`

**JSON schema:**

```json
{
  "metadata": {
    "project_name": "string",
    "trace_id": "string",
    "pattern": "Lakehouse | Data Warehouse | Hybrid",
    "primary_technology": "string",
    "target_environment": "string",
    "gate_status": "PASSED | IN REVIEW",
    "generated_date": "YYYY-MM-DD",
    "agent": "data-architect",
    "version": "1.1"
  },
  "principles": [
    { "number": "01", "title": "string", "description": "string" }
  ],
  "layers": {
    "sources":  { "systems": [], "ingestion_method": "string" },
    "bronze":   { "format": "string", "retention": "string", "naming": "brz_{domain}_{entity}", "transformations": "string" },
    "silver":   { "format": "string", "retention": "string", "naming": "slv_{domain}_{entity}", "transformations": "string" },
    "gold":     { "format": "string", "retention": "string", "naming": "gld_{domain}_{subject}", "optimizations": "string" },
    "serving":  { "bi_tool": "string", "access_pattern": "string", "consumers": [] }
  },
  "tech_stack": [
    { "layer": "string", "technology": "string", "replaces": "string", "justification": "string" }
  ],
  "sla_targets": [
    { "layer": "string", "metric": "string", "target": "string", "current_asis": "string", "improvement": "string" }
  ],
  "cross_cutting": {
    "governance": "string",
    "observability": "string",
    "security": {
      "encryption_rest": "string",
      "encryption_transit": "string",
      "key_management": "string"
    }
  },
  "adrs": [
    { "id": "ADR-001", "title": "string", "decision": "string", "rationale": "string" }
  ]
}
```

This JSON is the **canonical source of truth** for the MD and HTML outputs that follow.
All values in `architecture.md` and `tobe-target-architecture.html` must come from this JSON.

---

### Step 8: Generate Markdown Document (architecture.md)

Using the data from `architecture-spec.json` (Step 7), generate the Markdown document.

- **File:** `architecture.md`
- **Path:** `projects/{project_name}/outputs/midstream/`
- **Template:** `src/modules/dmf-fabric-agents/midstream-design/templates/architecture-tmpl.md`

Replace every `{placeholder}` in the template with real values.
The values MUST be identical to `architecture-spec.json`.

**Required sections (match the template structure):**
- Executive Summary
- Architecture Overview (include ASCII diagram)
- Data Layers (Landing, Bronze, Silver, Gold) — one table per layer
- Technology Stack (table with layer, technology, purpose, justification, replaces)
- Data Flow (Ingestion Flow table + Transformation Flow diagram)
- Security Architecture (Access Control table + Data Protection)
- Scalability
- Monitoring & Operations
- Disaster Recovery
- Architecture Decisions — reference to `decisions.md`

This file is consumed by downstream agents (`code-generator`, `downstream-executor`).
It must be structured and parseable. No unfilled `{placeholder}` text in the output.

The Markdown document must follow this structure (template):

```
# Data Architecture — {project_name}

**Pattern:** {architecture_pattern}
**Primary Technology:** {primary_technology}
**Target Environment:** {target_environment}
**Date:** {date}
**Version:** {version}

---

## Executive Summary

{executive_summary — 2-3 paragraphs}

---

## Architecture Principles

1. **{principle_1_title}**: {principle_1_desc}
2. **{principle_2_title}**: {principle_2_desc}
3. **{principle_3_title}**: {principle_3_desc}
4. **{principle_4_title}**: {principle_4_desc}

---

## Data Layers

### Sources
- Systems: {source_systems}
- Ingestion: {ingestion_method}

### Bronze Layer
- Format: {bronze_format}
- Retention: {bronze_retention}
- Naming: `brz_{domain}_{entity}`
- Transformations: {bronze_transformations}

### Silver Layer
- Format: {silver_format}
- Retention: {silver_retention}
- Naming: `slv_{domain}_{entity}`
- Transformations: {silver_transformations}

### Gold Layer
- Format: {gold_format}
- Retention: {gold_retention}
- Naming: `gld_{domain}_{subject}`
- Optimizations: {gold_optimizations}

### Serving
- BI Tool: {bi_tool}
- Access Pattern: {access_pattern}
- Consumers: {consumers}

---

## Technology Stack

| Layer | Technology | Replaces | Justification |
|-------|-----------|----------|---------------|
| Ingestion | {tech} | {replaces} | {justification} |
| Processing | {tech} | {replaces} | {justification} |
| Orchestration | {tech} | {replaces} | {justification} |
| Storage | {tech} | {replaces} | {justification} |
| Governance | {tech} | {replaces} | {justification} |
| Consumption | {tech} | {replaces} | {justification} |

---

## SLA Targets

| Layer | Metric | Target | Current (AS-IS) | Improvement |
|-------|--------|--------|-----------------|-------------|
| {layer} | {metric} | {target} | {current} | {delta} |

---

## Security Architecture

| Layer | Access Level | Method |
|-------|-------------|--------|
| Landing | ETL Service only | Service Principal |
| Bronze | ETL + Advanced Users | AAD Groups |
| Silver | Analytics Team | AAD Groups + RLS |
| Gold | All Authorized | AAD + RLS |

- Encryption at Rest: {encryption_rest}
- Encryption in Transit: {encryption_transit}
- Key Management: {key_management}

---

## Cross-Cutting Concerns

### Governance
{governance_description}

### Observability & SLO
{observability_description}

---

## Architecture Decisions (ADRs)

### ADR-001 — {title}
**Decision:** {decision_statement}
**Rationale:** {rationale}

### ADR-002 — {title}
**Decision:** {decision_statement}
**Rationale:** {rationale}

### ADR-003 — {title}
**Decision:** {decision_statement}
**Rationale:** {rationale}

### ADR-004 — {title}
**Decision:** {decision_statement}
**Rationale:** {rationale}

### ADR-005 — {title}
**Decision:** {decision_statement}
**Rationale:** {rationale}

### ADR-006 — {title}
**Decision:** {decision_statement}
**Rationale:** {rationale}

---

*Generated by DataArchitect Agent · Gate 2 · {date}*
```

---

### Step 9: Generate HTML Presentation (tobe-target-architecture.html)

Using the data from `architecture-spec.json` (Step 7), generate the executive HTML presentation.
This step generates HTML only. The Markdown was already saved in Step 8.

- **File:** `tobe-target-architecture.html`
- **Path:** `projects/{project_name}/outputs/midstream/`

Before generating, read the reference template:
`src/modules/dmf-fabric-agents/midstream-design/templates/tobe-target-architecture-tmpl.html`

The HTML must be a single self-contained file.
The values MUST be identical to `architecture-spec.json` and `architecture.md`.

**Style:** Light theme (#F7F8FA bg). Fonts: Playfair Display (headings —
elegant serif), JetBrains Mono (labels/tags/metadata), Plus Jakarta Sans
(body) via Google Fonts. Primary accent: Microsoft Fabric blue #0078D4.
Layer colors: Bronze #C0782A, Silver #5B7FA6, Gold #A8860C, each with
*-light bg variant and *-mid border variant. All as CSS variables.
Header: white card, border-radius 16px, 3px gradient top border spanning
all layer colors.

**Required sections (in order):**

1. Header — white card with gradient top border, fabric blue badge
   'TO-BE Architecture', Playfair Display title, subtitle, right-aligned
   metadata (Trace ID, agents, target platform, pattern, gate status, date).
2. Architecture Principles — 4-column grid. Each card: large muted number
   (01-04), bold title, 2-line description.
3. Medallion Architecture — main visual. Horizontal flow:
   Sources → Bronze → Silver → Gold → Serving.
   Each layer: tall card with colored top border + tinted background,
   uppercase layer label, large serif name, description, JetBrains Mono
   detail lines (Format, Naming, Retention, Access), colored mini-badges.
   SVG chevron arrows (opacity 0.3) between layers.
   Below flow: 2-column cross-cutting cards (Governance + Observability).
4. Technology Stack — 3-column grid. Each card: colored dot + layer tag,
   bold tech name, description mentioning what it replaces from AS-IS.
5. SLA Table — columns: Layer, Metric, Target (TO-BE in green mono),
   Current AS-IS, Improvement (green with + prefix). Hover on rows.
6. Architecture Decisions (ADRs) — 3-column grid, 6 cards. Each card:
   ADR-00X in muted mono, bold title, decision in fabric blue, rationale.
7. Footer — left: brand. Right: 'TO-BE Architecture · Gate 2 · date'.

Section titles: JetBrains Mono, uppercase, letter-spacing 0.14em,
::after line to the right. Hover effects: transition: all 0.2s.
No external JS. Single `<style>` block. No unfilled `{{...}}` placeholders.

---

## Data Consistency Contract

The three output files generated by this task must contain identical data:

| Data point        | JSON source field                          | MD location              | HTML location          |
|-------------------|--------------------------------------------|--------------------------|------------------------|
| Pattern           | `metadata.pattern`                         | Header block             | Header metadata        |
| Principles        | `principles[]`                             | Architecture Principles  | Principles grid (4)    |
| Tech stack items  | `tech_stack[].technology`                  | Technology Stack table   | Tech Stack cards       |
| SLA targets       | `sla_targets[].target`                     | SLA Targets table        | SLA Table              |
| ADRs              | `adrs[].title`                             | Architecture Decisions   | ADR cards (6)          |

**RULE:** If a value appears in `architecture-spec.json`, it MUST appear verbatim
(same string, same number) in the MD and HTML. Never invent or rephrase.
Copy from the JSON values set in Step 7.

---

## Cross-Format Validation

Before finishing, verify:

1. Pick 3 random values from `architecture-spec.json` (e.g., a tech name, an SLA target, an ADR title).
2. Find those exact values in `architecture.md`.
3. Find those exact values in `tobe-target-architecture.html`.
4. If any value is missing or different, fix the discrepancy before proceeding.

> All three files must be saved before the task is considered complete.
> JSON is the canonical source; MD is consumed by downstream agents and CI;
> HTML is the executive presentation for Gate 2 stakeholders.

---

## Validation Checklist

Before completing, verify:

- [ ] All data layers defined
- [ ] Technology stack documented with justifications
- [ ] Data flow clearly diagrammed
- [ ] Security approach documented
- [ ] Scalability strategy defined
- [ ] Monitoring approach specified
- [ ] Aligns with STTM requirements
- [ ] Supports all analytical questions
- [ ] `architecture-spec.json` saved to `outputs/midstream/`
- [ ] `architecture-spec.json` — valid JSON, all fields populated
- [ ] `architecture-spec.json` — minimum 4 principles, 6 ADRs, 5+ tech stack entries
- [ ] `architecture.md` saved to `outputs/midstream/`
- [ ] `architecture.md` — no `{placeholder}` remaining
- [ ] `architecture.md` contains all sections: layers, stack, SLAs, ADRs, security
- [ ] `tobe-target-architecture.html` saved to `outputs/midstream/`
- [ ] `tobe-target-architecture.html` — no `{{...}}` remaining
- [ ] `tobe-target-architecture.html` — opens in browser without console errors
- [ ] Values are consistent across all three files (same tech names, same SLA numbers)
