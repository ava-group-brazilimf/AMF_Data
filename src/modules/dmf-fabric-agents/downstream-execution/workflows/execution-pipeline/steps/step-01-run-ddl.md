# Step 01 — Run DDL

**Agente:** downstream-executor  
**Task:** create-ddl-etl  
**Input:** `outputs/midstream/generated-code/ddl/`  
**Output:** DDL aplicado no ambiente target

## Instrução
Ativar `downstream-executor` e executar `*run-wave` (fase DDL). O agente aplica os scripts DDL no ambiente target, criando estruturas de tabelas, views e schemas conforme o modelo.

## Critério de Conclusão
- [ ] Todos os objetos DDL criados sem erro
- [ ] Schemas e permissões configurados
- [ ] Log de execução registrado em `execution-log.md`
