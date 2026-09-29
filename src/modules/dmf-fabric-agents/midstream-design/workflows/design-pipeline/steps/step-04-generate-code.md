# Step 04 — Generate Code

**Agente:** code-generator  
**Task:** batch-generate  
**Input:** `pseudocode/*.json`, `architecture.md`, `data-contracts.md`  
**Output:** `outputs/midstream/generated-code/`

## Instrução
Ativar `code-generator` e executar `*batch-generate`. O agente converte o pseudocódigo semântico em código executável na plataforma target (DDL + ETL) com testes unitários.

## Critério de Conclusão
- [ ] DDL gerado para todas as entidades do modelo
- [ ] ETL gerado para todos os pipelines mapeados
- [ ] Testes unitários gerados (cobertura ≥ 80%)
