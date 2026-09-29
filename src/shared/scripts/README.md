# Governance Scripts

23 Python modules implementing the governance control plane for the Data Migration Factory.
Each module maps to one or more backlog items (B-xxx) and has full pytest coverage.

**Test status:** 271/271 passing — `python -m pytest src/shared/tests/ -q`

---

## Modules

### Governance and Policy

#### `audit_logger.py` — B-004

Persists audit events for gate pass/fail decisions and overrides.

```python
from scripts.audit_logger import AuditLogger, AuditEvent

logger = AuditLogger()
logger.log(AuditEvent(gate="gate-3", decision="PASS", approver="orion", wave_id="WAVE-001"))
events = logger.get_events(wave_id="WAVE-001")
```

---

#### `review_workflow.py` — B-003

Implements the review-required workflow for high-risk agent actions.
Blocks execution until explicit approval is recorded.

```python
from scripts.review_workflow import ReviewWorkflow

wf = ReviewWorkflow()
request_id = wf.submit(action="execute-prod-ddl", agent="downstream-executor", wave_id="WAVE-001")
wf.approve(request_id, approver="migration-coordinator")
```

---

#### `decision_log.py` — B-018

Decision log template for governance exceptions.
All exception decisions become searchable audit records.

```python
from scripts.decision_log import DecisionLog

log = DecisionLog()
log.record(decision="override-gate-2", rationale="deadline approved by lead", approver="architect")
entries = log.search(keyword="gate-2")
```

---

### Gate and Artifact Validation

#### `validate_gate3_artifacts.py` — B-006

Pre-transition artifact validator. Reports missing artifacts as blockers before Gate 3 promotion.

**Required artifacts:** `ddl/`, `etl/`, `tests/`, `documentation/`, `wave-report.md`, `execution-runbook.md`

```python
from scripts.validate_gate3_artifacts import validate_gate3_requirements, validate_ast_artifacts
from pathlib import Path

root = Path("projects/migration-northwind/outputs/downstream")
result = validate_gate3_requirements(root)
print(result)  # PASS / FAIL with blocker list

# Optional AST path validation by gate
ast_result = validate_ast_artifacts(gate=3, artifact_root=root)
print(ast_result)
```

---

#### `validate_wave_config.py` — B-017, B-008

Validates wave YAML config: enforces `discovery_owner_primary` + `discovery_owner_fallback` (B-017)
and `runbook_path` for non-dry-run UAT/PROD waves (B-008).

**Requires:** `pyyaml` (`pip install pyyaml`)

```python
from scripts.validate_wave_config import validate_wave_config
from pathlib import Path

result = validate_wave_config(Path("projects/migration-northwind/wave-config.yaml"))
# result.is_valid, result.errors, result.warnings
```

Standalone:

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_wave_config projects\migration-northwind\wave-config.yaml
```

---

#### `gate_score_report.py` — B-007

Calculates GateScore and emits a gate report.

Formula: `GateScore = 0.35×Completude + 0.25×Qualidade + 0.20×RiscoResidual + 0.20×Reconciliacao`

| Score | Decision |
| --- | --- |
| ≥ 85 | APPROVED |
| 70–84 | APPROVED with caveats |
| < 70 | BLOCKED |

```python
from scripts.gate_score_report import GateScoreReport

