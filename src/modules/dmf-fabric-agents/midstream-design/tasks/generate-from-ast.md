# Task: generate-from-ast

**Agent:** Coda ⚙️ — Code Generator  
**Phase:** MIDSTREAM · Gate 2  
**Command:** `*generate-from-ast`

---

## Objetivo

Gerar artefatos de código executável para múltiplas plataformas alvo diretamente a partir do `canonical-model.json` produzido pelo AST Engine. Determinístico — zero inferência LLM sobre estrutura de dados.

## Artefatos Produzidos

### Fabric
| Artefato | Descrição |
|---|---|
| `pipeline_<name>.json` | Definição de pipeline ADF/Fabric |
| `bronze_extract.py` | PySpark Bronze — extração raw |
| `silver_transform.py` | PySpark Silver — transformações |
| `gold_load.py` | PySpark Gold — carga final |
| `create_<table>.sql` | DDL Fabric Warehouse (T-SQL) |

### Databricks
| Artefato | Descrição |
|---|---|
| `bronze_extract.py` | Notebook Bronze (JDBC + Delta) |
| `silver_transform.py` | Notebook Silver (joins + filtros) |
| `gold_load.py` | Notebook Gold (MERGE INTO + OPTIMIZE) |
| `create_<table>.sql` | DDL Delta Lake + MERGE + OPTIMIZE |
| `job_<name>.json` | Databricks Workflow JSON |

### Airflow
| Artefato | Descrição |
|---|---|
| `dag_<name>.py` | DAG derivado do grafo canônico |

## Inputs Necessários

1. **Caminho do canonical-model.json:** ex. `outputs/midstream/canonical-model.json`
2. **Plataforma alvo:** `fabric`, `databricks`, `airflow` (ou múltiplas)
3. **Diretório de saída:** ex. `outputs/downstream/generated-code/` (padrão)

## Execução

```python
from pathlib import Path
from src.shared.pipeline_ast.model.canonical import MigrationPipeline
from src.shared.pipeline_ast.generators.fabric_generator import FabricGenerator
from src.shared.pipeline_ast.generators.databricks_generator import DatabricksGenerator
from src.shared.pipeline_ast.generators.airflow_generator import AirflowGenerator

pipeline = MigrationPipeline.load("outputs/midstream/canonical-model.json")
output_dir = Path("outputs/downstream/generated-code")

# Fabric
artifacts = FabricGenerator().generate(pipeline)
artifacts.save(output_dir)

# Databricks
artifacts = DatabricksGenerator().generate(pipeline)
artifacts.save(output_dir)

# Airflow
artifacts = AirflowGenerator().generate(pipeline)
artifacts.save(output_dir)
```

## Métricas de Qualidade (Gate 2 / Gate 3)

| Métrica | Fórmula | Meta |
|---|---|---|
| Code Generation Accuracy | Artefatos gerados sem correção humana | > 80% |
| Transformation Coverage | Transformações geradas / total no modelo | 100% |
| Platforms Generated | Plataformas com código gerado | ≥ 1 |

## Saída Esperada

```
✅ Geração multi-plataforma concluída
   outputs/downstream/generated-code/fabric/
      pipeline_orders.json
      bronze_extract.py
      silver_transform.py
      gold_load.py
      create_orders.sql

   outputs/downstream/generated-code/databricks/
      bronze_extract.py
      silver_transform.py
      gold_load.py
      create_orders.sql
      job_orders.json

   outputs/downstream/generated-code/airflow/
      dag_orders.py
```

## Próximos Passos

1. `@migration-coordinator *gate-2` — validar Gate 2
2. `*generate-tests` — gerar testes para o código gerado
3. `*optimize` — aplicar otimizações de performance
