# Task: Scan Source Platform

```yaml
task_id: scan-repo
agent: discovery-scout
version: "4.0"
command: "*scan-repo"
phase: UPSTREAM
gate: 1
output: "inventory.json"
output_folder: "projects/{project_name}/outputs/upstream/discovery/inventory/"
```

---

## Purpose

Scan the entire source platform to discover and catalog every object — databases, tables, views, stored procedures, pipelines, jobs, scripts, configurations, and connections. This task produces the foundational inventory that all subsequent agents depend on.

---

## Pre-Conditions

- [ ] Source platform connection configuration available (`source-connection-config.yaml`)
- [ ] Read-only access credentials validated
- [ ] Target output directory exists
- [ ] Migration plan received from Migration Coordinator (optional but recommended)
- [ ] IF source.type = powercenter: .xml export file(s) present in project/legacy/
      OR pmrep CLI accessible with read-only credentials
- [ ] IF source.type = spark_generic: legacy_path contém ao menos um arquivo
  .sql, .py ou .scala
- [ ] IF source.type = synapse: legacy_path contém as pastas do Git export do
  workspace (mínimo: pipeline/ ou sqlscript/)

---

## Execution Steps

### Step 1 — Connect to Source Platform

```
1.1  Load connection configuration from source-connection-config.yaml
1.2  Read source.type from wave-config.yaml and initialize connector:
     - cloudera / hadoop  → connectors: hive-metastore, hdfs, oozie, hue
     - ssis               → connectors: msdb-catalog, dtsx-parser
     - airflow            → connectors: airflow-api, dag-parser
     - powercenter        → connectors: pmrep-cli OR xml-export-parser
                            IF pmrep-cli available: connect to Repository Service
                            ELSE: locate .xml export files in project/legacy/
                                  validate XML root element = POWERMART schema
                                  log PowerCenter version from XML attributes
     - sap_bods           → connectors: bods-repository, xml-parser
     - spark_generic      → connectors: file-scanner
       (aliases: spark, mixed, sqlserver, mssql)
                            Enumerate all .sql/.py/.scala/.sh files in legacy_path
                            No platform API — pure file-based scan
     - synapse            → connectors: synapse-git-export-parser
       (alias: azure_synapse)
                            Locate workspace Git export folders in legacy_path:
                            pipeline/, dataset/, linkedService/, notebook/,
                            sqlscript/, dataflow/, trigger/
                            Validate at least pipeline/ OR sqlscript/ exists
1.3  Initialize appropriate connector/parser based on source.type identified in 1.2
1.4  Test connectivity and validate permissions
1.5  Log connection status and metadata
```

### Step 2 — Scan Databases & Schemas

