# 🔍 InventoryScout Agent - Quick Start Guide

## Overview

The **InventoryScout Agent** (Scout 🔍) is a specialized AI assistant for scanning legacy data platform repositories, identifying technical assets, and building **knowledge graphs** that capture dependencies and data lineage. Essential for **migration and modernization projects**.

---

## When to Use This Agent

Use the InventoryScout agent when you need to:
- **Scan legacy repositories** (ADF, Databricks, Airflow, BODS, etc.)
- **Identify technical assets** (pipelines, jobs, data sources, configurations)
- **Build dependency graphs** and knowledge graphs
- **Detect technologies** and framework versions
- **Map data lineage** (source-to-target flows)
- **Catalog all data assets** before migration
- **Generate inventory reports** for stakeholders
- **Reverse engineer** undocumented systems

---

## Activating the Agent

To activate the InventoryScout agent in your workspace:

```
@inventory-scout
```

The agent will:
1. Greet you as "Scout"
2. Automatically display available commands (*help)
3. Wait for your instructions

---

## Available Commands

Type any command with the `*` prefix:

| Command | Description |
|---------|-------------|
| `*help` | Show numbered list of available commands |
| `*scan-repo` | ⭐ Scan repository and identify all files |
| `*analyze-configs` | ⭐ Parse config files (.xml, .yaml, .json, .properties) |
| `*map-dependencies` | ⭐ Build dependency graph from code and configs |
| `*detect-tech-stack` | Identify technologies, frameworks, versions |
| `*build-lineage` | Build data lineage map from pipelines |
| `*catalog-assets` | Create catalog of all data assets |
| `*generate-knowledge-graph` | Generate structured knowledge graph (JSON/GraphML) |
| `*export-inventory` | Export complete inventory report |
| `*status` / `*WS` | Show progress on artifacts |
| `*dismiss` / `*DA` | End Scout session |

---

---

## Quick Start: Complete Inventory Workflow

### Step-by-Step (15-30 minutes)

```bash
# 1. Activate Scout
@inventory-scout

# 2. Scan repository structure
*scan-repo /path/to/legacy-platform

# 3. Analyze configuration files  
*analyze-configs

# 4. Detect technologies and versions
*detect-tech-stack

# 5. Map dependencies
*map-dependencies

# 6. Build data lineage
*build-lineage

# 7. (Optional) Generate knowledge graph
*generate-knowledge-graph

# 8. Export final report
*export-inventory

# 9. Check status
*status
```

### Quick Scan (5 minutes)

For simple assessments:

```bash
@inventory-scout

*scan-repo /path/to/repo
*detect-tech-stack
*export-inventory
```

---

## Output Artifacts

All artifacts are saved to: **`projects/{project_name}/outputs/upstream/inventory/`**

### Required (Gate 1 - Migration Projects)

| Artifact | Description |
|----------|-------------|
| **inventory-map.md** | Complete file structure, statistics, hot spots |
| **dependency-graph.json** | Graph of dependencies (nodes + edges) |
| **asset-catalog.md** | Catalog of all data assets |

### Recommended

| Artifact | Description |
|----------|-------------|
| **tech-stack-detected.md** | Technologies, versions, frameworks |
| **lineage-map.md** | Data lineage and transformation chains |

### Optional

| Artifact | Description |
|----------|-------------|
| **knowledge-graph.json** | Export for Neo4j/Gephi (GraphML/JSON) |
| **inventory-report.md** | Executive summary |

---

## Supported Technologies

### Orchestration & ETL Platforms

- ✅ **Azure Data Factory** (JSON pipelines)
- ✅ **Databricks** (Python, Scala, SQL, Notebooks)
- ✅ **Apache Airflow** (Python DAGs, YAML)
- ✅ **SAP BODS** (XML, ATL exports)
- ✅ **Informatica PowerCenter** (XML, JSON)
- ✅ **SSIS** (DTSX, XML)
- ✅ **dbt** (SQL, YAML)

### File Types

| Category | Extensions |
|----------|-----------|
| **Pipelines** | .json, .py, .sql, .yaml, .xml, .scala, .ipynb |
| **Configs** | .properties, .config, .ini, .env, .yaml, .json, .xml |
| **Code** | .py, .sql, .scala, .java, .sh, .ps1 |
| **IaC** | .tf, .tfvars |

### Graph Export Formats

- JSON
- GraphML (Neo4j, Gephi)
- GEXF (Gephi)
- CSV
- Interactive HTML (PyVis)

---

## Integration with Other Agents

### Workflow Position

```
DataStrategist (Alex) → InventoryScout (Scout) → BusinessAnalyst (Mary)
   *define-problem    →    *scan-repo, etc.    →    *create-sttm
```

**Timing:** Scout runs AFTER problem definition and BEFORE STTM creation.

### Handoffs

| To Agent | Artifact | Purpose |
|----------|----------|---------|
| **BusinessAnalyst (Mary)** | inventory-map.md | Input for STTM creation |
| **BusinessAnalyst (Mary)** | asset-catalog.md | Reference for mappings |
| **DataArchitect (Winston)** | tech-stack-detected.md | Target architecture planning |
| **DataArchitect (Winston)** | dependency-graph.json | Complexity assessment |
| **DataSteward (Gaia)** | lineage-map.md | Governance planning |

---

## Key Features

### 1. Knowledge Graph Generation

Scout builds structured graphs with:
- **Nodes:** Pipelines, DataSources, Datasets, Transformations, Schedules
- **Edges:** DEPENDS_ON, READS_FROM, WRITES_TO, TRANSFORMS, TRIGGERS
- **Export:** JSON, GraphML, GEXF for Neo4j, Gephi

### 2. Security Scanning

