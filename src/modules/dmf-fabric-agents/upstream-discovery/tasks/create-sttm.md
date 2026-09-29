# Create STTM Task

**Task ID:** create-sttm
**Agent:** BusinessAnalyst (Mary 📊)
**Version:** 2.0
**Phase:** UPSTREAM · Gate 1

---

## Purpose

Produce the canonical Source-to-Target Mapping (STTM) for the wave in **three synchronized formats**:

1. `sttm.json` — machine-readable canonical artifact (single source of truth, consumed by Winston, Sofia, Gaia, Coda).
2. `sttm.md` — human-readable rendering for Gate 1 review and archival.
3. `sttm-visual.html` — filterable visual dashboard for stakeholder review.

The JSON is the **source of truth**. The MD and HTML are derived strictly from the JSON.

---

## Inputs

| Required | Path | Source agent |
|---|---|---|
| ✅ | `outputs/upstream/strategy/problem-statement.md` | data-strategist |
| ✅ | `outputs/upstream/strategy/kpis.md` | data-strategist |
| ⬜ Optional | `outputs/upstream/inventory/inventory-enriched.json` | inventory-scout |
| ⬜ Optional | `outputs/upstream/discovery/dead-code-reports/dead-code-report.md` | discovery-scout |
| ⬜ Optional | Source system schemas / DDL extracts | provided by stakeholder |

If a required input is missing, **stop** and request it from the migration-coordinator before proceeding.

---

## Outputs

All three artifacts are written to `projects/<project-name>/outputs/upstream/sttm/`:

| File | Format | Purpose |
|---|---|---|
| `sttm.json` | JSON canonical | Source of truth — consumed downstream programmatically |
| `sttm.md` | Markdown | Human-readable for Gate 1 review |
| `sttm-visual.html` | HTML (dark theme) | Filterable dashboard for stakeholders |

---

## Templates

Read these files from `src/modules/dmf-fabric-agents/upstream-discovery/templates/` BEFORE generating output. Reproduce structure, placeholders and visual conventions exactly:

- [`sttm-tmpl.json`](../templates/sttm-tmpl.json) — canonical schema and shape
- [`sttm-tmpl.md`](../templates/sttm-tmpl.md) — Markdown rendering convention
- [`sttm-visual-tmpl.html`](../templates/sttm-visual-tmpl.html) — HTML rendering convention (dark theme, mirrors AS-IS landscape)

---

## Execution Steps

### Step 1 — Load and validate inputs

1. Read `problem-statement.md` and `kpis.md`. Extract: project name, scope, deadline, KPIs that must be answered by the target model.
2. Read any optional inputs available (`inventory-enriched.json`, source schemas, dead-code report).
3. If a required input is missing, stop and request it via the migration-coordinator. Do not proceed with assumptions.
4. Resolve runtime values: `{{PROJECT_NAME}}`, `{{WAVE_ID}}`, `{{TRACE_ID}}`, `{{DATE_ISO8601}}`, `{{VERSION}}` (start at `1.0`).

### Step 2 — Identify source systems

For each source system in scope, populate one entry in `source_systems[]` with: `id` (sequential `SRC-NNN`), `name`, `type` (`DATABASE | API | FILE | STREAM`), `technology`, `version`, `owner`, `owner_contact`, `refresh_frequency`, `connection_pattern`.

Stakeholder questions to drive this step:

- "Which systems contain the data in scope?"
- "How is the data extracted today?"
- "How often is it refreshed?"
- "Who is the technical owner and who is the business owner?"

### Step 3 — Build field-level mappings

For every target column in scope, append one entry to `mappings[]`:

- `id` — sequential `M-NNNN` (zero-padded to 4 digits, unique).
- `source.{system, schema, table, column, data_type}` — leave `source.column` empty only when status is `UNRESOLVED`.
- `target.{layer, schema, table, column, data_type}` — `layer ∈ { landing, bronze, silver, gold }` matching the prefixes in `target_layers[]`.
- `transformation_rule_id` — must reference an entry in `transformation_rules[]` (created in Step 4).
- `transformation_type` — `DIRECT | CAST | DERIVED | LOOKUP | AGG`.
- `dq_rule_ids` — array of DQ rule identifiers (may be empty if Gaia has not produced rules yet).
- `pk_fk` — `PK | FK | -`.
- `owner` — accountable owner.
- `status` — `MAPPED | UNRESOLVED | DEFERRED`.
- `notes` — optional free-text clarification.

### Step 4 — Document transformation rules

For each non-trivial transformation, append one entry to `transformation_rules[]`:

- `id` — `TR-NNN` (sequential).
- `name`, `target` (qualified `table.column`), `type`, `sql_or_pseudocode`, `example.{input, output}`, `business_justification`.

Every `transformation_rule_id` referenced from `mappings[]` must exist here. Pure pass-throughs may share a single `TR-001` named "Direct copy" for hygiene.

### Step 5 — Identify unresolved mappings and compute KPIs

1. For every mapping with `status == "UNRESOLVED"`, append a row to `unresolved_mappings[]` with: `mapping_id`, `reason`, `blocks_agents` (subset of `data-architect`, `data-modeler`, `data-steward`, `code-generator`), `follow_up_owner`, `due_date`.
2. Recompute `kpis`:
   - `total_mappings` — `len(mappings)`
   - `direct_pct` — `% of mappings where transformation_type ∈ { DIRECT, CAST }` (rounded to 1 decimal)
   - `derived_pct` — `% where transformation_type ∈ { DERIVED, LOOKUP, AGG }`
   - `lookup_pct`, `agg_pct` — analogous
   - `unresolved_count` — `len(unresolved_mappings)`
   - `source_systems_count` — `len(source_systems)`
   - `target_tables_count` — distinct `target.table` count

