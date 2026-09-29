"""AVA Data Migration Factory Pipeline Runner.

Runs the data migration agents in isolated phases through Azure AI Foundry.
The runner keeps the application-factory execution model while using this
repository's wave configuration, agent definitions, gate validators, and
output contracts.

Examples:
    python pipeline_runner.py --project orders-migration
    python pipeline_runner.py --project orders-migration --auto
    python pipeline_runner.py --project orders-migration --phases U G1 --auto
    python pipeline_runner.py --wave-config projects/orders-migration/wave-config.yaml --resume

Requirements:
    Python 3.11+, anthropic, pyyaml, requests (optional for Headroom health checks)
    .copilot-key at the repository root or AVA_FOUNDRY_API_KEY in the environment
"""
from __future__ import annotations

import argparse
import atexit
import datetime as _datetime
import html as _html
import importlib
import importlib.util
import json
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import textwrap
import time
import uuid
from pathlib import Path
from typing import Any

try:
    import anthropic as _anthropic
except ImportError:
    _anthropic = None

try:
    import requests as _requests
except ImportError:
    _requests = None

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

try:
    import openai as _openai
except ImportError:
    _openai = None

try:
    import msvcrt as _msvcrt
except ImportError:
    _msvcrt = None


def configure_stdio() -> None:
    """Keep runner-13's Unicode status output reliable on Windows terminals."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


configure_stdio()


USE_COLOR = (
    sys.stdout.isatty()
    and os.environ.get("NO_COLOR") is None
    and "--no-color" not in sys.argv
)
INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()


def color(code: str) -> str:
    return code if USE_COLOR else ""


RESET = color("\033[0m")
BOLD = color("\033[1m")
CYAN = color("\033[96m")
GREEN = color("\033[92m")
YELLOW = color("\033[93m")
RED = color("\033[91m")
DIM = color("\033[2m")
MAGENTA = color("\033[95m")

WORKSPACE = Path(__file__).resolve().parent
PROJECTS_ROOT = WORKSPACE / "projects"
API_KEY_FILE = WORKSPACE / ".copilot-key"
REFERENCE_RUNNER_ROOT = Path.home() / "Downloads" / "ava-fabric-run-java-openkoda"
API_KEY_CANDIDATES = (
    API_KEY_FILE,
    REFERENCE_RUNNER_ROOT / ".copilot-key",
)

ENDPOINT_ANTHROPIC = os.environ.get(
    "AVA_ANTHROPIC_ENDPOINT",
    "https://aif-imf-apps-prd-eus2-001.services.ai.azure.com/anthropic",
)
ENDPOINT_OPENAI = os.environ.get(
    "AVA_OPENAI_ENDPOINT",
    "https://aif-imf-apps-prd-eus2-001.services.ai.azure.com/openai",
)
OPENAI_API_VERSION = os.environ.get("AVA_OPENAI_API_VERSION", "2024-12-01-preview")

# Same private-endpoint fallback used by the application-factory runner.
# Native VPN DNS remains the preferred path; this only helps split-DNS laptops.
_DNS = {
    "aif-imf-agents-prd-eus2-001.services.ai.azure.com": "10.26.2.6",
    "aif-imf-agents-prd-eus2-001.privatelink.services.ai.azure.com": "10.26.2.6",
    "aif-imf-apps-prd-eus2-001.openai.azure.com": "10.26.2.11",
    "aif-imf-apps-prd-eus2-001.services.ai.azure.com": "10.26.2.12",
    "aif-imf-premium-models-prd-eus2-001.services.ai.azure.com": "10.26.2.27",
    "aif-imf-premium-models-prd-eus2-001.privatelink.services.ai.azure.com": "10.26.2.27",
}
_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def _patched_getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any):
    return _ORIGINAL_GETADDRINFO(_DNS.get(host, host), port, *args, **kwargs)


socket.getaddrinfo = _patched_getaddrinfo

MODEL_REGISTRY: dict[str, dict[str, str]] = {
    "claude-sonnet-4-6": {
        "label": "Claude Sonnet 4.6 (Anthropic-compatible)",
        "provider": "anthropic",
        "endpoint": ENDPOINT_ANTHROPIC,
        "deployment": "claude-sonnet-4-6",
    },
    "gpt-5.6-luna": {
        "label": "GPT-5.6 LUNA (Azure OpenAI-compatible)",
        "provider": "openai",
        "endpoint": ENDPOINT_OPENAI.rsplit("/openai", 1)[0],
        "deployment": "gpt-5.6-luna",
    },
}
DEFAULT_MODEL_KEY = "claude-sonnet-4-6"
DEPLOYMENT = MODEL_REGISTRY[DEFAULT_MODEL_KEY]["deployment"]
PROVIDER = MODEL_REGISTRY[DEFAULT_MODEL_KEY]["provider"]
ENDPOINT = MODEL_REGISTRY[DEFAULT_MODEL_KEY]["endpoint"]

MAX_TOKENS = 128_000
TEMPERATURE = 0.0
CTX_WINDOW = 1_000_000
CTX_INPUT_BUDGET_TOKENS = 300_000
ART_INJECT_CHARS = 80_000
SOURCE_INJECT_BUDGET_TOKENS = 200_000
SOURCE_FILE_CHARS = 60_000
CHARS_PER_TOKEN = 4
CTX_SKILL = 2_000_000
CTX_ARTIFACT_INDEX = 500
API_TIMEOUT_S = 3_600.0
API_MAX_RETRIES = 3
STREAM_RETRIES = 3
CONTINUATION_MAX = 4
ENABLE_PROMPT_CACHE = True
DRY_RUN = False

MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_write": 3.75,
    },
    "gpt-5.6-luna": {
        "input": 0.20,
        "output": 1.20,
        "cache_read": 0.02,
        "cache_write": 0.20,
    },
}

FINOPS_DB = WORKSPACE / ".claude-flow" / "agent-finops" / "telemetry.db"
FINOPS_ENABLED = os.environ.get("AVA_FINOPS_TELEMETRY", "1").lower() not in {
    "0",
    "false",
    "no",
    "off",
}
FINOPS_SESSION_ID = f"unscoped-{uuid.uuid4().hex}"
FINOPS_PROJECT = ""
FINOPS_STARTED = False
FINOPS_FINISHED = False
FINOPS_SOURCE_PROJECT = ""
FINOPS_WARNING_EMITTED = False

HEADROOM_PROXY_URL = os.environ.get("AVA_HEADROOM_PROXY_URL", "http://127.0.0.1:8787")
HEADROOM_EXE = os.environ.get("AVA_HEADROOM_EXE", "")
HEADROOM_PROCESS: subprocess.Popen | None = None
HEADROOM_EXTERNAL = False
AST_ENABLED = True
AST_PHASE = "A0"
HEADROOM_CONFIG_CANDIDATES = (
    WORKSPACE / "src" / "shared" / "tools" / "headroom" / "headroom_config.py",
    REFERENCE_RUNNER_ROOT / "src" / "shared" / "tools" / "headroom" / "headroom_config.py",
)
HEADROOM_PYTHON_CANDIDATES = (
    WORKSPACE / ".headroom" / ".venv" / "Scripts" / "python.exe",
    WORKSPACE / "src" / "shared" / "tools" / "headroom" / ".venv" / "Scripts" / "python.exe",
    REFERENCE_RUNNER_ROOT / "src" / "shared" / "tools" / "headroom" / ".venv" / "Scripts" / "python.exe",
)


PHASE_GROUPS: dict[str, list[str]] = {
    "A0": ["A0"],
    "AST": ["A0"],
    "U": [
        "A0",
        "U1",
        "U2",
        "U3",
        "U4",
        "U5",
        "U6",
        "U7",
        "U8",
        "U9",
        "U10",
        "U11",
        "U12",
        "U13",
        "G1",
    ],
    "UPSTREAM": [
        "A0",
        "U1",
        "U2",
        "U3",
        "U4",
        "U5",
        "U6",
        "U7",
        "U8",
        "U9",
        "U10",
        "U11",
        "U12",
        "U13",
        "G1",
    ],
    "G1": ["G1"],
    "M": [
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
        "M10",
        "M11",
        "G2",
    ],
    "MIDSTREAM": [
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
        "M10",
        "M11",
        "G2",
    ],
    "G2": ["G2"],
    "D": ["D1", "D2", "D3", "D4", "D5", "G3"],
    "DOWNSTREAM": ["D1", "D2", "D3", "D4", "D5", "G3"],
    "G3": ["G3"],
}

PHASE_MENU_GROUPS: dict[str, tuple[str, list[str]]] = {
    "A0": ("A0 — AST determinístico", ["A0"]),
    "U": ("UPSTREAM — Estratégia, descoberta e requisitos", [phase for phase in PHASE_GROUPS["U"] if phase != "A0"]),
    "G1": ("G1 — Gate de artefatos UPSTREAM", ["G1"]),
    "M": ("MIDSTREAM — Arquitetura, modelo, código e qualidade", PHASE_GROUPS["M"][:-1]),
    "G2": ("G2 — Gate de artefatos MIDSTREAM", ["G2"]),
    "D": ("DOWNSTREAM — Execução, BI e documentação", PHASE_GROUPS["D"][:-1]),
    "G3": ("G3 — Gate de artefatos DOWNSTREAM", ["G3"]),
}

PIPELINE: list[dict[str, Any]] = [
    {
        "phase": "A0",
        "label": "AST Engine - Deterministic Source Extraction",
        "agent": "_ast_engine",
        "command": None,
        "area": "upstream",
        "required": [
            "upstream/canonical-model.json",
            "upstream/column-lineage.json",
            "upstream/sttm.md",
            "downstream/generated-code/",
        ],
    },
    {
        "phase": "U1",
        "label": "Strategy - Problem Statement",
        "agent": "data-strategist",
        "command": "*define-problem",
        "area": "upstream",
        "required": ["upstream/strategy/problem-statement.md"],
    },
    {
        "phase": "U2",
        "label": "Strategy - KPIs and Success Criteria",
        "agent": "data-strategist",
        "command": "*create-kpis",
        "area": "upstream",
        "required": ["upstream/strategy/kpis.md"],
    },
    {
        "phase": "U3",
        "label": "Discovery - Scan Source Repository",
        "agent": "discovery-scout",
        "command": "*scan-repo",
        "area": "upstream",
        "required": ["upstream/analysis/inventory-report.md"],
    },
    {
        "phase": "U4",
        "label": "Discovery - Classify Pipelines",
        "agent": "discovery-scout",
        "command": "*classify",
        "area": "upstream",
        "required": ["upstream/analysis/complexity-classification.md"],
    },
    {
        "phase": "U5",
        "label": "Discovery - Map Dependencies",
        "agent": "discovery-scout",
        "command": "*map-dependencies",
        "area": "upstream",
        "required": ["upstream/analysis/dependency-graph.json"],
    },
    {
        "phase": "U6",
        "label": "Discovery - Detect Dead Code",
        "agent": "discovery-scout",
        "command": "*detect-dead-code",
        "area": "upstream",
        "required": ["upstream/analysis/dead-code-report.md"],
    },
    {
        "phase": "U7",
        "label": "Discovery - Estimate Data Volume",
        "agent": "discovery-scout",
        "command": "*estimate-volume",
        "area": "upstream",
        "required": ["upstream/analysis/data-volume-estimate.json"],
    },
    {
        "phase": "U8",
        "label": "Discovery - Generate Inventory",
        "agent": "discovery-scout",
        "command": "*generate-inventory",
        "area": "upstream",
        "required": ["upstream/analysis/inventory-report.md"],
    },
    {
        "phase": "U9",
        "label": "Logic - AST Extraction",
        "agent": "logic-extractor",
        "command": "*extract-ast",
        "area": "upstream",
        "required": [],
    },
    {
        "phase": "U10",
        "label": "Logic - Business Rule Extraction",
        "agent": "logic-extractor",
        "command": "*extract-logic",
        "area": "upstream",
        "required": ["upstream/analysis/business-rules.md"],
    },
    {
        "phase": "U11",
        "label": "Requirements - Source to Target Mapping",
        "agent": "business-analyst",
        "command": "*create-sttm",
        "area": "upstream",
        "required": ["upstream/sttm/sttm.md"],
    },
    {
        "phase": "U12",
        "label": "Requirements - Analytical Questions",
        "agent": "business-analyst",
        "command": "*analytical-questions",
        "area": "upstream",
        "required": ["upstream/analysis/analytical-questions.md"],
    },
    {
        "phase": "U13",
        "label": "Requirements - Initial Data Quality",
        "agent": "business-analyst",
        "command": "*dq-initial",
        "area": "upstream",
        "required": ["upstream/analysis/dq-initial.md"],
    },
    {
        "phase": "G1",
        "label": "Gate 1 - Validate Upstream Artifacts",
        "agent": "_gate_validator",
        "command": None,
        "gate": 1,
        "area": "upstream",
        "required": [],
    },
    {
        "phase": "M1",
        "label": "Architecture - Data Architecture",
        "agent": "data-architect",
        "command": "*create-architecture",
        "area": "midstream",
        "required": ["midstream/architecture.md", "midstream/monitoring-spec.md"],
    },
    {
        "phase": "M2",
        "label": "Architecture - Architecture Decisions",
        "agent": "data-architect",
        "command": "*document-decisions",
        "area": "midstream",
        "required": ["midstream/decisions.md"],
    },
    {
        "phase": "M3",
        "label": "Model - Logical Data Model",
        "agent": "data-modeler",
        "command": "*data-model",
        "area": "midstream",
        "required": ["midstream/data-model.md"],
    },
    {
        "phase": "M4",
        "label": "Model - Data Contracts",
        "agent": "data-modeler",
        "command": "*data-contracts",
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "M5",
        "label": "Model - Metrics Catalog",
        "agent": "data-modeler",
        "command": "*metrics",
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "M6",
        "label": "Governance - Data Quality Rules",
        "agent": "data-steward",
        "command": "*create-dq-rules",
        "area": "midstream",
        "required": ["midstream/dq-rules.md"],
    },
    {
        "phase": "M7",
        "label": "Governance - Governance Framework",
        "agent": "data-steward",
        "command": "*create-governance",
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "M8",
        "label": "Governance - Data Classification",
        "agent": "data-steward",
        "command": "*classify-data",
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "M9",
        "label": "Code - Generate DDL and ETL",
        "agent": "code-generator",
        "command": "*generate-code",
        "area": "midstream",
        "required": ["midstream/ddl/", "midstream/etl/"],
    },
    {
        "phase": "M10",
        "label": "Quality - Validate Generated Code",
        "agent": "quality-gate",
        "command": "*validate",
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "M11",
        "label": "Security - Scan PII and Compliance",
        "agent": "security-compliance",
        "command": "*scan-pii",
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "G2",
        "label": "Gate 2 - Validate Midstream Artifacts",
        "agent": "_gate_validator",
        "command": None,
        "gate": 2,
        "area": "midstream",
        "required": [],
    },
    {
        "phase": "D1",
        "label": "Execution - Create DDL and ETL Package",
        "agent": "downstream-executor",
        "command": "*create-ddl-etl",
        "area": "downstream",
        "required": ["downstream/ddl/", "downstream/etl/", "downstream/tests/"],
    },
    {
        "phase": "D2",
        "label": "Execution - Run Migration Wave",
        "agent": "downstream-executor",
        "command": "*run-wave",
        "area": "downstream",
        "required": ["downstream/wave-report.md"],
    },
    {
        "phase": "D3",
        "label": "Reconciliation - Validate Data Parity",
        "agent": "reconciliation",
        "command": "*reconcile-wave",
        "area": "downstream",
        "required": ["downstream/documentation/reconciliation-evidence.md"],
    },
    {
        "phase": "D4",
        "label": "BI - Semantic Model and Consumption Package",
        "agent": "bi-semantic",
        "command": "*create-semantic-model",
        "area": "downstream",
        "required": ["downstream/bi/"],
    },
    {
        "phase": "D5",
        "label": "Documentation - Generate Migration Package",
        "agent": "documentation",
        "command": "*generate-all",
        "area": "downstream",
        "required": [
            "downstream/documentation/execution-runbook.md",
            "downstream/documentation/quality-gate-evidence.md",
        ],
    },
    {
        "phase": "G3",
        "label": "Gate 3 - Validate Downstream Artifacts",
        "agent": "_gate_validator",
        "command": None,
        "gate": 3,
        "area": "downstream",
        "required": [],
    },
]

AGENT_FALLBACK_FILES: dict[str, str] = {
    "data-strategist": "src/modules/dmf-fabric-agents/upstream-discovery/agents/data-strategist/data-strategist.md",
    "business-analyst": "src/modules/dmf-fabric-agents/upstream-discovery/agents/business-analyst/business-analyst.md",
    "discovery-scout": "src/modules/dmf-fabric-agents/upstream-discovery/agents/discovery-scout/discovery-scout.md",
    "logic-extractor": "src/modules/dmf-fabric-agents/upstream-discovery/agents/logic-extractor/logic-extractor.md",
    "data-architect": "src/modules/dmf-fabric-agents/midstream-design/agents/data-architect/data-architect.md",
    "data-modeler": "src/modules/dmf-fabric-agents/midstream-design/agents/data-modeler/data-modeler.md",
    "data-steward": "src/modules/dmf-fabric-agents/midstream-design/agents/data-steward/data-steward.md",
    "code-generator": "src/modules/dmf-fabric-agents/midstream-design/agents/code-generator/code-generator.md",
    "quality-gate": "src/modules/dmf-fabric-agents/midstream-quality/agents/quality-gate/quality-gate.md",
    "security-compliance": "src/modules/dmf-fabric-agents/midstream-quality/agents/security-compliance/security-compliance.md",
    "downstream-executor": "src/modules/dmf-fabric-agents/downstream-execution/agents/downstream-executor/downstream-executor.md",
    "reconciliation": "src/modules/dmf-fabric-agents/downstream-execution/agents/reconciliation/reconciliation.md",
    "documentation": "src/modules/dmf-fabric-agents/downstream-execution/agents/documentation/documentation.md",
    "bi-semantic": "src/modules/dmf-fabric-agents/downstream-execution/agents/bi-semantic/bi-semantic.md",
}

FILE_BLOCK = re.compile(
    r"<!--\s*FILE:\s*([^\r\n]+?)\s*-->\r?\n(.*?)<!--\s*/FILE\s*-->",
    re.DOTALL,
)
FILE_OPEN = re.compile(
    r"<!--\s*FILE:\s*([^\r\n]+?)\s*-->\r?\n(.*?)(?=<!--\s*FILE:|<!--\s*/FILE|\Z)",
    re.DOTALL,
)

GATE_ARTIFACTS: dict[int, list[str]] = {
    1: [
        "strategy/problem-statement.md",
        "strategy/kpis.md",
        "analysis/analytical-questions.md",
        "sttm/sttm.md",
        "analysis/dq-initial.md",
    ],
    2: [
        "architecture.md",
        "data-model.md",
        "decisions.md",
        "dq-rules.md",
        "monitoring-spec.md",
    ],
    3: [
        "ddl/",
        "etl/",
        "tests/",
        "documentation/",
        "wave-report.md",
        "documentation/execution-runbook.md",
        "documentation/quality-gate-evidence.md",
        "documentation/reconciliation-evidence.md",
        "downstream/bi/",
    ],
}


class RunnerError(RuntimeError):
    """Expected runner configuration or execution error."""


def banner(message: str, selected_color: str = CYAN) -> None:
    line = "-" * 72
    print(f"\n{selected_color}{BOLD}{line}{RESET}")
    print(f"{selected_color}{BOLD}  {message}{RESET}")
    print(f"{selected_color}{BOLD}{line}{RESET}")


def safe_input(prompt: str, default: str = "") -> str:
    if not INTERACTIVE:
        print(f"{prompt}{DIM}[non-interactive -> '{default}']{RESET}")
        return default
    if _msvcrt is None:
        try:
            return input(prompt)
        except EOFError:
            return default

    sys.stdout.write(prompt)
    sys.stdout.flush()
    chars: list[str] = []
    while True:
        character = _msvcrt.getwch()
        if character in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(chars)
        if character == "\x03":
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise KeyboardInterrupt
        if character == "\x08":
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
        elif character in ("\x00", "\xe0"):
            _msvcrt.getwch()
        elif character >= " ":
            chars.append(character)
            sys.stdout.write(character)
            sys.stdout.flush()


def project_area(phase: str) -> str:
    if phase.startswith("U") or phase == "G1":
        return "upstream"
    if phase.startswith("M") or phase == "G2":
        return "midstream"
    if phase.startswith("D") or phase == "G3":
        return "downstream"
    return "summary"


def model_prices(model: str | None = None) -> dict[str, float]:
    return MODEL_PRICING.get(model or DEPLOYMENT, MODEL_PRICING[DEFAULT_MODEL_KEY])


def utc_timestamp() -> str:
    return _datetime.datetime.now(_datetime.timezone.utc).isoformat(
        timespec="milliseconds"
    ).replace("+00:00", "Z")


def finops_warn(error: Exception) -> None:
    global FINOPS_WARNING_EMITTED
    if FINOPS_WARNING_EMITTED:
        return
    FINOPS_WARNING_EMITTED = True
    print(f"  {YELLOW}FinOps telemetry disabled: {error}{RESET}")


def finops_open() -> sqlite3.Connection | None:
    if not FINOPS_ENABLED:
        return None
    connection: sqlite3.Connection | None = None
    try:
        FINOPS_DB.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(FINOPS_DB), timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                project TEXT NOT NULL,
                source_project TEXT,
                model TEXT,
                provider TEXT,
                status TEXT DEFAULT 'running',
                dry_run INTEGER DEFAULT 0,
                phases_total INTEGER DEFAULT 0,
                executed_count INTEGER DEFAULT 0,
                skipped_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                aborted_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS usage (
                message_id TEXT PRIMARY KEY,
                ts TEXT,
                session_id TEXT,
                project TEXT,
                model TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cache_read_tokens INTEGER DEFAULT 0,
                cache_write_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0,
                phase TEXT,
                agent TEXT,
                source_project TEXT,
                status TEXT,
                estimated INTEGER DEFAULT 0,
                provider TEXT,
                stop_reason TEXT,
                continuations INTEGER DEFAULT 0,
                duration_ms INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS tool_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                session_id TEXT,
                project TEXT,
                phase TEXT,
                agent TEXT,
                source_project TEXT,
                status TEXT,
                input_chars INTEGER DEFAULT 0,
                output_chars INTEGER DEFAULT 0,
                est_tokens INTEGER DEFAULT 0,
                duration_ms INTEGER DEFAULT 0,
                artifacts INTEGER DEFAULT 0,
                validation_ok INTEGER,
                headroom INTEGER
            );
            """
        )
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(tool_events)")
        }
        if "headroom" not in columns:
            connection.execute("ALTER TABLE tool_events ADD COLUMN headroom INTEGER")
        return connection
    except Exception as error:
        if connection is not None:
            connection.close()
        finops_warn(error)
        return None