```
IF source.type != powercenter:
  2.1  Enumerate all databases/schemas in the environment
  2.1a IF file_size > 500KB:
       CALL headroom_compress(content=file_content, type="code")
       USE compressed_content for downstream processing
       LOG "Headroom: {original_tokens} → {compressed_tokens} tokens ({savings_pct}% reduction)"
       NOTE: use headroom_retrieve(id) if full content needed by downstream agent
  2.2  For each database:
       - List all tables (with row counts, sizes, partitions)
       - List all views (with underlying queries)
       - List all stored procedures/functions
       - List all indexes and constraints
  2.3  Record schema metadata (creation date, last modified, owner)
  2.4  Log any access errors or restricted objects

IF source.type = powercenter:
  2.1  Parse XML export file(s) — enumerate all <FOLDER> nodes
  2.2  For each folder:
       - Extract all <MAPPING> nodes
         → For each Mapping: name, folder, description, is_valid,
           creation date, last saved date
         → For each <TRANSFORMATION> inside the Mapping:
           type (Aggregator, Joiner, Lookup, Expression, Filter, Router,
                 Sorter, Union, UpdateStrategy, Normalizer, Rank,
                 SequenceGenerator, XMLParser, JavaTransformation,
                 ExternalProcedure, StoredProcedure, PowerExchange),
           name, is_reusable, all ports (INPUT/OUTPUT/VARIABLE),
           transformation attributes (SQL override, cache settings)
         → Extract Source Qualifier SQL Override if present
       - Extract all <MAPPLET> nodes (reusable sub-mappings)
       - Extract all <SHORTCUT> nodes (cross-folder references)
  2.3  Record repository name and version from XML attributes
  2.4  Flag invalid Mappings (is_valid = NO) and log as REQUIRES_REVIEW
  2.5  Flag JavaTransformation and ExternalProcedure occurrences as HIGH RISK

IF source.type = spark_generic:
  2.1  Enumerate all files by extension in legacy_path (recursive):
       .sql → SQL scripts | .py → Python | .scala → Scala | .sh → Shell
  2.2  For each .sql file, parse and extract:
       - CREATE TABLE statements → object_type: TABLE
         (capture: table name, column count, ALL-VARCHAR smell flag,
          missing PK flag, denormalization indicator [>30 columns])
       - CREATE PROCEDURE statements → object_type: STORED_PROCEDURE
         (capture: name, parameter list, referenced tables via FROM/INSERT/UPDATE,
          linked server references [4-part names or IP-based names],
          BULK INSERT statements with their file paths,
          TRY/CATCH presence flag, transaction usage flag, cursor usage flag)
  2.3  For each .py file, extract:
       - module name, imports (flag pyodbc/pymssql = DB coupling)
       - connection strings (flag hardcoded credentials as SECURITY_FINDING —
         record presence and location, NEVER the credential value itself)
       - SQL statements embedded in strings → referenced tables
       - file paths read/written (open(), os.path, glob) → filesystem artifacts
       - flags: except-pass usage, missing sys.exit on failure, busy-wait loops
  2.4  For each .scala file, extract:
       - object/class name, spark.read sources (paths, formats)
       - write targets (paths, formats)
       - master() config (flag local[*] = not cluster-ready)
       - collect()/toLocalIterator usage → OOM_RISK flag
       - Thread.sleep usage → FRAGILE_SYNC flag
       - hardcoded OS paths (C:\, D:\, /home/) → PORTABILITY_RISK flag
  2.5  Flag every hardcoded credential, IP address and OS path as findings

IF source.type = synapse:
  2.1  Parse sqlscript/*.json — each contains T-SQL in properties.content.query:
       - CREATE TABLE (capture DISTRIBUTION = HASH/ROUND_ROBIN/REPLICATE,
         and INDEX type: CLUSTERED COLUMNSTORE / HEAP)
       - CREATE PROCEDURE (Dedicated SQL Pool dialect)
       - CTAS (CREATE TABLE AS SELECT) statements
       - OPENROWSET usage → Serverless SQL over data lake, capture lake paths
       - CREATE EXTERNAL TABLE → capture data source and file format
  2.2  Parse dataset/*.json:
       - dataset name, type (DelimitedText, Parquet, AzureSqlTable, etc.)
       - linked service reference, folder/file path or table name
  2.3  Parse linkedService/*.json:
       - service name, type (AzureBlobFS, AzureSqlDW, AzureSqlDatabase, etc.)
       - flag any inline credentials/keys as SECURITY_FINDING (record presence
         and location only — NEVER extract the secret value into the inventory)
  2.4  Parse notebook/*.json:
       - notebook name, language (from metadata.language_info)
       - cell count, magic commands (%%sql, %%pyspark)
       - mssparkutils.notebook.run() calls → notebook-to-notebook dependency
  2.5  Record workspace name and folder structure
```

### Step 3 — Scan Pipelines & Jobs

```
IF source.type != powercenter:
  3.1  Enumerate all ETL pipelines/dataflows
  3.2  For each pipeline:
       - Extract source and target connections
       - List all transformations/steps
       - Identify custom code (UDFs, scripts)
       - Record scheduling information
  3.3  Enumerate all orchestration jobs
  3.4  For each job:
       - Extract execution sequence
       - Record dependencies and triggers
       - Note last execution date and status

IF source.type = powercenter:
  3.1  Enumerate all <SESSION> nodes across all folders
  3.2  For each Session:
       - Extract parent Mapping name (MAPPINGNAME attribute)
       - Extract source connections (connection type, connection name)
       - Extract target connections (connection type, connection name)
       - Extract session config: commit interval, error threshold, recovery mode
       - Record partition settings if present
  3.3  Enumerate all <WORKFLOW> nodes across all folders
  3.4  For each Workflow:
       - Extract execution sequence of tasks (SESSION, DECISION, ASSIGNMENT,
         COMMAND, TIMER, EVENT-WAIT, EVENT-RAISE, WORKLET references)
       - Extract scheduling config: schedule type, start time, recurrence
       - Resolve all WORKLET references to their <WORKLET> definition nodes
       - Record is_valid and is_enabled flags
  3.5  Enumerate all <WORKLET> nodes
  3.6  For each Worklet:
       - Extract internal task sequence (same structure as Workflow)
       - Record which Workflows reference this Worklet

IF source.type = spark_generic:
  3.1  There is NO formal orchestration — reconstruct the implicit pipeline:
  3.2  Build the execution chain from filesystem coupling
       (load mixed-pipeline-coupling-patterns.md for detection rules):
       - flag files written by one script and awaited by another
       - CSV/parquet paths written by one component and read by another
       - BULK INSERT paths in SQL matching write paths in Python/Scala
       - sleep/busy-wait loops indicating implicit sequencing
  3.3  Record the reconstructed chain as pipelines[] with
       orchestration_type: "IMPLICIT_FILESYSTEM" — this is a KEY FINDING
       (no scheduler owns the sequence; it survives by convention only)
  3.4  Capture any scheduler artifacts if present (.bat, cron entries,
       Task Scheduler XML) as jobs[]

IF source.type = synapse:
  3.1  Parse pipeline/*.json — for each pipeline:
       - name, folder, activity list in dependency order
       - Activity types to catalog: Copy, ExecuteDataFlow, SynapseNotebook,
         SqlPoolStoredProcedure, Lookup, ForEach, IfCondition, Until,
         ExecutePipeline (nested), WebActivity, SetVariable
       - For Copy activities: source dataset, sink dataset, mapping presence
       - For ExecuteDataFlow: referenced dataflow name
       - For SynapseNotebook: referenced notebook + spark pool
       - For ExecutePipeline: child pipeline reference → pipeline dependency
  3.2  Parse dataflow/*.json — for each Mapping Data Flow:
       - name, source transformations, sink transformations
       - transformation chain: derivedColumn, aggregate, join, lookup,
         filter, select, union, alterRow, conditionalSplit, exists, window
       - record transformation count per dataflow (feeds classify-pipelines)
  3.3  Parse trigger/*.json:
       - trigger name, type (ScheduleTrigger, TumblingWindowTrigger,
         BlobEventsTrigger), recurrence, referenced pipelines
  3.4  Assign IDs: PL-{name} (pipelines), DF-{name} (dataflows),
       NB-{name} (notebooks), TR-{name} (triggers)
```

