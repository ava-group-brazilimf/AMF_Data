import tempfile
import unittest
from pathlib import Path

from scripts.validate_gate3_artifacts import validate_gate_requirements


class ValidateGate1ArtifactsTests(unittest.TestCase):
    def test_fails_when_gate1_artifacts_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "problem-statement.md").write_text("ok", encoding="utf-8")
            # kpis.md, analytical-questions.md, sttm.md, dq-initial.md missing

            result = validate_gate_requirements(1, root)

            self.assertFalse(result.is_valid)
            self.assertIn("strategy/kpis.md", result.missing)
            self.assertIn("sttm/sttm.md", result.missing)

    def test_passes_when_all_gate1_artifacts_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            required = [
                "problem-statement.md",
                "kpis.md",
                "analytical-questions.md",
                "sttm.md",
                "dq-initial.md",
            ]
            for artifact in required:
                (root / artifact).write_text("ok", encoding="utf-8")

            result = validate_gate_requirements(1, root)

            self.assertTrue(result.is_valid)
            self.assertEqual([], result.missing)


class ValidateGate2ArtifactsTests(unittest.TestCase):
    def test_missing_gate2_artifact_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "architecture.md").write_text("ok", encoding="utf-8")
            # data-model.md, decisions.md, dq-rules.md, monitoring-spec.md missing

            result = validate_gate_requirements(2, root)

            self.assertFalse(result.is_valid)
            self.assertIn("data-model.md", result.missing)
            self.assertIn("monitoring-spec.md", result.missing)


if __name__ == "__main__":
    unittest.main()
