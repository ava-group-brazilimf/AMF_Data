# Create Digital Twin Task

**Task ID:** create-digital-twin  
**Agent:** Logan (Logic Extractor)  
**Version:** 1.0  
**Command:** `*create-digital-twin`  
**Phase:** UPSTREAM

---

## Purpose

Create a semantic blueprint (Digital Twin) that maps the entire legacy environment across three layers: **Physical** (what exists today), **Semantic** (what it means), and **Target** (where it will exist). The Digital Twin is the central reference artifact for all downstream agents.

---

## Prerequisites

- `inventory.json` from Discovery Scout
- `dependency-graph.json` from Discovery Scout
- Pseudocode generated for all (or most) pipelines in scope
- `*extract-logic` and `*generate-pseudocode` completed

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| scope | string | Yes | "full" or "incremental" (add new pipelines) |
| pipeline_ids | list | No | Specific pipeline IDs (default: all in inventory) |
| target_platform | string | Yes | Target platform (e.g., "Databricks", "Synapse") |

---

## Execution Steps

### Step 1: Load Source Artifacts

```
LOAD inventory.json from Discovery Scout
LOAD dependency-graph.json from Discovery Scout
LOAD all pseudocode files from projects/{project_name}/outputs/upstream/logic/pseudocode/
VALIDATE that pseudocode exists for >= 80% of pipelines
IF coverage < 80%:
  WARN "Incomplete extraction — Digital Twin will have gaps"
  LIST missing pipelines
```

### Step 2: Build Physical Layer

```
FOR EACH object in inventory:
  MAP physical layer:
    {
      "physical_id": unique_id,
      "type": "table|pipeline|job|script|udf|config",
      "name": object_name,
      "platform": source_platform,
      "location": physical_location,
      "schema": {columns, types, partitions},
      "dependencies": [upstream_ids, downstream_ids],
      "complexity": complexity_score,
      "status": "active|deprecated|orphan",
      "last_modified": timestamp,
      "owner": data_owner
    }

BUILD physical layer graph (DAG)
VALIDATE against dependency-graph.json for consistency
```

### Step 3: Build Semantic Layer

```
FOR EACH physical object:
  DERIVE semantic meaning:
    {
      "semantic_id": unique_id,
      "physical_ref": physical_id,
      "business_name": human_readable_name,
      "business_domain": domain_classification,
      "business_description": what_it_represents,
      "business_rules": [rules from pseudocode],
      "data_classification": "PII|financial|operational|reference",
      "data_quality_rules": [quality checks from extraction],
      "lineage": {
        "sources": [upstream semantic entities],
        "targets": [downstream semantic entities]
      },
      "sme_owner": business_owner,
      "confidence": semantic_mapping_confidence
    }

USE LLM to enrich semantic descriptions:
  - Infer business domain from naming patterns
  - Classify data sensitivity
  - Suggest business-friendly names
  - Identify related business processes
```

### Step 4: Build Target Layer

```
FOR EACH semantic entity:
  MAP to target platform:
    {
      "target_id": unique_id,
      "semantic_ref": semantic_id,
      "target_platform": target_platform,
      "target_type": "delta_table|notebook|job|workflow",
      "target_location": suggested_path,
      "target_schema": {
        "catalog": target_catalog,
        "schema": target_schema,
        "table": target_table_name
      },
      "medallion_layer": "bronze|silver|gold",
      "storage_format": "delta|parquet|json",
      "partitioning": suggested_partition_strategy,
      "migration_strategy": "lift-and-shift|refactor|rebuild",
      "estimated_effort": effort_hours,
      "dependencies_resolved": boolean
    }
```

### Step 5: Cross-Reference and Validate

```
VALIDATE cross-layer consistency:
  CHECK every physical object has a semantic mapping
  CHECK every semantic entity has a target mapping
  CHECK dependency graph is preserved across layers
  CHECK no orphan entities in any layer
  CHECK data lineage is complete end-to-end

CALCULATE metrics:
  - physical_coverage: mapped/total physical objects
  - semantic_enrichment: enriched/total semantic entities
  - target_readiness: fully_mapped/total target entities
  - overall_confidence: weighted average confidence
```

### Step 6: Generate Digital Twin Output

```
BUILD digital twin document:
  {
    "digital_twin_id": unique_id,
    "creation_date": current_timestamp,
    "version": "1.0",
    "scope": scope,
    "source_platform": source_platform,
    "target_platform": target_platform,
    "layers": {
      "physical": [physical entities],
      "semantic": [semantic entities],
      "target": [target entities]
    },
    "cross_references": [layer mappings],
    "metrics": {
      "total_objects": count,
      "physical_coverage": percentage,
      "semantic_enrichment": percentage,
      "target_readiness": percentage,
      "overall_confidence": score
    },
    "gaps": [unmapped or low-confidence items],
    "sme_review_items": [items requiring human review]
  }

SAVE to projects/{project_name}/outputs/upstream/logic/digital-twin/digital-twin.json
LOG creation in audit trail
```

---

## Output

| Output | Format | Location |
|--------|--------|----------|
| Digital Twin | JSON | `projects/{project_name}/outputs/upstream/logic/digital-twin/digital-twin.json` |
| Gap Analysis | MD | `projects/{project_name}/outputs/upstream/logic/reports/digital-twin-gaps.md` |

---

## Quality Criteria

- 100% physical objects mapped from inventory
- >= 90% semantic layer enriched with business context
- 100% target layer has platform mapping
- Dependency graph preserved across all three layers
- Data lineage traceable end-to-end
- Gap analysis documented for unmapped items
- Overall confidence score >= 0.80

---

*Task defined by AI-Agent Migration Factory™ v4.0*
