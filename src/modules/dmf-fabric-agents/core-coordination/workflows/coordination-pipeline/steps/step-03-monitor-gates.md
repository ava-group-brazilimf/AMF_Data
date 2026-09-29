# Step 03 — Monitor Gates

**Agente:** migration-coordinator  
**Task:** project-status  
**Input:** artefatos de cada gate  
**Output:** `outputs/summary/wave-status.md`

## Instrução
Ativar `migration-coordinator` e executar `*project-status` após cada gate. O agente consolida scores, abre issues para itens pendentes e decide aprovação ou bloqueio.

## Critério de Conclusão
- [ ] Status atualizado após cada gate (Gate 1, 2 e 3)
- [ ] `wave-status.md` com score histórico por gate
- [ ] Bloqueios escalados ao PM quando GateScore < `gate_thresholds.gate_N` do `wave-config.yaml`
