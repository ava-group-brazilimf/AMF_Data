# Synapse Extraction Patterns
# Mapeamento: Synapse (Pipelines, Data Flows, Dedicated SQL) -> Pseudocode -> Databricks
# Carregado por: logic-extractor quando language = SynapsePipelineJSON
#                ou dialeto T-SQL Synapse detectado

---

## Pipeline Activities

### Copy Activity
**Extração:** source dataset (+ query se houver), sink dataset, column mapping.
**Databricks:**
```python
# Fonte lake -> Delta: Auto Loader ou COPY INTO
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "parquet")
      .load(source_path))
df.writeStream.toTable("catalog.schema.target")
# Fonte JDBC -> Delta: leitura JDBC + MERGE
```

### ExecuteDataFlow
**Extração:** nome do dataflow referenciado -> resolver e traduzir suas transformações.
**Databricks:** o Data Flow inteiro vira UM notebook PySpark (ver seção Data Flows).

### SqlPoolStoredProcedure
**Extração:** nome da SP + parâmetros -> resolver o corpo T-SQL no sqlscript/.
**Databricks:** corpo traduzido para célula Spark SQL ou PySpark no notebook;
a activity vira uma task do Workflow.

### SynapseNotebook
**Extração:** notebook referenciado + spark pool + parâmetros.
**Databricks:** lift quase direto - notebook task no Workflow (revisar apenas
mssparkutils -> dbutils).

### ForEach
**Extração:** items expression + activities internas + isSequential flag.
**Databricks:** `for` no notebook (sequential) ou Workflow for-each task /
`concurrent.futures` (parallel).

### IfCondition / Until
**Databricks:** if/while Python no notebook orquestrador, ou condicional de
task no Workflow.

### ExecutePipeline (aninhado)
**Databricks:** Run Job task apontando para o job filho - preserva a hierarquia.

### Lookup / GetMetadata / SetVariable
**Databricks:** leitura de DataFrame + variável Python / task values.

### WebActivity / Custom / AzureFunctionActivity
> **manual_migration_required = true** - chamadas externas exigem decisão de
> arquitetura (manter Function? converter em job?). Documentar URL/método/corpo.

---

## Mapping Data Flow - transformações

| Data Flow | Databricks (PySpark) |
|---|---|
| source | spark.read.format(...).load(...) |
| derivedColumn | withColumn(expr traduzida) |
| aggregate | groupBy().agg() |
| join | join(df2, cond, how) |
| lookup | join left + broadcast hint |
| filter | filter(expr) |
| select | select / drop / rename |
| union | unionByName |
| conditionalSplit | N filters (padrão Router) |
| exists | left_semi / left_anti join |
| window | Window functions |
| alterRow + sink | DeltaTable.merge (upsert/delete conforme política) |
| sink | write.format("delta").saveAsTable |

**Expression language ADF -> PySpark (mais comuns):**
`iif(c,a,b)`->`when(c,a).otherwise(b)` · `toString/toInteger/toDecimal`->`cast` ·
`concat`->`concat` · `isNull`->`isNull()` · `currentTimestamp()`->`current_timestamp()` ·
`regexReplace`->`regexp_replace` · byName/byPosition -> mapeamento de colunas.
Expressões com `byName()` dinâmico ou padrões meta-column -> confidence LOW.

---

## Dedicated SQL Pool -> Delta

| Synapse | Databricks |
|---|---|
| CTAS | CREATE TABLE AS SELECT (Delta) |
| DISTRIBUTION = HASH(col) | Liquid clustering / ZORDER BY (col) - REGISTRAR a coluna |
| DISTRIBUTION = ROUND_ROBIN | default Delta (sem ação) |
| DISTRIBUTION = REPLICATE | tabela pequena -> broadcast hint nos joins |
| CLUSTERED COLUMNSTORE | nativo Parquet/Delta (sem ação) |
| HEAP | default (sem ação) |
| PARTITION (col RANGE...) | PARTITIONED BY ou liquid clustering |
| EXTERNAL TABLE | tabela externa Unity Catalog ou ingestão para managed |
| OPENROWSET | spark.read direto do lake |
| Serverless views sobre lake | views Unity Catalog |

---

## Confidence scoring Synapse

| Condição | Ajuste |
|---|---|
| Pipeline só com Copy/DataFlow/Notebook/SP | +0.10 |
| ForEach paralelo com batch count | baseline |
| WebActivity / Custom / AzureFunction | -0.35 (mínimo LOW) |
| Expression ADF com @activity chain 3+ níveis | -0.15 |
| Data Flow com schema drift habilitado | -0.20 |
| CTAS com DISTRIBUTION capturada | +0.05 |
