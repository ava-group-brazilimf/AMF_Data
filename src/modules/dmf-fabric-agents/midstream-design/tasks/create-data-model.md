# Task: Create Data Model

**Command:** `*data-model` / `*DM`  
**Outputs:**
- `projects/{project_name}/outputs/midstream/data-model.json` — canonical source of truth (consumed by Coda, Diego, Gaia, Bianca)
- `projects/{project_name}/outputs/midstream/data-model.md` — derived Markdown report
- `projects/{project_name}/outputs/midstream/data-model-er.html` — derived visual ER diagram (Gate 2 stakeholder review)

---

## Objective

Create a comprehensive logical data model based on requirements from STTM and architecture documents,
persisted in three aligned formats (JSON canonical, Markdown report, HTML ER diagram).

---

## Prerequisites

- [ ] STTM document available
- [ ] Architecture document available
- [ ] KPIs defined
- [ ] Analytical questions documented

---

## Steps

### Step 1: Analyze Requirements

1. Load STTM document
2. Review analytical questions
3. Identify required entities
4. Understand metrics needs

### Step 2: Define Granularity

For each layer, define the grain:

| Layer | Question to Answer |
|-------|-------------------|
| Landing | What is one row from source? |
| Silver | What is one clean entity? |
| Gold Fact | What is one business event? |
| Gold Dim | What is one master entity? |

### Step 3: Design Facts

For each fact table:
- Define grain
- Identify measures
- Identify foreign keys
- Document aggregation rules

### Step 4: Design Dimensions

For each dimension:
- Define grain
- List attributes
- Determine SCD type
- Identify hierarchies

### Step 5: Map Relationships

- Connect facts to dimensions
- Specify cardinality
- Document relationship type
- Create bridge tables if needed

### Step 6: Persist Multi-Format Outputs

Generation MUST happen in this order:

```
1. Persist canonical JSON (source of truth):
     Template: templates/data-model-tmpl.json
     Output:   projects/{project_name}/outputs/midstream/data-model.json

   Required transformations BEFORE writing the file:
     - Remove the _template_metadata block.
     - Replace every {{...}} placeholder with computed values.
     - Naming MUST follow the naming_conventions block:
         bronze=brz_, silver=slv_, gold_facts=gld_fact_, gold_dims=gld_dim_.
     - Recompute kpis from layers[*] arrays before persisting.
     - Every relationships[].from / .to MUST reference an existing entity name.
     - scd_type ∈ {1,2,3} for dimensions; null for facts.
     - column[].pk_fk ∈ {PK, FK, NK, '-'}; pk MUST be unique per entity.

2. Render Markdown report (derived):
     Template: templates/data-model-tmpl.md
     Output:   projects/{project_name}/outputs/midstream/data-model.md

3. Render HTML ER diagram (derived, stakeholder-facing):
     Template: templates/data-model-er-tmpl.html
     Output:   projects/{project_name}/outputs/midstream/data-model-er.html

   Rendering rules (see template header comment for full spec):
     - Substitute every {{...}} placeholder; never leave placeholders in output.
     - Layer color map (LAYER_COLOR / --c on .entity-card and .layer-band):
         bronze     → bronze
         silver     → silver
         gold_facts → gold
         gold_dims  → green
     - Inline ER SVG: group entities by layer column, draw <g class="er-entity"> with
       a header band and one <text> per visible column (limit to PK/FK + 4 attributes
       to keep the diagram readable). Connect with <g class="er-rel"><line> showing
       cardinality.
     - col-key class map: PK→key-pk, FK→key-fk, NK→key-nk, '-'→key-none.
     - Relationship type pill class: pill-identifying | pill-non-identifying | pill-bridge.
```

**Pass Criteria:** JSON validates against template structure (all required keys present,
all relationships resolve to existing entities, naming conventions honored).

---

## Validation

### Content
- [ ] All STTM entities covered
- [ ] Granularity defined for all tables
- [ ] Relationships complete (every `from`/`to` resolves to an existing entity)
- [ ] SCD types assigned (`scd_type` ∈ {1,2,3} for dims; null for facts)
- [ ] Model supports all analytical questions
- [ ] PK unique per entity; FKs reference valid PKs

### Multi-Format Alignment
- [ ] `data-model.json` has no `{{...}}` placeholders and no `_template_metadata` block
- [ ] `data-model.md` reflects the same entities, columns and relationships as the JSON
- [ ] `data-model-er.html` renders without leftover `{{...}}` placeholders
- [ ] Naming uses `brz_` / `slv_` / `gld_fact_` / `gld_dim_` / `gld_bridge_` consistently
- [ ] `kpis` block in JSON matches the count of entries in `layers[*]` and `relationships[]`
