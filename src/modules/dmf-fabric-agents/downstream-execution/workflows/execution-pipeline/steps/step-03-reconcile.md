# Step 03 — Reconcile Data

**Agente:** reconciliation  
**Task:** reconcile-wave  
**Input:** dados origem e destino pós-carga  
**Output:** `outputs/downstream/reconciliation-report.md`

## Instrução
Ativar `reconciliation` e executar `*reconcile-wave`. O agente compara row counts, checksums e schemas entre origem e destino, identificando discrepâncias.

## Critério de Conclusão
- [ ] Paridade de dados ≥ 99.9% (threshold Gate 3)
- [ ] `reconciliation-report.md` gerado por tabela
- [ ] Discrepâncias documentadas e classificadas por severidade
