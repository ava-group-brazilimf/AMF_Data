"""
review_workflow.py
B-003 — Review-required workflow: blocks high-risk agent actions until a
human explicitly approves. Integrates with GovernancePolicy (B-001).

Usage:
    from scripts.review_workflow import ReviewWorkflow, GovernancePolicy

    policy = GovernancePolicy(name="execution", require_human_approval=["ddl-execute"])
    wf = ReviewWorkflow(policy)
    wf.check("downstream-executor", "ddl-execute", context={"wave_id": "WAVE-001"})
    # raises PermissionError → creates a pending ReviewRequest

    wf.approve(request_id, approved_by="lead@example.com")
    wf.check(...)  # now passes
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


# ---------------------------------------------------------------------------
# Shared enums / policy model (lightweight, no external deps)
# ---------------------------------------------------------------------------

class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


@dataclass
class GovernancePolicy:
    name: str
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    blocked_patterns: list[str] = field(default_factory=list)
    max_calls_per_request: int = 1000
    require_human_approval: list[str] = field(default_factory=list)

    def check_tool(self, tool_name: str) -> PolicyAction:
        if tool_name in self.blocked_tools:
            return PolicyAction.DENY
        if tool_name in self.require_human_approval:
            return PolicyAction.REVIEW
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return PolicyAction.DENY
        return PolicyAction.ALLOW


# ---------------------------------------------------------------------------
# Review request lifecycle
# ---------------------------------------------------------------------------

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ReviewRequest:
    id: str
    agent_id: str
    tool: str
    context: dict
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decided_at: str | None = None
    decided_by: str | None = None
    rejection_reason: str | None = None


# ---------------------------------------------------------------------------
# Workflow engine
# ---------------------------------------------------------------------------

class ReviewWorkflow:
    """Governs tool execution via policy checks and human-approval requests."""

    def __init__(self, policy: GovernancePolicy) -> None:
        self._policy = policy
        self._requests: dict[str, ReviewRequest] = {}
        # Track approved (agent_id, tool) pairs so subsequent checks pass
        self._approved_pairs: set[tuple[str, str]] = set()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def check(self, agent_id: str, tool: str, context: dict) -> PolicyAction:
        """Enforce policy for an agent/tool pair.

        Returns PolicyAction.ALLOW if the tool may proceed.
        Raises PermissionError for DENY or unresolved REVIEW.
        """
        action = self._policy.check_tool(tool)

        if action == PolicyAction.DENY:
            raise PermissionError(
                f"Policy '{self._policy.name}' blocks tool '{tool}' for agent '{agent_id}'."
            )

        if action == PolicyAction.REVIEW:
            # If already approved for this pair, let it through
            if (agent_id, tool) in self._approved_pairs:
                return PolicyAction.ALLOW
            # Create (or find existing pending) review request
            existing = self._find_pending(agent_id, tool)
            if existing is None:
                req = ReviewRequest(
                    id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    tool=tool,
                    context=context,
                )
                self._requests[req.id] = req
            raise PermissionError(
                f"Tool '{tool}' for agent '{agent_id}' requires human approval before execution."
            )

        return PolicyAction.ALLOW

    def pending_requests(self) -> list[ReviewRequest]:
        return [r for r in self._requests.values() if r.status == ReviewStatus.PENDING]

    def approve(self, request_id: str, approved_by: str) -> ReviewRequest:
        req = self._get_request(request_id)
        req.status = ReviewStatus.APPROVED
        req.decided_at = datetime.now(timezone.utc).isoformat()
        req.decided_by = approved_by
        self._approved_pairs.add((req.agent_id, req.tool))
        return req

    def reject(self, request_id: str, rejected_by: str, reason: str = "") -> ReviewRequest:
        req = self._get_request(request_id)
        req.status = ReviewStatus.REJECTED
        req.decided_at = datetime.now(timezone.utc).isoformat()
        req.decided_by = rejected_by
        req.rejection_reason = reason
        # Remove from approved pairs in case it was previously approved
        self._approved_pairs.discard((req.agent_id, req.tool))
        return req

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _get_request(self, request_id: str) -> ReviewRequest:
        if request_id not in self._requests:
            raise KeyError(f"Review request '{request_id}' not found.")
        return self._requests[request_id]

    def _find_pending(self, agent_id: str, tool: str) -> ReviewRequest | None:
        for r in self._requests.values():
            if r.agent_id == agent_id and r.tool == tool and r.status == ReviewStatus.PENDING:
                return r
        return None
