# Step 02 — Map Dependencies

**Agente:** inventory-scout  
**Task:** map-dependencies  
**Input:** `outputs/upstream/inventory.json`  
**Output:** `outputs/upstream/dependency-graph.json`

## Instrução
Ativar `inventory-scout` e executar `*map-dependencies` passando o inventory.json. O agente produz o grafo de dependências entre objetos (quem consome quem) e identifica objetos órfãos (dead-code).

## Critério de Conclusão
- [ ] `dependency-graph.json` gerado
- [ ] `dead-code-report.md` com objetos sem consumidores
- [ ] Profundidade máxima de dependência calculada