### Step 4 — Extract Metadata

```
IF source.type != powercenter:
  4.1  For every discovered object, extract:
       - Object name, type, location
       - Creation date, last modified date
       - Owner/creator
       - Size (where applicable)
       - Dependencies (references to other objects)
       - Tags/labels/categories
  4.2  Normalize metadata to standard schema
  4.3  Assign unique IDs to each object

IF source.type = powercenter:
  4.1  For every discovered object, extract:
       - Object name, type (PC_MAPPING / PC_SESSION / PC_WORKFLOW /
         PC_WORKLET / PC_MAPPLET / PC_SOURCE / PC_TARGET / PC_SHORTCUT)
       - Folder (location equivalent)
       - Creation date, last saved date
       - is_valid, is_enabled flags
       - transformation_count (Mappings only)
       - source_connection_type, target_connection_type (Sessions only)
       - Dependencies: Mapping → Sessions referencing it,
                       Session → Workflow containing it,
                       Shortcut → original object cross-folder reference
  4.2  Normalize to standard schema with PowerCenter extensions
  4.3  Assign unique IDs:
       - Mapping  → MAP-{folder}-{name}
       - Session  → SS-{folder}-{name}
       - Workflow → WF-{folder}-{name}
       - Worklet  → WL-{folder}-{name}
       - Mapplet  → ML-{folder}-{name}
```

### Step 5 — Catalog & Persist

```
5.1  Compile all objects into inventory.json
     IF source.type = powercenter:
       inventory.json must include top-level keys:
         mappings[], sessions[], workflows[], worklets[],
         mapplets[], source_definitions[], target_definitions[],
         connections[], shortcuts[]
       scan_metadata.platform = "Informatica PowerCenter"
       scan_metadata.repository = <repository name from XML>
     IF source.type = spark_generic:
       inventory.json top-level keys:
         sql_objects[] (tables, procedures), python_scripts[], scala_jobs[],
         shell_scripts[], filesystem_artifacts[] (flags, CSVs, paths),
         external_dependencies[] (linked servers, external IPs),
         implicit_pipeline_chain[] (reconstructed execution order)
       scan_metadata.platform = "Generic Spark / Mixed Code"
       scan_metadata.orchestration = "IMPLICIT_FILESYSTEM"
     IF source.type = synapse:
       inventory.json top-level keys:
         pipelines[], dataflows[], notebooks[], sql_scripts[],
         datasets[], linked_services[], triggers[],
         dedicated_sql_objects[] (tables with distribution, procedures, CTAS)
       scan_metadata.platform = "Azure Synapse Analytics"
       scan_metadata.workspace = <workspace name>
     ELSE:
       inventory.json standard schema (databases[], pipelines[], jobs[])
5.2  Generate summary statistics:
     - Total objects by type
     - Total databases/schemas (or folders for PowerCenter)
     - Total pipelines/mappings and jobs/workflows
     - Total data volume (estimated)
     IF source.type = powercenter:
       - transformation_type_breakdown (count per transformation type)
       - java_transformation_count (HIGH RISK indicator)
       - sql_override_count
       - cross_folder_shortcuts_count
5.3  Save inventory.json to projects/{project_name}/outputs/upstream/discovery/inventory/
5.4  Log scan completion with metrics
```

