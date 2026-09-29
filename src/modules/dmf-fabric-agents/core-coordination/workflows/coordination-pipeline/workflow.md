# Workflow: coordination-pipeline

**Módulo:** core-coordination  
**Fase:** CORE — Cross-phase  
**Trigger:** `*route` via master-agent ou início de nova wave

## Objetivo
Orquestrar o ciclo completo de uma wave de migração, desde o triage inicial até o fechamento pós-Gate 3, incluindo gestão de rollbacks e melhoria contínua.

## Sequência de Steps

| Step | Arquivo | Agente | Artefato |
|------|---------|--------|----------|
| 01 | steps/step-01-triage.md | master-agent | route-recommendation.md |
| 02 | steps/step-02-start-wave.md | migration-coordinator | wave-config validado |
| 03 | steps/step-03-monitor-gates.md | migration-coordinator | gate-status.md |
| 04 | steps/step-04-retrospective.md | iteration-improvement | improvement-backlog.md |

## Inputs Esperados
- `projects/{project_name}/context/project-config.yaml`
- `projects/{project_name}/context/agent-task-config.yaml`

## Outputs
- `outputs/summary/gate-decisions/`
- `outputs/summary/wave-status.md`
- `outputs/summary/improvement-backlog.md`

## Critério de Conclusão
Todos os 3 gates aprovados | wave-status.md com status COMPLETED
