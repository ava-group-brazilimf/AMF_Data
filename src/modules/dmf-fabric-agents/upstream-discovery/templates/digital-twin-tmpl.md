# Digital Twin Template
# Template ID: digital-twin-tmpl
# Agent: Logan (Logic Extractor)
# Version: 1.0

---

# 🧬 Digital Twin — Semantic Blueprint

**Twin ID:** {digital_twin_id}  
**Creation Date:** {creation_date}  
**Version:** {version}  
**Source Platform:** {source_platform}  
**Target Platform:** {target_platform}  
**Overall Confidence:** {overall_confidence}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Objects** | {total_objects} |
| **Physical Coverage** | {physical_coverage}% |
| **Semantic Enrichment** | {semantic_enrichment}% |
| **Target Readiness** | {target_readiness}% |
| **Gaps Identified** | {gap_count} |
| **SME Review Items** | {sme_review_count} |

---

## Layer Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PHYSICAL LAYER                            │
│  Source platform objects as they exist today                 │
│  Tables: {table_count}  Pipelines: {pipeline_count}         │
│  Jobs: {job_count}  UDFs: {udf_count}  Scripts: {script_count} │
└─────────────────────┬───────────────────────────────────────┘
                      │ mapping
┌─────────────────────▼───────────────────────────────────────┐
│                    SEMANTIC LAYER                            │
│  Business meaning and domain classification                 │
│  Domains: {domain_list}                                     │
│  Business Rules: {total_rules}  Quality Rules: {dq_rules}   │
│  Data Classifications: PII={pii_count} Financial={fin_count} │
└─────────────────────┬───────────────────────────────────────┘
                      │ mapping
┌─────────────────────▼───────────────────────────────────────┐
│                    TARGET LAYER                              │
│  Target platform mapping and migration strategy             │
│  Bronze: {bronze_count}  Silver: {silver_count}             │
│  Gold: {gold_count}                                         │
│  Strategy: Lift={lift_count} Refactor={refactor_count}      │
│            Rebuild={rebuild_count}                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Physical Layer — "What Exists"

### Tables

| # | Physical ID | Name | Schema | Columns | Rows (est.) | Format | Status |
|---|-------------|------|--------|:-------:|:-----------:|--------|:------:|
| 1 | {phys_id} | {table_name} | {schema} | {col_count} | {row_est} | {format} | {status_icon} |

### Pipelines

| # | Physical ID | Name | Language | Complexity | Dependencies | Status |
|---|-------------|------|----------|:----------:|:------------:|:------:|
| 1 | {phys_id} | {pipeline_name} | {language} | {complexity} | {dep_count} | {status_icon} |

### UDFs

| # | Physical ID | Name | Language | Type | Called By | Status |
|---|-------------|------|----------|------|:---------:|:------:|
| 1 | {phys_id} | {udf_name} | {language} | {SCALAR/TABULAR/AGGREGATE} | {pipeline_count} | {status_icon} |

---

## Semantic Layer — "What It Means"

### Entity Catalog

| # | Semantic ID | Business Name | Domain | Description | Data Class | Confidence |
|---|-------------|---------------|--------|-------------|:----------:|:----------:|
| 1 | {sem_id} | {business_name} | {domain} | {description} | {PII/FIN/OPS/REF} | {score} |

### Business Rules

| # | Rule ID | Rule Name | Type | Entity | Description | Confidence |
|---|---------|-----------|------|--------|-------------|:----------:|
| 1 | {rule_id} | {rule_name} | {type} | {entity} | {description} | {score} |

### Data Lineage

```
{source_1} ──→ {transform_1} ──→ {intermediate_1} ──→ {transform_2} ──→ {target_1}
{source_2} ──┘                                                          │
                                                                        ▼
                                                                   {target_2}
```

---

## Target Layer — "Where It's Going"

### Target Mapping

| # | Target ID | Source Entity | Target Location | Layer | Format | Strategy | Effort (hrs) |
|---|-----------|--------------|-----------------|:-----:|--------|:--------:|:------------:|
| 1 | {tgt_id} | {source_entity} | {catalog.schema.table} | {bronze/silver/gold} | {delta/parquet} | {strategy} | {hours} |

### Migration Strategy Summary

| Strategy | Count | Percentage | Total Effort (hrs) |
|----------|:-----:|:----------:|:-------------------:|
| Lift-and-Shift | {count} | {pct}% | {hours} |
| Refactor | {count} | {pct}% | {hours} |
| Rebuild | {count} | {pct}% | {hours} |

---

## Gaps & Unmapped Items

| # | Layer | Item | Reason | Impact | Recommended Action |
|---|:-----:|------|--------|:------:|-------------------|
| 1 | {physical/semantic/target} | {item_name} | {reason} | {HIGH/MED/LOW} | {action} |

---

## Cross-Layer Validation

| Check | Result | Details |
|-------|:------:|---------|
| Physical → Semantic coverage | {icon} | {pct}% mapped |
| Semantic → Target coverage | {icon} | {pct}% mapped |
| Dependency preservation | {icon} | {details} |
| Lineage completeness | {icon} | {details} |
| No orphan entities | {icon} | {orphan_count} found |

---

*Digital Twin generated by Logan 🧠 · AI-Agent Migration Factory™ v4.0*
