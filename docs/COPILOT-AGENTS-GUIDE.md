# Guia de Execução — Agentes via GitHub Copilot Chat

> **Tipo:** How-to Guide
> **Público:** Equipe de migração (analistas, engenheiros, estagiários)
> **Pré-requisito:** VS Code com GitHub Copilot habilitado e workspace aberto

---

## Tabela de Conteúdo

- [Como Trocar de Agente](#como-trocar-de-agente)

- [Mapa Completo de Agentes](#mapa-completo-de-agentes)

- [Fase 0 — Setup e Orientação](#fase-0--setup-e-orientação-inicial)

- [Fase 1 — UPSTREAM: Discovery e Gate 1](#fase-1--upstream-discovery-e-gate-1)

- [Fase 2 — MIDSTREAM: Design e Gate 2](#fase-2--midstream-design-e-gate-2)

- [Fase 3 — DOWNSTREAM: Execução e Gate 3](#fase-3--downstream-execução-e-gate-3)

- [Fase 4 — Pós-Migração](#fase-4--pós-migração)

- [Agentes Opcionais](#agentes-opcionais)

- [Ferramentas de Otimização de Tokens (Headroom MCP)](#ferramentas-de-otimização-de-tokens-headroom-mcp)

- [Troubleshooting de Agentes](#troubleshooting-de-agentes)

---

## Como Trocar de Agente

1. Abra o painel **GitHub Copilot Chat** no VS Code (`Ctrl+Alt+I`)
2. Clique no seletor de modo no canto superior esquerdo do chat:
   ```

   [ Ask ▼ ]  ← clique aqui
   ```

3. Selecione o agente desejado na lista
4. O agente se apresenta automaticamente com seu menu de comandos

> **Dica:** Se não souber qual agente usar, comece sempre pelo `master-agent` e digite `*route`.

---

## Mapa Completo de Agentes

| Ícone | Chat Mode | Persona | Fase | Gate | Quando Usar |
| --- | --- | --- | --- | --- | --- |

| 🎛️ | `master-agent` | Master Agent | ALL | Todos | Ponto de entrada, roteamento, dúvidas gerais |
| 🧭 | `migration-coordinator` | Orion | CORE | 1/2/3 | Orquestrar waves, validar gates, gerenciar rollbacks |
| 🔍 | `discovery-scout` | Scout | UPSTREAM | Pré-1 | Descobrir e catalogar objetos no sistema legado |
| 📦 | `inventory-scout` | Scout | UPSTREAM | Pré-1 | Inventário de repositório, detecção de tech-stack |
| 🎯 | `data-strategist` | DataStrategist | UPSTREAM | 1 | Problem statement, KPIs, critérios de sucesso |
| 📋 | `business-analyst` | Mary | UPSTREAM | 1 | STTM, regras de DQ, mapeamento fonte-destino |
| 🧠 | `logic-extractor` | Logan | UPSTREAM | 1 | Extrair lógica de negócio e gerar artefatos AST (`canonical-model.json`) |
| 🏛️ | `data-architect` | Winston | MIDSTREAM | 2 | Arquitetura de dados, decisões técnicas, Gate 2 |
| 🧩 | `data-modeler` | Sofia | MIDSTREAM | 2 | Modelo lógico, granularidade, metadados |
| 🛡️ | `data-steward` | Gaia | MIDSTREAM | 2 | Governança de dados, catálogo, políticas |
| ⚙️ | `code-generator` | Coda | MIDSTREAM | 2 | Gerar DDL/ETL a partir de pseudocódigo ou AST canônico |
| ✅ | `quality-gate` | Vera | MIDSTREAM | 2 | Validar código gerado, scoring de qualidade |
| 🔒 | `security-compliance` | Shield | MIDSTREAM | 2 | Detectar PII, data masking, compliance |
| 🛠️ | `downstream-executor` | Diego | DOWNSTREAM | 3 | Executar waves, DDL/ETL, Gate 3 readiness |
| ⚖️ | `reconciliation` | Balance | DOWNSTREAM | 3 | Row count, checksums, schema diffs, parity |
| 🔥 | `self-healing` | Phoenix | DOWNSTREAM | 3 | Diagnosticar erros, aplicar correções automáticas |
| 📚 | `documentation` | Scribe | DOWNSTREAM | 3 | Runbooks, changelogs, relatórios, wave report |
| 📊 | `bi-semantic` | Bianca | DOWNSTREAM | Opcional | Dashboards, semantic models, analytics |
| 🔁 | `iteration-improvement` | Kai | DOWNSTREAM | Pós-3 | Melhorias iterativas pós-wave |

---

## Fase 0 — Setup e Orientação Inicial

### Agente: `master-agent`

**Como ativar:**

```

[Selecione: master-agent]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*help` | Lista todos os comandos | Menu interativo |
| `*agents` | Lista todos os agentes com descrição | Tabela de agentes |
| `*route` | Recomenda o próximo agente com base no contexto | Recomendação + justificativa |
| `*kb` | Responde dúvidas sobre o Avanade Method | Explicação |
| `*status` | Mostra status geral do projeto | Dashboard de progresso |

**Prompts de exemplo:**

```

> *route
Contexto: estou começando um projeto de migração de SQL Server para Databricks

> *agents
Quero ver todos os agentes da fase DOWNSTREAM

> *kb
Qual a diferença entre Gate 2 e Gate 3?

```

**Saídas esperadas:**

- Recomendação do agente correto para o contexto

- Menu de navegação entre fases

- Respostas sobre o método

---

## Fase 1 — UPSTREAM: Discovery e Gate 1

### Agente: `discovery-scout` 🔍

**Como ativar:**

```

[Selecione: discovery-scout]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*scan-repo` | Escaneia o repositório legado | Inventário de objetos |
| `*classify` | Classifica objetos por complexidade | Heatmap de complexidade |
| `*map-dependencies` | Mapeia dependências entre objetos | Diagrama DAG (Mermaid) |
| `*detect-dead-code` | Identifica código não utilizado | Lista de objetos órfãos |
| `*estimate-volume` | Estima volumes de dados | Tabela de volumes por entidade |
| `*help` | Lista todos os comandos | Menu interativo |

**Prompts de exemplo:**

```

> *scan-repo
Fonte: SQL Server 2019, banco: NORTHWIND_PROD

> *classify
Classifique todos os stored procedures encontrados

> *map-dependencies
Mostre as dependências da tabela Orders

```

**Entradas necessárias:**

- Conexão ou path do sistema legado

- Lista de schemas/databases a escanear

**Saídas esperadas:**

- `inventory-report.md` — catálogo completo de objetos

- Diagrama de dependências (Mermaid `graph TD`)

- Matriz de complexidade (Low/Medium/High)

- Estimativa de volumes por entidade

---

### Agente: `data-strategist` 🎯

**Como ativar:**

```

[Selecione: data-strategist]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*define-problem` | Guia criação do problem statement | `gate1-problem-statement.md` |
| `*create-kpis` | Define KPIs mensuráveis | `gate1-kpis.md` |
| `*success-criteria` | Estabelece critérios de sucesso | `success-criteria.md` |
| `*stakeholders` | Mapeia stakeholders | `stakeholders.md` |
| `*value-prop` | Cria proposta de valor dos dados | `value_proposition.md` |
| `*strategy-summary` | Gera resumo da estratégia | `strategy-summary.md` |

**Prompts de exemplo:**

```

> *define-problem
Projeto: migração do ERP legado para Azure Databricks
Motorista de negócio: consolidar 3 sistemas de relatórios em um

> *create-kpis
Baseado no problem statement que acabamos de criar

> *success-criteria
Critério principal: zero perda de dados e latência ≤ 2h em PROD

```

**Entradas necessárias:**

- Briefing de negócio

- Escopo do projeto (sistemas, entidades, ambientes)

- Stakeholders identificados

**Saídas esperadas** (Gate 1 artifacts):

- `gate1-problem-statement.md` — template preenchido e aprovado

- `gate1-kpis.md` — 5 KPIs com owners, targets e método de medição

- `strategy-summary.md` — visão executiva

---

### Agente: `business-analyst` 📋

**Prompts de exemplo:**

```

> olá

> Criar STTM para a entidade Orders:
  Fonte: dbo.Orders (SQL Server)
  Destino: gold.orders (Delta Lake)
  Campos: OrderID, CustomerID, OrderDate, TotalAmount, Status

> Definir regras de DQ para a entidade Orders:
  - OrderID não pode ser nulo
  - TotalAmount deve ser > 0
  - Status deve ser um dos valores: OPEN, CLOSED, CANCELLED

```

**Saídas esperadas:**

- `sttm.md` — Source-to-Target Mapping completo

- `dq-rules.md` — regras de qualidade por entidade

- `data-dictionary.md` — dicionário de dados

---

### Agente: `logic-extractor` 🧠 (Logan)

**Como ativar:**

```text
[Selecione: logic-extractor]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*extract-logic` | Extrai lógica de negócio de código legado | `logic-report.md`, `pseudocode/*.json` |
| `*extract-ast` | Executa AST Engine para SQL/SSIS | `canonical-model.json`, `column-lineage.json`, `sttm.md` |
| `*generate-pseudocode` | Converte lógica para pseudocódigo agnóstico | `pseudocode/*.json` |
| `*create-digital-twin` | Cria blueprint semântico do ambiente legado | `digital-twin.json` |
| `*confidence-report` | Gera score de confiança por pipeline | `confidence-report.md` |
| `*help` | Lista todos os comandos | Menu interativo |

**Prompts de exemplo:**

```text
> *extract-ast
Tipo de origem: SQL
Dialeto: tsql
Path: projects/bradesco/legacy/extracted/orders.sql
Plataforma alvo: Fabric

> *extract-ast
Tipo de origem: SSIS
Path: projects/sample-migration/legacy/ssis/LoadOrders.dtsx
Plataforma alvo: Databricks
```

**Saídas esperadas:**

- `canonical-model.json` — modelo canônico da pipeline
- `column-lineage.json` — lineage coluna-a-coluna
- `sttm.md` — STTM derivado automaticamente

---

## Fase 2 — MIDSTREAM: Design e Gate 2

### Agente: `migration-coordinator` 🧭 (Orion)

**Como ativar:**

```text
[Selecione: migration-coordinator]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*start-wave` | Valida e inicia uma wave existente | Contexto carregado + `outputs/summary/wave-status.md` |
| `*gate1-validate` | Valida artefatos e calcula GateScore do Gate 1 | Relatório de gate com score |
| `*gate2-validate` | Valida artefatos e calcula GateScore do Gate 2 | Relatório de gate com score |
| `*gate3-validate` | Valida artefatos e calcula GateScore do Gate 3 | Relatório de gate com score |
| `*wave-status` | Resumo de status da wave atual | Dashboard de progresso |
| `*rollback` | Aciona playbook de rollback | Rollback plan ativado |
| `*route` | Recomenda próximo agente | Recomendação contextualizada |
| `*help` | Lista todos os comandos | Menu interativo |

**Prompts de exemplo:**

```text
> *start-wave
wave_config_path: projects/migration-northwind/wave-config.yaml

> *gate1-validate
Wave: WAVE-002

> *wave-status

```

**Saídas esperadas:**

- `projects/migration-northwind/context/` carregado antes da delegação
- Artefatos somente em `projects/migration-northwind/outputs/{upstream,midstream,downstream,summary}/`

- Relatório de GateScore com decisão APPROVED / CAVEATS / BLOCKED

- `gate{N}-decision.md` com score, aprovadores e open items

---

### Agente: `data-architect` 🏛️ (Winston)

**Como ativar:**

```text
[Selecione: data-architect]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*design-architecture` | Cria arquitetura de dados para a wave | `architecture.md` |
| `*adr` | Registra uma Architecture Decision Record | `decisions.md` atualizado |
| `*monitoring-spec` | Define especificação de observabilidade e SLOs | `monitoring-spec.md` |
| `*review-architecture` | Revisão crítica de uma arquitetura existente | Feedback estruturado |
| `*help` | Lista todos os comandos | Menu interativo |

**Entradas necessárias:**

- STTM da fase UPSTREAM

- Plataforma destino (Databricks / Fabric / Snowflake / outro)

- Nomes e tiers das entidades no escopo

**Saídas esperadas** (artefatos Winston — Gate 2):

- `architecture.md` — decisões de zona (bronze/silver/gold), particionamento, estratégia de carga

- `decisions.md` — ADRs com contexto, decisão e consequências

- `monitoring-spec.md` — SLIs, SLOs, alertas e dashboards

---

### Agente: `data-modeler` 🧩 (Sofia)

**Como ativar:**

```text
[Selecione: data-modeler]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*create-model` | Cria modelo lógico de dados | `data-model.md` |
| `*review-granularity` | Revisa granularidade e chaves | Recomendações de modelo |
| `*data-contracts` | Gera contratos de dados declarativos | `data-contracts.md` |
| `*metrics-catalog` | Cria catálogo de métricas de negócio | `metrics-catalog.md` |
| `*help` | Lista todos os comandos | Menu interativo |

**Saídas esperadas** (artefatos Sofia — Gate 2):

- `data-model.md` — modelo lógico com entidades, atributos, PKs/FKs, tipos, cardinalidades e diagrama ER (Mermaid)

- `data-contracts.md` — contratos YAML por entidade (compatível com `data_contract_validator.py`)

- `metrics-catalog.md` — métricas de negócio com owners e cálculo

---

### Agente: `data-steward` 🛡️ (Gaia)

**Como ativar:**

```text
[Selecione: data-steward]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*catalog` | Registra entidades no catálogo de dados | Entradas de catálogo por entidade |
| `*define-policies` | Define políticas de acesso e retenção | Políticas documentadas |
| `*dq-governance` | Revisa e formaliza regras de DQ | `dq-rules.md` governado |
| `*lineage` | Documenta lineagem de dados | `data-lineage.md` |
| `*help` | Lista todos os comandos | Menu interativo |

---

### Agente: `code-generator` ⚙️ (Coda)

**Como ativar:**

```text
[Selecione: code-generator]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*generate-ddl` | Gera DDL a partir do data-model.md | Scripts DDL por entidade |
| `*generate-etl` | Gera ETL por camada de pipeline | Scripts ETL (bronze→silver→gold) |
| `*generate-from-ast` | Gera código multi-plataforma a partir de `canonical-model.json` | `generated-code/fabric/`, `generated-code/databricks/`, `generated-code/airflow/` |
| `*generate-tests` | Gera testes de integração | `tests/` com cobertura >= 80% |
| `*refactor` | Refatora código gerado para padrões do projeto | Código refatorado |
| `*help` | Lista todos os comandos | Menu interativo |

---

### Agente: `quality-gate` ✅ (Vera)

**Como ativar:**

```text
[Selecione: quality-gate]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*validate-code` | Valida DDL/ETL gerado contra padrões | Lista de violações e recomendações |
| `*score` | Calcula GateScore de qualidade | Score por dimensão + decisão |
| `*review-artifacts` | Revisa artefatos de um gate | Feedback estruturado |
| `*checklist` | Valida checklist de artefatos obrigatórios | Status por artefato |
| `*help` | Lista todos os comandos | Menu interativo |

**Saídas esperadas:**

- `quality-gate-evidence.md` — scoring, status PASS/FAIL explícito, open items com severidade

---

### Agente: `security-compliance` 🔒 (Shield)

**Como ativar:**

```text
[Selecione: security-compliance]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*detect-pii` | Detecta campos com PII nas entidades | Lista de PII por campo |
| `*masking-rules` | Define estratégia de masking por ambiente | Regras de masking DEV/HML/PROD |
| `*compliance-check` | Verifica conformidade LGPD/GDPR | Relatório de compliance |
| `*help` | Lista todos os comandos | Menu interativo |

**Saídas esperadas:**

- `security-compliance-report.md` — PII detectados, status de masking, recomendações de compliance

---

## Fase 3 — DOWNSTREAM: Execução e Gate 3

### Agente: `downstream-executor` 🛠️ (Diego)

**Como ativar:**

```text
[Selecione: downstream-executor]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*dry-run` | Executa wave em modo dry run | Relatório de validação pré-execução |
| `*create-runbook` | Cria execution-runbook com rollback plan | `execution-runbook.md` |
| `*execute-wave` | Executa a wave no ambiente real | Logs de execução, evidências |
| `*rollback` | Executa rollback da wave | Relatório de rollback |
| `*gate3-package` | Prepara pacote completo de Gate 3 | Checklist de artefatos Gate 3 |
| `*help` | Lista todos os comandos | Menu interativo |

**Entradas necessárias:**

- Pacote Gate 2 completo (`ddl/`, `etl/`, `tests/`, artefatos de arquitetura)

- Credenciais e endpoint do ambiente destino

- `execution-runbook.md` aprovado (obrigatório antes de non-dry run)

**Saídas esperadas** (pacote Gate 3):

- `ddl/` — scripts DDL executados com sucesso

- `etl/` — scripts ETL executados com sucesso

- `tests/` — testes de integração passando

- `documentation/` — wave-report, runbook, lineage

- `wave-report.md` — relatório completo de entrega

---

### Agente: `reconciliation` ⚖️ (Balance)

**Como ativar:**

```text
[Selecione: reconciliation]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*row-count` | Compara contagens fonte vs destino | Paridade de row count por entidade |
| `*checksum` | Valida checksums para entidades de alto risco | Evidência de integridade |
| `*schema-diff` | Compara schemas fonte vs destino | Lista de divergências de schema |
| `*aggregate-parity` | Valida somas e médias de campos financeiros | Evidência de paridade agregada |
| `*help` | Lista todos os comandos | Menu interativo |

**Saídas esperadas:**

- `reconciliation-evidence.md` — row counts, checksums, schema diffs, status PASS/FAIL por entidade

- Entidades com desvio registradas com severidade (CRITICAL / WARNING)

---

### Agente: `self-healing` 🔥 (Phoenix)

**Como ativar:**

```text
[Selecione: self-healing]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*diagnose` | Diagnostica erro de execução | Root cause analysis estruturado |
| `*apply-fix` | Aplica correção sugerida | Fix aplicado + re-execução |
| `*pattern-log` | Registra padrão de erro para aprendizado | `error-pattern-log.md` |
| `*escalate` | Escala problema para coordinator | Ticket de escalação |
| `*reflect` | Auto-crítica da solução (Evaluator-Optimizer) | Score por dimensão + decisão ACCEPT/REFINE/ESCALATE |
| `*help` | Lista todos os comandos | Menu interativo |

**Protocolo `*reflect` (self-critique):**

O comando `*reflect` aplica o CRITIQUE_RUBRIC sobre a última solução gerada:

| Dimensão | Peso | Critério |
| --- | --- | --- |

| Correctness | 0.4 | A solução resolve o problema corretamente? |
| Safety | 0.3 | Existe risco de perda de dados ou side effects? |
| Idiomatic | 0.2 | Segue padrões e convenções do projeto? |
| Learnability | 0.1 | O resultado é auditável e documentável? |

Thresholds: `>= 0.8` ACCEPT | `0.6–0.79` REFINE (máx 2 loops) | `< 0.6` ESCALATE

---

### Agente: `documentation` 📚 (Scribe)

**Como ativar:**

```text
[Selecione: documentation]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*wave-report` | Gera wave report completo | `wave-report.md` |
| `*runbook-update` | Atualiza runbook com lições aprendidas | `execution-runbook.md` atualizado |
| `*data-lineage` | Documenta lineagem da wave | `data-lineage.md` |
| `*changelog` | Gera changelog da wave | `changelog.md` |
| `*help` | Lista todos os comandos | Menu interativo |

---

## Fase 4 — Pós-Migração

### Agente: `iteration-improvement` 🔁 (Kai)

**Como ativar:**

```text
[Selecione: iteration-improvement]
> olá

```

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*retrospective` | Conduz retrospectiva da wave | Ações de melhoria |
| `*update-patterns` | Atualiza base de padrões com lições | Base de conhecimento atualizada |
| `*kpi-review` | Revisa KPIs do projeto | Dashboard de KPIs atualizado |
| `*next-wave` | Planeja escopo da próxima wave | Draft de wave-config para próxima wave |
| `*help` | Lista todos os comandos | Menu interativo |

---

## Agentes Opcionais

### Agente: `bi-semantic` 📊 (Bianca)

> **Quando usar:** apenas quando há entrega de camada semântica / BI no escopo da wave.

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*semantic-model` | Cria semantic model (measures, dimensions) | Modelo semântico exportável |
| `*dashboard-spec` | Especifica dashboards de entrega | Spec de dashboards |
| `*kpi-catalog` | Cataloga KPIs de negócio com owners | `kpi-catalog.md` |
| `*help` | Lista todos os comandos | Menu interativo |

---

### Agente: `inventory-scout` 📦 (Scout)

> **Quando usar:** fallback de discovery quando o escopo exige inventário profundo de repositório ou detecção de tech-stack.

**Comandos disponíveis:**

| Comando | O que faz | Saída |
| --- | --- | --- |

| `*inventory` | Inventaria repositório completo | `inventory-report.md` detalhado |
| `*detect-stack` | Detecta tech stack e frameworks | Relatório de tech stack |
| `*knowledge-graph` | Gera grafo de conhecimento do repositório | Knowledge graph (JSON/Mermaid) |
| `*help` | Lista todos os comandos | Menu interativo |

---

## Ferramentas de Otimização de Tokens (Headroom MCP)

Quando o **Headroom** está instalado e o MCP server está configurado (`.vscode/settings.json`), todos os agentes ganham acesso automático a ferramentas de compressão de contexto:

| Ferramenta MCP | O que faz | Quando usar |
| --- | --- | --- |
| `headroom_compress` | Comprime conteúdo mantendo significado semântico | Antes de passar artefatos grandes (>500KB) entre agentes |
| `headroom_retrieve` | Recupera conteúdo original de um ID comprimido | Quando um agente downstream precisa do conteúdo completo |
| `headroom_perf` | Mostra métricas de economia de tokens da sessão | Para medir ROI da compressão ao final da wave |

### Integração automática nos tasks

Os seguintes tasks já utilizam Headroom automaticamente (se disponível):

| Task | Agent | Ponto de compressão |
| --- | --- | --- |
| `*scan-repo` Step 2.1a | `discovery-scout` | Arquivos fonte >500KB |
| `*generate-inventory` Step 4a | `discovery-scout` | `inventory-enriched.json` |
| `*learn-pattern` Step 7 | `self-healing` | Padrões de falha aprendidos |

### Scripts de governança com suporte a compressão

| Script | Função Comprimida |
| --- | --- |
| `gate_score_report.py` | `generate_gate_score_report_compressed()` |
| `kpi_dashboard_report.py` | `generate_kpi_dashboard_report_compressed()` |
| `reconciliation_checks.py` | `reconcile_checksums_compressed()` |

> **Sem Headroom?** Tudo funciona normalmente. As funções `_compressed()` fazem fallback gracioso para o output completo.

---

## Troubleshooting de Agentes

| Problema | Solução |
| --- | --- |

| Agente não aparece no seletor | Verifique se `.github/agents/<nome>.chatmode.md` existe. Execute `.\.venv\Scripts\python.exe -m src.shared.scripts.validate_agent_contracts --root .` para confirmar |
| Agente não entende o contexto | Forneça: nome da wave, entidades, plataforma fonte e destino. Use os comandos `*` em vez de linguagem livre |
| Resposta sem artefato de saída | Verifique se os inputs obrigatórios foram fornecidos. Tente usar o comando específico em vez de texto livre |
| Gate score inesperadamente baixo | Execute `.\.venv\Scripts\python.exe -m src.shared.scripts.gate_score_report` para ver o breakdown por dimensão |
| Artefatos obrigatórios faltando | Execute `.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate{1,2,3}_artifacts projects\<project_name>\outputs\<phase>` |
| Não sabe qual agente usar | Use `master-agent` → `*route` com uma descrição do que quer fazer |

---

## Referência Cruzada

| Documento | Conteúdo |
| --- | --- |

| [PLAYBOOK-MIGRATION-OPERATIONS.md](PLAYBOOK-MIGRATION-OPERATIONS.md) | Fluxo passo a passo de execução de wave |
| [PLAYBOOK-ONBOARDING.md](PLAYBOOK-ONBOARDING.md) | Setup inicial do ambiente |
| [SKILLS-BLUEPRINT-BY-GATE.md](SKILLS-BLUEPRINT-BY-GATE.md) | Skills por gate com prompts prontos |
| [OPERATING-MODEL-CANVAS-v2.md](OPERATING-MODEL-CANVAS-v2.md) | Permissões e modelo operacional |
| [scripts/README.md](../scripts/README.md) | Scripts de governança e validação |
