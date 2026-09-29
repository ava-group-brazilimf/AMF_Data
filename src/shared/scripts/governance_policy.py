"""
governance_policy.py
Programmatic governance policy engine for the agent ecosystem.

Models agent policies as composable dataclasses. Validates chatmode YAML
frontmatter against governance rules. Integrates with audit_logger for
decision recording.

Patterns from the agent-governance skill:
- GovernancePolicy with allowed_tools / blocked_tools / max_calls
- check_tool() → ALLOW / DENY / REVIEW
- Policy composition (most-restrictive-wins)
- Chatmode policy extraction and validation

Usage:
    from scripts.governance_policy import (
        GovernancePolicy, PolicyAction, compose_policies,
        validate_chatmode_policy, FACTORY_BASELINE_POLICY,
    )

    result = validate_chatmode_policy(Path(".github/agents/self-healing.chatmode.md"))
    print(result)  # PASS / FAIL with violations
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


@dataclass
class GovernancePolicy:
    """Declarative policy controlling agent behavior."""

    name: str
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    max_tools_per_agent: int = 15
    require_human_approval: list[str] = field(default_factory=list)

    def check_tool(self, tool_name: str) -> PolicyAction:
        """Check if a tool is allowed by this policy."""
        if tool_name in self.blocked_tools:
            return PolicyAction.DENY
        if tool_name in self.require_human_approval:
            return PolicyAction.REVIEW
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return PolicyAction.DENY
        return PolicyAction.ALLOW

    def check_tool_count(self, count: int) -> PolicyAction:
        """Check if number of tools exceeds maximum."""
        if count > self.max_tools_per_agent:
            return PolicyAction.DENY
        return PolicyAction.ALLOW


def compose_policies(*policies: GovernancePolicy) -> GovernancePolicy:
    """Merge policies with most-restrictive-wins semantics."""
    combined = GovernancePolicy(name="composed")

    for policy in policies:
        combined.blocked_tools.extend(policy.blocked_tools)
        combined.require_human_approval.extend(policy.require_human_approval)
        combined.max_tools_per_agent = min(
            combined.max_tools_per_agent,
            policy.max_tools_per_agent,
        )
        if policy.allowed_tools:
            if combined.allowed_tools:
                combined.allowed_tools = [
                    t for t in combined.allowed_tools if t in policy.allowed_tools
                ]
            else:
                combined.allowed_tools = list(policy.allowed_tools)

    # Deduplicate
    combined.blocked_tools = sorted(set(combined.blocked_tools))
    combined.require_human_approval = sorted(set(combined.require_human_approval))

    return combined


# ---------------------------------------------------------------------------
# Factory baseline policy — all agents in the migration factory must comply
# ---------------------------------------------------------------------------
FACTORY_BASELINE_POLICY = GovernancePolicy(
    name="factory-baseline",
    blocked_tools=["terminalLastCommand"],
    max_tools_per_agent=15,
    require_human_approval=[],
)

# Known valid VS Code Copilot Chat tools
KNOWN_TOOLS = {
    "edit", "search", "new", "runCommands", "runTasks", "usages",
    "vscodeAPI", "problems", "changes", "fetch", "githubRepo",
    "terminalLastCommand",
}


@dataclass
class PolicyViolation:
    agent: str
    rule: str
    detail: str


@dataclass
class PolicyValidationResult:
    agent: str
    passed: bool
    tools_declared: list[str] = field(default_factory=list)
    violations: list[PolicyViolation] = field(default_factory=list)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] {self.agent} — tools: {self.tools_declared}"]
        for v in self.violations:
            lines.append(f"  - {v.rule}: {v.detail}")
        return "\n".join(lines)


def _extract_tools_from_frontmatter(content: str) -> list[str]:
    """Extract tools list from chatmode YAML frontmatter."""
    # Strip UTF-8 BOM if present
    if content.startswith("\ufeff"):
        content = content[1:]
    if not content.startswith("---"):
        return []

    end = content.find("---", 3)
    if end == -1:
        return []

    fm = content[3:end]

    # Handle array-style tools: ['edit', 'search', ...]
    match = re.search(r"tools\s*:\s*\[([^\]]+)\]", fm)
    if match:
        raw = match.group(1)
        return [t.strip().strip("'\"") for t in raw.split(",") if t.strip()]

    # Handle YAML list with brackets across multiple lines
    match = re.search(r"tools\s*:\s*\n\s*\[([^\]]+)\]", fm, re.DOTALL)
    if match:
        raw = match.group(1)
        items = re.findall(r'"([^"]+)"', raw)
        if not items:
            items = re.findall(r"'([^']+)'", raw)
        if not items:
            items = [t.strip().strip("'\"") for t in raw.split(",") if t.strip()]
        return items

    # Handle YAML list style:
    # tools:
    #   - edit
    #   - search
    tools_lines = re.findall(r"^\s+-\s+(.+)$", fm, re.MULTILINE)
    # Only capture lines that come after 'tools:'
    in_tools = False
    result = []
    for line in fm.splitlines():
        if re.match(r"tools\s*:", line):
            in_tools = True
            continue
        if in_tools:
            m = re.match(r"\s+-\s+(.+)", line)
            if m:
                result.append(m.group(1).strip().strip("'\""))
            elif line.strip() and not line.startswith(" "):
                break
    if result:
        return result

    return tools_lines


def validate_chatmode_policy(
    chatmode_path: Path,
    policy: GovernancePolicy | None = None,
) -> PolicyValidationResult:
    """Validate a single chatmode file against governance policy.

    Args:
        chatmode_path: Path to the .chatmode.md file.
        policy: Policy to validate against. Defaults to FACTORY_BASELINE_POLICY.

    Returns:
        PolicyValidationResult with pass/fail and violations.
    """
    if policy is None:
        policy = FACTORY_BASELINE_POLICY

    agent_name = chatmode_path.stem.replace(".chatmode", "")
    content = chatmode_path.read_text(encoding="utf-8")
    tools = _extract_tools_from_frontmatter(content)

    violations: list[PolicyViolation] = []

    # Check tool count
    if policy.check_tool_count(len(tools)) == PolicyAction.DENY:
        violations.append(PolicyViolation(
            agent=agent_name,
            rule="max_tools",
            detail=f"Agent declares {len(tools)} tools (max: {policy.max_tools_per_agent})",
        ))

    # Check each tool against policy
    for tool in tools:
        action = policy.check_tool(tool)
        if action == PolicyAction.DENY:
            violations.append(PolicyViolation(
                agent=agent_name,
                rule="blocked_tool",
                detail=f"Tool '{tool}' is blocked by policy '{policy.name}'",
            ))
        elif action == PolicyAction.REVIEW:
            violations.append(PolicyViolation(
                agent=agent_name,
                rule="review_required",
                detail=f"Tool '{tool}' requires human approval",
            ))

    return PolicyValidationResult(
        agent=agent_name,
        passed=len(violations) == 0,
        tools_declared=tools,
        violations=violations,
    )


def validate_all_chatmode_policies(
    root: Path,
    policy: GovernancePolicy | None = None,
    skip_deprecated: set[str] | None = None,
) -> list[PolicyValidationResult]:
    """Validate all chatmode agents against governance policy."""
    if skip_deprecated is None:
        skip_deprecated = {"orchestrator"}

    agents_dir = root / ".github" / "agents"
    if not agents_dir.exists():
        return []

    results = []
    for chatmode in sorted(agents_dir.glob("*.chatmode.md")):
        agent_name = chatmode.stem.replace(".chatmode", "")
        if agent_name in skip_deprecated:
            results.append(PolicyValidationResult(
                agent=agent_name, passed=True, tools_declared=[],
            ))
            continue
        results.append(validate_chatmode_policy(chatmode, policy))

    return results
