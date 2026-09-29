import tempfile
import unittest
from pathlib import Path

from scripts.validate_gate3_artifacts import validate_gate3_requirements


class ValidateGate3ArtifactsTests(unittest.TestCase):
    def test_fails_when_required_files_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wave_root = Path(tmp)
            (wave_root / "ddl").mkdir()
            (wave_root / "etl").mkdir()
            (wave_root / "tests").mkdir()
            (wave_root / "documentation").mkdir()
            (wave_root / "downstream" / "bi").mkdir(parents=True)
            # Missing wave-report.md and evidence docs on purpose.

            result = validate_gate3_requirements(wave_root)

            self.assertFalse(result.is_valid)
            self.assertIn("wave-report.md", result.missing)
            self.assertIn("documentation/execution-runbook.md", result.missing)

    def test_passes_when_all_required_artifacts_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wave_root = Path(tmp)
            (wave_root / "ddl").mkdir()
            (wave_root / "etl").mkdir()
            (wave_root / "tests").mkdir()
            (wave_root / "documentation").mkdir()
            (wave_root / "downstream" / "bi").mkdir(parents=True)
            (wave_root / "wave-report.md").write_text("ok", encoding="utf-8")
            (wave_root / "documentation" / "execution-runbook.md").write_text("ok", encoding="utf-8")
            (wave_root / "documentation" / "quality-gate-evidence.md").write_text("ok", encoding="utf-8")
            (wave_root / "documentation" / "reconciliation-evidence.md").write_text("ok", encoding="utf-8")

            result = validate_gate3_requirements(wave_root)

            self.assertTrue(result.is_valid)
            self.assertEqual([], result.missing)


if __name__ == "__main__":
    unittest.main()
