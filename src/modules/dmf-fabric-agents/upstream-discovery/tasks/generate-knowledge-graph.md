# Task: Generate Knowledge Graph (*generate-knowledge-graph)

**Command:** `*generate-knowledge-graph`  
**Agent:** InventoryScout (Scout 🔍)  
**Phase:** UPSTREAM  
**Priority:** OPTIONAL (but recommended for complex systems)

---

## Purpose

Convert all inventory artifacts into a structured knowledge graph (JSON/GraphML format) that can be imported into Neo4j, Gephi, or other graph analysis tools for advanced visualization and analysis.

---

## When to Use

- ✅ Complex systems with many dependencies
- ✅ Need interactive visualization
- ✅ Want to query graph (e.g., "find all pipelines reading from X")
- ✅ Architecture modernization planning
- ✅ Impact analysis ("what breaks if I change X?")

---

## Prerequisites

Must run these commands first:
1. ✅ `*scan-repo`
2. ✅ `*analyze-configs`
3. ✅ `*map-dependencies`
4. ✅ `*build-lineage`

---

## Graph Schema

### Node Types

```yaml
DataSource:
  properties:
    - id: unique identifier
    - name: source name
    - type: [Database, API, FileSystem, CloudStorage]
    - connection_ref: reference to connection config
    - metadata: additional properties

Pipeline:
  properties:
    - id: unique identifier
    - name: pipeline/job name
    - technology: [ADF, Databricks, Airflow, SSIS, etc.]
    - file_path: path to definition file
    - schedule: cron or trigger info
    - status: [active, inactive, deprecated]
    - metadata: additional properties

Dataset:
  properties:
    - id: unique identifier
    - name: table/file/collection name
    - location: full path or connection string
    - schema: column definitions (if available)
    - row_count_estimate: approximate rows
    - last_modified: timestamp
    - metadata: additional properties

Transformation:
  properties:
    - id: unique identifier
    - name: transformation name
    - type: [Mapping, Filter, Aggregate, Join, Custom]
    - source_code_ref: path to code
    - metadata: additional properties

Schedule:
  properties:
    - id: unique identifier
    - name: schedule name
    - cron: cron expression
    - frequency: human-readable frequency
    - trigger_type: [Time, Event, Manual]
    - metadata: additional properties

Configuration:
  properties:
    - id: unique identifier
    - name: config file name
    - file_path: path to config
    - environment: [dev, test, prod]
    - key_value_pairs: config contents (anonymized)
    - metadata: additional properties
```

### Edge Types

```yaml
DEPENDS_ON:
  description: "Component A depends on Component B"
  properties:
    - dependency_type: [code, config, runtime]
    - required: boolean

READS_FROM:
  description: "Pipeline reads data from DataSource"
  properties:
    - query: SQL query or filter (if available)
    - read_mode: [full, incremental, streaming]
    - metadata: additional info

WRITES_TO:
  description: "Pipeline writes data to Dataset"
  properties:
    - write_mode: [append, overwrite, merge]
    - partition_key: partition columns
    - metadata: additional info

TRANSFORMS:
  description: "Transformation applied to data"
  properties:
    - transformation_logic: description or code ref
    - metadata: additional info

TRIGGERS:
  description: "Schedule triggers Pipeline"
  properties:
    - enabled: boolean
    - last_run: timestamp
    - metadata: additional info

REFERENCES:
  description: "Config references secret/parameter"
  properties:
    - reference_type: [secret, parameter, connection]
    - vault_name: key vault name (if applicable)
    - metadata: additional info
```

---

## Output Format

### JSON (Default)

```json
{
  "metadata": {
    "created": "2026-02-12T10:30:00Z",
    "agent": "inventory-scout",
    "version": "1.0",
    "repository": "/path/to/repo",
    "node_count": 156,
    "edge_count": 342
  },
  "nodes": [
    {
      "id": "pipeline_001",
      "type": "Pipeline",
      "name": "SalesDataIngestion",
      "technology": "Azure Data Factory",
      "file_path": "pipelines/sales_ingestion.json",
      "metadata": {
        "schedule": "daily",
        "owner": "data-team",
        "status": "active"
      }
    },
    {
      "id": "datasource_001",
      "type": "DataSource",
      "name": "SQL_Server_SalesDB",
      "technology": "SQL Server",
      "connection_string_ref": "LinkedService_SQLServer",
      "metadata": {
        "database": "SalesDB",
        "schemas": ["dbo", "staging"]
      }
    }
  ],
  "edges": [
    {
      "source": "pipeline_001",
      "target": "datasource_001",
      "type": "READS_FROM",
      "metadata": {
        "query": "SELECT * FROM dbo.customers WHERE modified_date > @LastRun"
      }
    }
  ]
}
```

### GraphML (For Neo4j/Gephi)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <key id="name" for="node" attr.name="name" attr.type="string"/>
  <graph id="G" edgedefault="directed">
    <node id="pipeline_001">
      <data key="type">Pipeline</data>
      <data key="name">SalesDataIngestion</data>
    </node>
    <edge source="pipeline_001" target="datasource_001">
      <data key="relationship">READS_FROM</data>
    </edge>
  </graph>
