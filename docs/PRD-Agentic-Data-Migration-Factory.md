# Product Requirements Document (PRD)

Project: Agentic Data Migration Factory
Version: 1.1
Date: 2026-03-21
Owner: Migration Factory Team
Status: **Active — Sprint 4 Complete | 189 tests GREEN | 23 scripts | 19 agents | 7 CI jobs**

---

## Status de Implementacao (2026-03-21)

| Item | Status |
| --- | --- |
| 4 sprints completos (B-001 a B-019) | Completo |
| 189 testes automatizados verdes | Completo |
| 23 modulos de governanca Python | Completo |
| 19 chatmode agents ativos (plataforma-agnosticos) | Completo |
| 21 chatmodes validados por `validate_agent_contracts.py` | Completo |
| 26 skills instaladas em `.github/skills/` | Completo |
| 7 jobs no CI pipeline (tests, lint, security, contracts, alignment, gate3, policy) | Completo |
| WAVE-001 dry run: fluxo Gate 3 validado end-to-end | Completo |
| `governance_policy.py` + `FACTORY_BASELINE_POLICY` | Completo |
| `data_contract_validator.py` (YAML contracts) | Completo |
| Self-critique `*reflect` no `self-healing` | Completo |

---

## 1. Executive Summary

### Problem Statement

Data platform migration initiatives are high-risk, slow, and inconsistent due to fragmented ownership, weak handoffs, and lack of standardized controls across discovery, design, execution, and validation phases.

### Proposed Solution

Implement and operate a multi-agent migration factory with phase-based orchestration (UPSTREAM, MIDSTREAM, DOWNSTREAM), mandatory quality gates, governance controls, and evidence-driven promotion to production.

### Success Criteria (KPIs)

- Gate first-pass approval rate >= 80% within 90 days.

- Lead time from discovery kickoff to executable wave package reduced by >= 35%.

- Rollback-required waves <= 10% per quarter.

- Reconciliation mismatch incidents in production <= 2% of migrated entities per wave.

- Mean time to recover (MTTR) for wave failures <= 4 hours.

## 2. User Experience and Functionality

### User Personas

- Migration Coordinator: needs visibility, gate control, and deterministic routing.

- Data Architect and Data Modeler: need clear handoff contracts and quality criteria before implementation.

- Downstream Executor: needs executable inputs, controlled runbooks, and rollback safety.

- Quality, Reconciliation, and Security Reviewers: need standardized evidence packages for sign-off.

- Delivery Leadership: needs measurable outcomes, risks, and continuous improvement signals.

### User Stories

- As a Migration Coordinator, I want each wave to have one discovery owner so that duplicated discovery effort is eliminated.

- As a Data Architect, I want Gate 2 artifacts to be mandatory and versioned so that downstream execution is deterministic.

- As a Downstream Executor, I want a standard wave execution package (DDL, ETL, tests, runbook) so that execution can be repeated safely.

- As a Quality Reviewer, I want formal quality evidence templates so that approval decisions are objective.

- As a Reconciliation Reviewer, I want parity and checksum evidence so that data migration integrity is auditable.

- As a Security Reviewer, I want tool access policies by agent role so that high-risk operations are controlled.

- As Delivery Leadership, I want gate and wave KPIs so that investment and risk decisions are data-driven.

### Acceptance Criteria

- Discovery ownership:
  - Each wave records primary discovery owner and optional fallback owner.
  - No wave can start Gate 2 without discovery owner assigned.

- Gate 2 integrity:
  - Gate 2 cannot pass without architecture.md, data-model.md, decisions.md, dq-rules.md, monitoring-spec.md.
  - Missing artifacts are reported with blocker severity.

- Gate 3 execution package:
  - Each wave has required outputs: ddl/, etl/, tests/, documentation/, wave-report.md.
  - execution-runbook.md is mandatory before non-dry run.

- Quality evidence:
  - quality-gate-evidence.md exists and follows standard template.
  - Quality pass/fail status is explicit with open items.

- Reconciliation evidence:
  - reconciliation-evidence.md exists and includes row-count and aggregate parity.
  - High-risk entities include checksum validation.