- ✅ Detects hard-coded credentials
- ✅ Flags exposed connection strings
- ✅ Anonymizes sensitive data in outputs
- ✅ Recommends vault references

### 3. Technology Detection

Automatically identifies:
- Orchestration platforms (ADF, Databricks, Airflow)
- Framework versions
- Programming languages
- Cloud services
- Deployment patterns

### 4. Data Lineage Mapping

Traces data flows:
- Source → Transformation → Target
- Identifies transformation chains
- Finds critical paths
- Detects dead code

---

## Example: ADF + Databricks Migration

### Scenario
Migrate ADF pipelines and Databricks notebooks to Medallion architecture.

### Commands

```bash
@inventory-scout

# Scan both repos
*scan-repo /legacy/adf-pipelines
*scan-repo /legacy/databricks-notebooks

# Analyze all configs
*analyze-configs

# Detect current tech stack
*detect-tech-stack

# Map dependencies
*map-dependencies

# Build lineage
*build-lineage

# Generate knowledge graph for visualization
*generate-knowledge-graph

# Export final report
*export-inventory

# Check completion
*status

# Handoff to BusinessAnalyst
@business-analyst *create-sttm
```

### Outputs

```
projects/{project_name}/outputs/upstream/inventory/
├── inventory-map.md              (1,247 files cataloged)
├── dependency-graph.json         (342 dependencies mapped)
├── asset-catalog.md              (87 pipelines, 23 data sources)
├── tech-stack-detected.md        (ADF v2, Databricks 11.3 LTS)
├── lineage-map.md                (12 lineage flows documented)
├── knowledge-graph.json          (Neo4j ready)
└── inventory-report.md           (Executive summary)
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
- ✅ Redact connection strings
- ✅ Use vault references instead of actual keys
- ✅ Flag hard-coded secrets as RED FLAGS
- ✅ Never include PII in outputs

### Performance

- ✅ Exclude build artifacts: `--exclude node_modules,dist,build`
- ✅ Limit depth for very deep hierarchies: `--max-depth 5`
- ✅ Scan subsystems separately for large repos
- ✅ Generate knowledge graphs only when needed (complex systems)

---

## When NOT to Use Scout

❌ **Greenfield projects** (building from scratch)  
❌ **Well-documented** simple architectures  
❌ **No legacy code** to analyze  
❌ **Business logic** analysis (use BusinessAnalyst)  
❌ **Data profiling** (use DataEngineerExec)

---

## Complete Documentation

For detailed documentation, see:

- **[INVENTORY-SCOUT-MANUAL.md](INVENTORY-SCOUT-MANUAL.md)** - Complete manual (50+ pages)
- **[.avanade-core/agents/inventory-scout.md](.avanade-core/agents/inventory-scout.md)** - Agent definition
- **[.avanade-core/core-config.yaml](.avanade-core/core-config.yaml)** - Configuration
- **[.avanade-core/tasks/](.avanade-core/tasks/)** - Individual command documentation
- **[Docs/agents-spec/GUIA-DE-USO-AGENTES.md](../Docs/agents-spec/GUIA-DE-USO-AGENTES.md)** - Framework guide

---

## Folder Structure

```
inventory-scout-agent/
├── README.md                           (Quick start - this file)
├── INVENTORY-SCOUT-MANUAL.md           (Complete manual)
├── .avanade-core/
│   ├── agents/
│   │   └── inventory-scout.md          (Agent definition)
│   ├── tasks/
│   │   ├── scan-repo.md                (Command: *scan-repo)
│   │   ├── generate-knowledge-graph.md (Command: *generate-knowledge-graph)
│   │   └── ...                         (Other commands)
│   ├── checklists/
│   ├── templates/
│   ├── data/
│   └── core-config.yaml                (Configuration)
└── projects/{project_name}/outputs/upstream/inventory/                  (Generated artifacts)
    ├── README.md
    ├── inventory-map.md
    ├── dependency-graph.json
    ├── asset-catalog.md
    ├── tech-stack-detected.md
    ├── lineage-map.md
    ├── knowledge-graph.json
    ├── inventory-report.md
    ├── graphs/
    │   ├── knowledge-graph-vis.html    (Interactive visualization)
    │   ├── knowledge-graph.graphml     (Neo4j import)
    │   └── lineage-diagram.mmd         (Mermaid diagram)
    └── exports/
        ├── file-inventory.csv
        ├── asset-list.csv
        └── dependency-matrix.csv
```

---

## FAQ

**Q: Do I always need Scout?**  
A: For greenfield projects, **no**. For migrations/modernizations, **YES**.

**Q: Can Scout profile actual data?**  
A: No. Scout scans code and configs. Use DataEngineerExec (`*profile-data`) for data profiling.

**Q: What if I have SAP BODS jobs?**  
A: Scout can scan XML exports of BODS jobs. Export ATL files to XML first.

**Q: Can Scout detect data quality issues?**  
A: No. Scout maps structure. Use DataSteward (Gaia) for DQ rules.

**Q: Where does Scout output go?**  
A: `projects/{project_name}/outputs/upstream/inventory/` folder in the agent directory.

**Q: How do I import into Neo4j?**  
A: Use `knowledge-graph.graphml` file. Import → Select file → Map labels → Import.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-12 | Initial release |

---

## Contact & Support

- **Framework:** Avanade™ Core for Data Engineering
- **Phase:** UPSTREAM
- **Gate:** Gate 1 (Post-Discovery)
- **Chatmode:** `@inventory-scout`
- **Orchestrator:** Use `*route` for Scout recommendation
- **Manual:** [INVENTORY-SCOUT-MANUAL.md](INVENTORY-SCOUT-MANUAL.md)

---

**🔍 Scout - Discover the unknown, map the complex, light the path.**
