# ✅ Discovery Scout — Checklist de Execução

> **Agent**: Discovery Scout 🔍 · **Phase**: UPSTREAM · **Gate**: 1

---

## 1. Pre-Scan

- [ ] Migration plan recebido do Migration Coordinator (Orion 🧭)
- [ ] Configuração de conexão com plataforma-fonte disponível
- [ ] Credenciais de leitura validadas e testadas
- [ ] Plataforma-fonte identificada (Cloudera, SSIS, Airflow, Informatica, SAP BODS)
- [ ] Diretório de output criado (`projects/{project_name}/outputs/upstream/discovery/`)
- [ ] Parsers e conectores apropriados inicializados
- [ ] Permissões de acesso a todos os repositórios confirmadas

---

## 2. Scan Execution (`*scan-repo`)

- [ ] Conexão com plataforma-fonte estabelecida
- [ ] Todos os databases/schemas enumerados
- [ ] Todas as tabelas catalogadas (com row counts e tamanhos)
- [ ] Todas as views catalogadas (com queries subjacentes)
- [ ] Todas as stored procedures/functions catalogadas
- [ ] Todos os pipelines ETL descobertos
- [ ] Todos os jobs de orquestração descobertos
- [ ] Todos os scripts catalogados
- [ ] Todas as conexões/ligações registradas
- [ ] Metadados extraídos para cada objeto
- [ ] IDs únicos atribuídos a todos os objetos
- [ ] `inventory.json` gerado e salvo
- [ ] Erros de acesso documentados e logados
- [ ] Summary statistics gerado

---

## 3. Classification (`*classify`)

- [ ] Inventory carregado com sucesso
- [ ] Algoritmo de scoring aplicado a todos os pipelines
- [ ] Scores calculados: transformações, linguagens, dependências, UDFs, volume
- [ ] Weighted scores calculados
- [ ] Classificação atribuída (Simple, Moderate, Complex, Very Complex)
- [ ] Effort estimates calculados
- [ ] Top 10 pipelines mais complexos identificados
- [ ] `classification.json` gerado e salvo

---

## 4. Dependency Mapping (`*map-dependencies`)

- [ ] Referências de SQL parseadas (FROM, JOIN, INSERT INTO)
- [ ] Imports de scripts parseados (Python, Scala, Java)
- [ ] Referências de configuração parseadas
- [ ] DAG construído com todos os nós e arestas
- [ ] Detecção de ciclos executada
- [ ] Métricas do grafo calculadas (depth, degree, components)
- [ ] Nós raiz (sources) identificados
- [ ] Nós folha (sinks) identificados
- [ ] Hub nodes identificados
- [ ] Topological sort calculado
- [ ] Critical path identificado
- [ ] `dependency-graph.json` gerado e salvo

---

## 5. Dead Code Detection (`*detect-dead-code`)

- [ ] Tabelas órfãs identificadas (in_degree=0, out_degree=0)
- [ ] Scripts sem uso identificados (sem referências em pipelines/jobs)
- [ ] Jobs depreciados identificados (sem execução > 90 dias + disabled)
- [ ] Cross-reference analysis executada
- [ ] Dead code clusters identificados
- [ ] Storage savings calculado
- [ ] Scope reduction calculado
- [ ] `dead-code-report.md` gerado e salvo
- [ ] Recomendações de exclusão documentadas

---

## 6. Volume Estimation (`*estimate-volume`)

- [ ] Tamanhos de tabelas consultados ou estimados
- [ ] Row counts obtidos
- [ ] Partition counts e métricas calculadas
- [ ] Tabelas com excesso de partições flagged (> 10.000)
- [ ] Tabelas com skew de partições flagged (> 10x ratio)
- [ ] Transfer times estimados (serial, parallel-4, parallel-8)
- [ ] Top 50 maiores tabelas identificadas
- [ ] `data-volume-estimate.json` gerado e salvo
- [ ] Recomendações de otimização documentadas

---

## 7. Post-Discovery (`*generate-inventory`)

- [ ] Todos os artefatos anteriores carregados
- [ ] Inventory enriquecido com: classificação, dependências, dead code, volumes
- [ ] Migration priority calculada para cada objeto
- [ ] Migration waves definidas (Wave 1, 2, 3+)
- [ ] Dead code flagged para exclusão
- [ ] Summary statistics consolidado
- [ ] Enriched `inventory.json` final gerado
- [ ] Relatório human-readable gerado (Markdown)
- [ ] Artefatos organizados nos subdiretórios corretos
- [ ] Pronto para Gate 1 review
- [ ] Artefatos entregues ao Migration Coordinator (Orion 🧭)
- [ ] Artefatos disponibilizados para Logic Extractor (Logan 🧠)

---

## Critérios de Aprovação — Gate 1

| Critério                                        | Status |
|-------------------------------------------------|--------|
| 100% dos objetos catalogados no inventário      | ⬜     |
| Classificação de complexidade atribuída          | ⬜     |
| Grafo de dependências sem erros críticos         | ⬜     |
| Dead code identificado e documentado             | ⬜     |
| Volumes estimados com accuracy > 80%             | ⬜     |
| Relatório final gerado e revisado                | ⬜     |
| Migration waves definidas                        | ⬜     |

---

> **Checklist**: Discovery Scout 🔍 · **Version**: 4.0 · **Phase**: UPSTREAM · **Gate**: 1
