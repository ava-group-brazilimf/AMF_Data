# Workflow: execution-pipeline

**Módulo:** downstream-execution  
**Fase:** DOWNSTREAM — Gate 3  
**Trigger:** `*start-downstream` via migration-coordinator (após Gate 2 aprovado)

## Objetivo
Executar a wave de migração: aplicar DDL/ETL no ambiente target, reconciliar dados, auto-corrigir erros, gerar documentação e entregar artefatos de BI.

## Sequência de Steps

| Step | Arquivo | Agente | Artefato |
|------|---------|--------|----------|
| 01 | steps/step-01-run-ddl.md | downstream-executor | ddl aplicado |
| 02 | steps/step-02-run-etl.md | downstream-executor | etl aplicado |
| 03 | steps/step-03-reconcile.md | reconciliation | reconciliation-report.md |
| 04 | steps/step-04-self-heal.md | self-healing | healing-report.md |
| 05 | steps/step-05-document.md | documentation | wave-report.md |
| 06 | steps/step-06-gate3-review.md | migration-coordinator | gate3-decision.md |

## Inputs Esperados
- `projects/{project_name}/outputs/midstream/` (Gate 2 aprovado)
- Credenciais de acesso ao ambiente target

## Outputs
Todos os artefatos em `projects/{project_name}/outputs/downstream/`

## Gate 3 — Critério de Saída
Paridade de dados ≥ 99.9% | Zero erros críticos | wave-report.md gerado