</graphml>
```

---

## Process

### Step 1: Collect All Artifacts
```
Read:
  - inventory-map.md
  - dependency-graph.json
  - asset-catalog.md
  - lineage-map.md
```

### Step 2: Build Node Registry
```
For each asset:
  1. Assign unique ID (type_NNN)
  2. Determine node type
  3. Extract properties
  4. Anonymize sensitive data
  5. Add to nodes array
```

### Step 3: Build Edge Registry
```
For each relationship:
  1. Identify source and target nodes
  2. Determine edge type
  3. Extract relationship properties
  4. Add to edges array
```

### Step 4: Enrich with Metadata
```
Add:
  - File paths
  - Line numbers
  - Technologies
  - Schedules
  - Owners (if available)
```

### Step 5: Validate Graph
```
Check:
  ✅ All edges reference valid nodes
  ✅ No orphaned nodes (unless intentional)
  ✅ No cycles in config dependencies
  ✅ All IDs unique
```

### Step 6: Export Formats
```
Generate:
  1. knowledge-graph.json (default)
  2. knowledge-graph.graphml (for Neo4j)
  3. knowledge-graph.gexf (for Gephi)
  4. knowledge-graph-vis.html (interactive PyVis)
```

---

## Outputs

### Primary Output
**File:** `projects/{project_name}/outputs/upstream/inventory/knowledge-graph.json`

### Additional Outputs
- `projects/{project_name}/outputs/upstream/inventory/graphs/knowledge-graph.graphml`
- `projects/{project_name}/outputs/upstream/inventory/graphs/knowledge-graph.gexf`
- `projects/{project_name}/outputs/upstream/inventory/graphs/knowledge-graph-vis.html` (interactive)

---

## Import to Neo4j

### Using Cypher
```cypher
// Load JSON into Neo4j
CALL apoc.load.json('file:///knowledge-graph.json') YIELD value
UNWIND value.nodes AS node
MERGE (n:Asset {id: node.id})
SET n += node

WITH value
UNWIND value.edges AS edge
MATCH (source:Asset {id: edge.source})
MATCH (target:Asset {id: edge.target})
CALL apoc.create.relationship(source, edge.type, edge.metadata, target) YIELD rel
RETURN count(rel)
```

### Using GraphML
```
1. Open Neo4j Desktop
2. Select your database
3. Go to Import
4. Select knowledge-graph.graphml
5. Map node labels and relationship types
6. Import
```

---

## Example Queries (Neo4j)

### Find all pipelines reading from a specific source
```cypher
MATCH (p:Pipeline)-[:READS_FROM]->(ds:DataSource {name: 'SQL_Server_SalesDB'})
RETURN p.name, p.technology, p.file_path
```

### Find transformation chains
```cypher
MATCH path = (source:DataSource)-[:READS_FROM*1..5]-(target:Dataset)
RETURN path
```

### Impact analysis
```cypher
// What breaks if I remove this dataset?
MATCH (d:Dataset {name: 'dim_customer'})<-[:WRITES_TO|READS_FROM]-(p:Pipeline)
RETURN p.name, p.technology
```

### Find circular dependencies
```cypher
MATCH (n)-[:DEPENDS_ON*]->(n)
RETURN n.name, n.type
```

---

## Visualization

### Interactive HTML (PyVis)
- Auto-generated at `projects/{project_name}/outputs/upstream/inventory/graphs/knowledge-graph-vis.html`
- Open in browser
- Interactive: zoom, pan, click nodes
- Color-coded by node type
- Edge labels show relationship types

### Import to Gephi
1. Open Gephi
2. File → Open → Select `knowledge-graph.gexf`
3. Choose layout (ForceAtlas2 recommended)
4. Apply colors by node type
5. Export as PNG/PDF

---

## Best Practices

### Performance
- ✅ Limit graph to critical paths for very large repos
- ✅ Use filters to focus on specific subsystems
- ✅ Export subgraphs for different stakeholders

### Security
- ✅ Anonymize all connection strings
- ✅ Redact credentials
- ✅ Use references to vaults, not actual keys

### Quality
- ✅ Validate all node IDs are unique
- ✅ Check for orphaned nodes
- ✅ Verify edge source/target exist
- ✅ Test import in Neo4j/Gephi

---

## Success Criteria

✅ **Complete when:**
- Graph generated successfully
- All nodes have valid IDs and types
- All edges reference existing nodes
- No circular dependencies in configs
- JSON/GraphML files created
- Interactive HTML visualization works

---

## Next Steps

After graph generation:
1. ✅ Import into Neo4j or Gephi
2. ✅ Run impact analysis queries
3. ✅ Share visualization with stakeholders
4. ✅ Use for architecture planning
5. ✅ Handoff to DataArchitect (Winston)

---

**Status:** ✅ Ready for use  
**Last Updated:** 2026-02-12
