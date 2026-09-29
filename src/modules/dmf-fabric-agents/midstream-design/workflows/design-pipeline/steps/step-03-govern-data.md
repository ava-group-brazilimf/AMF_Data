# Step 03 — Govern Data

**Agente:** data-steward  
**Task:** create-data-contracts  
**Input:** `data-model.md`, DQ rules do upstream  
**Output:** `outputs/midstream/data-contracts.md`

## Instrução
Ativar `data-steward` e executar `*create-data-contracts`. O agente define contratos de dados (SLAs de qualidade, regras de validação, classificação de PII e lineage).

## Critério de Conclusão
- [ ] `data-contracts.md` com contratos por entidade
- [ ] Classificação de dados sensíveis concluída
- [ ] Lineage documentado da origem ao destino