def finops_cost(usage: dict[str, int]) -> float:
    prices = model_prices()
    return round(
        (
            usage.get("input", 0) * prices["input"]
            + usage.get("output", 0) * prices["output"]
            + usage.get("cache_read", 0) * prices["cache_read"]
            + usage.get("cache_write", 0) * prices["cache_write"]
        )
        / 1_000_000,
        6,
    )


def finops_start(project: str, phases_total: int, dry_run: bool) -> None:
    global FINOPS_SESSION_ID, FINOPS_PROJECT, FINOPS_STARTED, FINOPS_FINISHED
    global FINOPS_SOURCE_PROJECT
    FINOPS_SESSION_ID = str(uuid.uuid4())
    FINOPS_PROJECT = f"ava-data-fabric-{project}"
    FINOPS_SOURCE_PROJECT = project
    FINOPS_STARTED = bool(project)
    FINOPS_FINISHED = False
    if not FINOPS_STARTED:
        return
    connection = finops_open()
    if connection is None:
        return
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO pipeline_runs (
                    run_id, started_at, project, source_project, model, provider,
                    status, dry_run, phases_total
                ) VALUES (?, ?, ?, ?, ?, ?, 'running', ?, ?)
                """,
                (
                    FINOPS_SESSION_ID,
                    utc_timestamp(),
                    FINOPS_PROJECT,
                    project,
                    DEPLOYMENT,
                    PROVIDER,
                    int(dry_run),
                    phases_total,
                ),
            )
    except Exception as error:
        finops_warn(error)
    finally:
        connection.close()


def finops_usage(
    phase: str,
    agent: str,
    usage: dict[str, int],
    status: str,
    stop_reason: str = "",
    continuations: int = 0,
    elapsed_s: float = 0.0,
    estimated: bool = False,
) -> None:
    if not FINOPS_STARTED:
        return
    connection = finops_open()
    if connection is None:
        return
    try:
        with connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO usage (
                    message_id, ts, session_id, project, model, input_tokens,
                    output_tokens, cache_read_tokens, cache_write_tokens, cost_usd,
                    phase, agent, source_project, status, estimated, provider,
                    stop_reason, continuations, duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{FINOPS_SESSION_ID}:{phase}:{uuid.uuid4().hex}",
                    utc_timestamp(),
                    FINOPS_SESSION_ID,
                    FINOPS_PROJECT,
                    DEPLOYMENT,
                    usage.get("input", 0),
                    usage.get("output", 0),
                    usage.get("cache_read", 0),
                    usage.get("cache_write", 0),
                    finops_cost(usage),
                    phase,
                    agent,
                    FINOPS_SOURCE_PROJECT,
                    status,
                    int(estimated),
                    PROVIDER,
                    stop_reason,
                    continuations,
                    int(max(elapsed_s, 0.0) * 1000),
                ),
            )
    except Exception as error:
        finops_warn(error)
    finally:
        connection.close()


def finops_event(
    phase: str,
    agent: str,
    status: str,
    input_chars: int = 0,
    output_chars: int = 0,
    estimated_tokens: int = 0,
    elapsed_s: float = 0.0,
    artifacts: int = 0,
    validation_ok: bool | None = None,
    headroom: bool | None = None,
) -> None:
    if not FINOPS_STARTED:
        return
    connection = finops_open()
    if connection is None:
        return
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO tool_events (
                    ts, session_id, project, phase, agent, source_project, status,
                    input_chars, output_chars, est_tokens, duration_ms, artifacts,
                    validation_ok, headroom
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_timestamp(),
                    FINOPS_SESSION_ID,
                    FINOPS_PROJECT,
                    phase,
                    agent,
                    FINOPS_SOURCE_PROJECT,
                    status,
                    input_chars,
                    output_chars,
                    estimated_tokens,
                    int(max(elapsed_s, 0.0) * 1000),
                    artifacts,
                    None if validation_ok is None else int(validation_ok),
                    None if headroom is None else int(headroom),
                ),
            )
    except Exception as error:
        finops_warn(error)
    finally:
        connection.close()


def _write_consolidated_html_report(
    project: str,
    run: sqlite3.Row,
    totals: sqlite3.Row,
    phase_rows: list[sqlite3.Row],
    tool_rows: list[sqlite3.Row],
    phase_snapshot: dict[str, dict[str, Any]],
    active_steps: list[dict[str, Any]],
) -> Path | None:
    """Write the runner-13-style consolidated HTML and phase visual asset."""
    report_dir = PROJECTS_ROOT / project / "outputs" / "summary"
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = report_dir / f"finops-report_{stamp}.html"
    summary_report = report_dir / f"AVA-FABRIC-SUMMARY-{project}-{stamp}.html"
    context_svg = report_dir / "context-by-phase.svg"
    escape = _html.escape

    event_by_phase: dict[str, sqlite3.Row] = {}
    for row in tool_rows:
        event_by_phase[str(row["phase"])] = row

    context_rows: list[dict[str, Any]] = []
    for step in active_steps:
        phase = str(step["phase"])
        metric = phase_snapshot.get(phase, {})
        event = event_by_phase.get(phase)
        raw_status = str(event["status"]) if event is not None else (
            "executed" if metric else "pending"
        )
        status = "completed" if raw_status == "response_received" else raw_status
        input_tokens = int(
            metric.get("inp_tokens", 0)
            + metric.get("cache_read", 0)
            + metric.get("cache_write", 0)
        )
        output_max = int(metric.get("out_max", 0))
        baseline = int(metric.get("baseline_tokens", 0))
        usage_pct = float(metric.get("ctx_pct", 0.0))
        compression = (
            max(0.0, (baseline - input_tokens) / baseline * 100)
            if baseline else 0.0
        )
        context_rows.append({
            "phase": phase,
            "agent": str(step.get("agent", "")),
            "status": status,
            "input": input_tokens,
            "output_max": output_max,
            "total": input_tokens + output_max,
            "usage_pct": usage_pct,
            "validation": "PASS" if metric.get("val_ok", True) else "FAIL",
            "headroom": (
                "on" if (
                    metric.get("headroom") is True
                    or (
                        "headroom" not in metric
                        and event is not None
                        and event["headroom"] == 1
                    )
                ) else "off" if (
                    metric.get("headroom") is False
                    or (
                        "headroom" not in metric
                        and event is not None
                        and event["headroom"] == 0
                    )
                ) else "n/a"
            ),
            "compression": compression,
            "artifacts": int(metric.get("artifacts", 0)),
        })

    if not context_rows:
        context_rows = [
            {
                "phase": str(row["phase"]),
                "agent": str(row["agent"]),
                "status": str(row["status"]),
                "input": int(row["input_tokens"] or 0),
                "output_max": 0,
                "total": int(row["input_tokens"] or 0),
                "usage_pct": 0.0,
                "validation": "PASS",
                "headroom": "off",
                "compression": 0.0,
                "artifacts": 0,
            }
            for row in phase_rows
        ]

    output_root = PROJECTS_ROOT / project / "outputs"
    all_artifacts = [
        path for path in output_root.rglob("*")
        if path.is_file() and "pipeline_runner" not in path.parts
    ] if output_root.exists() else []
    folder_counts: dict[str, int] = {}
    for artifact in all_artifacts:
        relative = artifact.relative_to(output_root)
        folder = relative.parts[0] if relative.parts else "."
        folder_counts[folder] = folder_counts.get(folder, 0) + 1

    ast_manifest: dict[str, Any] = {}
    ast_model: dict[str, Any] = {}
    manifest_path = output_root / "upstream" / "ast" / "manifest.json"
    model_path = output_root / "upstream" / "canonical-model.json"
    try:
        if manifest_path.exists():
            ast_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if model_path.exists():
            ast_model = json.loads(model_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        ast_manifest = {}
        ast_model = {}
    ast_coverage = float(
        ast_model.get("ast_coverage", ast_manifest.get("ast_coverage", 0.0)) or 0.0
    )
    if ast_coverage <= 1:
        ast_coverage *= 100
    ast_errors = len(ast_model.get("parse_errors", []) or [])

    gate_rows: list[dict[str, str]] = []
    for gate, area in ((1, "upstream"), (2, "midstream"), (3, "downstream")):
        decision_path = output_root / area / f"gate{gate}-decision.md"
        decision = "NOT RECORDED"
        if decision_path.exists():
            text = decision_path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"^\*\*Decision:\*\*\s*(.+)$", text, re.MULTILINE)
            if match:
                decision = match.group(1).strip()
        gate_rows.append({"gate": f"Gate {gate}", "decision": decision})

    status_class = "ok" if str(run["status"]) == "completed" else "critical"
    phase_html = []
    for row in context_rows:
        phase_status = escape(row["status"])
        phase_html.append(
            "<tr>"
            f"<td><strong>{escape(row['phase'])}</strong></td>"
            f"<td>{escape(row['agent'])}</td>"
            f"<td><span class=\"badge {('ok' if row['status'] in {'completed', 'dry-run', 'executed'} else 'critical')}\">{phase_status}</span></td>"
            f"<td>{row['input']:,}</td><td>{row['output_max']:,}</td>"
            f"<td>{row['total']:,}</td><td>{row['usage_pct']:.1f}%</td>"
            f"<td>{escape(row['validation'])}</td><td>{escape(row['headroom'])}</td>"
            f"<td>{row['compression']:.1f}%</td><td>{row['artifacts']}</td>"
            "</tr>"
        )
    phase_html_text = "\n".join(phase_html) or (
        '<tr><td colspan="11" class="empty">No phase data recorded.</td></tr>'
    )

    usage_html = []
    for row in phase_rows:
        usage_html.append(
            "<tr>"
            f"<td>{escape(str(row['phase']))}</td>"
            f"<td>{escape(str(row['agent']))}</td>"
            f"<td>{escape(str(row['status']))}</td>"
            f"<td>{int(row['input_tokens'] or 0):,}</td>"
            f"<td>{int(row['output_tokens'] or 0):,}</td>"
            f"<td>{int(row['cache_read_tokens'] or 0):,}</td>"
            f"<td>${float(row['cost_usd'] or 0):.2f}</td>"
            f"<td>{int(row['duration_ms'] or 0)}</td>"
            "</tr>"
        )
    usage_html_text = "\n".join(usage_html) or (
        '<tr><td colspan="8" class="empty">No model usage recorded.</td></tr>'
    )
    gates_html = "".join(
        f"<tr><td><strong>{escape(row['gate'])}</strong></td><td>"
        f"<span class=\"badge {('ok' if 'APPROVED' in row['decision'].upper() or 'PASS' in row['decision'].upper() else 'critical')}\">"
        f"{escape(row['decision'])}</span></td></tr>"
        for row in gate_rows
    )
    folders_html = "".join(
        f"<tr><td>{escape(folder)}/</td><td>{count}</td></tr>"
        for folder, count in sorted(folder_counts.items())
    ) or '<tr><td colspan="2" class="empty">No artifacts found.</td></tr>'

    svg_width = 1160
    svg_height = max(120, 52 * len(context_rows) + 40)
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" role="img">',
        '<rect width="100%" height="100%" fill="#171717"/>',
        '<text x="20" y="26" fill="#f4f4f4" font-family="Segoe UI,Arial" font-size="16" font-weight="700">Context usage by phase</text>',
    ]
    for index, row in enumerate(context_rows):
        y = 48 + index * 52
        bar_width = min(760, max(0, int(float(row["usage_pct"]) * 7.6)))
        bar_color = "#54d98b" if float(row["usage_pct"]) < 70 else ("#ffbd55" if float(row["usage_pct"]) < 90 else "#ff5b5b")
        label = escape(f"{row['phase']}  {row['agent']}")
        svg_lines.extend([
            f'<text x="20" y="{y + 15}" fill="#f4f4f4" font-family="Consolas,monospace" font-size="12">{label}</text>',
            f'<rect x="300" y="{y + 4}" width="760" height="18" rx="3" fill="#303030"/>',
            f'<rect x="300" y="{y + 4}" width="{bar_width}" height="18" rx="3" fill="{bar_color}"/>',
            f'<text x="1070" y="{y + 18}" fill="#a9a9a9" font-family="Consolas,monospace" font-size="12">{float(row["usage_pct"]):.1f}%</text>',
        ])
    svg_lines.append("</svg>")
    context_svg.write_text("\n".join(svg_lines) + "\n", encoding="utf-8", newline="\n")

    css = """
