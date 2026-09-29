# Skills Blueprint by Gate — Data Migration Factory

> **Tipo:** Reference Guide
> **Data:** 2026-03-21
> **Escopo:** Modelo prático de adoção de skills por gate para execução da migration factory
> **Público:** Mantenedores de agentes, migration coordinator, tech leads

---

## Tabela de Conteúdo

- [1. Propósito](#1-propósito)

- [2. Portfolio de Skills Instaladas](#2-portfolio-de-skills-instaladas)

- [3. Mapeamento Gate → Skill](#3-mapeamento-gate--skill)
  - [Gate 1 — UPSTREAM: Discovery](#gate-1--upstream-discovery)
  - [Gate 2 — MIDSTREAM: Design](#gate-2--midstream-design)
  - [Gate 3 — DOWNSTREAM: Execução](#gate-3--downstream-execução)
  - [Cross-Cutting: Governança e Agentes](#cross-cutting-governança-e-agentes)

- [4. Prompts Prontos por Skill](#4-prompts-prontos-por-skill)

- [5. Como Carregar uma Skill](#5-como-carregar-uma-skill)

---

## 1. Propósito

Definir quais skills usar em cada gate, por que cada skill foi selecionada, quais outputs ela produz, e fornecer prompts prontos para uso no dia a dia.

Uma **skill** é um pacote de conhecimento de domínio localizado em `.github/skills/<nome>/SKILL.md`. Os agentes carregam skills sob demanda para enriquecer o contexto de execução.

---

## 2. Portfolio de Skills Instaladas

### Skills Instaladas em `.github/skills/`

| Skill | Categoria | Status |
| --- | --- | --- |

| `data-quality-frameworks` | Data Quality | ✓ instalada |
| `agent-governance` | Governança | ✓ instalada |
| `observability-monitoring-slo-implement` | Observabilidade | ✓ instalada |
| `framework-migration-legacy-modernize` | Migração | ✓ instalada |
| `production-code-audit` | Qualidade | ✓ instalada |
| `tdd-orchestrator` | Testes | ✓ instalada |
| `sql-optimization-patterns` | SQL / Performance | ✓ instalada |
| `data-engineering-data-pipeline` | Engenharia | ✓ instalada |
| `multi-agent-patterns` | Arquitetura | ✓ instalada |
| `agent-evaluation` | Avaliação | ✓ instalada |
| `agentic-eval` | Avaliação | ✓ instalada |
| `agents-md` | Documentação | ✓ instalada |
| `agent-orchestration` | Orquestração | ✓ instalada |
| `agent-orchestration-improve-agent` | Orquestração | ✓ instalada |
| `agent-orchestration-multi-agent-optimize` | Orquestração | ✓ instalada |
| `agent-orchestrator` | Orquestração | ✓ instalada |
| `agentic-development-principles` | Desenvolvimento | ✓ instalada |
| `ai-agent-development` | Desenvolvimento | ✓ instalada |
| `ai-agents-architect` | Arquitetura | ✓ instalada |
| `autonomous-agent-patterns` | Padrões | ✓ instalada |
| `autonomous-agents` | Padrões | ✓ instalada |
| `agent-manager-skill` | Gerenciamento | ✓ instalada |
| `agent-memory-mcp` | Memória | ✓ instalada |
| `agent-memory-systems` | Memória | ✓ instalada |
| `multi-agent-brainstorming` | Padrões | ✓ instalada |
| `avanade-brand-guidelines` | Marca | ✓ instalada |

> Skills como `databricks`, `database-migration`, `documentation-writer`, `dependency-management-deps-audit` são gerenciadas externamente e não estão em `.github/skills/`.

---

## 3. Mapeamento Gate → Skill

### Gate 1 — UPSTREAM: Discovery

**Objetivo:** catalogar o ambiente legado, extrair lógica, mapear dependências, definir estratégia.

| Skill | Agente Primário | Por que usar | Output esperado |
| --- | --- | --- | --- |

| `framework-migration-legacy-modernize` | `discovery-scout` | Padrões strangler fig, mapeamento legado→moderno | Estratégia de migração gradual, risk registry |
| `data-quality-frameworks` | `business-analyst` | Definição de DQ rules com Great Expectations / dbt | `dq-rules.md` estruturado e validável |
| `sql-optimization-patterns` | `logic-extractor` | Análise de queries e stored procedures legadas | Mapa de problemas de performance no legado |
| `production-code-audit` | `discovery-scout`, `logic-extractor` | Auditoria linha-a-linha do código legado | Relatório de qualidade do código fonte |
| `agent-governance` | `migration-coordinator` | Políticas de tool use, audit trail de decisões | Gate decision com rastreabilidade completa |

**Artefatos obrigatórios que as skills suportam:**

- `inventory-report.md` — `framework-migration-legacy-modernize` + `production-code-audit`

- `sttm.md` — `data-quality-frameworks`

- `dq-initial.md` — `data-quality-frameworks`

- `gate1-problem-statement.md` — `framework-migration-legacy-modernize`

- `gate1-kpis.md` — `observability-monitoring-slo-implement`

---

### Gate 2 — MIDSTREAM: Design

**Objetivo:** arquitetura de dados, modelo lógico, contratos, governança, código gerado e validado.

| Skill | Agente Primário | Por que usar | Output esperado |
| --- | --- | --- | --- |

| `data-engineering-data-pipeline` | `data-architect` | Padrões de pipeline batch/streaming, camadas medallion | `architecture.md` com design de pipeline |
| `data-quality-frameworks` | `data-modeler`, `data-steward` | Data contracts, Great Expectations, dbt tests | `data-contracts.md`, `dq-rules.md` refinado |
| `tdd-orchestrator` | `code-generator`, `quality-gate` | Test-first para DDL/ETL gerado | `tests/` com cobertura >= 80% |
| `sql-optimization-patterns` | `code-generator` | DDL otimizado, índices, particionamento | DDL com estratégia de performance documentada |
| `observability-monitoring-slo-implement` | `data-architect` | SLOs, alertas, dashboards de observabilidade | `monitoring-spec.md` com SLIs e SLOs |
| `agent-governance` | `security-compliance` | Política allow/review/deny por classe de agente | Compliance report + masking rules |
| `multi-agent-patterns` | `migration-coordinator` | Coordenação supervisor/worker, handoffs | Fluxo de handoff Gate 1→2 documentado |

**Artefatos obrigatórios que as skills suportam:**

- `architecture.md` — `data-engineering-data-pipeline`

- `data-model.md` — `data-quality-frameworks`

- `decisions.md` — `agent-governance`

- `dq-rules.md` — `data-quality-frameworks`

- `monitoring-spec.md` — `observability-monitoring-slo-implement`

---

### Gate 3 — DOWNSTREAM: Execução

**Objetivo:** executar a wave, reconciliar dados, publicar evidências, fechar o ciclo com aprendizado.

| Skill | Agente Primário | Por que usar | Output esperado |
| --- | --- | --- | --- |

| `tdd-orchestrator` | `downstream-executor` | Garantir testes de integração antes do go-live | `tests/` passando com cobertura documentada |
| `observability-monitoring-slo-implement` | `reconciliation`, `downstream-executor` | SLO de desempenho, alertas de breach | SLO report + alertas configurados |
| `data-quality-frameworks` | `reconciliation` | Tolerâncias, threshold checks, evidência de paridade | `reconciliation-evidence.md` com checksums |
| `production-code-audit` | `quality-gate` | Review final do código antes de deployar em PROD | Sign-off de qualidade com auditoria |
| `agent-governance` | `migration-coordinator` | Audit trail de gate pass/fail, approvals | `gate3-decision.md` rastreável |
| `agentic-eval` | `self-healing` | Self-critique loop via `*reflect`, Evaluator-Optimizer | Diagnóstico estruturado com score de qualidade |

**Artefatos obrigatórios que as skills suportam:**

- `ddl/` + `etl/` — `tdd-orchestrator`, `sql-optimization-patterns`

- `tests/` — `tdd-orchestrator`

- `reconciliation-evidence.md` — `data-quality-frameworks`

- `wave-report.md` — `observability-monitoring-slo-implement`

- `execution-runbook.md` — `framework-migration-legacy-modernize`

---

### Cross-Cutting: Governança e Agentes

Skills que se aplicam a todos os gates e fases:

| Skill | Quando usar | Agentes que consomem |
| --- | --- | --- |

| `agent-governance` | Qualquer decisão de tool use, audit trail, policy | `migration-coordinator`, `quality-gate`, `security-compliance` |
| `agent-evaluation` | Avaliar qualidade de outputs gerados pelos agentes | `quality-gate`, `iteration-improvement` |
| `agentic-eval` | Self-critique loops, evaluator-optimizer | `self-healing`, `quality-gate` |
| `multi-agent-patterns` | Coordenação supervisor/worker, handoffs entre agentes | `migration-coordinator`, `master-agent` |
| `agent-orchestration-improve-agent` | Análise de desempenho, melhoria de prompts de agente | `iteration-improvement`, `agent-designer` |
| `production-code-audit` | Auditoria de código gerado antes de cada gate | `quality-gate`, `downstream-executor` |
| `agents-md` | Manutenção de AGENTS.md e chatmodes | `agent-designer`, `iteration-improvement` |

---

## 4. Prompts Prontos por Skill

### `framework-migration-legacy-modernize` (Gate 1)

```text
[Selecione: discovery-scout]
Usando o skill framework-migration-legacy-modernize:
Analise o sistema legado e produza uma estratégia de migração progressiva
para as entidades: [LISTA DE ENTIDADES]
Foco: strangler fig pattern, risk registry, mapeamento de dependências circulares

```

---

### `data-quality-frameworks` (Gates 1, 2, 3)

```text
[Selecione: business-analyst] (Gate 1) / [data-steward] (Gate 2)
Usando o skill data-quality-frameworks:
Defina um conjunto de data contracts e DQ rules para a entidade [ENTIDADE]
com thresholds de completeness >= 99% e uniqueness = 100% para campos chave.
Gere o contrato em formato YAML compatível com data_contract_validator.py

```

---

### `tdd-orchestrator` (Gate 2, 3)

```text
[Selecione: code-generator]
Usando o skill tdd-orchestrator:
Gere testes de integração (red-green-refactor) para o DDL e ETL da entidade [ENTIDADE]
Cobertura mínima: 80%. Inclua casos de borda e dados inválidos.

```

---

### `observability-monitoring-slo-implement` (Gate 2, 3)

```text
[Selecione: data-architect]
Usando o skill observability-monitoring-slo-implement:
Defina SLOs para a wave [WAVE-ID]:

- SLI: latência de carga < 2h

- SLI: error rate < 1%

- SLO: gate_cycle_time <= 48h

Inclua alertas de SLO breach e action items automáticos.

```

---

### `production-code-audit` (Gate 2, 3)

```text
[Selecione: quality-gate]
Usando o skill production-code-audit:
Audite o código DDL/ETL gerado para a wave [WAVE-ID]:

- Segurança: sem credenciais hardcoded, sem SQL injection

- Performance: índices corretos, particionamento adequado

- Manutenibilidade: comentários, nomes semânticos, estrutura limpa

Produza um quality-gate-evidence.md com score por dimensão.

```

---

### `agentic-eval` (Cross-cutting)

```text
[Selecione: self-healing]
*reflect
Avalie a solução produzida nesta sessão usando o CRITIQUE_RUBRIC:

- Correctness (0.4): a solução resolve o problema corretamente?

- Safety (0.3): existe risco de perda de dados ou side effects?

- Idiomatic (0.2): segue padrões e convenções do projeto?

- Learnability (0.1): o resultado é auditável e documentável?

Threshold para aceite: >= 0.8

```

---

### `agent-governance` (Cross-cutting)

```text
[Selecione: migration-coordinator]
Usando o skill agent-governance:
Valide a política de tool use para a wave [WAVE-ID]:

- Agents executando ações de alto risco devem solicitar review

- Nenhum agent deve usar terminalLastCommand sem aprovação

- Registre decisão de gate em gate{N}-decision.md com score, aprovadores e data

```

---

## 5. Como Carregar uma Skill

Skills são carregadas automaticamente quando o agente ou o usuário as referencia no prompt. Para carga manual:

### Via prompt direto

```text
[Selecione: <agente>]
Usando o skill <nome-do-skill>:
[sua instrução aqui]

```

### Via referência explícita ao arquivo

```text
[Selecione: <agente>]
Leia e aplique o skill em .github/skills/<nome>/SKILL.md para:
[sua instrução aqui]

```

### Via Copilot Chat file attach

No VS Code Copilot Chat, você pode anexar o arquivo SKILL.md diretamente ao chat usando `#file:.github/skills/<nome>/SKILL.md` antes do seu prompt.

---

## Referência Cruzada

| Documento | Conteúdo |
| --- | --- |

| [COPILOT-AGENTS-GUIDE.md](COPILOT-AGENTS-GUIDE.md) | Comandos completos por agente |
| [OPERATING-MODEL-CANVAS-v2.md](OPERATING-MODEL-CANVAS-v2.md) | Permissões e política operacional |
| [PLAYBOOK-MIGRATION-OPERATIONS.md](PLAYBOOK-MIGRATION-OPERATIONS.md) | Fluxo passo a passo de execução de wave |
| [scripts/README.md](../scripts/README.md) | Scripts de validação alinhados às skills de DQ e governança |
