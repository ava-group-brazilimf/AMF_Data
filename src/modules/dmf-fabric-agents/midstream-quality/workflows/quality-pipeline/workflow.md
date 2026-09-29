# Workflow: quality-pipeline

**Módulo:** midstream-quality  
**Fase:** MIDSTREAM — Gate 2 (paralelo ao design)  
**Trigger:** `*start-quality` via migration-coordinator

## Objetivo
Validar a equivalência semântica do código gerado, executar testes e garantir compliance de segurança antes da execução downstream.

## Sequência de Steps

| Step | Arquivo | Agente | Artefato |
|------|---------|--------|----------|
| 01 | steps/step-01-validate-code.md | quality-gate | validation-report.md |
| 02 | steps/step-02-scan-pii.md | security-compliance | pii-findings.md |
| 03 | steps/step-03-check-compliance.md | security-compliance | compliance-report.md |

## Inputs Esperados
- `projects/{project_name}/outputs/midstream/` (código gerado pelo design-pipeline)

## Outputs
- `outputs/midstream/validation-report.md`
- `outputs/midstream/pii-findings.md`
- `outputs/midstream/compliance-report.md`

## Gate 2 — Critério de Saída
Equivalência semântica ≥ 95% | Zero PII exposto | Compliance aprovado
