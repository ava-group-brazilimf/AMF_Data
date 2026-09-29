"""Tests for B-003: review-required workflow engine."""
import unittest

from scripts.review_workflow import (
    ReviewWorkflow,
    ReviewRequest,
    ReviewStatus,
    PolicyAction,
    GovernancePolicy,
)


class ReviewWorkflowTests(unittest.TestCase):
    def _make_policy(self, require_review: list[str], blocked: list[str] | None = None) -> GovernancePolicy:
        return GovernancePolicy(
            name="test",
            require_human_approval=require_review,
            blocked_tools=blocked or [],
        )

    # B-003-1: blocked tool raises immediately
    def test_denied_tool_raises_permission_error(self) -> None:
        policy = self._make_policy(require_review=[], blocked=["drop-table"])
        wf = ReviewWorkflow(policy)
        with self.assertRaises(PermissionError):
            wf.check("downstream-executor", "drop-table", context={})

    # B-003-2: review-required tool creates a pending request and blocks
    def test_review_required_tool_blocks_and_creates_request(self) -> None:
        policy = self._make_policy(require_review=["ddl-execute"])
        wf = ReviewWorkflow(policy)
        with self.assertRaises(PermissionError) as ctx:
            wf.check("downstream-executor", "ddl-execute", context={"wave_id": "WAVE-001"})
        self.assertIn("approval", str(ctx.exception).lower())
        # A pending review request must have been created
        pending = wf.pending_requests()
        self.assertEqual(1, len(pending))
        self.assertEqual(ReviewStatus.PENDING, pending[0].status)

    # B-003-3: allowed tool passes without creating a request
    def test_allowed_tool_passes(self) -> None:
        policy = self._make_policy(require_review=["ddl-execute"])
        wf = ReviewWorkflow(policy)
        result = wf.check("discovery-scout", "read-schema", context={})
        self.assertEqual(PolicyAction.ALLOW, result)
        self.assertEqual(0, len(wf.pending_requests()))

    # B-003-4: approving a request clears the block
    def test_approve_request_allows_subsequent_check(self) -> None:
        policy = self._make_policy(require_review=["ddl-execute"])
        wf = ReviewWorkflow(policy)
        try:
            wf.check("downstream-executor", "ddl-execute", context={"wave_id": "WAVE-001"})
        except PermissionError:
            pass
        req_id = wf.pending_requests()[0].id
        wf.approve(req_id, approved_by="tech-lead@example.com")
        # After approval the same check should pass
        result = wf.check("downstream-executor", "ddl-execute", context={"wave_id": "WAVE-001"})
        self.assertEqual(PolicyAction.ALLOW, result)

    # B-003-5: rejecting a request keeps it blocked
    def test_reject_request_keeps_blocking(self) -> None:
        policy = self._make_policy(require_review=["ddl-execute"])
        wf = ReviewWorkflow(policy)
        try:
            wf.check("downstream-executor", "ddl-execute", context={"wave_id": "WAVE-001"})
        except PermissionError:
            pass
        req_id = wf.pending_requests()[0].id
        wf.reject(req_id, rejected_by="tech-lead@example.com", reason="not ready")
        with self.assertRaises(PermissionError):
            wf.check("downstream-executor", "ddl-execute", context={"wave_id": "WAVE-001"})


if __name__ == "__main__":
    unittest.main()
