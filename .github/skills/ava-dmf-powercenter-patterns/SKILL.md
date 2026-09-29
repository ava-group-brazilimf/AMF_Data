---
name: ava-dmf-powercenter-patterns
description: >
  Knowledge pack para migração de Informatica PowerCenter para Databricks/Delta Lake.
  Cobre padrões de conversão de transformações, mapeamento de tipos de dados,
  equivalências de objetos (Mapping→PySpark Notebook, Workflow→Databricks Workflow,
  Session→Job Task, Worklet→Sub-workflow, Mapplet→Shared Function) e boas práticas
  para SQL Overrides e Java Transformations. Carregar quando inventory.json tiver
  platform=InformaticaPowerCenter ou quando Logan/Coda estiver processando pseudocode
  de origem PowerCenter.
version: "1.0"
platform_source: "Informatica PowerCenter"
platform_target: "Azure Databricks / Delta Lake"
---

# PowerCenter → Databricks Migration Patterns

## Quando carregar este skill

- Logan executando `*extract-logic` com `language=InformaticaPowerCenterXML`
- Coda gerando código a partir de pseudocode com `source_platform=PowerCenter`

## Referência interna

- Padrões de extração: `src/modules/dmf-fabric-agents/upstream-discovery/data/powercenter-extraction-patterns.md`

## Equivalências de objetos

| PowerCenter | Databricks |
|---|---|
| Mapping | PySpark Notebook (.py) |
| Session | Databricks Job Task |
| Workflow | Databricks Workflow |
| Worklet | Sub-workflow aninhado |
| Mapplet | Módulo Python reutilizável (src/shared/) |
| Java Transformation | Reescrita manual obrigatória |
| SQL Override | Processar via SQL parser antes de gerar PySpark |
