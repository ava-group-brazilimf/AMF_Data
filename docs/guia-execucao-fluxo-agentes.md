# Guia de Execução — Fábrica de Migração de Dados

## Fluxo de Agentes

### Fase 1 — Upstream (Descoberta)

1. **discovery-scout** — Inventário automatizado de pipelines legados
2. **inventory-scout** — Catalogação de artefatos e dependências
3. **business-analyst** — Levantamento de regras de negócio
4. **data-strategist** — Estratégia de migração e priorização
5. **logic-extractor** — Extração de lógica de negócio e pseudocódigo

> **Gate 1:** Validar inventário completo, grafo de dependências e pseudocódigo antes de avançar.

### Fase 2 — Midstream (Design e Qualidade)

1. **data-architect** — Arquitetura de dados e decisões técnicas
2. **data-modeler** — Modelagem de dados e contratos
3. **data-steward** — Governança de dados e linhagem
4. **code-generator** — Geração de código PySpark/SQL
5. **agent-designer** — Design de agentes auxiliares
6. **quality-gate** — Validação sintática e semântica
7. **security-compliance** — Verificação LGPD/GDPR/SOX

> **Gate 2:** Validar código gerado, testes unitários e compliance antes de avançar.

### Fase 3 — Downstream (Execução)

1. **downstream-executor** — Execução do plano de migração
2. **self-healing** — Diagnóstico e correção automática de erros
3. **reconciliation** — Reconciliação de dados (row count, checksum, schema)
4. **documentation** — Geração de relatórios, runbooks e diagramas de linhagem
5. **bi-semantic** — Validação de modelos semânticos BI

> **Gate 3:** Validar 99.9% paridade de dados, performance e rollback testado antes de produção.

## Coordenação

- **migration-coordinator** (Orion) — Orquestra waves e valida gates
- **master-agent** — Ponto de entrada e roteamento de tarefas

## Comandos Rápidos

| Ação | Comando |
|---|---|
| Iniciar wave | `@migration-coordinator *start-wave` + `wave_config_path: projects/<project_name>/wave-config.yaml` |
| Validar Gate 1 | `@migration-coordinator *gate-1` |
| Validar Gate 2 | `@migration-coordinator *gate-2` |
| Validar Gate 3 | `@migration-coordinator *gate-3` |
| Roteamento | `@master-agent *route` |
