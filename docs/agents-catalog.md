# Agents Catalog — Data Migration Factory v3

> Catálogo completo dos 19 agentes especializados da fábrica de migração de dados.
> Para ativar um agente, use o chatmode correspondente em `.github/agents/` ou execute `*route` no `master-agent`.

---

## Módulo: upstream-discovery (UPSTREAM — Gate 1)

| Agente | Persona | Responsabilidade | Skill | Chatmode |
|--------|---------|-----------------|-------|----------|
| **discovery-scout** | Scout | Descoberta, inventário e classificação de objetos legados | dmf-discovery-scout | `.github/agents/discovery-scout.chatmode.md` |
| **inventory-scout** | Scout | Mapeamento de repositório, dependências e detecção de tech stack | dmf-inventory-scout | `.github/agents/inventory-scout.chatmode.md` |
| **data-strategist** | — | Definição de problem statement, KPIs e critérios de sucesso | dmf-data-strategist | `.github/agents/data-strategist.chatmode.md` |
| **business-analyst** | — | Mapeamento de requisitos, STTM e DQ rules iniciais | dmf-business-analyst | `.github/agents/business-analyst.chatmode.md` |
| **logic-extractor** | Logan | Extração de lógica de negócio e geração de pseudocódigo semântico | dmf-logic-extractor | `.github/agents/logic-extractor.chatmode.md` |

---

## Módulo: midstream-design (MIDSTREAM — Gate 2)

| Agente | Persona | Responsabilidade | Skill | Chatmode |
|--------|---------|-----------------|-------|----------|
| **data-architect** | Winston | Arquitetura de dados target, ADRs, diagrama de componentes | dmf-data-architect | `.github/agents/data-architect.chatmode.md` |
| **data-modeler** | Sofia | Modelo lógico, granularidade, contratos e métricas | dmf-data-modeler | `.github/agents/data-modeler.chatmode.md` |
| **data-steward** | Gaia | Governança de dados, classificação, lineage e compliance | dmf-data-steward | `.github/agents/data-steward.chatmode.md` |
| **agent-designer** | — | Design de novos agentes e blueprints de orquestração | dmf-agent-designer | `.github/agents/agent-designer.chatmode.md` |
| **code-generator** | Coda | Geração de código DDL/ETL multiplataforma a partir de pseudocódigo | dmf-code-generator | `.github/agents/code-generator.chatmode.md` |

---

## Módulo: midstream-quality (MIDSTREAM — Gate 2)

| Agente | Persona | Responsabilidade | Skill | Chatmode |
|--------|---------|-----------------|-------|----------|
| **quality-gate** | Vera | Validação de código, equivalência semântica e scoring de qualidade | dmf-quality-gate | `.github/agents/quality-gate.chatmode.md` |
| **security-compliance** | Shield | Detecção de PII, mascaramento e conformidade regulatória | dmf-security-compliance | `.github/agents/security-compliance.chatmode.md` |

---

## Módulo: downstream-execution (DOWNSTREAM — Gate 3)

| Agente | Persona | Responsabilidade | Skill | Chatmode |
|--------|---------|-----------------|-------|----------|
| **downstream-executor** | Diego | Execução de DDL/ETL, runbook e wave execution | dmf-downstream-executor | `.github/agents/downstream-executor.chatmode.md` |
| **reconciliation** | Balance | Validação de paridade de dados (row counts, checksums, schema diff) | dmf-reconciliation | `.github/agents/reconciliation.chatmode.md` |
| **self-healing** | Phoenix | Diagnóstico automático de erros, correção e aprendizado de padrões | dmf-self-healing | `.github/agents/self-healing.chatmode.md` |
| **documentation** | Scribe | Geração de relatórios, lineage, runbooks e changelogs | dmf-documentation | `.github/agents/documentation.chatmode.md` |
| **bi-semantic** | Bianca | Desenvolvimento de dashboards, modelos semânticos e métricas DAX | dmf-bi-semantic | `.github/agents/bi-semantic.chatmode.md` |

---

## Módulo: core-coordination (CORE — Cross-phase)

| Agente | Persona | Responsabilidade | Skill | Chatmode |
|--------|---------|-----------------|-------|----------|
| **master-agent** | — | Triage, roteamento e base de conhecimento do método | — | `.github/agents/master-agent.chatmode.md` |
| **migration-coordinator** | Orion | Orquestração de waves, validação de gates e gestão de rollbacks | dmf-migration-coordinator | `.github/agents/migration-coordinator.chatmode.md` |
| **iteration-improvement** | — | Análise de métricas, retrospectivas e backlog de melhorias | dmf-iteration-improvement | `.github/agents/iteration-improvement.chatmode.md` |

---

## Agentes Legados (Deprecated)

| Agente | Status | Substituto |
|--------|--------|-----------|
| **orchestrator** | ⚠️ DEPRECATED | `migration-coordinator` |

---

## Como Usar

```
# Ponto de entrada recomendado — sempre começar aqui:
master-agent → *route

# Iniciar uma wave completa:
migration-coordinator → *start-wave
wave_config_path: projects/<project_name>/wave-config.yaml

# Verificar qual agente usar para uma tarefa:
master-agent → *route → <descrição da tarefa>
```

Referência completa de comandos: [docs/COPILOT-AGENTS-GUIDE.md](COPILOT-AGENTS-GUIDE.md)
