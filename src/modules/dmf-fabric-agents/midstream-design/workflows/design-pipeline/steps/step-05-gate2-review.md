# Step 05 — Gate 2 Review

**Agente:** migration-coordinator  
**Task:** validate-gate-2  
**Input:** `outputs/midstream/` completo + `outputs/midstream/validation-report.md`  
**Output:** `outputs/summary/gate2-decision.md`

## Instrução
Ativar `migration-coordinator` e executar `*validate-gate-2`. O agente verifica se todos os artefatos de Gate 2 estão presentes e calcula o GateScore.

## Critério de Conclusão
- [ ] GateScore ≥ `gate_thresholds.gate_2` do `wave-config.yaml` (fonte única de verdade - não usar valor fixo neste step)
- [ ] `gate2-decision.md` emitido com decisão APPROVED
- [ ] Aprovação formal registrada antes de avançar para DOWNSTREAM
