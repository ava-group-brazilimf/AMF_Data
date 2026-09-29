# Step 01 — Validate Code

**Agente:** quality-gate  
**Task:** semantic-equivalence  
**Input:** `outputs/midstream/generated-code/`, `pseudocode/*.json`  
**Output:** `outputs/midstream/validation-report.md`

## Instrução
Ativar `quality-gate` e executar `*semantic-equivalence`. O agente verifica se o código gerado é semanticamente equivalente ao pseudocódigo legado e executa os testes unitários.

## Critério de Conclusão
- [ ] Equivalência semântica ≥ 95%
- [ ] `validation-report.md` gerado com score por objeto
- [ ] Zero falhas críticas nos testes unitários
