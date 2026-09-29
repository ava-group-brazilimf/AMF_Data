# Step 04 — Map Requirements (STTM)

**Agente:** business-analyst  
**Task:** create-sttm  
**Input:** `inventory.json`, `problem-statement.md`  
**Output:** `outputs/upstream/sttm.md`

## Instrução
Ativar `business-analyst` e executar `*create-sttm`. O agente produz o Source-to-Target Mapping (STTM) mapeando cada entidade legada para sua correspondente no target, com regras de transformação e DQ rules iniciais.

## Critério de Conclusão
- [ ] STTM cobrindo 100% dos objetos do inventory
- [ ] Regras de transformação documentadas por campo
- [ ] DQ rules iniciais definidas (not-null, range, format)
