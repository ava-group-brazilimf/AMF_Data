# Step 02 — Start Wave

**Agente:** migration-coordinator  
**Task:** start-wave  
**Input:** caminho explícito do `wave-config.yaml`; dele são resolvidos `projects/{project_name}/context/project-config.yaml` e `agent-task-config.yaml`  
**Output:** wave iniciada com trace_id registrado

## Instrução
Ativar `migration-coordinator` e executar `*start-wave` informando o caminho do
`wave-config.yaml`. O agente deve validar a configuração, resolver `project_name`,
carregar os dois arquivos de `context/` e propagar `context_root` e `outputs_root`
para todos os agentes. Não inferir a raiz operacional a partir da pasta onde o
`wave-config.yaml` está armazenado. Em seguida, gerar o trace_id, registrar o início
da wave e disparar o primeiro módulo (upstream-discovery).

## Critério de Conclusão
- [ ] `wave-config` validado pelo `validate_wave_config.py`
- [ ] `project_name` idêntico no wave-config e nos dois arquivos de contexto
- [ ] `context_root` carregado e `outputs_root` fixado antes da primeira delegação
- [ ] trace_id UUID gerado e registrado
- [ ] upstream-discovery pipeline iniciado
