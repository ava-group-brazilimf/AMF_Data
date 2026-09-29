<!--
  ──────────────────────────────────────────────────────────────────────
  STTM — Source-to-Target Mapping — Reference Template (Markdown)
  Owner: business-analyst (Mary 📊) — DMF Fabric Agents
  Phase: UPSTREAM | Gate: 1 | Version: 1.0
  ──────────────────────────────────────────────────────────────────────

  PURPOSE
  -------
  Human-readable rendering of the canonical sttm.json. This file is
  derived FROM sttm.json — never edit it directly without updating
  the JSON first. Used in Gate 1 reviews and archival.

  PLACEHOLDERS (replace with project data — never leave {{...}} in output)
    {{PROJECT_NAME}}, {{DATE}}, {{VERSION}}, {{TRACE_ID}}, {{WAVE_ID}}
    {{TOTAL_MAPPINGS}}, {{DIRECT_PCT}}, {{DERIVED_PCT}},
    {{UNRESOLVED_COUNT}}, {{SOURCES_COUNT}}, {{TARGET_TABLES_COUNT}}
    {{SOURCE_SYSTEMS_BLOCK}}      — repeated ### Source N: blocks
    {{MAPPINGS_TABLE_ROWS}}        — repeated | rows | of mapping table
    {{TRANSFORMATION_RULES_BLOCK}} — repeated ### TR-NNN blocks
    {{UNRESOLVED_BLOCK}}           — repeated unresolved rows or "None"

  CONVENTIONS
  -----------
  - All transformation_rule_ids in the mapping table MUST be defined
    in the Transformation Rules section.
  - Unresolved mappings MUST list which downstream agent is blocked.
  - Strip this comment block from the produced sttm.md.
-->

# STTM — Source-to-Target Mapping

| Field | Value |
|---|---|
| **Project** | {{PROJECT_NAME}} |
| **Agent** | Mary (business-analyst) |
| **Date** | {{DATE}} |
| **Version** | {{VERSION}} |
| **Gate** | 1 |
| **Trace ID** | {{TRACE_ID}} |
| **Wave** | {{WAVE_ID}} |

---

## Executive Summary

This document defines the canonical Source-to-Target Mapping (STTM) for **{{PROJECT_NAME}}**. It maps **{{TOTAL_MAPPINGS}}** columns across **{{SOURCES_COUNT}}** source system(s) into **{{TARGET_TABLES_COUNT}}** target table(s).

| KPI | Value |
|---|---|
| Total mappings | {{TOTAL_MAPPINGS}} |
| Direct mappings | {{DIRECT_PCT}}% |
| Derived / transformed | {{DERIVED_PCT}}% |
| Unresolved | {{UNRESOLVED_COUNT}} |

> **Source of truth:** `sttm.json` (canonical). This `.md` file is generated from it.

---

## 1. Source Systems

{{SOURCE_SYSTEMS_BLOCK}}

<!--
  Repeat the block below for each source_systems[] entry in sttm.json.

  ### Source: {name} ({id})

  | Attribute | Value |
  |---|---|
  | Type | {type} |
  | Technology | {technology} {version} |
  | Refresh frequency | {refresh_frequency} |
  | Owner | {owner} ({owner_contact}) |
  | Connection pattern | `{connection_pattern}` |
-->

---

## 2. Target Layers

| Layer | Prefix | Purpose |
|---|---|---|
| Landing | `lnd_` | Raw ingestion |
| Bronze | `brz_` | Cleaned, typed |
| Silver | `slv_` | Business logic applied |
| Gold | `gld_` | Aggregated for consumption |

---

## 3. Field-Level Mapping

| # | Source System | Source Schema | Source Table | Source Column | Source Type | Target Layer | Target Table | Target Column | Target Type | Transformation | DQ Rules | PK/FK | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{{MAPPINGS_TABLE_ROWS}}

<!--
  Each row corresponds to one entry in mappings[] in sttm.json.
  The "Transformation" column shows the transformation_rule_id (TR-NNN).
  The "Status" column ∈ { MAPPED, UNRESOLVED, DEFERRED }.
-->

---

## 4. Transformation Rules

{{TRANSFORMATION_RULES_BLOCK}}

<!--
  Repeat for each transformation_rules[] entry in sttm.json:

  ### TR-NNN — {name}

  - **Applies to:** `{target}`
  - **Type:** {DIRECT | CAST | DERIVED | LOOKUP | AGG}
  - **Business justification:** {justification}

  **Logic:**
  ```sql
  {sql_or_pseudocode}
  ```

  **Example:**
  | Input | Output |
  |---|---|
  | {example.input} | {example.output} |
-->

---

## 5. Unresolved Mappings

{{UNRESOLVED_BLOCK}}

<!--
  If unresolved_mappings[] is empty, render literally:
  > _No unresolved mappings — STTM ready for Gate 1 review._

  Otherwise render a table:

  | Mapping ID | Reason | Blocks Agents | Follow-up Owner | Due Date |
  |---|---|---|---|---|
  | M-XXXX | {reason} | {blocks_agents joined by comma} | {follow_up_owner} | {due_date} |
-->

---

## 6. Downstream Consumers

This STTM is consumed by:

- **data-architect (Winston)** — derives target architecture and physical model boundaries.
- **data-modeler (Sofia)** — produces the logical data model and data contracts.
- **data-steward (Gaia)** — derives DQ rules and PII/compliance scope.
- **code-generator (Coda)** — indirectly, via the data model and DQ rules.

---

*Generated from `sttm.json` · business-analyst · DMF Fabric Agents · Gate 1*
