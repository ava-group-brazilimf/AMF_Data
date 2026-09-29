# Task: extract-ast

**Agent:** Logan 🧠 — Logic Extractor  
**Phase:** UPSTREAM · Gate 1  
**Command:** `*extract-ast`

---

## Objetivo

Executar o **AST Engine** (`src/shared/pipeline_ast/`) sobre artefatos legados SQL ou SSIS e produzir o modelo canônico estruturado, rastreabilidade de colunas e STTM — substituindo a leitura interpretativa do LLM por extração determinística via árvore sintática.

## Artefatos Produzidos

| Artefato | Descrição |
|---|---|
| `canonical-model.json` | Modelo canônico da pipeline (MigrationPipeline) |
| `column-lineage.json` | Rastreabilidade coluna-a-coluna ponta a ponta |
| `sttm.md` | Source-to-Target Mapping em Markdown |

## Inputs Necessários

Antes de executar, confirme com o usuário:

1. **Tipo de artefato legado:** SQL (`.sql`, `.ddl`) ou SSIS (`.dtsx`)
2. **Caminho do(s) arquivo(s) legado(s):** ex. `legacy/orders.sql`
3. **Dialeto SQL** (se SQL): `tsql`, `oracle`, `postgres`, `snowflake`, `databricks`, `mysql`, `bigquery` (padrão: ANSI)
4. **Plataforma alvo:** ex. `Fabric`, `Databricks`, `Airflow`, `Snowflake`
5. **Diretório de saída:** ex. `outputs/midstream/` (padrão)

## Execução

```python
# SQL
from src.shared.pipeline_ast.parsers.sql_parser import SQLASTParser
from src.shared.pipeline_ast.lineage.lineage_engine import LineageEngine
from pathlib import Path

parser = SQLASTParser(dialect="tsql")
result = parser.parse_file(Path("legacy/orders.sql"), target_platform="Fabric")
pipeline = result.pipeline

# Salvar canonical-model.json
pipeline.save(Path("outputs/midstream/canonical-model.json"))

# Lineage Engine → column-lineage.json + sttm.md
engine = LineageEngine()
report = engine.build(pipeline)
report.save_json(Path("outputs/midstream/column-lineage.json"))
report.save_sttm(Path("outputs/midstream/sttm.md"))
```

```python
# SSIS
from src.shared.pipeline_ast.parsers.ssis_parser import SSISASTParser

parser = SSISASTParser()
result = parser.parse_file(Path("legacy/ETL_Orders.dtsx"), target_platform="Databricks")
pipeline = result.pipeline
pipeline.save(Path("outputs/midstream/canonical-model.json"))
```

## Métricas de Qualidade (Gate 1)

| Métrica | Fórmula | Meta |
|---|---|---|
| AST Coverage | `pipeline.ast_coverage` | > 0.90 |
| Parse Errors | `len(pipeline.parse_errors)` | = 0 |
| Transformation Accuracy | transformações identificadas / esperadas | > 0.95 |

## Saída Esperada

```
✅ AST Engine concluído
   canonical-model.json  → outputs/midstream/
   column-lineage.json   → outputs/midstream/
   sttm.md               → outputs/midstream/

   AST Coverage: 97.3%
   Transformações: 42
   Joins: 8
   Filtros: 15
   Erros de parse: 0
```

## Próximos Passos

Após a extração AST:

1. `@code-generator *generate-from-ast` — gerar código Fabric/Databricks/Airflow
2. `@migration-coordinator *gate-1` — validar Gate 1 com artefatos AST
