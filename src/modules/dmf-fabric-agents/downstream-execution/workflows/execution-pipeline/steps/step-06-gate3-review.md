# Step 06 — Gate 3 Review

**Agente:** migration-coordinator  
**Task:** validate-gate-3  
**Input:** `outputs/downstream/` completo + `reconciliation-report.md`  
**Output:** `outputs/summary/gate3-decision.md`

## Instrução
Ativar `migration-coordinator` e executar `*validate-gate-3`. O agente verifica paridade de dados ≥ 99.9% e emite a decisão formal de encerramento da wave.

## Critério de Conclusão
- [ ] GateScore ≥ `gate_thresholds.gate_3` do `wave-config.yaml` (fonte única de verdade - não usar valor fixo neste step)
- [ ] Paridade de dados ≥ 99.9% confirmada
- [ ] `gate3-decision.md` com status APPROVED e wave encerrada