---

## Output Schema

```json
{
  "scan_metadata": {
    "scan_id": "string",
    "scan_date": "YYYY-MM-DD",
    "platform": "string",
    "duration_seconds": 0,
    "total_objects": 0
  },
  "databases": [
    {
      "name": "string",
      "tables": [],
      "views": [],
      "procedures": []
    }
  ],
  "pipelines": [],
  "jobs": [],
  "scripts": [],
  "connections": []
}
```

### Output Schema — PowerCenter (`source.type = powercenter`)

```json
{
  "scan_metadata": {
    "scan_id": "string",
    "scan_date": "YYYY-MM-DD",
    "platform": "Informatica PowerCenter",
    "repository": "string",
    "duration_seconds": 0,
    "total_objects": 0
  },
  "mappings": [
    {
      "id": "MAP-{folder}-{name}",
      "name": "string",
      "folder": "string",
      "is_valid": true,
      "transformation_count": 0,
      "transformation_types": [],
      "has_sql_override": false,
      "has_java_transformation": false,
      "source_qualifier_sql": "string|null"
    }
  ],
  "sessions": [],
  "workflows": [],
  "worklets": [],
  "mapplets": [],
  "source_definitions": [],
  "target_definitions": [],
  "connections": [],
  "shortcuts": []
}
```

### Output Schema — Generic Spark / Mixed Code (`source.type = spark_generic`)

```json
{
  "scan_metadata": {
    "platform": "Generic Spark / Mixed Code",
    "orchestration": "IMPLICIT_FILESYSTEM"
  },
  "sql_objects": [],
  "python_scripts": [],
  "scala_jobs": [],
  "shell_scripts": [],
  "filesystem_artifacts": [],
  "external_dependencies": [],
  "implicit_pipeline_chain": []
}
```

### Output Schema — Azure Synapse (`source.type = synapse`)

```json
{
  "scan_metadata": {
    "platform": "Azure Synapse Analytics",
    "workspace": "string"
  },
  "pipelines": [],
  "dataflows": [],
  "notebooks": [],
  "sql_scripts": [],
  "datasets": [],
  "linked_services": [],
  "triggers": [],
  "dedicated_sql_objects": []
}
```

---

## Error Handling

| Error                        | Action                                         |
|------------------------------|-------------------------------------------------|
| Connection timeout           | Retry 3x with exponential backoff, then log error |
| Permission denied            | Log object as restricted, continue scan         |
| Unsupported object type      | Log warning, add to inventory with type=UNKNOWN |
| Invalid XML / not POWERMART schema    | Abort scan, request correct export file         |
| Missing MAPPINGNAME in SESSION        | Log as ORPHAN_SESSION, continue scan            |
| Unresolved SHORTCUT reference         | Log as EXTERNAL_DEPENDENCY, flag for review     |
| JavaTransformation detected           | Log HIGH RISK, set complexity=VERY_COMPLEX      |
| PowerExchange connector detected      | Log as EXTERNAL_CONNECTOR, flag for infra review|
| spark_generic: nenhum arquivo .sql/.py/.scala | Abort — legacy_path incorreto ou vazio |
| spark_generic: credencial hardcoded          | SECURITY_FINDING, continua o scan       |
| synapse: pasta pipeline/ e sqlscript/ ausentes| Abort — export Git incompleto          |
| synapse: linkedService com credencial inline | SECURITY_FINDING (registrar presença/local, NUNCA o valor), continua |
| synapse: dataflow JSON com schema desconhecido| Log WARN, cataloga como UNKNOWN_DATAFLOW |
| Partial metadata             | Log warning, add with available fields          |

---

## Completion Criteria

- [ ] All databases/schemas enumerated
- [ ] All tables, views, procedures cataloged
- [ ] All pipelines and jobs discovered
- [ ] Metadata extracted for every object
- [ ] inventory.json generated and saved
- [ ] Summary statistics logged
- [ ] Zero unrecoverable errors (warnings acceptable)
- [ ] IF powercenter: all <MAPPING> nodes extracted with transformation breakdown
- [ ] IF powercenter: all <SESSION> nodes linked to parent Mappings
- [ ] IF powercenter: all <WORKFLOW> nodes extracted with execution sequence
- [ ] IF powercenter: Java Transformations and External Procedures flagged
- [ ] IF powercenter: cross-folder Shortcuts recorded in dependency list

---

> **Task**: `scan-repo` · **Agent**: Discovery Scout 🔍 · **Phase**: UPSTREAM · **Gate**: 1
