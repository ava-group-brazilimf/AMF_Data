# Data Model — {{PROJECT_NAME}}

> **Source of truth:** This Markdown is *derived* from the canonical
> [`data-model-tmpl.json`](./data-model-tmpl.json). The visual stakeholder
> rendering is [`data-model-er-tmpl.html`](./data-model-er-tmpl.html).
> All three artifacts MUST agree — the JSON is the only file consumed by
> Coda (code-generator), Diego (downstream-executor), Gaia (data-steward)
> and Bianca (bi-semantic).
>
> **LLM rules:**
> - Replace every `{{...}}` placeholder with project data.
> - Naming MUST follow `brz_` / `slv_` / `gld_fact_` / `gld_dim_` / `gld_bridge_`.
> - Recompute KPIs from the JSON `layers[*]` arrays before persisting.
> - Every relationship `from`/`to` MUST resolve to an existing entity name.

---

## Metadata

| Field | Value |
|---|---|
| Project | {{PROJECT_NAME}} |
| Wave | {{WAVE_ID}} |
| Trace | {{TRACE_ID}} |
| Version | {{VERSION}} |
| Date | {{DATE_ISO8601}} |
| Pattern | {{PATTERN}} |
| Target Platform | {{TARGET_PLATFORM}} |
| Owner | Sofia (DataModeler) |
| Gate | 2 |

---

## Model KPIs

| KPI | Value |
|---|---|
| Entities total | {{KPI_ENTITIES_TOTAL}} |
| Bronze | {{KPI_BRONZE}} |
| Silver | {{KPI_SILVER}} |
| Gold facts | {{KPI_FACTS}} |
| Gold dims | {{KPI_DIMS}} |
| Gold bridges | {{KPI_BRIDGES}} |
| SCD2 dimensions | {{KPI_SCD2}} |
| Relationships | {{KPI_RELATIONSHIPS}} |

---

## Naming Conventions

