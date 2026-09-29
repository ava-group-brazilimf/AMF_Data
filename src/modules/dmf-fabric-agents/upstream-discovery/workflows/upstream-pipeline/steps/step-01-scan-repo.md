# Step 01 — Scan Repository

**Agente:** discovery-scout  
**Task:** scan-repo  
**Input:** path do repositório legado  
**Output:** `outputs/upstream/inventory.json`

## Instrução
Ativar `discovery-scout` e executar `*scan-repo`. Fornecer o caminho do repositório legado e aguardar o `inventory.json` com a lista completa de objetos (tabelas, jobs, notebooks, scripts, views).

## Critério de Conclusão
- [ ] `inventory.json` gerado com ≥ 95% dos objetos mapeados
- [ ] Objetos classificados por tipo (table, view, job, notebook, script)
- [ ] Volume estimado de linhas por objeto registrado
