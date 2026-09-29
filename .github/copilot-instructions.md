# Data Migration Factory v3 — Copilot Instructions

## What This Project Is

A **multi-agent migration factory** for data platform migrations. The full lifecycle (UPSTREAM → MIDSTREAM → DOWNSTREAM) is orchestrated by specialized AI agents, validated by three mandatory quality gates with measurable scores.

```
UPSTREAM (Gate 1)  →  MIDSTREAM (Gate 2)  →  DOWNSTREAM (Gate 3)
Discovery               Architecture             Execution
STTM + DQ Rules         Data Model + Code        Reconciliation
```

GateScore formula: `0.35 × Completude + 0.25 × Qualidade + 0.20 × RiscoResidual + 0.20 × Reconciliação`  
Threshold: >= 0.85 approved | 0.70–0.84 approved with open items | < 0.70 blocked.

## Architecture

- **21 agents** in `src/modules/dmf-fabric-agents/` — organized by module (upstream-discovery, midstream-design, midstream-quality, downstream-execution, core-coordination). Note: `orchestrator` is deprecated — use `migration-coordinator` instead.
- **26 skills** in `.github/skills/` — prefixed `ava-dmf-*`, domain knowledge loaded on demand
- **23 governance scripts** in `src/shared/scripts/` — Python modules with 271 automated tests
- **Docs** in `docs/` — playbooks, operating model, agent guide, skills blueprint

See [README.md](../README.md) for project overview.

## Agent Entry Point

When unsure which agent to use, always start with `master-agent` and run `*route`. It will recommend the correct agent for the current context.

Agent map: [docs/COPILOT-AGENTS-GUIDE.md](docs/COPILOT-AGENTS-GUIDE.md)

## Build and Test

```powershell
# Setup (once per machine)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pytest pyyaml
pip install "headroom-ai[mcp,code]==0.27.0"   # optional — token cost reduction (no [proxy] on Python 3.13+)

# Run all governance tests
python -m pytest src/shared/tests/ -q
# Expected: 283 passed
```

Always activate `.venv` before running any Python script. If `pyyaml` is missing, 8 tests fail — install it.

## Token Optimization (Headroom)

The optional `headroom-ai` package provides context compression that reduces LLM token usage by 30–60% on large artifacts. Integration points:

- **MCP Server:** configured in `.vscode/settings.json` — exposes `compress`, `retrieve`, `perf` tools to all agents
- **Scripts:** `gate_score_report.py`, `kpi_dashboard_report.py`, `reconciliation_checks.py` have `_compressed()` variants
- **Tasks:** `scan-repo` (Step 2.1a) and `generate-inventory` (Step 4a) auto-compress large content
- **Learn config:** `.headroom/learn-config.yaml` maps agent failures to instruction files
- **Graceful fallback:** all integrations work without Headroom installed — compression is opportunistic

## Scripts Reference

Do not edit scripts without running tests after. All 23 modules in `src/shared/scripts/` are covered by tests in `src/shared/tests/`. See [src/shared/scripts/README.md](../src/shared/scripts/README.md) for module descriptions.

Key scripts:
- `src/shared/scripts/validate_wave_config.py` — validates wave YAML config
- `src/shared/scripts/validate_gate1_artifacts.py` — validates Gate 1 artifact package
- `src/shared/scripts/validate_gate2_artifacts.py` — validates Gate 2 artifact package
- `src/shared/scripts/validate_gate3_artifacts.py` — validates Gate 3 artifact package (also contains generic `validate_gate_requirements()`)
- `src/shared/scripts/gate_score_report.py` — calculates GateScore
- `src/shared/scripts/wave_status_tracker.py` — consolidated wave status across gates
- `src/shared/scripts/kpi_dashboard_report.py` — wave KPI dashboard report
- `src/shared/scripts/quality_thresholds.py` — entity-tier quality thresholds
- `src/shared/scripts/validate_agent_contracts.py` — structural contract validator for chatmode agents
- `src/shared/scripts/governance_policy.py` — programmatic governance policy engine
- `src/shared/scripts/data_contract_validator.py` — declarative data contract validation

## Conventions

- **Wave config:** every migration wave requires a `wave-config.yaml` validated by `validate_wave_config.py` before Gate 1
- **Gate decisions:** record in `gate{N}-decision.md` with score, approvers, and open items
- **Agent outputs:** store in `projects/<project-name>/outputs/<phase>/`
- **Discovery ownership:** each wave has exactly one `discovery_owner` in wave-config; `inventory-scout` is fallback only
- **Platform agnostic:** do not hardcode Databricks, Fabric, or Snowflake in agent instructions or scripts — use `(inform target platform)` or receive via prompt
- **Coordinator hierarchy:** `master-agent` = user triage + KB; `migration-coordinator` (Orion) = wave orchestration + gates. Do NOT use `orchestrator` (deprecated).
- **Artifact ownership:** Winston (DataArchitect) owns `architecture.md`, `decisions.md`, `monitoring-spec.md`. Sofia (DataModeler) owns `data-model.md`, `data-contracts.md`, `metrics-catalog.md`.
- **Token optimization:** use `headroom_compress` for artifacts >500KB before passing to downstream agents. Scripts expose `_compressed()` functions that auto-detect Headroom availability.

## Docs Index

| Document | Purpose |
|---|---|
| [docs/PLAYBOOK-ONBOARDING.md](docs/PLAYBOOK-ONBOARDING.md) | New team member setup guide |
| [docs/PLAYBOOK-MIGRATION-OPERATIONS.md](docs/PLAYBOOK-MIGRATION-OPERATIONS.md) | Step-by-step migration wave execution |
| [docs/COPILOT-AGENTS-GUIDE.md](docs/COPILOT-AGENTS-GUIDE.md) | Full command reference per agent |
| [docs/OPERATING-MODEL-CANVAS-v2.md](docs/OPERATING-MODEL-CANVAS-v2.md) | Agent roles, permissions, governance |
| [docs/SKILLS-BLUEPRINT-BY-GATE.md](docs/SKILLS-BLUEPRINT-BY-GATE.md) | Skills mapped to each gate |
| [docs/PRD-Agentic-Data-Migration-Factory.md](docs/PRD-Agentic-Data-Migration-Factory.md) | Requirements and acceptance criteria |
