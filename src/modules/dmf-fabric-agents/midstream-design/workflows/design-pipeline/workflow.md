# Workflow: design-pipeline

**Módulo:** midstream-design  
**Fase:** MIDSTREAM — Gate 2  
**Trigger:** `*start-midstream` via migration-coordinator (após Gate 1 aprovado)

## Objetivo
Projetar a arquitetura target, modelar os dados, definir contratos e gerar o código DDL/ETL de referência a partir do pseudocódigo produzido no UPSTREAM.

## Sequência de Steps

| Step | Arquivo | Agente | Artefato |
|------|---------|--------|----------|
| 01 | steps/step-01-design-architecture.md | data-architect | architecture.md |
| 02 | steps/step-02-model-data.md | data-modeler | data-model.md |
| 03 | steps/step-03-govern-data.md | data-steward | data-contracts.md |
| 04 | steps/step-04-generate-code.md | code-generator | ddl/*.sql, etl/*.py |
| 05 | steps/step-05-gate2-review.md | migration-coordinator | gate2-decision.md |

## Inputs Esperados
- `projects/{project_name}/outputs/upstream/` (Gate 1 aprovado)
- `projects/{project_name}/context/project-config.yaml`

## Outputs
Todos os artefatos em `projects/{project_name}/outputs/midstream/`

## Gate 2 — Critério de Saída
GateScore ≥ `gate_thresholds.gate_2` do `wave-config.yaml` | architecture.md + data-model.md + código gerado presentes
