# Step 02 — Run ETL

**Agente:** downstream-executor  
**Task:** run-wave  
**Input:** `outputs/midstream/generated-code/etl/`  
**Output:** dados carregados no ambiente target

## Instrução
Ativar `downstream-executor` e executar `*run-wave` (fase ETL). O agente executa os pipelines de transformação e carga, monitorando volumes e latência.

## Critério de Conclusão
- [ ] Todos os pipelines ETL executados com sucesso
- [ ] Volume de linhas carregadas registrado por tabela
- [ ] Erros de execução ≤ threshold configurado no project-config.yaml
