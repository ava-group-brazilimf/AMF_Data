# Step 06 — Gate 1 Review

**Agente:** migration-coordinator  
**Task:** validate-gate-1  
**Input:** todos os artefatos de `outputs/upstream/`  
**Output:** `outputs/summary/gate1-decision.md`

## Instrução
Ativar `migration-coordinator` e executar `*validate-gate-1`. O agente calcula o GateScore e emite a decisão formal de Gate 1.

## Fórmula GateScore
`0.35 × Completude + 0.25 × Qualidade + 0.20 × RiscoResidual + 0.20 × Reconciliação`

## Critério de Conclusão
- [ ] GateScore ≥ `gate_thresholds.gate_1` do `wave-config.yaml` (fonte única de verdade - não usar valor fixo neste step)
- [ ] `gate1-decision.md` gerado com decisão, score e open items
- [ ] Aprovação registrada antes de avançar para MIDSTREAM