:root{--orange:#ff5800;--dark:#171717;--panel:#242424;--panel2:#303030;--text:#f4f4f4;--muted:#a9a9a9;--red:#ff5b5b;--green:#54d98b;--line:#454545}
*{box-sizing:border-box}body{margin:0;background:var(--dark);color:var(--text);font:14px/1.5 'Segoe UI',Arial,sans-serif}header{background:#090909;border-bottom:3px solid var(--orange);padding:18px 28px;display:flex;align-items:center;gap:18px;position:sticky;top:0;z-index:5}.logo{background:var(--orange);color:#fff;font-size:24px;font-weight:900;padding:8px 12px;border-radius:7px}header h1{font-size:19px;margin:0}header small{display:block;color:var(--muted);font-size:11px}.layout{display:flex;min-height:calc(100vh - 78px)}nav{width:245px;background:#1e1e1e;border-right:1px solid var(--line);padding:16px 10px;flex:none}nav button{display:block;width:100%;text-align:left;background:transparent;color:var(--muted);border:0;border-left:3px solid transparent;padding:11px 13px;cursor:pointer;border-radius:4px;margin-bottom:3px}nav button:hover,nav button.active{background:#35251d;color:#fff;border-left-color:var(--orange)}main{max-width:1600px;width:100%;padding:28px 34px 60px}section{display:none}section.active{display:block}h2{font-size:24px;margin:0 0 5px}h3{font-size:16px;margin:0}.subtitle{color:var(--muted);margin:0 0 22px}.rule{height:3px;width:48px;background:var(--orange);margin:12px 0 22px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:18px 0 24px}.card,.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px}.card{padding:15px}.label{font-size:10px;text-transform:uppercase;color:var(--muted);letter-spacing:.08em}.value{font-size:26px;font-weight:700;margin-top:6px}.highlight{border-color:#a83d0b;background:#312219}.metric{color:var(--green)}.panel{margin:18px 0;overflow:hidden}.panel-head{padding:14px 17px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}.panel-body{padding:17px}table{width:100%;border-collapse:collapse;font-size:13px}th{text-align:left;text-transform:uppercase;font-size:10px;letter-spacing:.06em;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--line)}td{padding:10px 12px;border-bottom:1px solid #393939;vertical-align:top}tr:last-child td{border-bottom:0}.badge{display:inline-block;border-radius:12px;padding:3px 9px;font-size:10px;font-weight:700;white-space:nowrap}.critical{color:#fff;background:#a51f2d}.ok{color:#fff;background:#26734d}.kicker{border-left:3px solid var(--orange);background:#2b211c;padding:14px 17px;margin:0 0 22px}.empty{padding:24px;color:var(--muted);text-align:center!important}code{color:#f1c29f}img.visual{display:block;max-width:100%;background:#171717;border:1px solid var(--line);border-radius:6px;padding:8px}footer{position:fixed;right:12px;bottom:8px;color:#777;font:10px Consolas,monospace}@media(max-width:800px){.layout{display:block}nav{width:100%;display:flex;overflow:auto;padding:8px}nav button{min-width:150px}main{padding:22px 16px}header{padding:14px 16px}}
"""
    html_content = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AVA Fabric Summary - {escape(project)}</title><style>{css}</style></head>
<body><header><div class="logo">AVA</div><div><h1>AVA Fabric Summary - {escape(project)}</h1><small>Consolidated execution evidence | Run: {escape(str(run['run_id']))}</small></div><span class="badge {status_class}">{escape(str(run['status']).upper())}</span></header>
<div class="layout"><nav><button class="active" data-section="overview">Executive overview</button><button data-section="context">Context by phase</button><button data-section="usage">Usage by phase</button><button data-section="artifacts">Artifacts and AST</button><button data-section="gates">Gate decisions</button><button data-section="provenance">Provenance</button></nav><main>
<section id="overview" class="active"><h2>Consolidated execution report</h2><p class="subtitle">Runner-13-style summary for the DATA migration factory.</p><div class="rule"></div><div class="kicker"><strong>Status: <span class="metric">{escape(str(run['status']).upper())}</span>.</strong> Cost figures are reference estimates, not Foundry billing statements.</div><div class="grid"><div class="card highlight"><div class="label">Estimated cost</div><div class="value metric">${float(totals['cost_usd'] or 0):.2f}</div></div><div class="card"><div class="label">Input tokens</div><div class="value">{int(totals['input_tokens'] or 0):,}</div></div><div class="card"><div class="label">Output tokens</div><div class="value">{int(totals['output_tokens'] or 0):,}</div></div><div class="card"><div class="label">Artifacts</div><div class="value">{len(all_artifacts):,}</div></div><div class="card"><div class="label">AST coverage</div><div class="value metric">{ast_coverage:.1f}%</div></div><div class="card"><div class="label">AST parse errors</div><div class="value {'critical' if ast_errors else 'metric'}">{ast_errors}</div></div></div><div class="panel"><div class="panel-head"><h3>Execution metadata</h3><span class="badge {status_class}">{escape(str(run['status']).upper())}</span></div><div class="panel-body"><table><tbody><tr><td>Model / provider</td><td>{escape(str(run['model']))} / {escape(str(run['provider']))}</td></tr><tr><td>Started</td><td>{escape(str(run['started_at']))}</td></tr><tr><td>Finished</td><td>{escape(str(run['finished_at'] or 'n/a'))}</td></tr><tr><td>Dry-run</td><td>{'Yes' if run['dry_run'] else 'No'}</td></tr><tr><td>Phase count</td><td>{len(context_rows)}</td></tr></tbody></table></div></div></section>
<section id="context"><h2>Context usage by phase</h2><p class="subtitle">The visual equivalent of the runner-13 final context table, including the missing final analysis visual.</p><div class="rule"></div><div class="panel"><div class="panel-body"><img class="visual" src="context-by-phase.svg" alt="Context usage by phase"></div></div><div class="panel"><div class="panel-head"><h3>Phase telemetry snapshot</h3><span class="badge ok">{len(context_rows)} phase(s)</span></div><div class="panel-body" style="padding:0;overflow:auto"><table><thead><tr><th>Phase</th><th>Agent</th><th>Status</th><th>Input</th><th>OutMax</th><th>Total</th><th>Usage%</th><th>Validation</th><th>Headroom</th><th>%Comp</th><th>Arts</th></tr></thead><tbody>{phase_html_text}</tbody></table></div></div></section>
<section id="usage"><h2>Usage by phase</h2><p class="subtitle">Provider usage and estimated cost captured in telemetry.db.</p><div class="rule"></div><div class="panel"><div class="panel-body" style="padding:0;overflow:auto"><table><thead><tr><th>Phase</th><th>Agent</th><th>Status</th><th>Input</th><th>Output</th><th>Cache read</th><th>Cost</th><th>Time ms</th></tr></thead><tbody>{usage_html_text}</tbody></table></div></div></section>
<section id="artifacts"><h2>Artifacts and AST</h2><p class="subtitle">Files produced by the pipeline and deterministic source analysis.</p><div class="rule"></div><div class="grid"><div class="card"><div class="label">Source files scanned</div><div class="value">{int(ast_manifest.get('source_file_count', 0) or 0):,}</div></div><div class="card"><div class="label">SQL/HQL parsed</div><div class="value">{int(ast_manifest.get('sql_hql_file_count', 0) or 0):,}</div></div><div class="card"><div class="label">SSIS parsed</div><div class="value">{int(ast_manifest.get('ssis_file_count', 0) or 0):,}</div></div></div><div class="panel"><div class="panel-head"><h3>Artifacts by folder</h3></div><div class="panel-body"><table><thead><tr><th>Folder</th><th>Files</th></tr></thead><tbody>{folders_html}</tbody></table></div></div></section>
<section id="gates"><h2>Gate decisions</h2><p class="subtitle">Decisions read from the DATA factory gate artifacts.</p><div class="rule"></div><div class="panel"><div class="panel-body"><table><thead><tr><th>Gate</th><th>Decision</th></tr></thead><tbody>{gates_html}</tbody></table></div></div></section>
<section id="provenance"><h2>Run provenance</h2><p class="subtitle">Identifiers and report files for audit and reruns.</p><div class="rule"></div><div class="panel"><div class="panel-body"><table><tbody><tr><td>Run ID</td><td><code>{escape(str(run['run_id']))}</code></td></tr><tr><td>FinOps project</td><td><code>{escape(FINOPS_PROJECT)}</code></td></tr><tr><td>Markdown report</td><td><code>finops-report_{escape(stamp)}.md</code></td></tr><tr><td>HTML report</td><td><code>{escape(html_report.name)}</code></td></tr><tr><td>Visual asset</td><td><code>{escape(context_svg.name)}</code></td></tr><tr><td>Database</td><td><code>.claude-flow/agent-finops/telemetry.db</code></td></tr></tbody></table></div></div></section>
</main></div><footer>AVA Fabric DATA | FinOps | {escape(project)}</footer><script>document.querySelectorAll('nav button').forEach(button=>button.addEventListener('click',()=>{{document.querySelectorAll('nav button').forEach(item=>item.classList.remove('active'));document.querySelectorAll('main section').forEach(section=>section.classList.remove('active'));button.classList.add('active');document.getElementById(button.dataset.section).classList.add('active')}}));</script></body></html>"""
    html_report.write_text(html_content, encoding="utf-8", newline="\n")
    summary_report.write_text(html_content, encoding="utf-8", newline="\n")
    return html_report


def finops_finish(
    status: str,
    executed_count: int,
    skipped_count: int,
    failed_count: int,
    aborted_count: int,
    phase_snapshot: dict[str, dict[str, Any]] | None = None,
    active_steps: list[dict[str, Any]] | None = None,
) -> Path | None:
    global FINOPS_FINISHED
    if not FINOPS_STARTED or FINOPS_FINISHED:
        return None
    FINOPS_FINISHED = True
    connection = finops_open()
    if connection is None:
        return None
    try:
        with connection:
            connection.execute(
                """
                UPDATE pipeline_runs
                SET finished_at = ?, status = ?, executed_count = ?,
                    skipped_count = ?, failed_count = ?, aborted_count = ?
                WHERE run_id = ?
                """,
                (
                    utc_timestamp(),
                    status,
                    executed_count,
                    skipped_count,
                    failed_count,
                    aborted_count,
                    FINOPS_SESSION_ID,
                ),
            )
            run = connection.execute(
                "SELECT * FROM pipeline_runs WHERE run_id = ?",
                (FINOPS_SESSION_ID,),
            ).fetchone()
            totals = connection.execute(
                """
                SELECT COUNT(*) AS rows_count,
                       COALESCE(SUM(input_tokens), 0) AS input_tokens,
                       COALESCE(SUM(output_tokens), 0) AS output_tokens,
                       COALESCE(SUM(cache_read_tokens), 0) AS cache_read_tokens,
                       COALESCE(SUM(cache_write_tokens), 0) AS cache_write_tokens,
                       COALESCE(SUM(cost_usd), 0) AS cost_usd
                FROM usage WHERE session_id = ?
                """,
                (FINOPS_SESSION_ID,),
            ).fetchone()
            phase_rows = connection.execute(
                """
                SELECT phase, agent, status, input_tokens, output_tokens,
                       cache_read_tokens, cache_write_tokens, cost_usd,
                       estimated, duration_ms, continuations
                FROM usage WHERE session_id = ? ORDER BY rowid
                """,
                (FINOPS_SESSION_ID,),
            ).fetchall()
            tool_rows = connection.execute(
                """
                SELECT phase, agent, status, duration_ms, artifacts, validation_ok, headroom
                FROM tool_events WHERE session_id = ? ORDER BY id
                """,
                (FINOPS_SESSION_ID,),
            ).fetchall()
    except Exception as error:
        finops_warn(error)
        connection.close()
        return None
    finally:
        connection.close()

    report_dir = PROJECTS_ROOT / FINOPS_SOURCE_PROJECT / "outputs" / "summary"
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = report_dir / f"finops-report_{stamp}.md"
    prices = model_prices()
    lines = [
        f"# FinOps Report - {FINOPS_PROJECT}",
        "",
        f"**Run ID:** `{FINOPS_SESSION_ID}`  ",
        f"**Status:** {status}  ",
        f"**Model/provider:** `{DEPLOYMENT}` / `{PROVIDER}`  ",
        "",
        "## Totals",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Usage rows | {totals['rows_count']} |",
        f"| Input tokens | {totals['input_tokens']:,} |",
        f"| Output tokens | {totals['output_tokens']:,} |",
        f"| Cache read | {totals['cache_read_tokens']:,} |",
        f"| Cache write | {totals['cache_write_tokens']:,} |",
        f"| Estimated cost | ${float(totals['cost_usd'] or 0):.2f} |",
        "",
        "## Reference Prices (USD per 1M tokens)",
        "",
        "| Input | Output | Cache read | Cache write |",
        "|---:|---:|---:|---:|",
        f"| ${prices['input']:.2f} | ${prices['output']:.2f} | "
        f"${prices['cache_read']:.2f} | ${prices['cache_write']:.2f} |",
        "",
        "## Usage by Phase",
        "",
        "| Phase | Agent | Status | Input | Output | Cache R | Cache W | Cost | Est. | Time ms | Cont. |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for phase_row in phase_rows:
        lines.append(
            f"| {phase_row['phase']} | {phase_row['agent']} | {phase_row['status']} | "
            f"{phase_row['input_tokens']:,} | {phase_row['output_tokens']:,} | "
            f"{phase_row['cache_read_tokens']:,} | {phase_row['cache_write_tokens']:,} | "
            f"${float(phase_row['cost_usd'] or 0):.2f} | "
            f"{'yes' if phase_row['estimated'] else 'no'} | {phase_row['duration_ms']} | "
            f"{phase_row['continuations']} |"
        )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    if run is None:
        return report
    html_report = _write_consolidated_html_report(
        FINOPS_SOURCE_PROJECT,
        run,
        totals,
        phase_rows,
        tool_rows,
        phase_snapshot or {},
        active_steps or [],
    )
    return html_report or report


@atexit.register
def finalize_finops() -> None:
    if FINOPS_STARTED and not FINOPS_FINISHED:
        finops_finish("interrupted", 0, 0, 0, 1)


@atexit.register
def shutdown_headroom() -> None:
    global HEADROOM_PROCESS
    if HEADROOM_PROCESS is not None and HEADROOM_PROCESS.poll() is None:
        try:
            HEADROOM_PROCESS.terminate()
            HEADROOM_PROCESS.wait(timeout=5)
        except (subprocess.TimeoutExpired, OSError):
            try:
                HEADROOM_PROCESS.kill()
            except OSError:
                pass
    HEADROOM_PROCESS = None


def require_yaml() -> Any:
    if _yaml is None:
        raise RunnerError("PyYAML is not installed. Run: python -m pip install pyyaml")
    return _yaml


def load_yaml(path: Path) -> dict[str, Any]:
    yaml_module = require_yaml()
    try:
        content = path.read_text(encoding="utf-8")
        loaded = yaml_module.safe_load(content) or {}
    except OSError as error:
        raise RunnerError(f"Unable to read YAML: {path}: {error}") from error
    except Exception as error:
        raise RunnerError(f"Invalid YAML: {path}: {error}") from error
    if not isinstance(loaded, dict):
        raise RunnerError(f"Expected a YAML mapping in {path}")
    return loaded


def path_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(WORKSPACE).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_wave_config(args: argparse.Namespace) -> tuple[str, Path, Path, dict[str, Any]]:
    if args.wave_config:
        config_path = Path(args.wave_config).expanduser()
        if not config_path.is_absolute():
            config_path = WORKSPACE / config_path
        config_path = config_path.resolve()
    elif args.project:
        config_path = (PROJECTS_ROOT / args.project / "wave-config.yaml").resolve()
    else:
        available = (
            sorted(
                path.name
                for path in PROJECTS_ROOT.iterdir()
                if path.is_dir() and not path.name.startswith("_")
            )
            if PROJECTS_ROOT.exists()
            else []
        )
        if not available:
            raise RunnerError(
                "No project found. Provide --project and create "
                "projects/<project>/wave-config.yaml first."
            )
        print("\nProjects available:")
        for index, project_name in enumerate(available, 1):
            print(f"  {index}. {project_name}")
        selected = safe_input("Select project [number or name]: ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(available):
            selected = available[int(selected) - 1]
        if not selected:
            raise RunnerError("Project name cannot be empty")
        config_path = (PROJECTS_ROOT / selected / "wave-config.yaml").resolve()

    if not path_inside(config_path, WORKSPACE):
        raise RunnerError("wave-config.yaml must be inside the repository")
    if not config_path.is_file():
        raise RunnerError(f"wave-config.yaml not found: {config_path}")

    config = load_yaml(config_path)
    project_name = str(config.get("project_name") or "").strip()
    if not project_name:
        raise RunnerError("wave-config.yaml must define project_name")
    if Path(project_name).name != project_name or project_name in {".", ".."}:
        raise RunnerError(f"Invalid project_name: {project_name}")
    if args.project and args.project != project_name:
        raise RunnerError(
            f"--project '{args.project}' does not match project_name '{project_name}'"
        )

    project_root = (PROJECTS_ROOT / project_name).resolve()
    if not path_inside(project_root, WORKSPACE):
        raise RunnerError("Project path must remain inside projects/")
    if not project_root.is_dir():
        raise RunnerError(f"Project directory not found: {project_root}")
    return project_name, config_path, project_root, config


def validate_wave(config_path: Path) -> Any:
    try:
        from src.shared.scripts.validate_wave_config import validate_wave_config
    except ImportError as error:
        raise RunnerError(f"Cannot load wave validator: {error}") from error
    result = validate_wave_config(config_path)
    print(result)
    return result


def resolve_agent_file(agent_name: str) -> Path | None:
    stub_path = WORKSPACE / ".github" / "agents" / f"{agent_name}.chatmode.md"
    if stub_path.exists():
        stub_text = stub_path.read_text(encoding="utf-8", errors="ignore")
        target_match = re.search(r"@file\s+([^\r\n]+)", stub_text)
        if target_match:
            target_path = (WORKSPACE / target_match.group(1).strip()).resolve()
            if path_inside(target_path, WORKSPACE) and target_path.exists():
                return target_path
    fallback = AGENT_FALLBACK_FILES.get(agent_name)
    if fallback:
        fallback_path = (WORKSPACE / fallback).resolve()
        if fallback_path.exists():
            return fallback_path
    return None


def load_agent(agent_name: str) -> str:
    agent_path = resolve_agent_file(agent_name)
    if agent_path is None:
        return f"[Agent definition not found for {agent_name}]"
    content = agent_path.read_text(encoding="utf-8", errors="ignore")
    print(f"  {DIM}[agent] {agent_path.relative_to(WORKSPACE)} ({len(content) // 1024} KB){RESET}")
    return content[:CTX_SKILL]


def phase_contract(step: dict[str, Any]) -> str:
    required = step.get("required", [])
    gate = step.get("gate")
    if gate:
        required = GATE_ARTIFACTS[gate]
    if not required:
        required_text = "No single mandatory artifact for this step; preserve the agent's useful outputs."
    else:
        required_text = "\n".join(f"- {path}" for path in required)
    area = step.get("area", project_area(step["phase"]))
    return (
        f"Canonical phase output root: projects/{{project}}/outputs/{area}/\n"
        f"Required artifacts for this step:\n{required_text}"
    )


def artifact_priority(path: Path, phase: str) -> tuple[int, float]:
    relative = str(path).replace("\\", "/")
    if phase.startswith("U") or phase == "G1":
        preferred = ("/upstream/",)
    elif phase.startswith("M") or phase == "G2":
        preferred = ("/midstream/", "/upstream/")
    else:
        preferred = ("/downstream/", "/midstream/", "/upstream/")
    rank = next(
        (index for index, marker in enumerate(preferred) if marker in relative),
        len(preferred),
    )
    try:
        modified = path.stat().st_mtime
    except OSError:
        modified = 0.0
    return rank, -modified


def resolve_config_path(project_root: Path, config: dict[str, Any], key: str, default: str) -> Path:
    value = str(config.get(key, default)).format(
        project_name=project_root.name,
    )
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = WORKSPACE / candidate
    return candidate.resolve()


def resolve_source_path(project_root: Path, config: dict[str, Any]) -> Path | None:
    source_config = config.get("source") or {}
    configured = ""
    if isinstance(source_config, dict):
        configured = str(source_config.get("legacy_path") or "").strip()
    if not configured:
        configured = str(config.get("legacy_path") or "").strip()
    if not configured:
        return None

    raw_path = Path(configured).expanduser()
    candidates: list[Path] = []
    if raw_path.is_absolute():
        candidates.append(raw_path)
    elif configured.replace("\\", "/").startswith("projects/"):
        candidates.append(WORKSPACE / raw_path)
        candidates.append(project_root / raw_path)
    else:
        candidates.append(project_root / raw_path)
        candidates.append(WORKSPACE / raw_path)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve() if candidates else None


def load_legacy_context(project_root: Path, config: dict[str, Any], phase: str) -> str:
    source_root = resolve_source_path(project_root, config)
    if source_root is None:
        return ""
    if not source_root.exists():
        print(f"  {YELLOW}[source] legacy path not found: {source_root}{RESET}")
        return ""
    source_files = [path for path in source_root.rglob("*") if path.is_file()]
    if not source_files:
        print(f"  {YELLOW}[source] legacy path is empty: {source_root}{RESET}")
        return ""

    index_lines: list[str] = []
    for path in sorted(source_files)[:CTX_ARTIFACT_INDEX]:
        try:
            relative = path.relative_to(source_root).as_posix()
        except ValueError:
            relative = path.name
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        index_lines.append(f"- {relative} ({size:,} bytes)")

    text_suffixes = {
        ".cfg", ".conf", ".csv", ".dtsx", ".hql", ".ini", ".java", ".json",
        ".md", ".py", ".scala", ".sh", ".sql", ".txt", ".xml", ".yaml", ".yml",
    }
    preferred = []
    if phase in {"U3", "U4", "U5", "U6", "U7", "U8", "U9", "U10"}:
        preferred = sorted(
            [path for path in source_files if path.suffix.lower() in text_suffixes],
            key=lambda path: (path.suffix.lower(), str(path).lower()),
        )
    budget_chars = SOURCE_INJECT_BUDGET_TOKENS * CHARS_PER_TOKEN
    used_chars = 0
    injected: list[str] = []
    omitted = 0
    for path in preferred:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:SOURCE_FILE_CHARS]
        except OSError:
            continue
        if "\x00" in text or not text.strip():
            continue
        if used_chars + len(text) > budget_chars:
            omitted += 1
            continue
        used_chars += len(text)
        try:
            relative = path.relative_to(source_root).as_posix()
        except ValueError:
            relative = path.name
        injected.append(f"### legacy/{relative}\n```\n{text}\n```")

    print(
        f"  {DIM}[source] {source_root} | {len(source_files)} files | "
        f"{len(injected)} text files injected (~{used_chars // CHARS_PER_TOKEN:,} tokens)"
        + (f" | {omitted} omitted" if omitted else "")
        + RESET
    )
    source_parts = [
        f"### Legacy source index ({source_root})\n" + "\n".join(index_lines),
    ]
    if injected:
        source_parts.append("## Legacy source content\n\n" + "\n\n".join(injected))
    return "\n\n".join(source_parts)


def load_context(project_root: Path, phase: str, config: dict[str, Any]) -> str:
    parts: list[str] = []
    context_root = resolve_config_path(
        project_root,
        config,
        "context_base_path",
        f"projects/{project_root.name}/context",
    )
    wave_config = project_root / "wave-config.yaml"
    context_files = [
        wave_config,
        context_root / "project-config.yaml",
        context_root / "agent-task-config.yaml",
    ]
    for context_file in context_files:
        if context_file.is_file():
            text = context_file.read_text(encoding="utf-8", errors="ignore")
            parts.append(f"### {display_path(context_file)}\n```\n{text[:2_000_000]}\n```")

    legacy_context = load_legacy_context(project_root, config, phase)
    if legacy_context:
        parts.append(legacy_context)

    outputs_root = project_root / "outputs"
    if not outputs_root.exists():
        return "\n\n".join(parts) if parts else "[No project context available]"

    files = [
        path
        for path in outputs_root.rglob("*")
        if path.is_file() and "pipeline_runner" not in str(path)
    ]
    index = [str(path.relative_to(WORKSPACE)).replace("\\", "/") for path in sorted(files)]
    if index:
        parts.append(
            "### Existing artifacts (index only)\n"
            + "\n".join(index[:CTX_ARTIFACT_INDEX])
        )

    injectable = sorted(
        [
            path
            for path in files
            if path.suffix.lower() in {".md", ".mmd", ".yaml", ".yml", ".json"}
        ],
        key=lambda path: artifact_priority(path, phase),
    )
    budget_chars = CTX_INPUT_BUDGET_TOKENS * CHARS_PER_TOKEN
    used_chars = 0
    injected: list[str] = []
    omitted: list[str] = []
    for artifact in injectable:
        try:
            text = artifact.read_text(encoding="utf-8", errors="ignore")[:ART_INJECT_CHARS]
        except OSError:
            continue
        if not text.strip():
            continue
        if used_chars + len(text) > budget_chars:
            omitted.append(artifact.name)
            continue
        used_chars += len(text)
        injected.append(
            f"### {artifact.relative_to(WORKSPACE)}\n```\n{text}\n```"
        )
    if injected:
        parts.append("## Existing artifact content\n\n" + "\n\n".join(injected))
    status = (
        f"  {DIM}[context] {len(injected)} artifacts injected "
        f"(~{used_chars // CHARS_PER_TOKEN:,} tokens / budget {CTX_INPUT_BUDGET_TOKENS:,})"
    )
    if omitted:
        status += f"; {len(omitted)} omitted"
    print(status + RESET)
    return "\n\n".join(parts) if parts else "[No project context available]"


def build_user_prompt(
    step: dict[str, Any],
    project: str,
    wave_config_path: Path,
    config: dict[str, Any],
) -> str:
    entities = config.get("entities") or []
    entity_names = [str(entity.get("name")) for entity in entities if isinstance(entity, dict)]
    target = str(config.get("target_platform") or "not specified")
    source = config.get("source") or {}
    source_type = source.get("type", "not specified") if isinstance(source, dict) else "not specified"
    command = step["command"]
    return (
        f"@{step['agent']} {command}\n"
        f"Project: {project}\n"
        f"Wave config: {wave_config_path.relative_to(WORKSPACE).as_posix()}\n"
        f"Source platform: {source_type}\n"
        f"Target platform: {target}\n"
        f"Entities in scope: {', '.join(entity_names) or 'see wave-config.yaml'}\n"
        "Execute only this isolated step and return complete artifacts using the FILE contract."
    )


def build_system_blocks(
    step: dict[str, Any],
    agent_content: str,
    context: str,
    project: str,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    area = step.get("area", project_area(step["phase"]))
    output_root = f"projects/{project}/outputs/{area}/"
    contract = phase_contract(step).format(project=project)
    rules = f"""You are executing one isolated phase of the AVA Data Migration Factory.

ACTIVE PROJECT: {project}
WORKSPACE: {WORKSPACE}
WAVE OUTPUT ROOT: projects/{project}/outputs/
PHASE: {step['phase']} - {step['label']}

EXECUTION RULES
- Use the agent definition as domain guidance, but execute only the requested command.
- Do not call tools, shell commands, editors, or sub-agents in the response.
- Do not describe a future dispatch instead of producing the requested artifacts.
- Do not write outside projects/{project}/outputs/.
- Use UTF-8 text and LF line endings.
- Preserve evidence, assumptions, source references, and unresolved items.
- Output complete, useful content; do not use placeholders such as TODO or TBD when evidence exists.

FILE OUTPUT CONTRACT
For every file to create or update, emit exactly:
<!-- FILE: {output_root}<relative-path> -->
<complete file content>
<!-- /FILE -->

The runner writes only FILE blocks. A Markdown table or prose summary without FILE blocks is not an artifact.
Use the canonical output root above even when the agent definition mentions docs/ or another path.
Never use a path beginning with docs/, project/, or a path outside projects/{project}/outputs/.
At the end, list generated files briefly after all FILE blocks.

{contract}
"""
    runner_override = ""
    if step["phase"] == "D1":
        runner_override = f"""
## RUNNER OVERRIDE - DOWNSTREAM PACKAGE
This is the downstream packaging step. Materialize all three required areas in
this call, using complete content based on the approved midstream artifacts:
- `projects/{project}/outputs/downstream/ddl/`
- `projects/{project}/outputs/downstream/etl/`
- `projects/{project}/outputs/downstream/tests/`
The tests directory must contain runnable or directly executable test files for
the generated ETL/DDL behavior. Do not claim that tests passed unless evidence
exists; document unavailable runtime dependencies explicitly.
"""
    elif step["agent"] == "bi-semantic":
        runner_override = f"""
## RUNNER OVERRIDE - BI PACKAGE
The BI agent is optional in the generic factory, but this wave's Gate 3
contract requires the semantic package. Materialize it directly in one call
under `projects/{project}/outputs/downstream/bi/` with at least:
1. `semantic-model.yaml`
2. `dax-measures.md`
3. `dashboard-spec.md`
Use the existing data-model, metrics catalog, KPIs, analytical questions, and
governance artifacts. Do not use the agent's example `bi-outputs` path.
"""
    elif step["agent"] == "documentation":
        runner_override = f"""
## RUNNER OVERRIDE - GATE 3 DOCUMENTATION PACKAGE
Generate both required documents in this call:
- `projects/{project}/outputs/downstream/documentation/execution-runbook.md`
- `projects/{project}/outputs/downstream/documentation/quality-gate-evidence.md`
The quality evidence must faithfully summarize the existing M10 quality
artifacts, including the 83.4% formal Gate 2 score, review items, blockers,
and test coverage limitations. Never state that Gate 3 is approved unless the
local validator has approved it.
"""
    if runner_override:
        rules += "\n" + runner_override
    wave_summary = json.dumps(config, ensure_ascii=False, indent=2)[:300_000]
    agent_block = f"## AGENT OPERATING GUIDE\n\n{agent_content}"
    context_block = (
        "## WAVE CONFIG SNAPSHOT\n\n```yaml\n"
        + wave_summary
        + "\n```\n\n## PROJECT ARTIFACT CONTEXT\n\n"
        + context
    )
    blocks: list[dict[str, Any]] = [
        {"type": "text", "text": rules},
        {"type": "text", "text": agent_block},
        {"type": "text", "text": context_block},
    ]
    if ENABLE_PROMPT_CACHE:
        blocks[0]["cache_control"] = {"type": "ephemeral"}
        blocks[1]["cache_control"] = {"type": "ephemeral"}
    return blocks


def system_blocks_length(blocks: list[dict[str, Any]]) -> int:
    return sum(len(str(block.get("text", ""))) for block in blocks)


def client_base_url(client: Any) -> str:
    return str(getattr(client, "base_url", ""))


def headroom_client_url(proxy_url: str) -> str:
    return f"{proxy_url.rstrip('/')}/v1" if PROVIDER == "openai" else proxy_url.rstrip("/")


def headroom_alive(proxy_url: str) -> bool:
    if _requests is None:
        return False
    try:
        response = _requests.get(proxy_url.rstrip("/"), timeout=3)
        return response.status_code < 500
    except Exception:
        return False


def headroom_executable() -> str | None:
    if HEADROOM_EXE:
        candidate = Path(HEADROOM_EXE)
        if candidate.exists():
            return str(candidate)
    candidates = [
        WORKSPACE / ".headroom" / ".venv" / "Scripts" / "headroom.exe",
        WORKSPACE / ".headroom" / ".venv" / "bin" / "headroom",
        WORKSPACE / "src" / "shared" / "tools" / "headroom" / ".venv" / "Scripts" / "headroom.exe",
        # Reuse the exact Headroom deployment prepared by runner 13 when the
        # DATA repository is cloned beside the application factory.
        REFERENCE_RUNNER_ROOT / "src" / "shared" / "tools" / "headroom" / ".venv" / "Scripts" / "headroom.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return shutil.which("headroom")


def headroom_python() -> str:
    for candidate in HEADROOM_PYTHON_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return "python"


def configured_headroom_url() -> str:
    """Resolve the proxy URL using the same headroom_config.py as runner 13."""
    for config_path in HEADROOM_CONFIG_CANDIDATES:
        if not config_path.exists():
            continue
        try:
            result = subprocess.run(
                [headroom_python(), str(config_path), "--proxy-url"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            url = result.stdout.strip()
            if url.startswith("http"):
                return url
        except (OSError, subprocess.SubprocessError):
            continue
    return HEADROOM_PROXY_URL


def start_headroom() -> str:
    global HEADROOM_PROCESS, HEADROOM_EXTERNAL, HEADROOM_PROXY_URL
    HEADROOM_PROXY_URL = configured_headroom_url()
    if headroom_alive(HEADROOM_PROXY_URL):
        HEADROOM_EXTERNAL = True
        print(f"  {GREEN}Headroom already active at {HEADROOM_PROXY_URL}.{RESET}")
        return headroom_client_url(HEADROOM_PROXY_URL)

    executable = headroom_executable()
    if not executable:
        print(f"  {DIM}Headroom unavailable; using the Foundry endpoint directly.{RESET}")
        return ENDPOINT

    parsed = __import__("urllib.parse", fromlist=["urlparse"]).urlparse(HEADROOM_PROXY_URL)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8787
    environment = os.environ.copy()
    environment["AVA_FOUNDRY_MODEL"] = DEPLOYMENT
    if PROVIDER == "openai":
        environment["OPENAI_TARGET_API_URL"] = ENDPOINT_OPENAI
    else:
        environment["ANTHROPIC_TARGET_API_URL"] = ENDPOINT_ANTHROPIC
    try:
        HEADROOM_PROCESS = subprocess.Popen(
            [executable, "proxy", "--host", host, "--port", str(port), "--no-http2"],
            cwd=str(WORKSPACE),
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as error:
        print(f"  {YELLOW}Headroom could not start ({error}); using direct endpoint.{RESET}")
        return ENDPOINT

    for attempt in range(120):
        time.sleep(0.5)
        if headroom_alive(HEADROOM_PROXY_URL):
            print(f"  {GREEN}Headroom started (PID {HEADROOM_PROCESS.pid}).{RESET}")
            return headroom_client_url(HEADROOM_PROXY_URL)
        if attempt and attempt % 20 == 0:
            print(f"  {DIM}Waiting for Headroom... {attempt // 2}s{RESET}")
    print(f"  {YELLOW}Headroom did not respond within 60s; using direct endpoint.{RESET}")
    shutdown_headroom()
    return ENDPOINT


def build_client(api_key: str, base_url: str) -> Any:
    if PROVIDER == "openai":
        if _openai is None:
            raise RunnerError("Package 'openai' is required for --model gpt-5.6-luna")
        if base_url.rstrip("/") in {
            HEADROOM_PROXY_URL.rstrip("/"),
            f"{HEADROOM_PROXY_URL.rstrip('/')}/v1",
        }:
            return _openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=API_TIMEOUT_S,
                max_retries=API_MAX_RETRIES,
            )
        return _openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=OPENAI_API_VERSION,
            timeout=API_TIMEOUT_S,
            max_retries=API_MAX_RETRIES,
        )
    if _anthropic is None:
        raise RunnerError("Package 'anthropic' is required for the Anthropic provider")
    return _anthropic.Anthropic(
        api_key=api_key,
        base_url=base_url,
        timeout=API_TIMEOUT_S,
        max_retries=API_MAX_RETRIES,
        default_headers={"anthropic-version": "2023-06-01"},
    )


def normalize_usage(usage_object: Any) -> dict[str, int]:
    if usage_object is None:
        return {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    prompt_details = getattr(usage_object, "prompt_tokens_details", None)
    return {
        "input": int(
            getattr(usage_object, "input_tokens", None)
            or getattr(usage_object, "prompt_tokens", 0)
            or 0
        ),
        "output": int(
            getattr(usage_object, "output_tokens", None)
            or getattr(usage_object, "completion_tokens", 0)
            or 0
        ),
        "cache_read": int(
            getattr(usage_object, "cache_read_input_tokens", None)
            or getattr(prompt_details, "cached_tokens", 0)
            or 0
        ),
        "cache_write": int(
            getattr(usage_object, "cache_creation_input_tokens", 0) or 0
        ),
    }


class OpenAIUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int, cached_tokens: int):
        self.input_tokens = prompt_tokens
        self.output_tokens = completion_tokens
        self.cache_read_input_tokens = cached_tokens
        self.cache_creation_input_tokens = 0


def ping_model(client: Any) -> dict[str, int]:
    if PROVIDER == "openai":
        try:
            response = client.chat.completions.create(
                model=DEPLOYMENT,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
        except Exception as error:
            if "max_completion_tokens" in str(error):
                response = client.chat.completions.create(
                    model=DEPLOYMENT,
                    messages=[{"role": "user", "content": "ping"}],
                    max_completion_tokens=5,
                )
            else:
                raise
        return normalize_usage(getattr(response, "usage", None))
    with client.messages.stream(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=5,
    ) as stream:
        final_message = stream.get_final_message()
    return normalize_usage(getattr(final_message, "usage", None))


def stream_once_openai(
    client: Any,
    system: list[dict[str, Any]],
    messages: list[dict[str, str]],
    output_tokens: int,
) -> tuple[str, str, OpenAIUsage]:
    system_text = "\n\n".join(block["text"] for block in system)
    openai_messages = [{"role": "system", "content": system_text}] + messages
    base_kwargs = {
        "model": DEPLOYMENT,
        "messages": openai_messages,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    try:
        stream = client.chat.completions.create(
            max_tokens=output_tokens,
            temperature=TEMPERATURE,
            **base_kwargs,
        )
    except Exception as error:
        message = str(error)
        if "max_completion_tokens" in message:
            stream = client.chat.completions.create(
                max_completion_tokens=output_tokens,
                **base_kwargs,
            )
        elif "temperature" in message:
            stream = client.chat.completions.create(
                max_tokens=output_tokens,
                **base_kwargs,
            )
        else:
            raise

    accumulated = ""
    finish_reason = "unknown"
    prompt_tokens = 0
    completion_tokens = 0
    cached_tokens = 0
    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                print(delta, end="", flush=True)
                accumulated += delta
            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason
        usage_object = getattr(chunk, "usage", None)
        if usage_object:
            prompt_tokens = usage_object.prompt_tokens or prompt_tokens
            completion_tokens = usage_object.completion_tokens or completion_tokens
            details = getattr(usage_object, "prompt_tokens_details", None)
            if details is not None:
                cached_tokens = getattr(details, "cached_tokens", None) or cached_tokens

    if accumulated and prompt_tokens == 0 and completion_tokens == 0:
        prompt_tokens = sum(len(str(message.get("content") or "")) for message in openai_messages) // CHARS_PER_TOKEN
        completion_tokens = len(accumulated) // CHARS_PER_TOKEN
        if finish_reason == "unknown":
            finish_reason = "stop"
    stop_reason = "max_tokens" if finish_reason == "length" else finish_reason
    return accumulated, stop_reason, OpenAIUsage(prompt_tokens, completion_tokens, cached_tokens)


def stream_once(
    client: Any,
    system: list[dict[str, Any]],
    messages: list[dict[str, str]],
    output_tokens: int,
) -> tuple[str, str, Any]:
    if PROVIDER == "openai":
        return stream_once_openai(client, system, messages, output_tokens)
    accumulated = ""
    with client.messages.stream(
        model=DEPLOYMENT,
        system=system,
        messages=messages,
        max_tokens=output_tokens,
        temperature=TEMPERATURE,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            accumulated += text
        final_message = stream.get_final_message()
    return accumulated, final_message.stop_reason or "unknown", final_message.usage


def transient_errors() -> tuple[type[BaseException], ...]:
    if _anthropic is None:
        return (TimeoutError, ConnectionError)
    candidates = [
        getattr(_anthropic, "APIConnectionError", None),
        getattr(_anthropic, "APITimeoutError", None),
        getattr(_anthropic, "RateLimitError", None),
        getattr(_anthropic, "InternalServerError", None),
        getattr(_anthropic, "OverloadedError", None),
    ]
    return tuple(error for error in candidates if error is not None)


def stream_with_continuation(
    client: Any,
    system: list[dict[str, Any]],
    user_prompt: str,
    output_tokens: int,
) -> tuple[str, str, dict[str, int], int]:
    full_response = ""
    aggregate = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    continuations = 0
    retry_count = 0
    stop_reason = "unknown"
    while True:
        messages: list[dict[str, str]] = [{"role": "user", "content": user_prompt}]
        if full_response:
            messages.append({"role": "assistant", "content": full_response.rstrip()})
            if PROVIDER == "openai":
                messages.append(
                    {
                        "role": "user",
                        "content": "Continue exactly where you stopped; do not repeat prior content.",
                    }
                )
        try:
            chunk, stop_reason, usage_object = stream_once(
                client, system, messages, output_tokens
            )
            retry_count = 0
        except transient_errors() as error:
            retry_count += 1
            if retry_count > STREAM_RETRIES:
                raise
            wait_seconds = min(60, 5 * 2**retry_count)
            print(
                f"\n  {YELLOW}{type(error).__name__}; retry "
                f"{retry_count}/{STREAM_RETRIES} in {wait_seconds}s "
                f"(partial preserved: {len(full_response):,} chars){RESET}"
            )
            time.sleep(wait_seconds)
            continue

        full_response += chunk
        normalized = normalize_usage(usage_object)
        for key in aggregate:
            aggregate[key] += normalized[key]
        if stop_reason != "max_tokens" or continuations >= CONTINUATION_MAX:
            break
        continuations += 1
        print(
            f"\n  {CYAN}Continuation {continuations}/{CONTINUATION_MAX}; "
            f"resuming at {len(full_response):,} chars...{RESET}\n"
        )
    return full_response, stop_reason, aggregate, continuations


def normalize_artifact_path(path_text: str, project: str, area: str) -> str | None:
    cleaned = path_text.strip().strip("`\"'").replace("\\", "/")
    cleaned = re.sub(r"^\./+", "", cleaned)
    output_prefix = f"projects/{project}/outputs/"
    if cleaned.startswith(output_prefix):
        cleaned = cleaned[len(output_prefix):]
    elif cleaned.startswith("outputs/"):
        cleaned = cleaned[len("outputs/"):]
    elif cleaned.startswith("projects/"):
        return None

    if cleaned.startswith("docs/strategy/"):
        cleaned = "upstream/strategy/" + cleaned[len("docs/strategy/"):]
    elif cleaned.startswith("docs/requirements/"):
        filename = Path(cleaned).name
        requirements_area = "upstream/sttm/" if filename == "sttm.md" else "upstream/analysis/"
        cleaned = requirements_area + filename
    elif cleaned.startswith("docs/analysis/"):
        cleaned = "upstream/analysis/" + cleaned[len("docs/analysis/"):]

    if not cleaned or any(part in {"", ".", ".."} for part in Path(cleaned).parts):
        return None
    if not cleaned.startswith(("upstream/", "midstream/", "downstream/", "summary/")):
        cleaned = f"{area}/{cleaned}"
    if not cleaned.startswith(f"{area}/") and cleaned.split("/", 1)[0] not in {
        "upstream",
        "midstream",
        "downstream",
        "summary",
    }:
        return None
    return cleaned


def write_artifact(
    path_text: str,
    body: str,
    project: str,
    area: str,
    tag: str = "FILE",
) -> str | None:
    normalized = normalize_artifact_path(path_text, project, area)
    if normalized is None:
        print(f"  {YELLOW}[SKIP] Unsafe or invalid artifact path: {path_text.strip()}{RESET}")
        return None
    output_root = (PROJECTS_ROOT / project / "outputs").resolve()
    target = (output_root / normalized).resolve()
    if not path_inside(target, output_root):
        print(f"  {YELLOW}[SKIP] Artifact outside outputs/: {path_text.strip()}{RESET}")
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8", newline="\n")
    relative = display_path(target)
    selected_color = GREEN if tag == "FILE" else YELLOW
    print(f"  {selected_color}[{tag}] {relative} ({len(body):,} chars){RESET}")
    return relative


def parse_and_write_outputs(
    response: str,
    project: str,
    area: str,
) -> list[str]:
    written: list[str] = []
    seen: set[str] = set()
    for match in FILE_BLOCK.finditer(response):
        path_text = match.group(1).strip()
        if path_text in seen:
            continue
        relative = write_artifact(path_text, match.group(2), project, area)
        if relative:
            seen.add(path_text)
            written.append(relative)
    for match in FILE_OPEN.finditer(response):
        path_text = match.group(1).strip()
        body = match.group(2).rstrip()
        if path_text in seen or len(body) < 50:
            continue
        relative = write_artifact(path_text, body, project, area, "FILE-INCOMPLETE")
        if relative:
            seen.add(path_text)
            written.append(relative)
            print(
                f"  {RED}Warning: unclosed FILE block for {path_text}; "
                f"review the artifact manually.{RESET}"
            )
    if not written:
        print(f"  {YELLOW}Warning: no FILE blocks found in the response.{RESET}")
    return written


def path_matches(root: Path, pattern: str) -> bool:
    clean = pattern.rstrip("/")
    if pattern.endswith("/"):
        return (root / clean).is_dir() and any((root / clean).rglob("*"))
    return (root / clean).is_file()


def validate_phase_artifacts(
    step: dict[str, Any],
    project: str,
    written: list[str],
) -> dict[str, Any]:
    required = [str(item) for item in step.get("required", [])]
    output_root = (PROJECTS_ROOT / project / "outputs").resolve()
    disk = {
        path.relative_to(output_root).as_posix()
        for path in output_root.rglob("*")
        if path.is_file()
    } if output_root.exists() else set()
    new = {path.replace("\\", "/") for path in written}
    missing: list[str] = []
    reused: list[str] = []
    new_required: list[str] = []
    for pattern in required:
        clean = pattern.replace("\\", "/")
        if any(path == clean or path.startswith(clean.rstrip("/") + "/") for path in new):
            new_required.append(pattern)
        elif path_matches(output_root, clean):
            reused.append(pattern)
        else:
            missing.append(pattern)
    return {
        "ok": not missing,
        "produced": bool(written),
        "written_count": len(written),
        "required_new": new_required,
        "required_reused": reused,
        "required_missing": missing,
    }


def print_phase_validation(phase: str, validation: dict[str, Any]) -> None:
    if validation["ok"] and validation["produced"]:
        status = f"{GREEN}PASS{RESET}"
    elif validation["ok"]:
        status = f"{YELLOW}REUSED{RESET}"
    else:
        status = f"{RED}FAIL{RESET}"
    print(f"\n{CYAN}{'-' * 72}{RESET}")
    print(f"{BOLD}  Artifact validation - {phase} [{status}{BOLD}]{RESET}")
    print(f"{CYAN}{'-' * 72}{RESET}")
    print(f"  Files written in this execution: {validation['written_count']}")
    for artifact in validation["required_new"]:
        print(f"  {GREEN}NEW      {artifact}{RESET}")
    for artifact in validation["required_reused"]:
        print(f"  {YELLOW}REUSED   {artifact}{RESET}")
    for artifact in validation["required_missing"]:
        print(f"  {RED}MISSING  {artifact}{RESET}")


def run_gate_validation(
    gate: int,
    project: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    try:
        from src.shared.scripts.validate_gate3_artifacts import (
            validate_ast_artifacts,
            validate_gate_requirements,
        )
    except ImportError as error:
        raise RunnerError(f"Cannot load gate validator: {error}") from error

    area = {1: "upstream", 2: "midstream", 3: "downstream"}[gate]
    artifact_root = PROJECTS_ROOT / project / "outputs" / area
    artifact_result = validate_gate_requirements(gate, artifact_root)
    ast_result = validate_ast_artifacts(gate, artifact_root)
    threshold_config = config.get("gate_thresholds") or {}
    threshold = float(threshold_config.get(f"gate_{gate}", {1: 80, 2: 85, 3: 85}[gate]))
    required_total = len(GATE_ARTIFACTS[gate])
    present_count = len(artifact_result.present)
    completeness = present_count / required_total * 100 if required_total else 100.0
    passed = artifact_result.is_valid and ast_result.is_valid
    decision = "APPROVED" if passed else "BLOCKED"
    print(f"\n{artifact_result}")
    if ast_result.present or ast_result.missing:
        print(ast_result)
    print(
        f"  Gate {gate} artifact completeness: {completeness:.1f}% "
        f"(configured threshold: {threshold:.1f})"
    )
    print(f"  Decision: {GREEN if passed else RED}{decision}{RESET}")

    decision_path = artifact_root / f"gate{gate}-decision.md"
    decision_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Gate {gate} Decision - {project}",
        "",
        f"**Decision:** {decision}",
        f"**Generated:** {_datetime.datetime.now().isoformat(timespec='seconds')}",
        f"**Artifact completeness:** {completeness:.1f}%",
        f"**Configured threshold:** {threshold:.1f}",
        "",
        "> This runner validates artifact presence and AST structure. A formal GateScore "
        "> still requires measured tests, DQ, and row-parity inputs.",
        "",
        "## Required Artifacts",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]
    for artifact in GATE_ARTIFACTS[gate]:
        status = "present" if artifact in artifact_result.present else "missing"
        lines.append(f"| `{artifact}` | {status} |")
    if artifact_result.missing:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- `{artifact}`" for artifact in artifact_result.missing)
    decision_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return {
        "phase": f"G{gate}",
        "agent": "_gate_validator",
        "artifacts": present_count,
        "val_ok": passed,
        "ctx_pct": 0.0,
        "inp_tokens": 0,
        "resp_tokens": 0,
        "elapsed_s": 0.0,
        "written": [decision_path.relative_to(WORKSPACE).as_posix()],
        "gate_completeness": completeness,
    }


def _ast_output_relative(project: str, path: Path) -> str:
    return path.relative_to(PROJECTS_ROOT / project / "outputs").as_posix()


def _write_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_ast_step(
    step: dict[str, Any],
    project: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Run the DATA factory AST Engine before every model phase.

    SQL/HQL and SSIS packages are parsed locally, merged into one canonical
    wave model, enriched with column lineage/STTM, and used to generate a
    deterministic Databricks baseline. No LLM call is used in this phase.
    """
    phase_started = time.perf_counter()
    project_root = PROJECTS_ROOT / project
    source_root = resolve_source_path(project_root, config)
    output_root = project_root / "outputs"
    upstream_root = output_root / "upstream"
    ast_root = upstream_root / "ast"
    canonical_path = upstream_root / "canonical-model.json"
    manifest_path = ast_root / "manifest.json"
    target_platform = str(config.get("target_platform") or "databricks")
    source_config = config.get("source") or {}
    source_platform = (
        str(source_config.get("type") or "legacy")
        if isinstance(source_config, dict)
        else "legacy"
    )

    banner("A0 - Deterministic AST Extraction", CYAN)
    if source_root is None or not source_root.exists():
        message = f"AST source path not found: {source_root or '(not configured)'}"
        print(f"  {RED}{message}{RESET}")
        if DRY_RUN:
            print(f"  {YELLOW}[DRY-RUN] AST extraction not executed.{RESET}")
            return {
                "phase": step["phase"], "agent": step["agent"],
                "inp_tokens": 0, "resp_tokens": 0, "baseline_tokens": 0,
                "cache_read": 0, "cache_write": 0, "out_max": 0, "ctx_pct": 0.0,
                "elapsed_s": time.perf_counter() - phase_started, "artifacts": 0,
                "val_ok": True, "continuations": 0, "written": [],
            }
        raise RunnerError(message)

    source_files = [path for path in source_root.rglob("*") if path.is_file()]
    sql_files = [path for path in source_files if path.suffix.lower() in {".sql", ".hql"}]
    ssis_files = [path for path in source_files if path.suffix.lower() == ".dtsx"]
    print(
        f"  {DIM}Source: {source_root} | files={len(source_files)} | "
        f"SQL/HQL={len(sql_files)} | SSIS={len(ssis_files)}{RESET}"
    )

    if DRY_RUN:
        print(f"  {MAGENTA}[DRY-RUN] AST extraction not executed.{RESET}")
        return {
            "phase": step["phase"], "agent": step["agent"],
            "inp_tokens": 0, "resp_tokens": 0, "baseline_tokens": 0,
            "cache_read": 0, "cache_write": 0, "out_max": 0, "ctx_pct": 0.0,
            "elapsed_s": time.perf_counter() - phase_started, "artifacts": 0,
            "val_ok": True, "continuations": 0, "written": [],
        }

    if canonical_path.exists() and manifest_path.exists():
        try:
            cached = json.loads(canonical_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if (
                {"pipeline_id", "pipeline_name", "source_platform"}.issubset(cached)
                and manifest.get("source_file_count") == len(source_files)
                and manifest.get("target_platform") == target_platform
            ):
                print(f"  {GREEN}AST cache found; reusing {display_path(canonical_path)}.{RESET}")
                written = [
                    _ast_output_relative(project, path)
                    for path in output_root.rglob("*")
                    if path.is_file() and (
                        path.name in {"canonical-model.json", "column-lineage.json", "sttm.md"}
                        or "generated-code" in path.parts
                    )
                ]
                return {
                    "phase": step["phase"], "agent": step["agent"],
                    "inp_tokens": 0, "resp_tokens": 0, "baseline_tokens": 0,
                    "cache_read": 0, "cache_write": 0, "out_max": 0, "ctx_pct": 0.0,
                    "elapsed_s": time.perf_counter() - phase_started,
                    "artifacts": len(written), "val_ok": True, "continuations": 0,
                    "written": written,
                }
        except (OSError, json.JSONDecodeError):
            print(f"  {YELLOW}AST cache invalid; rebuilding deterministically.{RESET}")

    try:
        from src.shared.pipeline_ast.lineage.lineage_engine import LineageEngine
        from src.shared.pipeline_ast.model.canonical import MigrationPipeline
        from src.shared.pipeline_ast.parsers.sql_parser import SQLASTParser
        from src.shared.pipeline_ast.parsers.ssis_parser import SSISASTParser
        from src.shared.pipeline_ast.generators.databricks_generator import DatabricksGenerator
    except ImportError as error:
        raise RunnerError(f"Cannot load DATA AST Engine: {error}") from error

    aggregate = MigrationPipeline(
        pipeline_id=f"wave-{project}",
        pipeline_name=f"{project}-legacy-wave",
        source_platform=source_platform,
        target_platform=target_platform,
        metadata={
            "project": project,
            "source_root": str(source_root),
            "extraction_method": "deterministic-data-factory-ast",
        },
    )
    parse_errors: list[str] = []
    parsed_sql = parsed_ssis = 0
    coverage_values: list[float] = []

    for source_file in sorted(sql_files + ssis_files):
        relative = source_file.relative_to(source_root).as_posix()
        try:
            if source_file.suffix.lower() == ".dtsx":
                result = SSISASTParser().parse_file(
                    source_file,
                    target_platform=target_platform,
                )
                parsed_ssis += 1
            else:
                result = SQLASTParser(dialect="spark").parse_file(
                    source_file,
                    pipeline_name=source_file.stem,
                    target_platform=target_platform,
                )
                parsed_sql += 1
            parsed = result.pipeline
            coverage_values.append(float(getattr(result, "ast_coverage", 0.0) or 0.0))
            aggregate.source_tables.extend(parsed.source_tables)
            aggregate.target_tables.extend(parsed.target_tables)
            aggregate.joins.extend(parsed.joins)
            aggregate.filters.extend(parsed.filters)
            aggregate.transformations.extend(parsed.transformations)
            aggregate.nodes.extend(parsed.nodes)
            aggregate.execution_order.extend(parsed.execution_order)
            parse_errors.extend(f"{relative}: {error}" for error in parsed.parse_errors)
            parse_errors.extend(f"{relative}: {error}" for error in getattr(result, "parse_errors", []))
        except Exception as error:  # keep one malformed legacy file from hiding the rest
            parse_errors.append(f"{relative}: {type(error).__name__}: {error}")

    aggregate.ast_coverage = (
        sum(coverage_values) / len(coverage_values) if coverage_values else 0.0
    )
    aggregate.parse_errors = parse_errors
    aggregate.metadata.update({
        "source_file_count": len(source_files),
        "sql_hql_file_count": len(sql_files),
        "ssis_file_count": len(ssis_files),
        "parsed_sql_hql": parsed_sql,
        "parsed_ssis": parsed_ssis,
        "parse_error_count": len(parse_errors),
    })

    canonical_json = aggregate.to_json(indent=2)
    lineage = LineageEngine().build(aggregate)
    lineage_json = lineage.to_json(indent=2)
    sttm_md = lineage.to_sttm_md()
    generated_paths: list[Path] = []

    # Keep one canonical AST copy in every lifecycle area so every phase and
    # every AST-aware gate reads the same deterministic source of truth.
    for area in ("upstream", "midstream", "downstream"):
        area_root = output_root / area
        area_root.mkdir(parents=True, exist_ok=True)
        _write_lf(area_root / "canonical-model.json", canonical_json)
        _write_lf(area_root / "column-lineage.json", lineage_json)
        _write_lf(area_root / "sttm.md", sttm_md)
        generated_paths.extend([
            area_root / "canonical-model.json",
            area_root / "column-lineage.json",
            area_root / "sttm.md",
        ])

    _write_lf(ast_root / "canonical-model.json", canonical_json)
    _write_lf(ast_root / "column-lineage.json", lineage_json)
    _write_lf(ast_root / "sttm.md", sttm_md)
    report = (
        f"# AST Extraction Report - {project}\n\n"
        f"**Source:** `{source_root}`  \n"
        f"**Target:** `{target_platform}`  \n"
        f"**Files scanned:** {len(source_files)}  \n"
        f"**SQL/HQL parsed:** {parsed_sql}  \n"
        f"**SSIS parsed:** {parsed_ssis}  \n"
        f"**Average AST coverage:** {aggregate.ast_coverage:.1%}  \n"
        f"**Parse errors:** {len(parse_errors)}  \n"
        f"**Source tables:** {len(aggregate.source_tables)}  \n"
        f"**Target tables:** {len(aggregate.target_tables)}  \n"
        f"**Transformations:** {len(aggregate.transformations)}  \n\n"
        "The canonical model, lineage, and STTM are injected into every later "
        "pipeline phase. Parse errors remain explicitly recorded in the model.\n"
    )
    _write_lf(ast_root / "ast-extraction-report.md", report)
    manifest = {
        "engine": "src.shared.pipeline_ast",
        "source_root": str(source_root),
        "source_file_count": len(source_files),
        "sql_hql_file_count": len(sql_files),
        "ssis_file_count": len(ssis_files),
        "target_platform": target_platform,
        "canonical_model": str(canonical_path.relative_to(output_root)).replace("\\", "/"),
        "parse_error_count": len(parse_errors),
    }
    _write_lf(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False))

    generated_root = output_root / "downstream" / "generated-code"
    generated_root.mkdir(parents=True, exist_ok=True)
    generated = DatabricksGenerator().generate(aggregate).save(generated_root)
    generated_paths.extend(generated.values())
    generated_paths.extend([ast_root / "canonical-model.json", ast_root / "column-lineage.json", ast_root / "sttm.md", ast_root / "ast-extraction-report.md", manifest_path])

    written = sorted({_ast_output_relative(project, path) for path in generated_paths if path.exists()})
    print(
        f"  {GREEN}AST complete: {len(written)} artifacts, "
        f"coverage={aggregate.ast_coverage:.1%}, errors={len(parse_errors)}.{RESET}"
    )
    return {
        "phase": step["phase"], "agent": step["agent"],
        "inp_tokens": 0, "resp_tokens": 0, "baseline_tokens": 0,
        "cache_read": 0, "cache_write": 0, "out_max": 0, "ctx_pct": 0.0,
        "elapsed_s": time.perf_counter() - phase_started,
        "artifacts": len(written), "val_ok": True, "continuations": 0,
        "written": written,
    }


def save_phase_log(
    project: str,
    step: dict[str, Any],
    response: str,
    usage: dict[str, int],
    stop_reason: str,
    continuations: int,
    written: list[str],
) -> Path:
    log_dir = PROJECTS_ROOT / project / "outputs" / "pipeline_runner"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"{step['phase']}_{step['agent']}_{timestamp}.md"
    trigger = step.get("command") or "deterministic gate validation"
    content = (
        f"# {step['phase']} - {step['label']}\n\n"
        f"**Agent:** @{step['agent']}  \n"
        f"**Command:** {trigger}  \n"
        f"**Project:** {project}  \n"
        f"**Stop reason:** {stop_reason}  \n"
        f"**Continuations:** {continuations}  \n"
        f"**Tokens:** input={usage['input']:,}, output={usage['output']:,}, "
        f"cache_read={usage['cache_read']:,}, cache_write={usage['cache_write']:,}\n\n"
        "## Files written\n\n"
        + ("\n".join(f"- `{path}`" for path in written) if written else "_None_")
        + "\n\n## Response\n\n"
        + response
        + "\n"
    )
    log_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"  {GREEN}Execution log: {display_path(log_path)}{RESET}")
    return log_path


def postprocess_phase_outputs(step: dict[str, Any], project: str) -> list[str]:
    """Package existing evidence and mirror BI output for the local gate contract."""
    outputs_root = PROJECTS_ROOT / project / "outputs"
    packaged: list[str] = []

    if step["phase"] == "D4":
        bi_root = outputs_root / "downstream" / "bi"
        validator_bi_root = outputs_root / "downstream" / "downstream" / "bi"
        if bi_root.is_dir():
            for source in bi_root.rglob("*"):
                if not source.is_file():
                    continue
                target = validator_bi_root / source.relative_to(bi_root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                packaged.append(display_path(target))
            if packaged:
                print(
                    f"  {DIM}[package] mirrored {len(packaged)} BI artifact(s) "
                    f"for the repository Gate 3 validator.{RESET}"
                )

    if step["phase"] == "D5":
        quality_source = outputs_root / "midstream" / "quality" / "validation-report.md"
        quality_target = outputs_root / "downstream" / "documentation" / "quality-gate-evidence.md"
        if not quality_target.exists() and quality_source.is_file():
            quality_target.parent.mkdir(parents=True, exist_ok=True)
            source_text = quality_source.read_text(encoding="utf-8", errors="ignore")
            quality_target.write_text(
                "# Gate 3 Quality Gate Evidence\n\n"
                "This package was materialized from the M10 Quality Gate validation report. "
                "It preserves the original score, review items, blockers, and execution limitations.\n\n"
                + source_text,
                encoding="utf-8",
                newline="\n",
            )
            packaged.append(display_path(quality_target))
            print(f"  {DIM}[package] quality evidence copied from M10.{RESET}")

    return packaged


def run_llm_step(
    client: Any,
    step: dict[str, Any],
    project: str,
    wave_config_path: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    phase_started = time.perf_counter()
    agent_content = load_agent(step["agent"])
    context = load_context(PROJECTS_ROOT / project, step["phase"], config)
    system_blocks = build_system_blocks(step, agent_content, context, project, config)
    user_prompt = build_user_prompt(step, project, wave_config_path, config)
    baseline_chars = system_blocks_length(system_blocks) + len(user_prompt)
    baseline_tokens = baseline_chars // CHARS_PER_TOKEN
    output_tokens = MAX_TOKENS
    headroom_on = ENDPOINT not in client_base_url(client)
    print(f"\n{DIM}Sending: {user_prompt}{RESET}")
    print(
        f"{DIM}baseline~{baseline_tokens:,} tokens  out_max={output_tokens:,}  "
        f"window={(baseline_tokens + output_tokens) / CTX_WINDOW * 100:.1f}%  "
        f"cache={'on' if ENABLE_PROMPT_CACHE else 'off'}  "
        f"headroom={'on' if headroom_on else 'off'}{RESET}"
    )

    if DRY_RUN:
        usage = {"input": baseline_tokens, "output": 0, "cache_read": 0, "cache_write": 0}
        estimated_cost = baseline_tokens * model_prices()["input"] / 1_000_000
        print(
            f"  {MAGENTA}[DRY-RUN] No API call. Estimated input: "
            f"{baseline_tokens:,} tokens (${estimated_cost:.2f}).{RESET}"
        )
        finops_usage(
            step["phase"],
            step["agent"],
            usage,
            "dry-run",
            stop_reason="dry-run",
            estimated=True,
        )
        finops_event(
            step["phase"],
            step["agent"],
            "dry-run",
            input_chars=baseline_chars,
            estimated_tokens=baseline_tokens,
            headroom=headroom_on,
        )
        save_phase_log(project, step, "[dry-run: response not requested]", usage, "dry-run", 0, [])
        return {
            "phase": step["phase"],
            "agent": step["agent"],
            "inp_tokens": baseline_tokens,
            "resp_tokens": 0,
            "baseline_tokens": baseline_tokens,
            "cache_read": 0,
            "cache_write": 0,
            "out_max": output_tokens,
            "ctx_pct": (baseline_tokens + output_tokens) / CTX_WINDOW * 100,
            "elapsed_s": time.perf_counter() - phase_started,
            "artifacts": 0,
            "val_ok": True,
            "continuations": 0,
            "headroom": headroom_on,
            "written": [],
        }

    try:
        response, stop_reason, usage, continuations = stream_with_continuation(
            client, system_blocks, user_prompt, output_tokens
        )
    except Exception:
        finops_event(
            step["phase"],
            step["agent"],
            "failed",
            input_chars=baseline_chars,
            elapsed_s=time.perf_counter() - phase_started,
        )
        raise

    elapsed_s = time.perf_counter() - phase_started
    finops_usage(
        step["phase"],
        step["agent"],
        usage,
        "response_received",
        stop_reason=stop_reason,
        continuations=continuations,
        elapsed_s=elapsed_s,
    )
    print(f"\n{CYAN}{'-' * 72}{RESET}")
    if stop_reason == "max_tokens":
        print(
            f"{RED}Warning: response remains truncated after "
            f"{CONTINUATION_MAX} continuations.{RESET}"
        )
    written = parse_and_write_outputs(response, project, step.get("area", "summary"))
    for packaged_path in postprocess_phase_outputs(step, project):
        if packaged_path not in written:
            written.append(packaged_path)
    validation = validate_phase_artifacts(step, project, written)
    print_phase_validation(step["phase"], validation)
    save_phase_log(
        project,
        step,
        response,
        usage,
        stop_reason,
        continuations,
        written,
    )
    finops_event(
        step["phase"],
        step["agent"],
        "completed" if validation["ok"] else "validation_failed",
        input_chars=baseline_chars,
        output_chars=len(response),
        estimated_tokens=sum(usage.values()),
        elapsed_s=elapsed_s,
        artifacts=len(written),
        validation_ok=validation["ok"],
        headroom=headroom_on,
    )
    return {
        "phase": step["phase"],
        "agent": step["agent"],
        "inp_tokens": usage["input"],
        "resp_tokens": usage["output"],
        "baseline_tokens": baseline_tokens,
        "cache_read": usage["cache_read"],
        "cache_write": usage["cache_write"],
        "out_max": output_tokens,
        "ctx_pct": (
            usage["input"]
            + usage["cache_read"]
            + usage["cache_write"]
            + output_tokens
        )
        / CTX_WINDOW
        * 100,
        "elapsed_s": elapsed_s,
        "artifacts": len(written),
        "val_ok": validation["ok"],
        "continuations": continuations,
        "headroom": headroom_on,
        "written": written,
    }


def run_step(
    client: Any,
    step: dict[str, Any],
    project: str,
    wave_config_path: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    if step["agent"] == "_ast_engine":
        result = run_ast_step(step, project, config)
        finops_event(
            step["phase"],
            step["agent"],
            "completed" if result["val_ok"] else "validation_failed",
            artifacts=result["artifacts"],
            elapsed_s=result["elapsed_s"],
            validation_ok=result["val_ok"],
        )
        save_phase_log(
            project,
            step,
            "Deterministic AST extraction completed locally.",
            {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0},
            "local_ast",
            0,
            result.get("written", []),
        )
        return result
    if step.get("gate"):
        started = time.perf_counter()
        result = run_gate_validation(step["gate"], project, config)
        result["elapsed_s"] = time.perf_counter() - started
        finops_event(
            step["phase"],
            step["agent"],
            "completed" if result["val_ok"] else "validation_failed",
            artifacts=result["artifacts"],
            elapsed_s=result["elapsed_s"],
            validation_ok=result["val_ok"],
        )
        return result
    return run_llm_step(client, step, project, wave_config_path, config)


def state_path(project: str) -> Path:
    return PROJECTS_ROOT / project / "outputs" / "pipeline_runner" / "run-state.json"


def load_state(project: str) -> dict[str, Any]:
    path = state_path(project)
    if not path.exists():
        return {"completed": [], "failed": []}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"completed": [], "failed": []}
    return loaded if isinstance(loaded, dict) else {"completed": [], "failed": []}


def save_state(project: str, state: dict[str, Any]) -> None:
    path = state_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _datetime.datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(state, indent=2), encoding="utf-8", newline="\n")


def status_bar(
    active_steps: list[dict[str, Any]],
    index: int,
    executed: list[str],
    skipped: list[str],
    failed: list[str],
) -> str:
    parts: list[str] = []
    for step_index, step in enumerate(active_steps):
        phase = step["phase"]
        if phase in executed:
            parts.append(f"{GREEN}OK:{phase}{RESET}")
        elif phase in failed:
            parts.append(f"{RED}FAIL:{phase}{RESET}")
        elif phase in skipped:
            parts.append(f"{YELLOW}SKIP:{phase}{RESET}")
        elif step_index == index:
            parts.append(f"{CYAN}{BOLD}>{phase}{RESET}")
        else:
            parts.append(f"{DIM}..:{phase}{RESET}")
    return "  " + "  ".join(parts)


def ask_permission(
    step: dict[str, Any],
    index: int,
    total: int,
    automatic: bool,
    active_steps: list[dict[str, Any]],
    executed: list[str],
    skipped: list[str],
    failed: list[str],
) -> str:
    print(f"\n{YELLOW}{'=' * 72}{RESET}")
    print(f"{YELLOW}{BOLD}  Step {index + 1}/{total} - {step['phase']}{RESET}")
    print(f"{YELLOW}  {step['label']}{RESET}")
    print(f"{DIM}  Agent: @{step['agent']}{RESET}")
    if step.get("command"):
        print(f"{DIM}  Command: {step['command']}{RESET}")
    print(f"{YELLOW}{'=' * 72}{RESET}")
    print(status_bar(active_steps, index, executed, skipped, failed))
    if automatic:
        print(f"  {DIM}[AUTO] Executando automaticamente...{RESET}")
        return "S"
    while True:
        response = safe_input(
            f"\n  {BOLD}Executar? [S]im / [T]odos / [P]ular / [V]er skill / [A]bortar: {RESET}",
            "S",
        ).strip().upper()
        if response in {"", "S"}:
            return "S"
        if response == "T":
            return "T"
        if response in {"P", "N"}:
            return "P"
        if response == "V":
            return "V"
        if response == "A":
            return "A"
        print(f"  {RED}Digite S, T, P, V ou A.{RESET}")


def show_skill_preview(step: dict[str, Any]) -> None:
    if step["agent"] == "_gate_validator":
        print(f"\n{DIM}Deterministic local gate validator; no model prompt is sent.{RESET}")
        return
    content = load_agent(step["agent"])
    print(f"\n{DIM}{textwrap.fill(content[:2_000], width=100)}{RESET}")
    if len(content) > 2_000:
        print(f"{DIM}[preview truncated; {len(content):,} chars total]{RESET}")


def resolve_project(args: argparse.Namespace) -> str:
    """Resolve a project with the same interactive menu used by runner 13."""
    if args.project:
        return args.project
    if args.wave_config:
        return Path(args.wave_config).expanduser().resolve().parent.name

    projects = sorted(
        path.name
        for path in PROJECTS_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    ) if PROJECTS_ROOT.exists() else []
    if not projects:
        raise RunnerError("No projects found under projects/")

    print(f"\n{BOLD}Projetos disponíveis:{RESET}")
    for index, project in enumerate(projects, 1):
        print(f"  {CYAN}{index}.{RESET} {project}")
    print(f"  {CYAN}{len(projects) + 1}.{RESET} Digitar nome manualmente")
    raw = safe_input(
        f"\n{BOLD}Selecione o projeto [número ou nome]: {RESET}",
        default=projects[0],
    ).strip()
    if raw.isdigit():
        index = int(raw) - 1
        if index == len(projects):
            raw = safe_input("  Nome do projeto: ").strip()
        elif 0 <= index < len(projects):
            raw = projects[index]
        else:
            raise RunnerError("Seleção de projeto inválida")
    if not raw:
        raise RunnerError("Nome do projeto não pode ser vazio")
    return raw


def resolve_steps(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str]:
    def with_ast(selected: set[str]) -> set[str]:
        if AST_ENABLED and selected and selected != {"A0"}:
            selected.add(AST_PHASE)
        return selected

    if args.phases is None:
        print(f"\n{BOLD}Modo de execução:{RESET}")
        print(f"  {CYAN}1.{RESET} Full Pipeline  (todas as {len(PIPELINE)} etapas)")
        print(f"  {CYAN}2.{RESET} Por Fase       (selecionar grupos de fases)")
        mode = safe_input(
            f"\n{BOLD}Escolha [1/2]: {RESET}",
            default="1",
        ).strip()
        if mode != "2":
            return PIPELINE, "Full Pipeline"

        group_keys = list(PHASE_MENU_GROUPS)
        print(f"\n{BOLD}Fases disponíveis (múltipla seleção, ex: 1 3):{RESET}")
        for index, key in enumerate(group_keys, 1):
            label, phases = PHASE_MENU_GROUPS[key]
            print(f"  {CYAN}{index}.{RESET} {label}")
            print(f"     {DIM}{', '.join(phases)}{RESET}")
        selected: set[str] = set()
        raw_selection = safe_input(
            f"\n{BOLD}Números das fases (ex: 2 4 6): {RESET}",
            default="1 2 3 4 5 6 7",
        ).strip()
        for token in raw_selection.split():
            if token.isdigit() and 1 <= int(token) <= len(group_keys):
                selected.update(PHASE_MENU_GROUPS[group_keys[int(token) - 1]][1])
        if not selected:
            raise RunnerError("Nenhuma fase selecionada")
        selected = with_ast(selected)
        steps = [step for step in PIPELINE if step["phase"] in selected]
        return steps, "Fases selecionadas: " + ", ".join(step["phase"] for step in steps)

    selected: set[str] = set()
    for token in args.phases:
        key = token.upper()
        if key in PHASE_GROUPS:
            selected.update(PHASE_GROUPS[key])
        elif any(step["phase"] == key for step in PIPELINE):
            selected.add(key)
        else:
            print(f"{YELLOW}Warning: unknown phase/group ignored: {token}{RESET}")
    if not selected:
        return PIPELINE, "Full Pipeline"
    selected = with_ast(selected)
    steps = [step for step in PIPELINE if step["phase"] in selected]
    return steps, "Selected phases: " + ", ".join(step["phase"] for step in steps)


def _snapshot_from_telemetry(
    phase_rows: list[sqlite3.Row],
    tool_rows: list[sqlite3.Row],
) -> dict[str, dict[str, Any]]:
    events = {str(row["phase"]): row for row in tool_rows}

    snapshot: dict[str, dict[str, Any]] = {}
    for row in phase_rows:
        phase = str(row["phase"])
        if phase == "AUTH":
            continue
        event = events.get(phase)
        input_tokens = int(row["input_tokens"] or 0)
        cache_read = int(row["cache_read_tokens"] or 0)
        cache_write = int(row["cache_write_tokens"] or 0)
        total_input = input_tokens + cache_read + cache_write
        output_max = 0 if phase in {"A0", "G1", "G2", "G3"} else MAX_TOKENS
        snapshot[phase] = {
            "inp_tokens": input_tokens,
            "cache_read": cache_read,
            "cache_write": cache_write,
            "out_max": output_max,
            "ctx_pct": (total_input + output_max) / CTX_WINDOW * 100,
            "baseline_tokens": (
                int(event["input_chars"] or 0) // CHARS_PER_TOKEN
                if event is not None else 0
            ),
            "resp_tokens": int(row["output_tokens"] or 0),
            "elapsed_s": (
                int(event["duration_ms"] or 0) / 1000
                if event is not None else 0.0
            ),
            "artifacts": int(event["artifacts"] or 0) if event is not None else 0,
            "val_ok": (
                bool(event["validation_ok"])
                if event is not None and event["validation_ok"] is not None
                else True
            ),
            "headroom": (
                bool(event["headroom"])
                if event is not None and event["headroom"] is not None
                else None
            ),
            "continuations": int(row["continuations"] or 0),
        }
    for event in tool_rows:
        phase = str(event["phase"])
        if phase == "AUTH" or phase in snapshot:
            continue
        snapshot[phase] = {
            "inp_tokens": 0,
            "cache_read": 0,
            "cache_write": 0,
            "out_max": 0,
            "ctx_pct": 0.0,
            "baseline_tokens": int(event["input_chars"] or 0) // CHARS_PER_TOKEN,
            "resp_tokens": 0,
            "elapsed_s": int(event["duration_ms"] or 0) / 1000,
            "artifacts": int(event["artifacts"] or 0),
            "val_ok": (
                bool(event["validation_ok"])
                if event["validation_ok"] is not None else True
            ),
            "headroom": (
                bool(event["headroom"])
                if event["headroom"] is not None else None
            ),
            "continuations": 0,
        }
    return snapshot


def render_latest_summary(project: str) -> Path:
    """Regenerate Markdown/HTML/SVG summary from the latest telemetry run."""
    connection = finops_open()
    if connection is None:
        raise RunnerError("FinOps telemetry is disabled or unavailable")
    try:
        run = connection.execute(
            """
            SELECT * FROM pipeline_runs
            WHERE source_project = ?
              AND status = 'completed'
              AND failed_count = 0
              AND executed_count = phases_total
            ORDER BY phases_total DESC, started_at DESC
            LIMIT 1
            """,
            (project,),
        ).fetchone()
        if run is None:
            run = connection.execute(
                """
                SELECT * FROM pipeline_runs
                WHERE source_project = ?
                ORDER BY started_at DESC
                LIMIT 1
                """,
                (project,),
            ).fetchone()
        if run is None:
            raise RunnerError(f"No telemetry run found for project '{project}'")
        totals = connection.execute(
            """
            SELECT COUNT(*) AS rows_count,
                   COALESCE(SUM(input_tokens), 0) AS input_tokens,
                   COALESCE(SUM(output_tokens), 0) AS output_tokens,
                   COALESCE(SUM(cache_read_tokens), 0) AS cache_read_tokens,
                   COALESCE(SUM(cache_write_tokens), 0) AS cache_write_tokens,
                   COALESCE(SUM(cost_usd), 0) AS cost_usd
            FROM usage WHERE session_id = ?
            """,
            (run["run_id"],),
        ).fetchone()
        phase_rows = connection.execute(
            """
            SELECT phase, agent, status, input_tokens, output_tokens,
                   cache_read_tokens, cache_write_tokens, cost_usd,
                   estimated, duration_ms, continuations
            FROM usage WHERE session_id = ? ORDER BY rowid
            """,
            (run["run_id"],),
        ).fetchall()
        tool_rows = connection.execute(
            """
                SELECT phase, agent, status, input_chars, duration_ms, artifacts, validation_ok, headroom
            FROM tool_events WHERE session_id = ? ORDER BY id
            """,
            (run["run_id"],),
        ).fetchall()
    finally:
        connection.close()

    global FINOPS_SESSION_ID, FINOPS_PROJECT, FINOPS_SOURCE_PROJECT
    FINOPS_SESSION_ID = str(run["run_id"])
    FINOPS_PROJECT = str(run["project"])
    FINOPS_SOURCE_PROJECT = project
    phase_snapshot = _snapshot_from_telemetry(phase_rows, tool_rows)
    seen_phases = {
        str(row["phase"]) for row in phase_rows
    } | {
        str(row["phase"]) for row in tool_rows
    }
    active_steps = [
        step for step in PIPELINE
        if step["phase"] in seen_phases and step["phase"] != "AUTH"
    ] or PIPELINE
    event_by_phase = {str(row["phase"]): row for row in tool_rows}
    def event_status(phase: str) -> str:
        event = event_by_phase.get(phase)
        return str(event["status"]) if event is not None else ""

    executed = [
        step["phase"] for step in active_steps
        if step["phase"] in seen_phases
        and event_status(step["phase"]) not in {"skipped", "aborted", "failed"}
    ]
    skipped = [
        step["phase"] for step in active_steps
        if event_status(step["phase"]) == "skipped"
    ]
    aborted = [
        step["phase"] for step in active_steps
        if event_status(step["phase"]) == "aborted"
    ]
    failed = [
        step["phase"] for step in active_steps
        if event_status(step["phase"]) in {"failed", "validation_failed"}
    ]
    report = _write_consolidated_html_report(
        project,
        run,
        totals,
        phase_rows,
        tool_rows,
        phase_snapshot,
        active_steps,
    )
    if report is None:
        raise RunnerError("Consolidated summary could not be generated")
    print_phase_telemetry_snapshot(
        active_steps,
        executed,
        skipped,
        failed,
        aborted,
        phase_snapshot,
    )
    return report


def load_api_key() -> str:
    if DRY_RUN:
        return os.environ.get("AVA_FOUNDRY_API_KEY", "dry-run-no-key")
    environment_key = os.environ.get("AVA_FOUNDRY_API_KEY", "").strip()
    if environment_key:
        return environment_key
    for key_file in API_KEY_CANDIDATES:
        if not key_file.is_file():
            continue
        key = key_file.read_text(encoding="utf-8").strip()
        if key:
            print(f"  {GREEN}Credencial carregada de {display_path(key_file)}.{RESET}")
            return key
    candidates = " ou ".join(str(path) for path in API_KEY_CANDIDATES)
    raise RunnerError(f"Credencial ausente: {candidates} ou AVA_FOUNDRY_API_KEY")


def check_requirements(config_path: Path | None = None) -> None:
    required = [("pyyaml", "yaml"), ("anthropic", "anthropic")]
    if PROVIDER == "openai":
        required.append(("openai", "openai"))
    missing = [package for package, module in required if importlib.util.find_spec(module) is None]
    if missing:
        raise RunnerError(
            "Missing Python package(s): "
            + ", ".join(missing)
            + ". Install with: python -m pip install anthropic pyyaml"
        )
    if config_path is not None and not config_path.is_file():
        raise RunnerError(f"Wave config not found: {config_path}")
    print(f"  {GREEN}Dependências Python{(' e wave config' if config_path else '')}: OK{RESET}")
    has_key_file = any(path.is_file() for path in API_KEY_CANDIDATES)
    if not has_key_file and not os.environ.get("AVA_FOUNDRY_API_KEY"):
        if DRY_RUN:
            print(f"  {DIM}Credencial não necessária no dry-run.{RESET}")
        else:
            raise RunnerError("Credencial do Foundry não encontrada")
    if has_key_file:
        gitignore = WORKSPACE / ".gitignore"
        if gitignore.exists() and ".copilot-key" not in gitignore.read_text(
            encoding="utf-8", errors="ignore"
        ):
            print(f"  {YELLOW}Aviso: .copilot-key não está no .gitignore.{RESET}")


def resolve_model(args: argparse.Namespace) -> str:
    if args.model:
        return args.model
    if not INTERACTIVE:
        return DEFAULT_MODEL_KEY
    print(f"\n{BOLD}Modelos disponíveis:{RESET}")
    keys = list(MODEL_REGISTRY)
    for index, key in enumerate(keys, 1):
        default = " (default)" if key == DEFAULT_MODEL_KEY else ""
        print(f"  {CYAN}{index}.{RESET} {MODEL_REGISTRY[key]['label']}{default}")
    selected = safe_input(
        f"\n{BOLD}Selecione o modelo [número]: {RESET}",
        "1",
    ).strip()
    if selected.isdigit() and 1 <= int(selected) <= len(keys):
        return keys[int(selected) - 1]
    return DEFAULT_MODEL_KEY


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AVA Data Migration Factory Pipeline Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--project", help="Project folder name under projects/")
    parser.add_argument("--wave-config", help="Explicit wave-config.yaml path")
    parser.add_argument(
        "--phases",
        nargs="*",
        metavar="PHASE_OR_GROUP",
        help="Grupos A0/U/G1/M/G2/D/G3 ou fases individuais como U3 U4 G1",
    )
    parser.add_argument("--auto", action="store_true", help="Run without per-step confirmation")
    parser.add_argument("--dry-run", action="store_true", help="Build prompts without calling Foundry")
    parser.add_argument("--resume", action="store_true", help="Skip phases in run-state.json")
    parser.add_argument("--no-headroom", action="store_true", help="Do not start Headroom proxy")
    parser.add_argument("--no-cache", action="store_true", help="Disable prompt caching")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--model", choices=list(MODEL_REGISTRY), help="Foundry deployment")
    parser.add_argument("--list-phases", action="store_true", help="List phases and exit")
    parser.add_argument(
        "--render-summary",
        metavar="PROJECT",
        help="Regenerate the latest Markdown/HTML/SVG summary from telemetry without running agents",
    )
    parser.add_argument("--finops-budget-usd", type=float, default=500.0, help="Reference monthly budget")
    return parser.parse_args()


def print_phase_list() -> None:
    for step in PIPELINE:
        command = step.get("command") or "local validator"
        print(f"{step['phase']:<4} {step['label']:<48} @{step['agent']} {command}")


def save_execution_report(
    project: str,
    active_steps: list[dict[str, Any]],
    executed: list[str],
    skipped: list[str],
    failed: list[str],
    aborted: list[str],
    metrics: dict[str, dict[str, Any]],
) -> Path:
    report_dir = PROJECTS_ROOT / project / "outputs" / "pipeline_runner"
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"execution-report_{stamp}.md"
    lines = [
        f"# Execution Report - {project}",
        "",
        f"**Generated:** {_datetime.datetime.now().isoformat(timespec='seconds')}",
        f"**Model/provider:** {DEPLOYMENT} / {PROVIDER}",
        f"**Prompt cache:** {'enabled' if ENABLE_PROMPT_CACHE else 'disabled'}",
        "",
        "## Result",
        "",
        "| Status | Phases |",
        "|---|---|",
        f"| Executed | {len(executed)} - {', '.join(executed) or '-'} |",
        f"| Skipped | {len(skipped)} - {', '.join(skipped) or '-'} |",
        f"| Failed | {len(failed)} - {', '.join(failed) or '-'} |",
        f"| Aborted | {len(aborted)} - {', '.join(aborted) or '-'} |",
        "",
        "## Phase Metrics",
        "",
        "| Phase | Agent | Input | Output | Cache R | Cache W | Artifacts | Validation | Time |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_write = 0
    total_artifacts = 0
    for step in active_steps:
        phase = step["phase"]
        metric = metrics.get(phase, {})
        if phase in skipped:
            lines.append(f"| {phase} | {step['agent']} | - | - | - | - | - | SKIP | - |")
            continue
        if phase in failed:
            lines.append(f"| {phase} | {step['agent']} | - | - | - | - | - | FAIL | - |")
            continue
        if phase in aborted:
            lines.append(f"| {phase} | {step['agent']} | - | - | - | - | - | ABORT | - |")
            continue
        lines.append(
            f"| {phase} | {step['agent']} | {metric.get('inp_tokens', 0):,} | "
            f"{metric.get('resp_tokens', 0):,} | {metric.get('cache_read', 0):,} | "
            f"{metric.get('cache_write', 0):,} | {metric.get('artifacts', 0)} | "
            f"{'PASS' if metric.get('val_ok', True) else 'FAIL'} | "
            f"{metric.get('elapsed_s', 0.0):.1f}s |"
        )
        total_input += metric.get("inp_tokens", 0)
        total_output += metric.get("resp_tokens", 0)
        total_cache_read += metric.get("cache_read", 0)
        total_cache_write += metric.get("cache_write", 0)
        total_artifacts += metric.get("artifacts", 0)
    lines.extend(
        [
            "",
            "## Totals",
            "",
            f"- Input tokens: {total_input:,}",
            f"- Output tokens: {total_output:,}",
            f"- Cache read: {total_cache_read:,}",
            f"- Cache write: {total_cache_write:,}",
            f"- Artifacts written: {total_artifacts}",
            "",
            "> Token costs are reference estimates, not Foundry billing statements.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return report_path


def print_phase_telemetry_snapshot(
    active_steps: list[dict[str, Any]],
    executed: list[str],
    skipped: list[str],
    failed: list[str],
    aborted: list[str],
    metrics: dict[str, dict[str, Any]],
) -> None:
    """Print the runner-13-style phase telemetry table after execution."""
    banner("Phase telemetry snapshot", CYAN)
    print(f"  {len(active_steps)} phase(s)")
    header = (
        f"  {'Phase':<6} {'Agent':<28} {'Status':<10} {'Input':>10} "
        f"{'OutMax':>9} {'Total':>10} {'Usage%':>8} {'Validation':>10} "
        f"{'Headroom':>9} {'%Comp':>8} {'Arts':>5}"
    )
    separator = "  " + "-" * (len(header) - 2)
    print(header)
    print(separator)

    total_input = 0
    total_output_max = 0
    total_tokens = 0
    total_baseline = 0
    total_artifacts = 0
    executed_with_metrics = 0
    valid_phases = 0
    headroom_on = 0
    headroom_measured = 0

    for step in active_steps:
        phase = str(step["phase"])
        agent = str(step.get("agent", ""))
        metric = metrics.get(phase, {})
        if phase in skipped:
            status = "skipped"
        elif phase in failed:
            status = "failed"
        elif phase in aborted:
            status = "aborted"
        elif phase in executed:
            status = "completed"
        else:
            status = "pending"

        if status in {"skipped", "failed", "aborted", "pending"} or not metric:
            print(f"  {phase:<6} {agent:<28} {status:<10} {'-':>10} {'-':>9} {'-':>10} {'-':>8} {'-':>10} {'-':>9} {'-':>8} {'-':>5}")
            continue

        input_tokens = int(
            metric.get("inp_tokens", 0)
            + metric.get("cache_read", 0)
            + metric.get("cache_write", 0)
        )
        output_max = int(metric.get("out_max", 0))
        row_total_tokens = input_tokens + output_max
        usage_pct = row_total_tokens / CTX_WINDOW * 100
        baseline = int(metric.get("baseline_tokens", 0))
        if baseline > 0:
            compression_pct = max(0.0, (baseline - input_tokens) / baseline * 100)
            compression = f"{compression_pct:.1f}%"
        else:
            compression = "-"
        validation = "PASS" if metric.get("val_ok", True) else "FAIL"
        headroom_value = metric.get("headroom")
        headroom = "on" if headroom_value is True else "off" if headroom_value is False else "n/a"
        total_input += input_tokens
        total_output_max += output_max
        total_tokens += row_total_tokens
        total_baseline += baseline
        total_artifacts += int(metric.get("artifacts", 0))
        executed_with_metrics += 1
        valid_phases += int(bool(metric.get("val_ok", True)))
        if headroom_value is not None:
            headroom_measured += 1
            headroom_on += int(headroom_value is True)
        print(
            f"  {phase:<6} {agent:<28} {status:<10} {input_tokens:>10,} "
            f"{output_max:>9,} {row_total_tokens:>10,} {usage_pct:>7.1f}% "
            f"{validation:>10} {headroom:>9} {compression:>8} "
            f"{int(metric.get('artifacts', 0)):>5}"
        )

    print(separator)
    total_usage_pct = total_tokens / CTX_WINDOW * 100
    total_compression = (
        max(0.0, (total_baseline - total_input) / total_baseline * 100)
        if total_baseline else 0.0
    )
    total_validation = (
        "PASS" if executed_with_metrics and valid_phases == executed_with_metrics
        else "FAIL" if executed_with_metrics
        else "-"
    )
    total_headroom = (
        f"{headroom_on}/{headroom_measured} on"
        if headroom_measured else "n/a"
    )
    print(
        f"  {'TOTAL':<6} {'':<28} {'':<10} {total_input:>10,} "
        f"{total_output_max:>9,} {total_tokens:>10,} {total_usage_pct:>7.1f}% "
        f"{total_validation:>10} {total_headroom:>9} {total_compression:>7.1f}% "
        f"{total_artifacts:>5}"
    )
    print(
        f"  Soma: Input={total_input:,} | OutMax={total_output_max:,} | "
        f"Total={total_tokens:,} | Arts={total_artifacts:,}"
    )
    print(
        "  Headroom=on significa que a chamada passou pelo proxy. "
        "%Comp = redução medida entre baseline local e input reportado pelo provider."
    )
    print(
        "  Se Headroom=on e %Comp=0.0%, o proxy estava ativo, mas não houve redução "
        "mensurável (o input pode ser igual/maior que o baseline estimado)."
    )


def main() -> int:
    global DEPLOYMENT, PROVIDER, ENDPOINT, DRY_RUN, ENABLE_PROMPT_CACHE
    args = parse_args()
    if args.list_phases:
        print_phase_list()
        return 0
    if args.render_summary:
        report = render_latest_summary(args.render_summary)
        print(f"{GREEN}Summary HTML generated: {display_path(report)}{RESET}")
        print(
            f"{GREEN}Visual asset generated: "
            f"{display_path(report.with_name('context-by-phase.svg'))}{RESET}"
        )
        return 0
    DRY_RUN = args.dry_run
    ENABLE_PROMPT_CACHE = not args.no_cache
    model_key = resolve_model(args)
    model_config = MODEL_REGISTRY[model_key]
    DEPLOYMENT = model_config["deployment"]
    PROVIDER = model_config["provider"]
    ENDPOINT = model_config["endpoint"]

    banner(
        f"AVA Data Migration Factory — Pipeline Runner v2 | "
        f"{DEPLOYMENT} | contexto {CTX_WINDOW // 1_000_000}M",
        MAGENTA,
    )
    if DRY_RUN:
        print(f"{MAGENTA}{BOLD}  MODO DRY-RUN — nenhuma chamada à API será feita{RESET}")

    # Runner 13 startup order: prerequisites -> model -> project -> scope -> mode.
    check_requirements()
    args.project = resolve_project(args)
    project, wave_config_path, project_root, config = resolve_wave_config(args)
    validation = validate_wave(wave_config_path)
    if not validation.is_valid:
        raise RunnerError("Wave configuration is invalid; fix it before running")
    config_dry_run = config.get("dry_run", False)
    if isinstance(config_dry_run, str):
        config_dry_run = config_dry_run.strip().lower() in {"1", "true", "yes", "on"}
    if config_dry_run and not DRY_RUN:
        DRY_RUN = True
        print(f"  {YELLOW}A wave possui dry_run: true; chamadas à API desabilitadas.{RESET}")
    active_steps, mode_label = resolve_steps(args)

    auto_mode = args.auto
    if not args.auto and args.phases is None and INTERACTIVE:
        print(f"\n{BOLD}Modo de confirmação:{RESET}")
        print(f"  {CYAN}1.{RESET} Manual       (confirmar cada etapa)")
        print(f"  {CYAN}2.{RESET} Automático   (executar todas sem parar)")
        auto_mode = safe_input(
            f"\n{BOLD}Escolha [1/2]: {RESET}",
            "1",
        ).strip() == "2"

    state = load_state(project)
    if args.resume:
        completed = set(state.get("completed", []))
        already_done = [step["phase"] for step in active_steps if step["phase"] in completed]
        active_steps = [step for step in active_steps if step["phase"] not in completed]
        print(f"  {CYAN}[resume] skipped completed phases: {', '.join(already_done) or '-'}{RESET}")
        if not active_steps:
            print(f"  {GREEN}Nothing to run; all selected phases are complete.{RESET}")
            return 0

    finops_start(project, len(active_steps), DRY_RUN)
    banner(f"Project: {project} | {mode_label} | {len(active_steps)} steps", MAGENTA)

    base_url = ENDPOINT
    if not args.no_headroom and not DRY_RUN:
        base_url = start_headroom()
    elif args.no_headroom:
        print(f"  {DIM}Headroom disabled; using direct endpoint.{RESET}")
    else:
        print(f"  {DIM}Headroom skipped in dry-run.{RESET}")

    api_key = load_api_key()
    client = build_client(api_key, base_url)
    if not DRY_RUN:
        print(f"  {DIM}Pinging Foundry deployment...{RESET}")
        ping_usage = ping_model(client)
        finops_usage("AUTH", "_ping_model", ping_usage, "completed", stop_reason="stop")
        finops_event("AUTH", "_ping_model", "completed", input_chars=4)
        print(f"  {GREEN}Connected to {DEPLOYMENT} via {base_url}.{RESET}")

    executed: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []
    aborted: list[str] = []
    metrics: dict[str, dict[str, Any]] = {}
    automatic = auto_mode or not INTERACTIVE
    pipeline_blocked = False

    for index, step in enumerate(active_steps):
        while True:
            decision = ask_permission(
                step,
                index,
                len(active_steps),
                automatic,
                active_steps,
                executed,
                skipped,
                failed,
            )
            if decision == "V":
                show_skill_preview(step)
                continue
            if decision == "T":
                automatic = True
                decision = "S"
            if decision == "A":
                aborted.append(step["phase"])
                finops_event(step["phase"], step["agent"], "aborted")
                break
            if decision == "P":
                skipped.append(step["phase"])
                finops_event(step["phase"], step["agent"], "skipped")
                break
            try:
                metrics[step["phase"]] = run_step(
                    client,
                    step,
                    project,
                    wave_config_path,
                    config,
                )
                executed.append(step["phase"])
                state.setdefault("completed", [])
                if step["phase"] not in state["completed"]:
                    state["completed"].append(step["phase"])
                state["failed"] = [
                    phase for phase in state.get("failed", [])
                    if phase != step["phase"]
                ]
                save_state(project, state)
                if step.get("gate") and not metrics[step["phase"]]["val_ok"] and not DRY_RUN:
                    failed.append(step["phase"])
                    state.setdefault("failed", [])
                    if step["phase"] not in state["failed"]:
                        state["failed"].append(step["phase"])
                    if step["phase"] in state.get("completed", []):
                        state["completed"].remove(step["phase"])
                    save_state(project, state)
                    pipeline_blocked = True
                    print(f"{RED}Pipeline stopped: Gate {step['gate']} is blocked.{RESET}")
                    break
            except KeyboardInterrupt:
                raise
            except Exception as error:
                print(
                    f"\n{RED}Error in {step['phase']}: "
                    f"{type(error).__name__}: {error}{RESET}"
                )
                retry = safe_input("Retry this step? [S/N]: ", "N").strip().upper()
                if retry == "S":
                    continue
                failed.append(step["phase"])
                state.setdefault("failed", [])
                if step["phase"] not in state["failed"]:
                    state["failed"].append(step["phase"])
                save_state(project, state)
            break
        if aborted or pipeline_blocked:
            break

    status = "failed" if failed else ("aborted" if aborted else "completed")
    finops_report = finops_finish(
        status,
        len(executed),
        len(skipped),
        len(failed),
        len(aborted),
        phase_snapshot=metrics,
        active_steps=active_steps,
    )
    report = save_execution_report(
        project,
        active_steps,
        executed,
        skipped,
        failed,
        aborted,
        metrics,
    )
    banner("Execution complete", GREEN if status == "completed" else YELLOW)
    print(f"  {GREEN}Executed ({len(executed)}): {', '.join(executed) or '-'}{RESET}")
    print(f"  {YELLOW}Skipped  ({len(skipped)}): {', '.join(skipped) or '-'}{RESET}")
    if failed:
        print(f"  {RED}Failed   ({len(failed)}): {', '.join(failed)}{RESET}")
    if aborted:
        print(f"  {RED}Aborted  ({', '.join(aborted)}){RESET}")
    print_phase_telemetry_snapshot(
        active_steps,
        executed,
        skipped,
        failed,
        aborted,
        metrics,
    )
    print(f"  {DIM}Execution report: {display_path(report)}{RESET}")
    if finops_report:
        print(f"  {DIM}FinOps report: {display_path(finops_report)}{RESET}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user.{RESET}")
        raise SystemExit(130)
    except RunnerError as error:
        print(f"{RED}Runner error: {error}{RESET}", file=sys.stderr)
        raise SystemExit(2)