report = GateScoreReport(completude=90, qualidade=88, risco_residual=85, reconciliacao=92)
print(report.score)    # 89.15
print(report.decision) # APPROVED
```

---

#### `check_chatmode_alignment.py` — B-005, B-017

Detects mismatches between `.github/agents/*.chatmode.md` files and `*-agent/` folders.
Used in CI to prevent orphaned agents.

```bash
python -m scripts.check_chatmode_alignment
```

---

#### `validate_gate1_artifacts.py` — Improvement Round

Convenience module for Gate 1 artifact validation (delegates to `validate_gate3_artifacts.validate_gate_requirements`).

Required artifacts: `problem-statement.md`, `kpis.md`, `analytical-questions.md`, `sttm.md`, `dq-initial.md`

```python
from scripts.validate_gate1_artifacts import validate_gate1_artifacts
from pathlib import Path

result = validate_gate1_artifacts(Path("projects/migration-northwind/outputs/upstream"))
print(result)  # PASS / FAIL
```

Standalone:

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate1_artifacts projects\migration-northwind\outputs\upstream
```

---

#### `validate_gate2_artifacts.py` — Improvement Round

Convenience module for Gate 2 artifact validation.

Required artifacts: `architecture.md`, `data-model.md`, `decisions.md`, `dq-rules.md`, `monitoring-spec.md`

```python
from scripts.validate_gate2_artifacts import validate_gate2_artifacts
from pathlib import Path

result = validate_gate2_artifacts(Path("projects/migration-northwind/outputs/midstream"))
print(result)  # PASS / FAIL
```

Standalone:

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate2_artifacts projects\migration-northwind\outputs\midstream
```

---

### Quality and Reconciliation

#### `quality_thresholds.py` — B-011

Defines threshold-based quality checks per entity tier (CRITICAL / STANDARD / REFERENCE).

| Tier | Min completeness | Max null rate | Min uniqueness |
| --- | --- | --- | --- |
| CRITICAL | 99% | 0.1% | 100% |
| STANDARD | 95% | 1% | 99% |
| REFERENCE | 90% | 5% | 95% |

```python
from scripts.quality_thresholds import QualityThresholds

thresholds = QualityThresholds.for_tier("CRITICAL")
result = thresholds.validate(completeness=98.5, null_rate=0.05, uniqueness=100)
# result.passed, result.violations
```

---

#### `reconciliation_checks.py` — B-009

Row-count and SHA-256 checksum reconciliation for high-risk entities. Supports two operation modes:

| Mode | Description | When to use |
| --- | --- | --- |
| **DISCONNECTED** (default) | Rows are supplied externally as Python lists or CSV file paths. No live DB connection needed. | Pilots, CI tests, air-gapped environments |
| **CONNECTED** | Rows are fetched via callable adapters provided by the operator (e.g., SQL query functions). | Automated reconciliation pipelines with direct DB access |

**Original disconnected API (in-memory lists — backward compatible):**

```python
from scripts.reconciliation_checks import reconcile_checksums

report = reconcile_checksums(
    entity="orders",
    source_rows=[{"id": 1, "amount": 100}],
    target_rows=[{"id": 1, "amount": 100}],
)
print(report)
# Reconciliation [orders] (DISCONNECTED): PASS
```

**Disconnected via CSV files (no live connection):**

```python
from scripts.reconciliation_checks import reconcile_from_sources, ReconciliationMode
from pathlib import Path

report = reconcile_from_sources(
    entity="orders",
    source_loader=Path("exports/source_orders.csv"),
    target_loader=Path("exports/target_orders.csv"),
    mode=ReconciliationMode.DISCONNECTED,
)
```

**Connected via callable adapters:**

```python
from scripts.reconciliation_checks import reconcile_from_sources, ReconciliationMode

report = reconcile_from_sources(
    entity="orders",
    source_loader=lambda: source_db.query("SELECT * FROM orders"),
    target_loader=lambda: target_db.query("SELECT * FROM orders"),
    mode=ReconciliationMode.CONNECTED,
)
print(report.status)  # ReconciliationStatus.PASS / FAIL
print(report.mode)    # ReconciliationMode.CONNECTED
```

**Load rows from CSV (helper):**

```python
from scripts.reconciliation_checks import load_rows_from_csv
from pathlib import Path

rows = load_rows_from_csv(Path("exports/orders.csv"))
# Returns list[dict] — all values are strings; cast as needed
```

---

#### `reconciliation_tolerance.py` — B-012

Defines tolerance bands for reconciliation (e.g., ≤0.01% row count variance allowed for CRITICAL entities).

```python
from scripts.reconciliation_tolerance import ReconciliationTolerance

tol = ReconciliationTolerance.for_tier("CRITICAL")
result = tol.check(source_count=100000, target_count=99999)
# result.within_tolerance, result.variance_pct
```

---

#### `mismatch_taxonomy.py` — B-013

Tracks and categorizes mismatch root causes in reconciliation reports.

Categories: `NULL_MISMATCH`, `TYPE_CAST`, `ENCODING`, `TRUNCATION`, `BUSINESS_RULE`, `UNKNOWN`

```python
from scripts.mismatch_taxonomy import MismatchTaxonomy

taxonomy = MismatchTaxonomy()
taxonomy.record(entity="Orders", field="OrderDate", category="TYPE_CAST", count=3)
print(taxonomy.summary())
```

---

#### `performance_benchmark.py` — B-010

Production-like performance benchmark for migration waves. Computes rows/second and compares against a configurable baseline with tolerance bands.

```python
from scripts.performance_benchmark import BenchmarkRun, run_benchmark

run = BenchmarkRun(
    wave_id="WAVE-001",
    entity="orders",
    rows_processed=1_000_000,
    duration_seconds=60.0,
    baseline_rows_per_second=10_000.0,
)
report = run_benchmark(run)
print(report)  # PASS/FAIL with delta %
```

---

### Automation

#### `generate_github_issues.py` — Backlog Automation

Reads a MoSCoW backlog Markdown table (B-001 through B-019) and generates one GitHub Issue template file per Must item.

```python
from scripts.generate_github_issues import parse_must_items

items = parse_must_items(backlog_text)
for item in items:
    print(item.to_issue_markdown())
```

Standalone:

```bash
python -m scripts.generate_github_issues --backlog BACKLOG.md --out .github/ISSUE_TEMPLATE/backlog/
```

---

### Observability and KPIs

#### `kpi_dictionary.py` — B-014

Defines the KPI dictionary with owners and measurement methods.

```python
from scripts.kpi_dictionary import KPIDictionary

kpi_dict = KPIDictionary()
kpi = kpi_dict.get("first_pass_rate")
# kpi.owner, kpi.target, kpi.measurement_method
```

---

#### `kpi_dashboard_report.py` — B-015

Generates wave KPI dashboard report artifact.

Execution KPIs tracked:

- `first_pass_rate`
- `rollback_count`
- `mttr`
- `cycle_time`

Optional AST KPIs tracked when informed:

- `ast_coverage`
- `transformation_accuracy`
- `code_generation_accuracy`

```python
from scripts.kpi_dashboard_report import WaveExecutionMetrics, generate_kpi_dashboard_report

metrics = WaveExecutionMetrics(
    wave_id="WAVE-001",
    first_pass_rate_pct=97.0,
    rollback_count=0,
    mttr_minutes=20.0,
    cycle_time_minutes=180.0,
    ast_coverage_pct=94.2,
    transformation_accuracy_pct=96.5,
    code_generation_accuracy_pct=83.0,
)

report = generate_kpi_dashboard_report(metrics)
for row in report.rows:
    print(row.kpi_id, row.actual, row.status)
```

---

#### `slo_workflow.py` — B-016

SLO baseline and breach action workflow. Triggers action items when thresholds are violated.

```python
from scripts.slo_workflow import SLOWorkflow

wf = SLOWorkflow()
wf.define(slo="gate_cycle_time", threshold=48, unit="hours", operator="lte")
result = wf.evaluate_wave(wave_id="WAVE-001", gate_cycle_time=52)
# result.breached_slos → list of SLO breaches with action items
```

---

### Traceability

#### `prd_traceability.py` — B-019

Maps stories and epics back to PRD IDs for full audit traceability.

```python
from scripts.prd_traceability import PRDTraceability

trace = PRDTraceability()
trace.link(story_id="B-009", prd_section="3.5 Reconciliation Evidence")
print(trace.coverage_report())
```

---

### Wave Status Tracking

#### `wave_status_tracker.py` — Improvement Round

Consolidates wave status across all three gates: artifact completeness, gate scores, and overall readiness.

```python
from scripts.wave_status_tracker import WaveStatusTracker

tracker = WaveStatusTracker(wave_id="WAVE-001")
tracker.set_gate_artifacts(1, present=5, total=5)
tracker.set_gate_artifacts(2, present=4, total=5)
tracker.set_gate_artifacts(3, present=0, total=8)
tracker.set_gate_score(1, 88.0)
print(tracker.summary())
# Wave Status: WAVE-001  (overall: 50%)
#   Gate 1: COMPLETE  artifacts=5/5 (100.0%)  score=88.0
#   Gate 2: IN_PROGRESS  artifacts=4/5 (80.0%)  score=N/A
#   Gate 3: NOT_STARTED  artifacts=0/8 (0.0%)  score=N/A
```

---

### Agent Governance and Contracts

#### `validate_agent_contracts.py` — Improvement Round 2

Structural contract validator for `.chatmode.md` agent files. Checks frontmatter fields (`description`, `tools`), heading, commands, and activation instructions. Handles UTF-8 BOM.

```python
from scripts.validate_agent_contracts import validate_agent_contracts
from pathlib import Path

result = validate_agent_contracts(Path("."))
print(result)  # 21/21 passed
```

Standalone:

```bash
python -m scripts.validate_agent_contracts --root .
```

---

#### `governance_policy.py` — Improvement Round 2

Programmatic governance policy engine. Models allowed/blocked tools, max tool counts, and policy composition with most-restrictive-wins semantics. Validates chatmodes against policy.

```python
from scripts.governance_policy import (
    GovernancePolicy, PolicyAction, compose_policies,
    validate_chatmode_policy, FACTORY_BASELINE_POLICY,
)
from pathlib import Path

result = validate_chatmode_policy(Path(".github/agents/self-healing.chatmode.md"))
print(result)  # [PASS] self-healing — tools: ['edit', 'search', ...]
```

---

#### `data_contract_validator.py` — Improvement Round 2

Declarative data contract validation. Loads YAML contracts (entity, owner, tier, fields, quality expectations) and evaluates measured metrics against thresholds.

```python
from scripts.data_contract_validator import load_contract, validate_contract_schema, evaluate_contract
from pathlib import Path

contract = load_contract(Path("contracts/orders.yaml"))
schema_result = validate_contract_schema(contract)
eval_result = evaluate_contract(contract, completeness=0.99, row_parity=1.0, dq_score=0.98)
print(eval_result)  # Contract Eval [orders]: PASS
```

---

## Running Tests

```bash
# All scripts
python -m pytest tests/ -q

# One module
python -m pytest tests/test_validate_wave_config.py -v

# With coverage (requires pytest-cov)
python -m pytest tests/ --cov=scripts --cov-report=term-missing
```

---

## Dependencies

| Package | Used by |
| --- | --- |
| `pytest` | All tests |
| `pyyaml` | `validate_wave_config.py`, `kpi_dictionary.py`, `data_contract_validator.py` |

Install: `pip install pytest pyyaml`
