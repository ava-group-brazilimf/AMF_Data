"""
Integration test: Gate 1 validation against the REAL folder structure the
upstream tasks produce (subfolders per domain), plus the legacy flat layout.

This is the test that was missing when the flat-vs-subfolder divergence
shipped: unit tests validated the validator against its own expectation,
never against what the tasks actually write.
"""
import tempfile
import unittest
from pathlib import Path

from scripts.validate_gate1_artifacts import validate_gate1_artifacts


CANONICAL = {
    "strategy/problem-statement.md": "# Problem Statement",
    "strategy/kpis.md": "# KPIs",
    "analysis/analytical-questions.md": "# Analytical Questions",
    "sttm/sttm.md": "# STTM",
    "analysis/dq-initial.md": "# DQ Initial",
}

FLAT = [Path(p).name for p in CANONICAL]


def _write(root: Path, rel: str, content: str = "ok") -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


class Gate1CanonicalStructureTests(unittest.TestCase):
    """Validate Gate 1 against the structure the tasks really produce."""

    def test_passes_on_canonical_subfolder_structure(self) -> None:
        """The exact layout written by the upstream tasks must PASS."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, content in CANONICAL.items():
                _write(root, rel, content)

            result = validate_gate1_artifacts(root)

            self.assertTrue(
                result.is_valid,
                f"Canonical task structure must validate. Missing: {result.missing}",
            )
            self.assertEqual(result.missing, [])

    def test_passes_on_legacy_flat_structure(self) -> None:
        """Pre-existing waves with flat files at root must keep passing."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in FLAT:
                _write(root, name)

            result = validate_gate1_artifacts(root)

            self.assertTrue(result.is_valid, f"Flat legacy layout broke: {result.missing}")

    def test_passes_on_agent_variant_subfolder(self) -> None:
        """An agent saving to a sibling 1st-level folder still validates."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "strategy/problem-statement.md")
            _write(root, "strategy/kpis.md")
            _write(root, "sttm/sttm.md")
            # Agent improvised a different folder for the BA artifacts:
            _write(root, "business-analysis/analytical-questions.md")
            _write(root, "business-analysis/dq-initial.md")

            result = validate_gate1_artifacts(root)

            self.assertTrue(result.is_valid, f"1st-level variant broke: {result.missing}")

    def test_fails_when_artifact_truly_absent(self) -> None:
        """Tolerance must not create false positives."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in list(CANONICAL)[:-1]:
                _write(root, rel)

            result = validate_gate1_artifacts(root)

            self.assertFalse(result.is_valid)
            self.assertTrue(any("dq-initial.md" in m for m in result.missing))

    def test_fails_on_second_level_nesting(self) -> None:
        """Two levels deep is NOT tolerated - keeps the contract meaningful."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in list(CANONICAL)[:-1]:
                _write(root, rel)
            _write(root, "analysis/extra/dq-initial.md")

            result = validate_gate1_artifacts(root)

            self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