| Object Type | Convention | Example |
|---|---|---|
| Bronze table | `brz_{entity}` | `brz_customer` |
| Silver table | `slv_{entity}` | `slv_customer` |
| Gold fact | `gld_fact_{subject}` | `gld_fact_sales` |
| Gold dimension | `gld_dim_{entity}` | `gld_dim_customer` |
| Gold bridge | `gld_bridge_{rel}` | `gld_bridge_customer_segment` |
| Surrogate PK | `{entity}_key` | `customer_key` |
| Foreign key | `{entity}_key` | `customer_key` |

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    {{MERMAID_ER_BLOCK}}
    %% Render one relationship line per JSON relationships[]:
    %%   GLD_DIM_CUSTOMER ||--o{ GLD_FACT_SALES : "customer_key"
    %% Render one entity block per layers[*].entities[]:
    %%   GLD_FACT_SALES {
    %%     bigint sales_key PK
    %%     bigint customer_key FK
    %%     decimal amount
    %%   }
```

---

## Bronze Layer

> Grain: 1:1 with source row · No history · Ingestion timestamp mandatory.

{{BRONZE_BLOCK}}

<!--
Repeat one block per layers.bronze[]:

### `brz_{entity}`

| Attribute | Value |
|---|---|
| Type | TABLE |
| Grain | 1:1 with source row |
| Source | SRC-001 / {src_table} (mappings: M-0001) |
| Owner | {owner} |

| Column | Type | Nullable | Key | Description |
|---|---|---|---|---|
| {entity}_id | STRING | NO | NK | Natural key from source |
| ingested_at | TIMESTAMP | NO | - | Bronze ingestion timestamp |
-->

---

## Silver Layer

> Grain: One clean entity · SCD applied where required · Lineage to Bronze mandatory.

{{SILVER_BLOCK}}

<!--
Repeat one block per layers.silver[]:

### `slv_{entity}`

| Attribute | Value |
|---|---|
| Type | TABLE |
| Grain | One clean {entity} |
| SCD Type | 1 |
| From | brz_{entity} (rules: TR-001) |
| Owner | {owner} |

| Column | Type | Nullable | Key | Description |
|---|---|---|---|---|
| {entity}_id | STRING | NO | NK | Cleansed natural key |
| valid_from | TIMESTAMP | NO | - | SCD valid_from |
| valid_to | TIMESTAMP | YES | - | SCD valid_to |
-->

---

## Gold Layer — Facts

> Grain: One row per business event · Surrogate PK · Foreign keys to dimensions only.

{{GOLD_FACTS_BLOCK}}

<!--
Repeat one block per layers.gold_facts[]:

### `gld_fact_{subject}`

| Attribute | Value |
|---|---|
| Type | FACT |
| Grain | One row per {business_event} |
| Update Frequency | DAILY |
| Retention | 7 years |
| From | slv_{entity} (rules: TR-002) |
| Owner | {owner} |

| Column | Type | Nullable | Key | Description |
|---|---|---|---|---|
| {subject}_key | BIGINT | NO | PK | Surrogate key |
| customer_key | BIGINT | NO | FK | FK to gld_dim_customer |
| amount | DECIMAL(18,2) | NO | - | Monetary amount |

**Measures**

| Measure | Aggregation |
|---|---|
| amount | SUM |
| quantity | SUM |
-->

---

## Gold Layer — Dimensions

> Grain: One row per master entity · SCD2 with `valid_from` / `valid_to` / `is_current` when historical tracking required.

{{GOLD_DIMS_BLOCK}}

<!--
Repeat one block per layers.gold_dims[]:

### `gld_dim_{entity}`

| Attribute | Value |
|---|---|
| Type | DIM |
| Grain | One row per {entity} |
| SCD Type | 2 |
| Tracked Attributes | {attr_1}, {attr_2} |
| History Retention | Unlimited |
| From | slv_{entity} (rules: TR-003) |
| Owner | {owner} |

| Column | Type | Nullable | Key | Description |
|---|---|---|---|---|
| {entity}_key | BIGINT | NO | PK | Surrogate key |
| {entity}_id | STRING | NO | NK | Natural key from source |
| valid_from | TIMESTAMP | NO | - | SCD2 valid_from |
| valid_to | TIMESTAMP | YES | - | SCD2 valid_to |
| is_current | BOOLEAN | NO | - | Current record flag |

**Hierarchies**

| Hierarchy | Levels |
|---|---|
| {hierarchy_name} | Level1 → Level2 → Level3 |
-->

---

## Granularity Matrix

| Layer | Pattern | Grain |
|---|---|---|
| Bronze | `brz_{entity}` | 1:1 with source row |
| Silver | `slv_{entity}` | One clean entity |
| Gold Fact | `gld_fact_{subject}` | One business event |
| Gold Dim | `gld_dim_{entity}` | One master entity |

---

## Relationships

| From | To | From Column | To Column | Cardinality | Type |
|---|---|---|---|---|---|

{{RELATIONSHIPS_TABLE_BLOCK}}

<!--
Repeat one row per relationships[]. Type ∈ { IDENTIFYING, NON_IDENTIFYING, BRIDGE }.
| gld_fact_sales | gld_dim_customer | customer_key | customer_key | N:1 | IDENTIFYING |
-->

---

## SCD Specifications

| Dimension | SCD Type | Tracked Attributes | History Retention |
|---|---|---|---|

{{SCD_TABLE_BLOCK}}

<!--
Repeat one row per layers.gold_dims[] with scd_type ∈ {2,3}:
| gld_dim_customer | 2 | name, segment, address | Unlimited |
-->

---

## Validation Rules

{{VALIDATION_RULES_BLOCK}}

<!--
Repeat one bullet per validation_rules[]:
- No orphan facts: every FK must have matching PK in dimension
- Complete dimensions: all required attributes present
- Valid SCD2 dates: valid_from < valid_to
- Single current: only one is_current=true per natural key
-->

---

## Cross-References

| Consumer | Artifact Used | Purpose |
|---|---|---|
| Coda (code-generator) | `data-model.json` | DDL & ETL generation |
| Diego (downstream-executor) | `data-model.json` | Execution planning |
| Gaia (data-steward) | `data-model.json` | DQ rules binding |
| Bianca (bi-semantic) | `data-model.json` | Semantic layer build |
| Stakeholders | `data-model-er.html` | Visual review at Gate 2 |

---

*Generated by Sofia (data-modeler) · DMF Fabric Agents · Gate 2*
