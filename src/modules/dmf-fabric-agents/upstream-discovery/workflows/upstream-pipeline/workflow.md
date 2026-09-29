# Workflow: upstream-pipeline

**Módulo:** upstream-discovery  
**Fase:** UPSTREAM — Gate 1  
**Trigger:** `*start-upstream` via migration-coordinator  

## Objetivo
Executar o ciclo completo de descoberta do ambiente legado: inventário, análise de dependências, extração de lógica e definição estratégica, produzindo todos os artefatos necessários para o Gate 1.

## Sequência de Steps

| Step | Arquivo | Agente | Artefato |
|------|---------|--------|----------|
| 01 | steps/step-01-scan-repo.md | discovery-scout | inventory.json |
| 02 | steps/step-02-map-dependencies.md | inventory-scout | dependency-graph.json |
| 03 | steps/step-03-define-strategy.md | data-strategist | problem-statement.md |
| 04 | steps/step-04-map-requirements.md | business-analyst | sttm.md |
| 05 | steps/step-05-extract-logic.md | logic-extractor | pseudocode/*.json |
| 06 | steps/step-06-gate1-review.md | migration-coordinator | gate1-decision.md |

## Inputs Esperados
- Acesso ao repositório legado (path ou URL)
- `projects/{project_name}/context/project-config.yaml`
- `projects/{project_name}/context/agent-task-config.yaml`

## Outputs
Todos os artefatos em `projects/{project_name}/outputs/upstream/`

## Gate 1 — Critério de Saída
GateScore ≥ `gate_thresholds.gate_1` do `wave-config.yaml` | Completude ≥ 80% | inventory.json e dependency-graph.json presentes
