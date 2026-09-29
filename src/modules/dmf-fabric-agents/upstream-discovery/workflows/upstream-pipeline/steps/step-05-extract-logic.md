# Step 05 — Extract Logic

**Agente:** logic-extractor  
**Task:** extract-logic  
**Input:** código-fonte legado, `inventory.json`  
**Output:** `outputs/upstream/pseudocode/*.json`, `digital-twin.json`

## Instrução
Ativar `logic-extractor` e executar `*extract-logic`. O agente analisa o código legado (HiveQL, PySpark, SQL) e gera pseudocódigo semântico normalizado para cada objeto, além do digital-twin do ambiente legado.

## Critério de Conclusão
- [ ] Pseudocódigo gerado para ≥ 90% dos objetos
- [ ] `digital-twin.json` com representação completa do ambiente
- [ ] Confidence score ≥ 0.75 no relatório de extração
