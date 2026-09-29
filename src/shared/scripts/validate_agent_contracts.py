"""
validate_agent_contracts.py
Structural contract validator for .chatmode.md agent files.

Verifies that each chatmode agent meets minimum structural requirements:
- Has a YAML frontmatter with 'description' and 'tools'
- Has a markdown heading (# agent-name)
- Has at least one command (* prefixed)
- Has activation instructions or greeting behavior
- Has a persona/role section

Does NOT require LLM runtime — purely deterministic structural checks.

Usage:
    python -m scripts.validate_agent_contracts [--root <workspace_root>]
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ContractViolation:
    agent: str
    rule: str
    detail: str


@dataclass
class AgentContractReport:
    agent: str
    passed: bool
    violations: list[ContractViolation] = field(default_factory=list)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] {self.agent}"]
        for v in self.violations:
            lines.append(f"  - {v.rule}: {v.detail}")
        return "\n".join(lines)


@dataclass
class ContractValidationResult:
    agents_checked: int
    agents_passed: int
    agents_failed: int
    reports: list[AgentContractReport] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return self.agents_failed == 0

    def __str__(self) -> str:
        lines = [
            f"Agent Contract Validation: {self.agents_passed}/{self.agents_checked} passed",
        ]
        for r in self.reports:
            if not r.passed:
                lines.append(str(r))
        return "\n".join(lines)


# Agents exempt from full structural checks
DEPRECATED_AGENTS = {"orchestrator"}

# Required YAML frontmatter keys
REQUIRED_FRONTMATTER = {"description"}

# Minimum required sections (regex patterns matched against the body)
REQUIRED_PATTERNS = {
    "heading": (r"^#\s+\S+", "Must have a markdown heading (# agent-name)"),
    "tools_frontmatter": (r"^tools:", "Must declare tools: in YAML frontmatter"),
}


def _parse_frontmatter(content: str) -> tuple[str, str]:
    """Split content into frontmatter and body."""
    # Strip UTF-8 BOM if present
    if content.startswith("\ufeff"):
        content = content[1:]
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[3:end].strip(), content[end + 3:].strip()
    return "", content


def _check_frontmatter(agent: str, fm: str) -> list[ContractViolation]:
    """Validate frontmatter has required fields."""
    violations = []
    for key in REQUIRED_FRONTMATTER:
        pattern = rf"(?:^|\n){key}\s*:"
        if not re.search(pattern, fm):
            violations.append(ContractViolation(
                agent=agent,
                rule=f"frontmatter_{key}",
                detail=f"Missing '{key}' in YAML frontmatter",
            ))
    # tools check in frontmatter
    if not re.search(r"(?:^|\n)tools\s*:", fm):
        violations.append(ContractViolation(
            agent=agent,
            rule="frontmatter_tools",
            detail="Missing 'tools' in YAML frontmatter",
        ))
    return violations


def _check_body(agent: str, body: str) -> list[ContractViolation]:
    """Validate body has required structural elements."""
    violations = []

    # Must have a heading
    if not re.search(r"^#\s+\S+", body, re.MULTILINE):
        violations.append(ContractViolation(
            agent=agent,
            rule="heading",
            detail="No markdown heading found",
        ))

    # Must have at least one command (YAML commands: section, *command, or ## commands/tasks heading)
    has_commands = (
        re.search(r"commands:", body) is not None
        or re.search(r"\*\w+", body) is not None
        or re.search(r"##.*(?:command|task|capabilit|workflow|mission)", body, re.IGNORECASE) is not None
    )
    if not has_commands:
        violations.append(ContractViolation(
            agent=agent,
            rule="commands",
            detail="No commands section or *command references found",
        ))

    # Must have activation instructions or greeting or role/behavior section
    has_activation = (
        re.search(
            r"activation.instruction|greeting|saudação|STEP\s+\d+:|##.*(?:activation|behavior|role)",
            body, re.IGNORECASE,
        ) is not None
    )
    if not has_activation:
        violations.append(ContractViolation(
            agent=agent,
            rule="activation",
            detail="No activation instructions or greeting behavior found",
        ))

    return violations


def validate_agent_contracts(
    root: Path,
    skip_deprecated: bool = True,
) -> ContractValidationResult:
    """Validate all chatmode agents against structural contracts.

    Args:
        root: Workspace root directory.
        skip_deprecated: If True, deprecated agents get a PASS with no checks.

    Returns:
        ContractValidationResult with per-agent reports.
    """
    agents_dir = root / ".github" / "agents"
    if not agents_dir.exists():
        return ContractValidationResult(
            agents_checked=0, agents_passed=0, agents_failed=0,
        )

    reports: list[AgentContractReport] = []

    for chatmode in sorted(agents_dir.glob("*.chatmode.md")):
        agent_name = chatmode.stem.replace(".chatmode", "")
        content = chatmode.read_text(encoding="utf-8")

        # Skip deprecated agents
        if skip_deprecated and agent_name in DEPRECATED_AGENTS:
            reports.append(AgentContractReport(agent=agent_name, passed=True))
            continue

        frontmatter, body = _parse_frontmatter(content)
        violations: list[ContractViolation] = []

        violations.extend(_check_frontmatter(agent_name, frontmatter))
        violations.extend(_check_body(agent_name, body))

        reports.append(AgentContractReport(
            agent=agent_name,
            passed=len(violations) == 0,
            violations=violations,
        ))

    passed = sum(1 for r in reports if r.passed)
    failed = sum(1 for r in reports if not r.passed)

    return ContractValidationResult(
        agents_checked=len(reports),
        agents_passed=passed,
        agents_failed=failed,
        reports=reports,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate agent chatmode contracts")
    parser.add_argument("--root", default=".", help="Workspace root (default: .)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    result = validate_agent_contracts(root)

    print(result)
    for r in result.reports:
        if r.passed:
            print(f"  [PASS] {r.agent}")

    return 0 if result.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
