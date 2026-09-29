# Agent Instructions

## Environment

Use **Python 3.13+** with venv: `.venv\Scripts\Activate.ps1`
Dependencies: `pip install pytest pyyaml`

## File-Scoped Commands

| Task              | Command                                                    |
| ----------------- | ---------------------------------------------------------- |
| All tests         | `python -m pytest src/shared/tests/ -q`                    |
| Single test       | `python -m pytest src/shared/tests/test_<module>.py -v`    |
| Validate wave     | `.venv\Scripts\python.exe -m src.shared.scripts.validate_wave_config projects/<project_name>/wave-config.yaml` |
| Validate Gate N   | `.venv\Scripts\python.exe -m src.shared.scripts.validate_gate{1,2,3}_artifacts projects/<project_name>/outputs/<phase>` |
| Chatmode align    | `.venv\Scripts\python.exe -m src.shared.scripts.check_chatmode_alignment --root .` |
| Lint              | `ruff check src/shared/scripts/ src/shared/tests/`         |

## Commit Attribution

AI commits MUST include:

```text
Co-Authored-By: GitHub Copilot <noreply@github.com>
```

## Key Conventions

- **Wave root:** use `projects/<project_name>/`; keep `project_name` identical in the folder, `wave-config.yaml`, `context/project-config.yaml`, and `context/agent-task-config.yaml`
- **Wave config:** declare `context_base_path` and `outputs_base_path`, then validate the explicit file path before `*start-wave`
- **Gate decisions:** record in `gate{N}-decision.md` with score + approvers
- **Agent context:** read from `projects/<project_name>/context/`
- **Agent outputs:** store only below `projects/<project_name>/outputs/{upstream|midstream|downstream|summary}/`
- **Platform agnostic:** never hardcode Databricks/Fabric/Snowflake
- **Entry point:** start with `master-agent` → `*route`
- **Coordinator:** use `migration-coordinator` (Orion), NOT `orchestrator` (deprecated)
- **Artifact ownership:** Winston → `architecture.md`, `decisions.md`, `monitoring-spec.md`; Sofia → `data-model.md`, `data-contracts.md`
- **Scripts:** always run tests after editing — expected `python -m pytest src/shared/tests/ -q` → all passed

## Structure

- `src/shared/scripts/` — 23 governance modules (see `src/shared/scripts/README.md`)
- `src/shared/tests/` — full pytest coverage (271 tests)
- `.github/agents/` — 21 chatmode agents (20 active + 1 deprecated)
- `.github/skills/` — 26 domain skills
- `src/modules/dmf-fabric-agents/` — 5 agent modules by phase
- `docs/` — playbooks, PRD, operating model
- `src/shared/samples/wave-config-sample.yaml` — reference template