### Step 6 — Persist `sttm.json`

1. Load `sttm-tmpl.json`.
2. Remove the `_template_metadata` block.
3. Replace **every** `{{...}}` placeholder with computed values.
4. Write the result to `projects/<project-name>/outputs/upstream/sttm/sttm.json`.
5. Validate: parse the file as JSON; abort and report if parsing fails.

### Step 7 — Render `sttm.md` and `sttm-visual.html`

1. Load `sttm-tmpl.md` and `sttm-tmpl.html` references.
2. Strip the leading template comment blocks from the produced files.
3. Replace block placeholders by iterating over the JSON arrays:
   - `{{SOURCE_SYSTEMS_BLOCK}}` / `{{SOURCES_BLOCK}}` — one entry per `source_systems[]`.
   - `{{MAPPINGS_TABLE_ROWS}}` / `{{MAPPINGS_BLOCK}}` — one row per `mappings[]`. In HTML, set `class` per status/type and `data-source` / `data-status` attributes per the comment guide in the template.
   - `{{TRANSFORMATION_RULES_BLOCK}}` / `{{RULES_BLOCK}}` — one entry per `transformation_rules[]`. In HTML, populate the `<select id="filter-source">` with one `<option value="{id}">{name}</option>` per source system.
   - `{{UNRESOLVED_BLOCK}}` — render the empty-state literal if `unresolved_mappings[]` is empty; otherwise render the table rows.
4. Replace all scalar placeholders (`{{PROJECT_NAME}}`, `{{TOTAL_MAPPINGS}}`, etc.).
5. Write outputs to `projects/<project-name>/outputs/upstream/sttm/sttm.md` and `sttm-visual.html`.

---

## Validation Checklist

Run all checks before declaring the task complete. Any failure must be fixed (not waived).

- [ ] All three files exist at `projects/<project-name>/outputs/upstream/sttm/`.
- [ ] `sttm.json` parses as valid JSON.
- [ ] No `{{` remains in any of the three output files (zero placeholders).
- [ ] No `_template_metadata` key remains in `sttm.json`.
- [ ] All `mappings[].id` values are unique.
- [ ] Every `transformation_rule_id` referenced in `mappings[]` exists in `transformation_rules[]`.
- [ ] Every `unresolved_mappings[].mapping_id` exists in `mappings[]` with `status == "UNRESOLVED"`.
- [ ] `kpis.total_mappings == len(mappings)` and `kpis.unresolved_count == len(unresolved_mappings)`.
- [ ] `kpis.direct_pct + kpis.derived_pct + kpis.lookup_pct + kpis.agg_pct ≈ 100` (within 0.5).
- [ ] `sttm-visual.html` opens in a browser without console errors; the source/status filter dropdowns work.
- [ ] Visual style matches the AS-IS dark palette — no inline styles outside the `<style>` block.

---

## Downstream Consumers

| Agent | Reads | Purpose |
|---|---|---|
| data-architect (Winston) | `sttm.json` | Derives target architecture and physical model boundaries |
| data-modeler (Sofia) | `sttm.json` | Produces logical model and data contracts |
| data-steward (Gaia) | `sttm.json` | Derives DQ rules and PII / compliance scope |
| code-generator (Coda) | `sttm.json` (indirect, via data model) | Generates DDL and ETL |
| migration-coordinator (Orion) | `sttm.json`, `sttm-visual.html` | Gate 1 promotion decision |

---

## Notes

- **Single source of truth:** `sttm.json` wins over `sttm.md` and `sttm-visual.html` if any drift is detected. Always regenerate the MD / HTML from the JSON — never edit them by hand.
- **Iterative refinement:** unresolved mappings are expected on the first pass. Re-run this task after stakeholder Q&A or when inventory-scout enriches `inventory-enriched.json`.


{same format}

---

## Reference Data

### Reference Tables Required

| Table | Description | Source | Update Frequency |
|-------|-------------|--------|------------------|
| {ref_table} | {desc} | {source} | {freq} |

---

## Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SOURCE    │────▶│   LANDING   │────▶│   BRONZE    │────▶│   SILVER    │────▶│   GOLD   │
│  {source}   │     │  Raw Copy   │     │   Cleaned   │     │  Business   │     │  Aggregated│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘
```

---

## Key Mapping Decisions

| Decision | Rationale |
|----------|-----------|
| {decision_1} | {rationale} |
| {decision_2} | {rationale} |

---

## Open Questions

| # | Question | Owner | Due Date |
|---|----------|-------|----------|
| 1 | {question} | {owner} | {date} |

---

## Next Steps

1. Review STTM with stakeholders
2. Define analytical questions - `*analytical-questions`
3. Define initial DQ requirements - `*dq-initial`

---

*Document generated by BusinessAnalyst Agent*
```

---

## Validation Checklist

Before completing, verify:

- [ ] All source systems documented
- [ ] All source tables listed with PKs
- [ ] Target layers defined (Landing, Bronze, Silver, Gold)
- [ ] All target tables documented
- [ ] Field mapping is complete (no gaps)
- [ ] Transformation rules documented
- [ ] Data types specified for source and target
- [ ] PK/FK relationships identified
- [ ] Reference data identified
- [ ] Open questions captured

---

## Common Transformation Types

| Type | Description | Example |
|------|-------------|---------|
| Direct Copy | No transformation | source.field → target.field |
| Type Cast | Data type change | VARCHAR → DATE |
| Lookup | Reference table join | code → description |
| Derivation | Calculate new value | price × quantity |
| Aggregation | Sum, count, avg | SUM(amount) |
| Cleansing | Trim, upper, null handling | TRIM(UPPER(field)) |
| Concatenation | Combine fields | first + ' ' + last |
| Split | Separate field | address → city, state, zip |
