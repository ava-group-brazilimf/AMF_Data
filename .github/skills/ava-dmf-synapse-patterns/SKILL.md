---
name: ava-dmf-synapse-patterns
description: >
  Knowledge pack para migração de Azure Synapse Analytics para Databricks.
  Cobre conversão de Pipelines (activities->Workflow tasks), Mapping Data Flows
  (transformações->PySpark), Dedicated SQL Pool (CTAS/DISTRIBUTION->Delta com
  liquid clustering), Serverless SQL (OPENROWSET->spark.read) e Spark Pool
  notebooks (mssparkutils->dbutils). Carregar quando inventory.json tiver
  platform=AzureSynapse ou quando Logan/Coda processar pseudocode de origem Synapse.
version: "1.0"
platform_source: "Azure Synapse Analytics"
platform_target: "Azure Databricks / Delta Lake"
---

# Synapse -> Databricks Migration Patterns

## Referência interna
- Padrões de extração: `src/modules/dmf-fabric-agents/upstream-discovery/data/synapse-extraction-patterns.md`

## Equivalências de objetos

| Synapse | Databricks |
|---|---|
| Pipeline | Databricks Workflow |
| Activity | Workflow task |
| Mapping Data Flow | Notebook PySpark |
| Notebook (Spark Pool) | Notebook (lift + mssparkutils->dbutils) |
| Dedicated SQL table | Delta table (DISTRIBUTION->clustering) |
| Serverless view | Unity Catalog view |
| Linked Service | Unity Catalog connection / secret scope |
| Trigger (Schedule/Tumbling) | Job schedule / file arrival trigger |
| WebActivity / Custom | Revisão manual obrigatória |

## Regras fundamentais
1. NUNCA descartar DISTRIBUTION hints - viram liquid clustering/ZORDER
2. ExecutePipeline aninhado -> Run Job task (preservar hierarquia)
3. mssparkutils.notebook.run -> dbutils.notebook.run (revisar retorno)
4. Expressions ADF viram Python - validar com testes gerados
5. Schema drift habilitado em Data Flow -> tratar com Auto Loader schema evolution
