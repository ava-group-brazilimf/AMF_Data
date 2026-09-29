# Step 03 — Check Compliance

**Agente:** security-compliance  
**Task:** check-compliance  
**Input:** `pii-findings.md`, `data-contracts.md`  
**Output:** `outputs/midstream/compliance-report.md`

## Instrução
Ativar `security-compliance` e executar `*check-compliance`. O agente valida aderência às normas regulatórias aplicáveis (LGPD, GDPR, SOC2) e aos contratos de dados definidos.

## Critério de Conclusão
- [ ] `compliance-report.md` emitido com status COMPLIANT ou lista de gaps
- [ ] Todos os campos PII com mascaramento aplicado
- [ ] Controles de acesso (RBAC) verificados