- Governance controls:
  - Governance policy defines allow/review/deny for each agent class.
  - Review-required actions block execution until explicit approval.

- Operational visibility:
  - Dashboard/report captures GateScore, first-pass rate, rollback rate, MTTR, and cycle time.

### Non-Goals

- Rebuilding all existing agents from scratch.

- Migrating immediately to a different agent runtime framework.

- Full autonomous production execution without human approval.

- Replacing enterprise data governance outside migration scope.

## 3. AI System Requirements

### Tool Requirements

- File and config tooling: read/write files, search, dependency discovery, diff inspection.

- Execution and validation tooling: controlled command execution for packaging and checks.

- Governance tooling: policy loading/checking and audit log capture for critical actions.

### Evaluation Strategy

- Gate-level evaluation:
  - GateScore = 0.35*Completude + 0.25*Qualidade + 0.20*RiscoResidual + 0.20*Reconciliacao.

- Wave-level evaluation:
  - Success/failure state.
  - Rollback triggered or not.
  - MTTR if failed.

- Agent output quality evaluation:
  - Structured checklists per agent deliverable.
  - Reflection loop for critical artifacts (generate -> evaluate -> refine).

- Operational quality benchmarks:
  - Minimum test coverage >= 80% at Gate 3.
  - Required evidence documents present and validated.

## 4. Technical Specifications

### Architecture Overview

The system follows a hierarchical multi-agent model with centralized orchestration and gate-driven control.

Flow:

- Intake and routing by coordinator agents.

- Discovery and scoping (UPSTREAM).

- Architecture and contracts (MIDSTREAM).

- Execution and evidence generation (DOWNSTREAM).

- Gate validation and controlled promotion.

Core process contracts:

- One discovery owner per wave.

- Mandatory artifacts at each gate.

- Human approval required for gate transitions to production.

### Integration Points

- Agent routing and orchestration: master-agent and migration-coordinator (Orion) route based on phase and artifact readiness. *(orchestrator deprecated)*

- Gate validation: criteria maintained in migration-coordinator config and checked per wave.

- Downstream execution: downstream-executor produces wave package and execution evidence.

- Control-plane integration: quality-gate, reconciliation, and security-compliance consume evidence and issue sign-off.

### Security and Privacy

- Policy-as-code is mandatory with allow/review/deny matrix by agent class.

- Human-in-the-loop controls are mandatory for high-risk operations.

- Audit trail logs decisions, approvals, command intents, and gate outcomes.

- No hardcoded secrets in artifacts and sensitive data must be redacted in evidence outputs.

## 5. Governance Policy Requirements

### Agent Classes

- Coordination class:
  - Agents: master-agent, migration-coordinator. *(orchestrator deprecated)*
  - Policy profile: broad read, restricted write, no destructive execution.

- Design class:
  - Agents: data-architect, data-modeler, data-steward, business-analyst.
  - Policy profile: design artifact write, no production execution.

- Execution class:
  - Agent: downstream-executor.
  - Policy profile: controlled execution with review-required for production-impacting actions.

- Control class:
  - Agents: quality-gate, reconciliation, security-compliance.
  - Policy profile: read and validate, approval authority, limited write for evidence reports.

### Minimum Policy Controls

- Pre-tool intent check before any high-risk tool call.

- Tool policy enforcement: deny blocked tools and require approval for review tools.

- Rate and scope limits: max tool calls per request and scope boundaries per wave.

- Decision logging: mandatory audit record for gate pass/fail and overrides.

## 6. Risks and Roadmap

### Technical Risks

- Discovery overlap causing duplicated outputs and routing ambiguity.

- Incomplete evidence causing delayed gate approvals.

- Performance bottlenecks under full monthly production volumes.

- Governance bypass risk without strict policy enforcement hooks.

### Mitigations

- Set discovery-scout as primary and inventory-scout as fallback by exception.

- Make quality and reconciliation evidence mandatory Gate 3 artifacts.

- Add production-like performance benchmark stage before promotion.

