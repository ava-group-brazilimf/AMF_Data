# 🔍 InventoryScout Agent - Complete Manual

**Agent ID:** `inventory-scout`  
**Name:** Scout  
**Version:** 1.0.0  
**Phase:** UPSTREAM  
**Gate:** Gate 1  
**Created:** February 12, 2026  

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Overview](#overview)
3. [When to Use](#when-to-use)
4. [Commands Reference](#commands-reference)
5. [Workflows](#workflows)
6. [Artifacts](#artifacts)
7. [Integration](#integration)
8. [Best Practices](#best-practices)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Activation

```
@inventory-scout
```

### Basic Workflow (5 minutes)

```bash
# 1. Scan repository
*scan-repo /path/to/legacy-platform

# 2. Analyze configurations
*analyze-configs

# 3. Detect technologies
*detect-tech-stack

# 4. Map dependencies
*map-dependencies

# 5. Build lineage
*build-lineage

# 6. Export report
*export-inventory

# 7. Check status
*status
```

### Output Location

All artifacts are saved to:
```
projects/{project_name}/outputs/upstream/inventory/
```

---

## Overview

### What is InventoryScout?

InventoryScout (Scout 🔍) is a specialized AI agent designed to **scan legacy data platform repositories**, **identify technical assets**, and **build knowledge graphs** that capture dependencies and data lineage. Essential for migration and modernization projects.

### Key Capabilities

| Capability | Description |
|-----------|-------------|
| **Repository Scanning** | Recursive file discovery and categorization |
| **Configuration Analysis** | Parse XML, YAML, JSON, Properties files |
| **Dependency Mapping** | Build graph of component dependencies |
| **Technology Detection** | Identify frameworks, versions, cloud services |
| **Lineage Building** | Trace source-to-target data flows |
| **Asset Cataloging** | Inventory pipelines, jobs, databases, APIs |
| **Knowledge Graph** | Export structured graphs (JSON, GraphML) |
| **Security Scanning** | Flag hard-coded credentials and secrets |

### Supported Technologies

- **Orchestration:** ADF, Databricks, Airflow, SAP BODS, Informatica, SSIS, dbt
- **Languages:** Python, SQL, Scala, Java, Shell
- **Configs:** XML, YAML, JSON, Properties, INI, Terraform
- **Outputs:** Markdown, JSON, GraphML, CSV, Mermaid

---

## When to Use

### ✅ Use InventoryScout When:

- **Migration projects** (Legacy → Cloud, Platform modernization)
- **Complex architectures** with multiple technologies
- **Undocumented systems** needing reverse engineering
- **Multiple repositories** requiring consolidation
- **Dependency analysis** before refactoring
- Working with ADF, Databricks, Airflow, BODS, Informatica, SSIS, dbt

### ❌ Don't Use When:

- **Greenfield projects** (building from scratch)
- **Well-documented** simple architectures
- **No legacy code** to analyze
- **Business logic** analysis needed (use BusinessAnalyst)
- **Data profiling** needed (use DataEngineerExec)

### Timing

```
DataStrategist (Alex) → InventoryScout (Scout) → BusinessAnalyst (Mary)
   *define-problem    →    *scan-repo, etc.    →    *create-sttm
```

**Scout runs AFTER problem definition and BEFORE STTM creation.**

---

## Commands Reference

### Core Commands

| Command | Purpose | Priority | Outputs |
|---------|---------|----------|---------|
| `*scan-repo` | Scan repository and identify files | ⭐ MANDATORY | inventory-map.md |
| `*analyze-configs` | Parse config files | ⭐ MANDATORY | Updated inventory-map.md, asset-catalog.md |
| `*map-dependencies` | Build dependency graph | ⭐ MANDATORY | dependency-graph.json |
| `*detect-tech-stack` | Identify technologies | ⚠️ RECOMMENDED | tech-stack-detected.md |
| `*build-lineage` | Trace data flows | ⚠️ RECOMMENDED | lineage-map.md |
| `*catalog-assets` | Create asset catalog | ⚠️ RECOMMENDED | asset-catalog.md |
| `*generate-knowledge-graph` | Export structured graph | 💡 OPTIONAL | knowledge-graph.json |
| `*export-inventory` | Generate executive report | ⚠️ RECOMMENDED | inventory-report.md |

### Utility Commands

| Command | Purpose |
|---------|---------|
| `*help` | Show all available commands |
| `*status` / `*WS` | Show progress on artifacts |
| `*dismiss` / `*DA` | End Scout session |

---

## Workflows

### Workflow 1: Complete Inventory (Recommended)

**Duration:** 15-30 minutes (depends on repo size)

```bash
@inventory-scout

# Step 1: Scan repository structure
*scan-repo /path/to/legacy-platform
# ✅ Output: inventory-map.md

# Step 2: Analyze configuration files
*analyze-configs
# ✅ Output: Updated inventory-map.md, asset-catalog.md

# Step 3: Detect technologies and versions
*detect-tech-stack
# ✅ Output: tech-stack-detected.md

# Step 4: Map dependencies between components
*map-dependencies
# ✅ Output: dependency-graph.json

# Step 5: Build data lineage
*build-lineage
# ✅ Output: lineage-map.md

# Step 6: Generate knowledge graph (optional)
*generate-knowledge-graph
# ✅ Output: knowledge-graph.json, GraphML, HTML

# Step 7: Export final report
*export-inventory
# ✅ Output: inventory-report.md

# Step 8: Verify completion
*status
```

### Workflow 2: Quick Scan (5 minutes)

For simple assessments or POCs:

```bash
@inventory-scout

*scan-repo /path/to/repo
*detect-tech-stack
*export-inventory

*status
```

### Workflow 3: Focused Analysis

For specific subsystems:

```bash
@inventory-scout

*scan-repo /path/to/repo/adf-pipelines
*analyze-configs
*map-dependencies
*export-inventory
```

---

## Artifacts

### Required Artifacts (Gate 1 - Migration Projects)

#### 1. inventory-map.md

**Purpose:** Complete repository structure and statistics  
**Location:** `projects/{project_name}/outputs/upstream/inventory/inventory-map.md`  
**Generated by:** `*scan-repo`, `*analyze-configs`

**Contents:**
- Summary statistics (file counts, sizes)
- Files by extension (table with percentages)
- Directory structure (ASCII tree)
- Hot spots (high-activity areas)
- Red flags (security issues, technical debt)

**Example:**
```markdown
# Repository Inventory Map

## Summary Statistics
| Metric | Value |
|--------|-------|
| Total Files | 1,247 |
| Total Size | 3.2 GB |
| Directories | 89 |
| Max Depth | 7 levels |

## Files by Extension
| Extension | Count | % | Purpose |
|-----------|-------|---|---------|
| .py | 342 | 27.4% | Python scripts |
| .json | 298 | 23.9% | ADF pipelines |
...
```

#### 2. dependency-graph.json

**Purpose:** Structured dependency graph (nodes + edges)  
**Location:** `projects/{project_name}/outputs/upstream/inventory/dependency-graph.json`  
**Generated by:** `*map-dependencies`

**Contents:**
- Nodes: Components (pipelines, data sources, datasets)
- Edges: Dependencies, data flows
- Metadata: File paths, technologies, properties

**Example:**
```json
{
  "nodes": [
    {"id": "pipeline_001", "type": "Pipeline", "name": "SalesIngestion"},
    {"id": "datasource_001", "type": "DataSource", "name": "SQL_SalesDB"}
  ],
  "edges": [
    {"source": "pipeline_001", "target": "datasource_001", "type": "READS_FROM"}
  ]
}
```

#### 3. asset-catalog.md

**Purpose:** Catalog of all data assets  
**Location:** `projects/{project_name}/outputs/upstream/inventory/asset-catalog.md`  
**Generated by:** `*catalog-assets`, `*analyze-configs`

**Contents:**
- All pipelines/jobs (name, technology, file path, status)
- All data sources (databases, APIs, files)
- All datasets (tables, files, collections)
- Scheduled jobs (cron, triggers)
- Configuration files

**Example:**
```markdown
# Asset Catalog

## Pipelines (87 total)
| Name | Technology | Status | File |
|------|-----------|--------|------|
| SalesIngestion | ADF | Active | pipelines/sales.json |
...

## Data Sources (23 total)
| Name | Type | Connection |
|------|------|-----------|
| SQL_SalesDB | SQL Server | LinkedService_SQL |
...
```

### Recommended Artifacts

#### 4. tech-stack-detected.md

**Purpose:** Technologies, versions, frameworks identified  
**Location:** `projects/{project_name}/outputs/upstream/inventory/tech-stack-detected.md`  
**Generated by:** `*detect-tech-stack`

**Example:**
```markdown
# Technology Stack Detected

## Primary Technologies
| Technology | Version | File Count | Usage |
|------------|---------|------------|-------|
| Azure Data Factory | v2 | 298 | Orchestration |
| Databricks | 11.3 LTS | 342 | Processing |
| Apache Airflow | 2.5.0 | 127 | Scheduling |
...
```

#### 5. lineage-map.md

**Purpose:** Data lineage and transformation chains  
**Location:** `projects/{project_name}/outputs/upstream/inventory/lineage-map.md`  
**Generated by:** `*build-lineage`

**Example:**
```markdown
# Data Lineage Map

## Lineage Flows (12 identified)

### Flow 1: Sales Orders
Source: SQL Server (SalesDB.dbo.orders)
  ↓ ADF Pipeline: SalesIngestion
  ↓ Transform: CleanseAndEnrich
  ↓ Databricks Job: AggregateOrders
Target: Azure Synapse (DW.fact_orders)
```

### Optional Artifacts

#### 6. knowledge-graph.json

**Purpose:** Export for Neo4j, Gephi (GraphML/JSON)  
**Location:** `projects/{project_name}/outputs/upstream/inventory/knowledge-graph.json`  
**Generated by:** `*generate-knowledge-graph`

---

## Integration

### Receives From

| Agent | Artifact | Purpose |
|-------|----------|---------|
| DataStrategist (Alex) | problem-statement.md | Understand migration scope |

### Sends To

| Agent | Artifact | Purpose |
|-------|----------|---------|
| BusinessAnalyst (Mary) | inventory-map.md | Input for STTM creation |
| BusinessAnalyst (Mary) | asset-catalog.md | Reference for mappings |
| DataArchitect (Winston) | tech-stack-detected.md | Target architecture planning |
| DataArchitect (Winston) | dependency-graph.json | Complexity assessment |
| DataSteward (Gaia) | lineage-map.md | Governance planning |

### Example Integration Flow

```
┌─────────────────────────────────────────┐
│ Alex (DataStrategist)                  │
│ *define-problem                         │
│ Output: problem-statement.md            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ Scout (InventoryScout)  ⭐ YOU ARE HERE│
│ *scan-repo, *analyze-configs, etc.     │
│ Outputs:                                │
│   - inventory-map.md                    │
│   - asset-catalog.md                    │
│   - dependency-graph.json               │
│   - tech-stack-detected.md              │
│   - lineage-map.md                      │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│ Mary          │   │ Winston       │
│ (Business     │   │ (Data         │
│  Analyst)     │   │  Architect)   │
│               │   │               │
│ Uses:         │   │ Uses:         │
│ • inventory-  │   │ • tech-stack- │
│   map.md      │   │   detected.md │
│ • asset-      │   │ • dependency- │
│   catalog.md  │   │   graph.json  │
│               │   │               │
│ *create-sttm  │   │ *create-      │
│               │   │  architecture │
└───────────────┘   └───────────────┘
```

---

## Best Practices

### Execution Order

1. ✅ Always run `*scan-repo` first
2. ✅ Then `*analyze-configs`
3. ✅ Then `*detect-tech-stack`
4. ✅ Then `*map-dependencies`
5. ✅ Then `*build-lineage`
6. ✅ Finally `*export-inventory`

### Security

- ✅ Always anonymize credentials
- ✅ Redact connection strings (show structure only)
- ✅ Use vault references (e.g., `@{KeyVault.secret-name}`)
- ✅ Flag hard-coded secrets as RED FLAGS
- ✅ Never include PII in outputs

### Quality

- ✅ Parse files properly (not just regex)
- ✅ Validate syntax (JSON, YAML, XML)
- ✅ Handle encoding issues (UTF-8, Latin-1)
- ✅ Report parsing errors separately
- ✅ Include dead code (mark as unused)

### Performance

- ✅ Exclude build artifacts (dist, build, node_modules)
- ✅ Use exclusion patterns for large repos
- ✅ Limit depth for very deep hierarchies
- ✅ Run in batches for very large repos (> 50k files)

---

## Examples

### Example 1: ADF + Databricks Migration

**Scenario:** Migrate ADF pipelines and Databricks notebooks to new Medallion architecture

```bash
@inventory-scout

# Scan ADF and Databricks repos
*scan-repo /legacy/adf-pipelines
*scan-repo /legacy/databricks-notebooks

# Analyze all configs
*analyze-configs

# Detect current tech stack
*detect-tech-stack

# Map dependencies between ADF and Databricks
*map-dependencies

# Build lineage
*build-lineage

# Generate knowledge graph
*generate-knowledge-graph

# Export for stakeholders
*export-inventory

# Check status
*status

# Handoff to Mary
@business-analyst *create-sttm
```

### Example 2: Airflow DAGs Assessment

**Scenario:** Quick assessment of Airflow DAGs complexity

```bash
@inventory-scout

*scan-repo /airflow/dags
*detect-tech-stack
*map-dependencies
*export-inventory
```

### Example 3: SAP BODS Job Analysis

**Scenario:** Analyze SAP BODS XML exports

```bash
@inventory-scout

*scan-repo /bods-exports
*analyze-configs
*build-lineage
*export-inventory
```

---

## Troubleshooting

### Issue: Repository path not found

**Symptom:** Error: "Repository path does not exist"

**Solution:**
1. Verify path is correct (absolute or relative)
2. Check permissions
3. Use forward slashes or escape backslashes on Windows

### Issue: Large repository taking too long

**Symptom:** Scan running for > 10 minutes

**Solution:**
1. Exclude build artifacts: `*scan-repo /path --exclude node_modules,dist,build`
2. Limit depth: `*scan-repo /path --max-depth 5`
3. Scan subsystems separately

### Issue: Parsing errors in config files

**Symptom:** "Failed to parse X files"

**Solution:**
1. Check encoding (use UTF-8)
2. Validate syntax manually
3. Review error log in output
4. Continue with valid files

### Issue: Hard-coded credentials found

**Symptom:** Red flags in inventory-map.md

**Solution:**
1. Review flagged files
2. Replace with vault references
3. Update configs before migration
4. Document in security review

### Issue: Dependency graph too complex

**Symptom:** knowledge-graph.json has 1000s of nodes

**Solution:**
1. Filter by subsystem
2. Focus on critical paths only
3. Use Neo4j for large graphs (better performance)

---

## FAQ

**Q: Do I always need Scout?**  
A: For greenfield projects, **no**. For migrations/modernizations, **YES**.

**Q: Can Scout profile actual data?**  
A: No. Scout scans code and configs. Use DataEngineerExec (`*profile-data`) for data profiling.

**Q: What if I have multiple repositories?**  
A: Run `*scan-repo` multiple times, one per repo. Scout will merge results.

**Q: Can Scout detect data quality issues?**  
A: No. Scout maps structure. Use DataSteward (Gaia) for DQ rules and validation.

**Q: Where does Scout output go?**  
A: `projects/{project_name}/outputs/upstream/inventory/` folder.

**Q: Can I customize the knowledge graph schema?**  
A: Yes. Edit `.avanade-core/core-config.yaml` to add custom node/edge types.

**Q: How do I import into Neo4j?**  
A: Use `knowledge-graph.graphml` file. Import → Select file → Map labels → Import.

---

## Command Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 🔍 INVENTORYSCOUT QUICK REFERENCE                       │
├──────────────────────────────────────────────────────────┤
│ ACTIVATION:                                              │
│   @inventory-scout                                       │
│                                                          │
│ ESSENTIAL COMMANDS:                                      │
│   *scan-repo /path          → Scan repository            │
│   *analyze-configs          → Parse configs              │
│   *map-dependencies         → Build dependency graph     │
│   *detect-tech-stack        → Identify technologies      │
│   *build-lineage            → Trace data flows           │
│   *export-inventory         → Generate final report      │
│                                                          │
│ UTILITY:                                                 │
│   *help                     → Show all commands          │
│   *status                   → Check progress             │
│   *dismiss                  → End session                │
│                                                          │
│ OUTPUTS:                                                 │
│   projects/{project_name}/outputs/upstream/inventory/        → All artifacts here         │
│                                                          │
│ INTEGRATION:                                             │
│   inventory-map.md          → Handoff to Mary (STTM)     │
│   tech-stack-detected.md    → Handoff to Winston (Arch)  │
│   lineage-map.md            → Handoff to Gaia (Gov)      │
└──────────────────────────────────────────────────────────┘
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-12 | Initial release |

---

## Resources

- **Agent Definition:** `.avanade-core/agents/inventory-scout.md`
- **Configuration:** `.avanade-core/core-config.yaml`
- **Tasks:** `.avanade-core/tasks/*.md`
- **Framework Docs:** `Docs/agents-spec/GUIA-DE-USO-AGENTES.md`

---

## Contact & Support

- **Framework:** Avanade™ Core for Data Engineering
- **Phase:** UPSTREAM
- **Chatmode:** `@inventory-scout`
- **Orchestrator:** Use `*route` for Scout recommendation

---

**🔍 Scout - Discover the unknown, map the complex, light the path.**
