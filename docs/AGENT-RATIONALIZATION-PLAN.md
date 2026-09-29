# Agent Rationalization Plan — Data Migration Factory

> **Data:** 2026-03-21
> **Escopo:** Modelo operacional multi-agente para a migration factory com Downstream Executor ativo
> **Publico:** Platform owner, migration coordinator, architecture and delivery leads

---

## Tabela de Conteudo

- [1. Objetivo](#1-objetivo)
- [2. Estado Atual](#2-estado-atual)
- [3. Target Operating Model](#3-target-operating-model)
- [4. Adicoes e Remocoes](#4-adicoes-e-remocoes)
- [5. Fluxo de Trabalho Padrao](#5-fluxo-de-trabalho-padrao)
- [6. Matriz de Decisao para Escopo de Agente](#6-matriz-de-decisao-para-escopo-de-agente)
- [7. Status de Implementacao](#7-status-de-implementacao)
- [8. Resultados do Piloto e Licoes Aprendidas](#8-resultados-do-piloto-e-licoes-aprendidas)
- [9. Decisao Final sobre Discovery Ownership](#9-decisao-final-sobre-discovery-ownership)

---

## 1. Objetivo

Simplificar o landscape de agentes, eliminar sobreposicao, restaurar cobertura de entrega no DOWNSTREAM, e melhorar governanca para projetos de migracao em producao.

---

## 2. Estado Atual

### O que esta funcionando bem

- Cobertura de dominio forte: discovery, modelagem, governanca, qualidade, reconciliacao, documentacao
- Estrutura consistente na maioria dos agent folders com .avanade-core
- Hierarquia de coordenadores (master-agent -> migration-coordinator) permite fluxos controlados
- 19 agentes ativos + 1 deprecated (orchestrator) + 1 meta-agente (gent-designer)
- 189 testes automatizados verdes | 23 modulos de governanca

### Gaps e riscos (resolvidos)

| Gap | Status | Resolucao |
| --- | --- | --- |
| Sobreposicao discovery-scout vs inventory-scout | Resolvido | discovery-scout = primario, inventory-scout = fallback |
| Score de gate (nao apenas checklist) | Resolvido | gate_score_report.py com formula 4 dimensoes |
| Padrao unico para auditoria de decisoes | Resolvido | udit_logger.py, 
eview_workflow.py, decision_log.py |
| DQ procedural sem contratos declarativos | Resolvido | data_contract_validator.py com YAML contracts |
| Governanca sem enforcement programatico | Resolvido | governance_policy.py + FACTORY_BASELINE_POLICY |
| Agentes sem validacao de contrato estrutural | Resolvido | alidate_agent_contracts.py -- 21/21 passando |

---

## 3. Target Operating Model

### Core (use em todas as waves)

| Agente | Papel |
| --- | --- |
| master-agent, migration-coordinator | Estrategia, roteamento, orquestracao, validacao de gates |
| discovery-scout | Discovery e reverse engineering do legado |
| logic-extractor, usiness-analyst, data-strategist | Analise e definicao de requisitos |
| data-architect, data-modeler, data-steward | Design e governanca |
| quality-gate, 
econciliation, security-compliance | Controles e assurance |
| documentation, iteration-improvement, self-healing | Enablement e sustentabilidade |

### Opcional (sob demanda)

| Agente | Quando usar |
| --- | --- |
| gent-designer | Apenas para expansoes multi-agente complexas |
| i-semantic | Apenas quando BI semantic layer esta no escopo |
| code-generator | Para aceleracao de tarefas de geracao repetitiva |
| inventory-scout | Fallback de discovery por excecao documentada |

### Regra de discovery ownership

1. Cada wave tem **exatamente 1** discovery owner primario definido em wave-config.yaml
2. inventory-scout so entra por excecao com criterio documentado
3. discovery-scout e o padrao para projetos de migracao enterprise

---

## 4. Adicoes e Remocoes

### Adicoes implementadas

1. **downstream-executor-agent** com criacao de pacotes DDL/ETL, workflow de execucao, runbook, artefatos Gate 3
2. **alidate_agent_contracts.py** -- validacao estrutural de contracts dos chatmodes
3. **governance_policy.py** -- motor de politica policy-as-code
4. **data_contract_validator.py** -- validacao declarativa de contratos de dados YAML
5. **self-healing *reflect** -- self-critique Evaluator-Optimizer (comando #7)
6. **CI expandido** -- jobs: Lint (Ruff), Security (Bandit), Agent Contracts

### Limpeza obrigatoria (implementada)

1. Chatmode data-engineer-exec stale removido
2. Chatmode inventory-scout adicionado e alinhado com inventory-scout-agent
3. orchestrator.chatmode.md depreciado -- use migration-coordinator

---

## 5. Fluxo de Trabalho Padrao

`	ext
1.  master-agent           -- intake e routing
2.  discovery-scout        -- (ou inventory-scout, um unico primario)
3.  logic-extractor        -- extracao de logica legada
4.  business-analyst       -- STTM e regras de DQ
5.  data-strategist        -- problem statement e KPIs
6.  data-architect         -- arquitetura e decisoes
7.  data-modeler           -- modelo logico e contratos
8.  data-steward           -- governanca e catalogo
9.  code-generator         -- geracao de DDL/ETL
10. quality-gate           -- validacao e scoring
11. security-compliance    -- PII e compliance
12. downstream-executor    -- execucao da wave
13. reconciliation         -- evidencia de paridade
14. self-healing           -- diagnostico e fix (se necessario)
15. documentation          -- wave report e runbook
16. iteration-improvement  -- retrospectiva e melhoria
`

---

## 6. Matriz de Decisao para Escopo de Agente

### Adicionar um agente quando TODOS sao verdadeiros

- O novo dominio exige tools ou output contracts unicos
- O agente existente nao consegue absorver o escopo sem conflito major
- O papel aparece em pelo menos 2 migration waves

### Remover ou merger um agente quando QUALQUER e verdadeiro

- Output sobrepo mais de 70% com um agente existente
- Ativacao e rara e pode ser tratada como comando opcional de outro agente
- Nao ha owner claro de manutencao

---

## 7. Status de Implementacao (2026-03-21)

| Item | Status |
| --- | --- |
| downstream-executor-agent criado com .avanade-core | Completo |
| Chatmode downstream-executor adicionado | Completo |
| Chatmode inventory-scout adicionado e alinhado | Completo |
| Alinhamento chatmode-folder validado (21/21) | Completo |
| alidate_agent_contracts.py -- 21/21 passando | Completo |
| governance_policy.py com FACTORY_BASELINE_POLICY | Completo |
| data_contract_validator.py com YAML contracts | Completo |
| CI expandido: Ruff, Bandit, Agent Contracts | Completo |
| Self-critique *reflect no self-healing | Completo |
| 189 testes automatizados verdes | Completo |

---

## 8. Resultados do Piloto e Licoes Aprendidas

**Wave piloto:** WAVE-001 (dry run)

**Resultados:**

- Fluxo tecnico de artefatos Gate 3 validado end-to-end com outputs do downstream-executor
- Criterios Gate 3 do coordinator alinhados a wave-report e documentos de evidencia
- Routing do master-agent agora inclui downstream-executor como delivery path explicito

**Licoes aprendidas:**

1. Manter discovery ownership singular por wave (modelo primary + fallback)
2. Tratar evidencias de quality e reconciliacao como artefatos Gate 3 de primeira classe
3. Exigir publicacao do runbook antes de qualquer execucao non-dry
4. Adicionar benchmarking de performance antecipado para volumes production-like

---

## 9. Decisao Final sobre Discovery Ownership

- **Agente primario de discovery:** discovery-scout
- **Agente fallback de discovery:** inventory-scout (ativacao por excecao)

**Regra de decisao:**

1. Cada migration wave tem exatamente 1 discovery owner (discovery_owner_primary em wave-config.yaml)
2. inventory-scout e ativado somente quando explicitamente requerido pela complexidade do escopo
3. A excecao deve ser documentada no campo discovery_owner_fallback com justificativa
