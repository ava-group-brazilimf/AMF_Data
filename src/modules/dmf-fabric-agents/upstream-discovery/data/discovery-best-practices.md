# 📚 Discovery Scout — Best Practices

> **Agent**: Discovery Scout 🔍 · **Phase**: UPSTREAM · **Gate**: 1

---

## 1. Multi-Platform Scanning

### General Principles
- **Sempre use credenciais read-only** — o Discovery Scout nunca deve modificar o ambiente de origem.
- **Prefira APIs oficiais** sobre acesso direto a repositories quando disponível.
- **Implemente timeout e retry** — conexões com plataformas legacy são instáveis.
- **Scan em horários de baixa carga** — evite competir com workloads de produção.

### Per-Platform Guidelines

#### Cloudera/Hadoop
- Use o **Hive Metastore** via Thrift API para listar databases, tabelas e partições.
- Acesse o **HDFS** via WebHDFS para tamanhos de arquivos e contagens.
- Parse o **Oozie** coordinator/workflow XML para descobrir jobs.
- Consulte o **Hue** saved queries para scripts ad-hoc.
- **Cuidado**: partições em Hive podem chegar a centenas de milhares — use paginação.

#### SSIS
- Consulte o catálogo **MSDB/SSISDB** para listar packages, projects e environments.
- Parse **DTSX files** como XML para extrair dataflows e transformações.
- Verifique **SQL Server Agent Jobs** para scheduling e histórico de execução.
- **Cuidado**: packages DTSX podem ser muito grandes (>100MB) — parse incremental.

#### Airflow
- Use a **Airflow REST API** para listar DAGs, tasks e runs.
- Parse **DAG files** (Python) com AST walkers para extrair dependências.
- Verifique **Variables e Connections** para configurações de ambiente.
- **Cuidado**: DAGs com geração dinâmica de tasks requerem execução do Python para resolução.

#### Informatica
- Use a **Repository API** para listar mappings, sessions e workflows.
- Parse **XML exports** para detalhes de transformações.
- Verifique **PowerCenter Repository** para dependências.
- **Cuidado**: naming conventions em Informatica são frequentemente inconsistentes.

#### SAP BODS
- Acesse o **BODS Repository** para listar dataflows, jobs e workflows.
- Parse **XML exports** para transformações e lógica.
- Verifique **Data Services Management Console** para scheduling.
- **Cuidado**: BODS tem objetos aninhados profundamente — ensure recursive scanning.

---

## 2. Metadata Extraction

### Essential Metadata Fields
Para cada objeto, extraia no mínimo:

| Campo              | Descrição                          | Obrigatório |
|--------------------|------------------------------------|-------------|
| `object_id`        | Identificador único                | ✅          |
| `object_name`      | Nome do objeto                     | ✅          |
| `object_type`      | Tipo (table, view, pipeline, etc.) | ✅          |
| `database/schema`  | Localização no ambiente            | ✅          |
| `created_date`     | Data de criação                    | ✅          |
| `modified_date`    | Última modificação                 | ✅          |
| `owner`            | Proprietário/criador               | ⚠️          |
| `row_count`        | Contagem de linhas (tabelas)       | ⚠️          |
| `size_bytes`       | Tamanho em bytes (tabelas)         | ⚠️          |
| `partition_count`  | Número de partições                | ⚠️          |
| `description`      | Descrição/comentário               | ⚠️          |

### Best Practices
- **Normalize nomes**: converta para lowercase, remova espaços, use underscores.
- **Valide tipos**: use um enum fixo de tipos (TABLE, VIEW, PROCEDURE, PIPELINE, JOB, SCRIPT).
- **Trate nulls**: use "UNKNOWN" para campos obrigatórios sem valor.
- **Registre a fonte**: indique de onde cada metadado veio (API, query, file parse).
- **Timestamp tudo**: registre quando cada metadado foi coletado.

---

## 3. Complexity Classification

