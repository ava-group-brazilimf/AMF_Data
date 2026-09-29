"""Tests for scripts/governance_policy.py"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from scripts.governance_policy import (
    GovernancePolicy,
    PolicyAction,
    PolicyValidationResult,
    PolicyViolation,
    compose_policies,
    validate_chatmode_policy,
    validate_all_chatmode_policies,
    FACTORY_BASELINE_POLICY,
    _extract_tools_from_frontmatter,
)


# ---------------------------------------------------------------------------
# GovernancePolicy unit tests
# ---------------------------------------------------------------------------

class TestGovernancePolicy:
    def test_allow_when_no_restrictions(self):
        policy = GovernancePolicy(name="open")
        assert policy.check_tool("anything") == PolicyAction.ALLOW

    def test_deny_blocked_tool(self):
        policy = GovernancePolicy(name="strict", blocked_tools=["shell"])
        assert policy.check_tool("shell") == PolicyAction.DENY
        assert policy.check_tool("edit") == PolicyAction.ALLOW

    def test_deny_not_in_allowlist(self):
        policy = GovernancePolicy(name="allowlist", allowed_tools=["edit", "search"])
        assert policy.check_tool("edit") == PolicyAction.ALLOW
        assert policy.check_tool("delete") == PolicyAction.DENY

    def test_review_required(self):
        policy = GovernancePolicy(name="review", require_human_approval=["runCommands"])
        assert policy.check_tool("runCommands") == PolicyAction.REVIEW
        assert policy.check_tool("edit") == PolicyAction.ALLOW

    def test_blocked_overrides_review(self):
        policy = GovernancePolicy(
            name="both",
            blocked_tools=["dangerous"],
            require_human_approval=["dangerous"],
        )
        # Blocked check happens first
        assert policy.check_tool("dangerous") == PolicyAction.DENY

    def test_check_tool_count_within_limit(self):
        policy = GovernancePolicy(name="counting", max_tools_per_agent=5)
        assert policy.check_tool_count(5) == PolicyAction.ALLOW
        assert policy.check_tool_count(3) == PolicyAction.ALLOW

    def test_check_tool_count_exceeds_limit(self):
        policy = GovernancePolicy(name="counting", max_tools_per_agent=5)
        assert policy.check_tool_count(6) == PolicyAction.DENY


# ---------------------------------------------------------------------------
# compose_policies
# ---------------------------------------------------------------------------

class TestComposePolicies:
    def test_merge_blocked_tools(self):
        p1 = GovernancePolicy(name="a", blocked_tools=["shell"])
        p2 = GovernancePolicy(name="b", blocked_tools=["delete"])
        composed = compose_policies(p1, p2)
        assert "shell" in composed.blocked_tools
        assert "delete" in composed.blocked_tools

    def test_most_restrictive_max_tools(self):
        p1 = GovernancePolicy(name="a", max_tools_per_agent=10)
        p2 = GovernancePolicy(name="b", max_tools_per_agent=5)
        composed = compose_policies(p1, p2)
        assert composed.max_tools_per_agent == 5

    def test_allowlist_intersection(self):
        p1 = GovernancePolicy(name="a", allowed_tools=["edit", "search", "new"])
        p2 = GovernancePolicy(name="b", allowed_tools=["edit", "search"])
        composed = compose_policies(p1, p2)
        assert "edit" in composed.allowed_tools
        assert "search" in composed.allowed_tools
        assert "new" not in composed.allowed_tools

    def test_merge_review_tools(self):
        p1 = GovernancePolicy(name="a", require_human_approval=["runCommands"])
        p2 = GovernancePolicy(name="b", require_human_approval=["githubRepo"])
        composed = compose_policies(p1, p2)
        assert "runCommands" in composed.require_human_approval
        assert "githubRepo" in composed.require_human_approval

    def test_deduplication(self):
        p1 = GovernancePolicy(name="a", blocked_tools=["shell", "shell"])
        composed = compose_policies(p1)
        assert composed.blocked_tools.count("shell") == 1


# ---------------------------------------------------------------------------
# _extract_tools_from_frontmatter
# ---------------------------------------------------------------------------

class TestExtractTools:
    def test_inline_array(self):
        content = "---\ndescription: test\ntools: ['edit', 'search']\n---\n# body"
        tools = _extract_tools_from_frontmatter(content)
        assert tools == ["edit", "search"]

    def test_multiline_array(self):
        content = textwrap.dedent("""\
            ---
            description: test
            tools:
              [
                "edit",
                "search",
                "new",
              ]
            ---
            # body
        """)
        tools = _extract_tools_from_frontmatter(content)
        assert "edit" in tools
        assert "search" in tools
        assert "new" in tools

    def test_no_frontmatter(self):
        content = "# Just a heading"
        tools = _extract_tools_from_frontmatter(content)
        assert tools == []

    def test_no_tools_key(self):
        content = "---\ndescription: test\n---\n# body"
        tools = _extract_tools_from_frontmatter(content)
        assert tools == []

    def test_bom_prefix(self):
        content = "\ufeff---\ndescription: test\ntools: ['edit', 'search']\n---\n# body"
        tools = _extract_tools_from_frontmatter(content)
        assert tools == ["edit", "search"]


# ---------------------------------------------------------------------------
# validate_chatmode_policy
# ---------------------------------------------------------------------------

class TestValidateChatmodePolicy:
    def _write_chatmode(self, tmp_path: Path, name: str, content: str) -> Path:
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        path = agents_dir / f"{name}.chatmode.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_chatmode_passes_baseline(self, tmp_path):
        content = "---\ndescription: test\ntools: ['edit', 'search']\n---\n# body"
        path = self._write_chatmode(tmp_path, "test", content)
        result = validate_chatmode_policy(path)
        assert result.passed
        assert result.tools_declared == ["edit", "search"]

    def test_blocked_tool_fails(self, tmp_path):
        content = "---\ndescription: test\ntools: ['edit', 'terminalLastCommand']\n---\n# body"
        path = self._write_chatmode(tmp_path, "test", content)
        result = validate_chatmode_policy(path)
        assert not result.passed
        rules = [v.rule for v in result.violations]
        assert "blocked_tool" in rules

    def test_too_many_tools_fails(self, tmp_path):
        many_tools = ", ".join(f"'tool{i}'" for i in range(20))
        content = f"---\ndescription: test\ntools: [{many_tools}]\n---\n# body"
        path = self._write_chatmode(tmp_path, "test", content)
        policy = GovernancePolicy(name="strict", max_tools_per_agent=5)
        result = validate_chatmode_policy(path, policy)
        assert not result.passed

    def test_custom_policy(self, tmp_path):
        content = "---\ndescription: test\ntools: ['edit', 'search']\n---\n# body"
        path = self._write_chatmode(tmp_path, "test", content)
        policy = GovernancePolicy(
            name="restricted",
            allowed_tools=["edit"],
        )
        result = validate_chatmode_policy(path, policy)
        assert not result.passed  # 'search' not in allowed_tools


# ---------------------------------------------------------------------------
# validate_all_chatmode_policies
# ---------------------------------------------------------------------------

class TestValidateAllPolicies:
    def _setup_agents(self, tmp_path: Path, chatmodes: dict[str, str]):
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        for name, content in chatmodes.items():
            (agents_dir / f"{name}.chatmode.md").write_text(content, encoding="utf-8")
        return tmp_path

    def test_all_pass(self, tmp_path):
        root = self._setup_agents(tmp_path, {
            "agent-a": "---\ndescription: a\ntools: ['edit']\n---\n# a",
            "agent-b": "---\ndescription: b\ntools: ['search']\n---\n# b",
        })
        results = validate_all_chatmode_policies(root)
        assert all(r.passed for r in results)

    def test_deprecated_skipped(self, tmp_path):
        root = self._setup_agents(tmp_path, {
            "orchestrator": "---\ndescription: deprecated\ntools: ['terminalLastCommand']\n---\n# dep",
        })
        results = validate_all_chatmode_policies(root)
        assert all(r.passed for r in results)

    def test_no_agents_dir(self, tmp_path):
        results = validate_all_chatmode_policies(tmp_path)
        assert results == []

    def test_real_workspace_baseline(self):
        """Validate actual project chatmodes against factory baseline policy."""
        root = Path(__file__).resolve().parent.parent
        agents_dir = root / ".github" / "agents"
        if not agents_dir.exists():
            pytest.skip("No .github/agents/ directory found")
        results = validate_all_chatmode_policies(root)
        for r in results:
            if not r.passed:
                print(r)
        assert all(r.passed for r in results), f"Policy failures: {[r.agent for r in results if not r.passed]}"


# ---------------------------------------------------------------------------
# Dataclass __str__
# ---------------------------------------------------------------------------

class TestPolicyStr:
    def test_pass_str(self):
        r = PolicyValidationResult(agent="test", passed=True, tools_declared=["edit"])
        assert "[PASS]" in str(r)

    def test_fail_str(self):
        r = PolicyValidationResult(
            agent="test", passed=False, tools_declared=["bad"],
            violations=[PolicyViolation("test", "blocked", "bad is blocked")],
        )
        assert "[FAIL]" in str(r)
        assert "blocked" in str(r)


# ---------------------------------------------------------------------------
# Factory baseline policy sanity
# ---------------------------------------------------------------------------

class TestFactoryBaseline:
    def test_baseline_exists(self):
        assert FACTORY_BASELINE_POLICY.name == "factory-baseline"

    def test_baseline_blocks_terminal(self):
        assert FACTORY_BASELINE_POLICY.check_tool("terminalLastCommand") == PolicyAction.DENY

    def test_baseline_allows_edit(self):
        assert FACTORY_BASELINE_POLICY.check_tool("edit") == PolicyAction.ALLOW
