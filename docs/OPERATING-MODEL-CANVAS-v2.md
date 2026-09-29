# Operating Model Canvas v2 — Solução Agêntica de Migração de Dados

> **Data:** 2026-03-21
> **Escopo:** Arquitetura, governança e processo operacional da migration factory
> **Status:** Implementado — WAVE-001 dry run validado

---

## Tabela de Conteúdo

- [1. Portfolio de Agentes](#1-portfolio-de-agentes)
- [2. Padronização Estrutural](#2-padronização-estrutural)
- [3. Governança — Policy-as-Code](#3-governança--policy-as-code)
- [4. GateScore e Qualidade](#4-gatescore-e-qualidade)
- [5. Scripts de Governança (23 módulos)](#5-scripts-de-governança-23-módulos)
- [6. Pipeline de CI/CD (7 jobs)](#6-pipeline-de-cicd-7-jobs)
- [7. Roadmap de 30 Dias](#7-roadmap-de-30-dias)
- [8. Decisão Executiva](#8-decisão-executiva)

---

## 1. Portfolio de Agentes

### Core (19 ativos)

| Agente | Persona | Fase | Papel |
| --- | --- | --- | --- |
| `master-agent` | — | ALL | Entrada, roteamento, base de conhecimento |
| `migration-coordinator` | Orion | CORE | Orquestração de waves, validação de gates |
| `discovery-scout` | Scout | UPSTREAM | Descoberta e catalogação do ambiente legado |
| `inventory-scout` | Scout | UPSTREAM | Inventário de repositório (fallback de discovery) |
| `data-strategist` | DataStrategist | UPSTREAM | Problem statement, KPIs, critérios de sucesso |
| `business-analyst` | Mary | UPSTREAM | STTM, regras de DQ, mapeamento fonte-destino |
| `logic-extractor` | Logan | UPSTREAM | Extração de lógica de negócio de código legado |
| `data-architect` | Winston | MIDSTREAM | Arquitetura, decisões técnicas, Gate 2 |
| `data-modeler` | Sofia | MIDSTREAM | Modelo lógico, contratos de dados, métricas |
| `data-steward` | Gaia | MIDSTREAM | Governança, catálogo, políticas de acesso |
| `code-generator` | Coda | MIDSTREAM | Geração de DDL/ETL a partir do modelo |
| `quality-gate` | Vera | MIDSTREAM | Validação de código, scoring de qualidade |
| `security-compliance` | Shield | MIDSTREAM | Detecção de PII, masking, compliance |
| `downstream-executor` | Diego | DOWNSTREAM | Execução da wave, pacote Gate 3 |
| `reconciliation` | Balance | DOWNSTREAM | Row count, checksums, schema diffs |
| `self-healing` | Phoenix | DOWNSTREAM | Diagnóstico de erros, auto-fix, self-critique |
| `documentation` | Scribe | DOWNSTREAM | Runbooks, wave report, changelog |
| `bi-semantic` | Bianca | DOWNSTREAM | Semantic layer, dashboards (opcional) |
| `iteration-improvement` | Kai | PÓS-WAVE | Retrospectiva, melhoria contínua |

> **Deprecado:** `orchestrator` está **inativo**. Use `migration-coordinator` (Orion).

### Opcional (sob demanda)

- `bi-semantic` — somente quando há entrega de camada semântica/BI no escopo
- `code-generator` — somente para aceleração de boilerplate repetitivo
- `agent-designer` — somente para expansões multi-agente complexas
- `inventory-scout` — fallback de discovery com critério documentado

### Regra de discovery ownership

1. Cada wave tem **exatamente 1** discovery owner primário definido em `wave-config.yaml`
2. `inventory-scout` só entra por exceção com critério documentado
3. `discovery-scout` é o padrão para projetos de migração enterprise

---

## 2. Padronização Estrutural

### Estrutura de definição dos agentes e execução das waves

```text
<agente>-agent/
├── .avanade-core/
│   ├── core-config.yaml
│   ├── agents/<agent>.md
│   ├── tasks/
│   ├── checklists/
│   └── templates/
└── README.md

projects/<project_name>/
├── wave-config.yaml
├── context/
│   ├── project-config.yaml
│   └── agent-task-config.yaml
└── outputs/
    ├── upstream/
    ├── midstream/
    ├── downstream/
    └── summary/
```

### Contratos de handoff por gate

| De → Para | Artefatos obrigatórios |
| --- | --- |
| Gate 1 → Gate 2 | `inventory-report.md`, `sttm.md`, `dq-initial.md`, `gate1-problem-statement.md`, `gate1-kpis.md` |
| Gate 2 → Gate 3 | `architecture.md`, `data-model.md`, `decisions.md`, `dq-rules.md`, `monitoring-spec.md` |
| Gate 3 → Produção | `ddl/`, `etl/`, `tests/`, `documentation/`, `wave-report.md`, `execution-runbook.md`, `reconciliation-evidence.md`, `migration-metrics-{wave_id}.pbip` |

### Convenções de nomes

- Agentes: `<nome>-agent/`
- Ativação: `.github/agents/<nome>.chatmode.md`
- Contexto: `projects/<project_name>/context/`
- Saídas: `projects/<project_name>/outputs/{upstream|midstream|downstream|summary}/`
- Decisões de gate: `gate{N}-decision.md` (score + aprovadores + data)

### Ownership de artefatos

| Artefato | Owner |
| --- | --- |
| `architecture.md`, `decisions.md`, `monitoring-spec.md` | Winston (`data-architect`) |
| `data-model.md`, `data-contracts.md`, `metrics-catalog.md` | Sofia (`data-modeler`) |
| `wave-report.md`, `execution-runbook.md` | Diego (`downstream-executor`) + Scribe (`documentation`) |
| `reconciliation-evidence.md` | Balance (`reconciliation`) |
| `quality-gate-evidence.md` | Vera (`quality-gate`) |

---

## 3. Governança — Policy-as-Code

### Matriz de permissão por classe de agente

| Classe | Agentes | Tools permitidas | Restrições |
| --- | --- | --- | --- |
| **Coordenação** | `master-agent`, `migration-coordinator` | Roteamento, leitura, auditoria | Sem escrita destrutiva |
| **Design** | `data-architect`, `data-modeler`, `data-steward`, `business-analyst` | Leitura ampla, escrita de artefato | Sem execução em produção |
| **Execução** | `downstream-executor` | Escrita operacional, comandos controlados | Review obrigatório para PROD |
| **Controle** | `quality-gate`, `reconciliation`, `security-compliance` | Leitura ampla, validação, relatório | Autoridade de aprovação de gate |

### Níveis de policy

- **allow**: uso livre
- **review**: exige aprovação humana antes de executar
- **deny**: bloqueado — o agente não pode usar este tool

### FACTORY_BASELINE_POLICY (implementada em `scripts/governance_policy.py`)

```python
FACTORY_BASELINE_POLICY = GovernancePolicy(
    name="factory-baseline",
    blocked_tools=["terminalLastCommand"],
    max_tools_per_agent=15,
)
```

Validada em CI via `python -m scripts.validate_agent_contracts --root .`.

### Tipos de controle obrigatórios

1. **Audit trail**: todo gate pass/fail registrado em `audit_logger.py`
2. **Review workflow**: ações de alto risco bloqueam até aprovação explícita (`review_workflow.py`)
3. **Decision log**: exceções de governança registradas (`decision_log.py`)
4. **Data contracts**: entidades críticas têm contratos declarativos YAML validados por `data_contract_validator.py`

---

## 4. GateScore e Qualidade

### Fórmula do GateScore

$$GateScore = 0.35 \times Completude + 0.25 \times Qualidade + 0.20 \times RiscoResidual + 0.20 \times Reconciliação$$

### Política de decisão

| Score | Decisão | Ação |
| --- | --- | --- |
| ≥ 0.85 | **Aprovado** | Avançar para próxima fase |
| 0.70 – 0.84 | **Aprovado com ressalvas** | Avançar registrando open items obrigatórios |
| < 0.70 | **Bloqueado** | Corrigir artefatos, recalcular score |

### Thresholds de qualidade por tier de entidade

| Tier | Min Completeness | Max Null Rate | Min Uniqueness |
| --- | --- | --- | --- |
| CRITICAL | 99% | 0.1% | 100% |
| STANDARD | 95% | 1% | 99% |
| REFERENCE | 90% | 5% | 95% |

### Self-critique de agentes (`self-healing` → `*reflect`)

| Dimensão | Peso | Critério |
| --- | --- | --- |
| Correctness | 0.4 | Solução resolve o problema corretamente? |
| Safety | 0.3 | Risco de perda de dados ou side effects? |
| Idiomatic | 0.2 | Segue padrões do projeto? |
| Learnability | 0.1 | Resultado auditável e documentável? |

Thresholds: `≥ 0.8` ACCEPT | `0.6–0.79` REFINE (máx 2 loops) | `< 0.6` ESCALATE

---

## 5. Scripts de Governança (23 módulos)

| Categoria | Módulos-chave |
| --- | --- |
| Validação de gates | `validate_gate1_artifacts`, `validate_gate2_artifacts`, `validate_gate3_artifacts` |
| Configuração | `validate_wave_config` |
| Score e KPIs | `gate_score_report`, `kpi_dashboard_report`, `kpi_dictionary` |
| Reconciliação | `reconciliation_checks`, `reconciliation_tolerance`, `mismatch_taxonomy` |
| Qualidade | `quality_thresholds`, `performance_benchmark` |
| Auditoria | `audit_logger`, `review_workflow`, `decision_log` |
| Observabilidade | `slo_workflow` |
| Rastreabilidade | `prd_traceability`, `generate_github_issues`, `wave_status_tracker` |
| Alinhamento | `check_chatmode_alignment` |
| Governança de agentes | `validate_agent_contracts`, `governance_policy` |
| Contratos de dados | `data_contract_validator` |

**271 testes automatizados — todos GREEN.**

Ver [src/shared/scripts/README.md](../src/shared/scripts/README.md) para documentação completa.

---

## 6. Pipeline de CI/CD (7 jobs)

| Job | O que valida |
| --- | --- |
| 1 — Unit Tests | `python -m pytest src/shared/tests/ -v` — 271 testes |
| 2 — Lint (Ruff) | `ruff check scripts/ tests/` — quality de código |
| 3 — Security (Bandit) | `bandit -r scripts/ -ll` — vulnerabilidades |
| 4 — Agent Contracts | `python -m scripts.validate_agent_contracts --root .` — 21 chatmodes |
| 5 — Chatmode Alignment | `python -m scripts.check_chatmode_alignment --root .` — orphan check |
| 6 — Gate 3 Validation | `python -m scripts.validate_gate3_artifacts` — artefatos DOWNSTREAM |
| 7 — Policy Schema | Presença dos arquivos `.avanade-core/policies/` |

Pipeline definido em `.github/workflows/ci-governance.yml`.

---

## 7. Roadmap de 30 Dias

> **Status (2026-03-21):** todas as semanas 1–4 foram executadas e entregues.

### Semana 1 — Estabilizar ✅

1. Formalizar `discovery-scout` como primário e `inventory-scout` como fallback
2. Publicar matriz allow/review/deny por classe de agente
3. Definir fórmula e threshold do GateScore

### Semana 2 — Padronizar ✅

1. Padronizar checklists e templates mínimos em todos os agentes core
2. Criar runbook de handoff por gate
3. Validar naming e output folders

### Semana 3 — Governar ✅

1. Restringir tools de alto risco por classe de agente
2. Adicionar checks de gate obrigatórios antes de routing
3. Implementar audit trail para decisões críticas

### Semana 4 — Otimizar ✅

1. Adicionar `validate_agent_contracts.py` e `governance_policy.py`
2. Criar `data_contract_validator.py` para DQ declarativa
3. Adicionar self-critique (`*reflect`) ao `self-healing`
4. Expandir CI com Lint (Ruff), Security (Bandit), Agent Contracts
5. Atualizar AGENTS.md e todos os docs

---

## 8. Decisão Executiva

| Decisão | Status | Racional |
| --- | --- | --- |
| Adicionar novos agentes | Não necessário agora | Cobertura funcional completa com 19 agentes |
| Excluir agentes | Não imediato | Operar core vs opcional e medir utilização antes |
| Padronizar contratos | ✅ Implementado | govern_policy.py + data_contract_validator.py |
| Score de gate | ✅ Implementado | gate_score_report.py (fórmula 4 dimensões) |
| Ownership de discovery | ✅ Implementado | validate_wave_config.py exige discovery_owner_primary |
| Policy-as-code | ✅ Implementado | FACTORY_BASELINE_POLICY em governance_policy.py |
| Self-critique de agentes | ✅ Implementado | `*reflect` no self-healing com Evaluator-Optimizer |
| CI com lint e segurança | ✅ Implementado | Jobs 2 (Ruff) e 3 (Bandit) no ci-governance.yml |
