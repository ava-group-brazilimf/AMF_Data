# Step 02 — Scan PII

**Agente:** security-compliance  
**Task:** scan-pii  
**Input:** `outputs/midstream/generated-code/`, `data-model.md`  
**Output:** `outputs/midstream/pii-findings.md`

## Instrução
Ativar `security-compliance` e executar `*scan-pii`. O agente detecta campos com dados pessoais identificáveis (PII) no código e no modelo, propondo mascaramento ou anonimização.

## Critério de Conclusão
- [ ] `pii-findings.md` gerado com lista de campos PII
- [ ] Estratégia de mascaramento proposta por campo
- [ ] Zero PII exposto sem mascaramento na camada Gold