### Scoring Algorithm Best Practices
- **Calibre pesos com dados históricos** — se disponível, use dados de migrações anteriores.
- **Revise outliers manualmente** — pipelines com score muito alto ou muito baixo merecem revisão humana.
- **Documente exceções** — quando um pipeline é reclassificado manualmente, registre justificativa.
- **Use bins progressivos** — os thresholds devem refletir a distribuição real dos dados.

### Classification Tips
- Pipelines com **UDFs em linguagens não-standard** (ex: C++, R) devem receber bonus de complexidade.
- Pipelines com **mais de 3 fontes de dados distintas** são inerentemente mais complexos.
- **Jobs que chamam outros jobs** (cascata) devem ser classificados como conjunto, não individualmente.
- **Pipelines com error handling complexo** (try-catch, retry logic) são mais difíceis de migrar.
- **Não subestime pipelines "simples"** — frequentemente têm lógica escondida em views ou procedures.

---

## 4. Dependency Analysis

### Graph Construction Best Practices
- **Use IDs únicos como nós**, não nomes — nomes podem ser duplicados entre databases.
- **Classifique arestas por tipo**: DATA_FLOW (dados fluem), CONTROL_FLOW (orquestração), REFERENCE (menção).
- **Inclua objetos externos não controlados**: se um pipeline lê de uma API externa, crie um nó EXTERNAL.
- **Valide com stakeholders**: o grafo de dependências deve ser revisado por quem conhece o ambiente.

### Cycle Detection
- **Ciclos verdadeiros são raros** — geralmente indicam que a mesma tabela é source e target (SCD).
- **Ciclos aparentes podem ser temporais** — tabela A depende de B (mensal), B depende de A (diário).
- **Documente todos os ciclos** — mesmo que resolvíveis, são riscos de migração.

### Graph Optimization
- **Remova self-loops** (tabela referenciando a si mesma) antes de calcular métricas.
- **Identifique bridge nodes** — nós cuja remoção desconecta o grafo; são pontos críticos.
- **Calcule betweenness centrality** — identifica os objetos mais "importantes" na rede.

---

## 5. Dead Code Detection

### Detection Rules
- **Seja conservador**: é melhor marcar como "SUSPECT" do que excluir erroneamente.
- **Use múltiplos sinais**: uma tabela é orphan somente se TODOS os sinais confirmam (sem referências + sem acesso recente + sem jobs ativos).
- **Consulte stakeholders** antes de confirmar exclusão — pode haver processos manuais não documentados.
- **Verifique sazonalidade**: um job que roda apenas no fim do ano fiscal pode parecer deprecated em julho.

### Thresholds Recomendados
| Sinal                     | Threshold | Confidence |
|---------------------------|-----------|------------|
| Sem referências no grafo  | -         | MEDIUM     |
| Sem acesso > 180 dias     | 180 dias  | MEDIUM     |
| Job disabled > 90 dias    | 90 dias   | HIGH       |
| Sem execução > 365 dias   | 365 dias  | HIGH       |
| Múltiplos sinais combinados | -       | VERY HIGH  |

### Exclusion Workflow
1. **Identificar** → agente detecta automaticamente
2. **Classificar** → atribuir nível de confiança
3. **Documentar** → incluir no dead-code-report.md
4. **Revisar** → stakeholder valida exclusão
5. **Confirmar** → marcar como excluded no inventory final
6. **Preservar** → manter backup/referência do código excluído

---

## Checklist de Qualidade do Inventário

| Critério                                | Meta      |
|-----------------------------------------|-----------|
| Cobertura de objetos                    | 100%      |
| Metadados completos (campos obrigatórios)| > 95%    |
| Classificação atribuída                 | 100%      |
| Dependências mapeadas                   | > 90%     |
| Dead code identificado                  | > 85%     |
| Volumes estimados                       | > 80%     |
| Validação com stakeholders              | ✅        |

---

> **Best Practices**: Discovery Scout 🔍 · **Version**: 4.0 · **Phase**: UPSTREAM · **Gate**: 1
