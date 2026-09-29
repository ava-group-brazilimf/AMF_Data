# Step 01 — Triage & Route

**Agente:** master-agent  
**Task:** route  
**Input:** solicitação do usuário  
**Output:** `route-recommendation.md` (agente recomendado)

## Instrução
Ativar `master-agent` e executar `*route`. O agente identifica o contexto atual (fase, gate, agente mais adequado) e recomenda o próximo passo.

## Critério de Conclusão
- [ ] Agente correto identificado
- [ ] Contexto da wave compreendido
- [ ] Usuário direcionado ao agente especializado