- Enforce review-required controls for high-risk actions.

### Phased Rollout

- MVP (now to +30 days):
  - Stabilize core agent model and gate contracts.
  - Run controlled non-dry wave pilot.
  - Baseline KPIs and GateScore.

- v1.1 (+31 to +60 days):
  - Implement policy-as-code files and approval workflows.
  - Add score-based gate dashboards.
  - Standardize runbooks/checklists across all core agents.

- v2.0 (+61 to +120 days):
  - Automate governance checks with policy enforcement hooks.
  - Implement richer agentic evaluation loops for critical artifacts.
  - Optimize wave throughput with measured parallelization patterns.

## 7. Epic Decomposition Blueprint

- Epic 1: Governance and Control Plane.
  - Outcome: enforceable policy-as-code and auditable approvals.
  - Candidate stories:
    - Build allow/review/deny matrix by agent class.
    - Add approval workflow for review-required actions.
    - Persist audit events for gate decisions.

- Epic 2: Gate and Artifact Standardization.
  - Outcome: deterministic handoffs and reduced rework.
  - Candidate stories:
    - Standardize artifact templates for all gates.
    - Add GateScore calculator and gate report schema.
    - Validate required artifacts pre-transition.

- Epic 3: Downstream Execution Reliability.
  - Outcome: safer wave execution with predictable rollback.
  - Candidate stories:
    - Harden runbook and rollback playbooks.
    - Expand reconciliation checks with checksums.
    - Add performance and scalability tests for production-like loads.

- Epic 4: Quality and Reconciliation Excellence.
  - Outcome: objective sign-off quality with lower incident rates.
  - Candidate stories:
    - Add threshold-based data quality checks.
    - Add entity-level reconciliation tolerance bands.
    - Track and report mismatch root causes.

- Epic 5: Observability and Continuous Improvement.
  - Outcome: measurable operational improvement cycle.
  - Candidate stories:
    - Implement wave KPI dashboard and SLO views.
    - Track first-pass rate, rollback rate, and MTTR trends.
    - Automate lessons-learned feedback into templates.

## 8. Open Decisions (TBD)

| Decisao | Status |
| --- | --- |
| Local de implementacao do governance engine (centralizado vs por-agente) | Resolvido: centralizado em `scripts/governance_policy.py` |
| Tooling para KPI dashboard | Resolvido: `kpi_dashboard_report.py` + `slo_workflow.py` |
| RACI de aprovacao para review-required actions | Em definicao por projeto |
| Cadencia de release por migration wave | Em definicao por projeto |
| Orquestracao programatica (LangGraph, CrewAI) | Nao planejado para MVP -- human-in-the-loop intencional |

---

## 9. Referencias

| Documento | Conteudo |
| --- | --- |
| [README.md](../README.md) | Visao geral, setup, arquitetura |
| [AGENTS.md](../AGENTS.md) | Referencia canonica de agentes (comandos, convencoes) |
| [COPILOT-AGENTS-GUIDE.md](COPILOT-AGENTS-GUIDE.md) | Guia completo de uso dos agentes |
| [PLAYBOOK-ONBOARDING.md](PLAYBOOK-ONBOARDING.md) | Setup para novos membros |
| [PLAYBOOK-MIGRATION-OPERATIONS.md](PLAYBOOK-MIGRATION-OPERATIONS.md) | Execucao passo a passo de waves |
| [OPERATING-MODEL-CANVAS-v2.md](OPERATING-MODEL-CANVAS-v2.md) | Modelo operacional, permissoes, roadmap |
| [SKILLS-BLUEPRINT-BY-GATE.md](SKILLS-BLUEPRINT-BY-GATE.md) | Skills por gate com prompts prontos |
| [AGENT-RATIONALIZATION-PLAN.md](AGENT-RATIONALIZATION-PLAN.md) | Decisoes de ownership e racionalizacao |
| [scripts/README.md](../scripts/README.md) | Documentacao dos 23 modulos de governanca |
| [wave-config-sample.yaml](../wave-config-sample.yaml) | Template de configuracao de wave |
