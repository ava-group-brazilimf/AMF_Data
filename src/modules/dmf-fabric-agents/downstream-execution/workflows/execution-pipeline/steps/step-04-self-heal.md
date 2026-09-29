# Step 04 — Self-Heal Errors

**Agente:** self-healing  
**Task:** diagnose-error  
**Input:** `execution-log.md`, discrepâncias do reconciliation  
**Output:** `outputs/downstream/healing-report.md`

## Instrução
Ativar `self-healing` e executar `*diagnose-error` para cada erro ou discrepância identificada. O agente diagnostica a causa raiz, aplica a correção e aprende o padrão.

## Critério de Conclusão
- [ ] Todos os erros críticos corrigidos ou escalados
- [ ] `healing-report.md` com causa raiz e fix aplicado
- [ ] Padrões de erro registrados para reuso futuro
