"""Tests for scripts/validate_agent_contracts.py"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scripts.validate_agent_contracts import (
    AgentContractReport,
    ContractValidationResult,
    ContractViolation,
    validate_agent_contracts,
    _parse_frontmatter,
    _check_frontmatter,
    _check_body,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_CHATMODE = textwrap.dedent("""\
    ---
    description: "Test agent for unit testing"
    tools: ['edit', 'search']
    ---

    # test-agent

    You are **Test**, responsible for testing.

    ## Greeting Behavior

    When activated, greet the user.

    commands:
      - help: Show help
      - diagnose: Run diagnostics
""")

MINIMAL_CHATMODE = textwrap.dedent("""\
    ---
    description: "Minimal agent"
    tools: ['edit']
    ---

    # minimal

    You are Minimal.

    activation-instructions:
      - STEP 1: Read this file

    *help — show help
""")

NO_TOOLS_CHATMODE = textwrap.dedent("""\
    ---
    description: "Agent without tools"
    ---

    # no-tools

    greeting: hello

    commands:
      - help: Show help
""")

NO_HEADING_CHATMODE = textwrap.dedent("""\
    ---
    description: "Agent without heading"
    tools: ['edit']
    ---

    Just text without heading.
    commands:
      - help: Show help
    greeting: yes
""")

DEPRECATED_CHATMODE = textwrap.dedent("""\
    ---
    name: Orchestrator
    description: "DEPRECATED"
    tools: ['edit']
    ---

    # Deprecated
""")


# ---------------------------------------------------------------------------
# Unit tests — internal helpers
# ---------------------------------------------------------------------------

class TestParseFrontmatter:
    def test_standard_frontmatter(self):
        fm, body = _parse_frontmatter(VALID_CHATMODE)
        assert "description" in fm
        assert "tools" in fm
        assert "# test-agent" in body

    def test_no_frontmatter(self):
        fm, body = _parse_frontmatter("# Just a heading\nSome text.")
        assert fm == ""
        assert "# Just a heading" in body

    def test_bom_frontmatter(self):
        """UTF-8 BOM should be stripped before parsing."""
        bom_content = "\ufeff" + VALID_CHATMODE
        fm, body = _parse_frontmatter(bom_content)
        assert "description" in fm
        assert "tools" in fm


class TestCheckFrontmatter:
    def test_valid(self):
        fm, _ = _parse_frontmatter(VALID_CHATMODE)
        violations = _check_frontmatter("test", fm)
        assert len(violations) == 0

    def test_missing_description(self):
        violations = _check_frontmatter("test", "tools: ['edit']")
        rules = [v.rule for v in violations]
        assert "frontmatter_description" in rules

    def test_missing_tools(self):
        violations = _check_frontmatter("test", 'description: "A test"')
        rules = [v.rule for v in violations]
        assert "frontmatter_tools" in rules


class TestCheckBody:
    def test_valid_body(self):
        _, body = _parse_frontmatter(VALID_CHATMODE)
        violations = _check_body("test", body)
        assert len(violations) == 0

    def test_no_heading(self):
        violations = _check_body("test", "Just text.\ncommands:\n  - help\ngreeting: hi")
        rules = [v.rule for v in violations]
        assert "heading" in rules

    def test_no_commands(self):
        violations = _check_body("test", "# agent\nSome text.\ngreeting: hi")
        rules = [v.rule for v in violations]
        assert "commands" in rules

    def test_no_activation(self):
        violations = _check_body("test", "# agent\ncommands:\n  - help: test")
        rules = [v.rule for v in violations]
        assert "activation" in rules


# ---------------------------------------------------------------------------
# Integration tests — validate_agent_contracts()
# ---------------------------------------------------------------------------

class TestValidateAgentContracts:
    def _setup_agents(self, tmp_path: Path, chatmodes: dict[str, str]):
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        for name, content in chatmodes.items():
            (agents_dir / f"{name}.chatmode.md").write_text(content, encoding="utf-8")
        return tmp_path

    def test_all_valid(self, tmp_path):
        root = self._setup_agents(tmp_path, {
            "test-agent": VALID_CHATMODE,
            "minimal": MINIMAL_CHATMODE,
        })
        result = validate_agent_contracts(root)
        assert result.all_passed
        assert result.agents_checked == 2
        assert result.agents_passed == 2

    def test_missing_tools(self, tmp_path):
        root = self._setup_agents(tmp_path, {"no-tools": NO_TOOLS_CHATMODE})
        result = validate_agent_contracts(root)
        assert not result.all_passed
        assert result.agents_failed == 1
        report = result.reports[0]
        rules = [v.rule for v in report.violations]
        assert "frontmatter_tools" in rules

    def test_missing_heading(self, tmp_path):
        root = self._setup_agents(tmp_path, {"no-heading": NO_HEADING_CHATMODE})
        result = validate_agent_contracts(root)
        assert not result.all_passed

    def test_deprecated_skipped(self, tmp_path):
        root = self._setup_agents(tmp_path, {"orchestrator": DEPRECATED_CHATMODE})
        result = validate_agent_contracts(root, skip_deprecated=True)
        assert result.all_passed
        assert result.agents_checked == 1

    def test_deprecated_not_skipped(self, tmp_path):
        root = self._setup_agents(tmp_path, {"orchestrator": DEPRECATED_CHATMODE})
        result = validate_agent_contracts(root, skip_deprecated=False)
        # Will have violations because deprecated chatmode lacks activation
        assert result.agents_checked == 1

    def test_no_agents_dir(self, tmp_path):
        result = validate_agent_contracts(tmp_path)
        assert result.agents_checked == 0
        assert result.all_passed

    def test_real_workspace(self):
        """Validate the actual project chatmodes pass contracts."""
        root = Path(__file__).resolve().parent.parent
        agents_dir = root / ".github" / "agents"
        if not agents_dir.exists():
            pytest.skip("No .github/agents/ directory found")
        result = validate_agent_contracts(root)
        # All non-deprecated agents should pass
        for report in result.reports:
            if not report.passed:
                print(report)
        assert result.all_passed, f"Failed agents: {[r.agent for r in result.reports if not r.passed]}"


# ---------------------------------------------------------------------------
# Dataclass __str__ tests
# ---------------------------------------------------------------------------

class TestDataclassStr:
    def test_report_pass(self):
        r = AgentContractReport(agent="test", passed=True)
        assert "[PASS]" in str(r)

    def test_report_fail(self):
        r = AgentContractReport(
            agent="test", passed=False,
            violations=[ContractViolation("test", "heading", "No heading")],
        )
        assert "[FAIL]" in str(r)
        assert "heading" in str(r)

    def test_result_str(self):
        result = ContractValidationResult(
            agents_checked=2, agents_passed=1, agents_failed=1,
            reports=[
                AgentContractReport(agent="good", passed=True),
                AgentContractReport(agent="bad", passed=False,
                                    violations=[ContractViolation("bad", "x", "y")]),
            ],
        )
        s = str(result)
        assert "1/2 passed" in s
