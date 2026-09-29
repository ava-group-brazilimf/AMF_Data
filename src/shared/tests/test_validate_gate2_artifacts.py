import tempfile
import unittest
from pathlib import Path

from scripts.validate_gate2_artifacts import validate_gate2_artifacts


class ValidateGate2ArtifactsModuleTests(unittest.TestCase):
    """Tests for the standalone validate_gate2_artifacts convenience module."""

    REQUIRED = [
        "architecture.md",
        "data-model.md",
        "decisions.md",
        "dq-rules.md",
        "monitoring-spec.md",
    ]

    def test_passes_when_all_gate2_artifacts_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for artifact in self.REQUIRED:
                (root / artifact).write_text("ok", encoding="utf-8")

            result = validate_gate2_artifacts(root)

            self.assertTrue(result.is_valid)
            self.assertEqual(result.gate, 2)
            self.assertEqual(result.missing, [])

    def test_fails_when_data_model_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for artifact in self.REQUIRED:
                if artifact != "data-model.md":
                    (root / artifact).write_text("ok", encoding="utf-8")

            result = validate_gate2_artifacts(root)

            self.assertFalse(result.is_valid)
            self.assertIn("data-model.md", result.missing)

    def test_fails_on_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = validate_gate2_artifacts(Path(tmp))

            self.assertFalse(result.is_valid)
            self.assertEqual(len(result.missing), len(self.REQUIRED))

    def test_cli_returns_zero_on_pass(self) -> None:
        from scripts.validate_gate2_artifacts import main

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for artifact in self.REQUIRED:
                (root / artifact).write_text("ok", encoding="utf-8")

            exit_code = main([str(root)])
            self.assertEqual(exit_code, 0)

    def test_cli_returns_one_on_fail(self) -> None:
        from scripts.validate_gate2_artifacts import main

        with tempfile.TemporaryDirectory() as tmp:
            exit_code = main([str(tmp)])
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
