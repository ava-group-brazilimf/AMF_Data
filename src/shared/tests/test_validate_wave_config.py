import tempfile
import unittest
from pathlib import Path

from scripts.validate_wave_config import validate_wave_config


def _write_config(directory: str, content: str) -> Path:
    p = Path(directory) / "wave-config.yaml"
    p.write_text(content, encoding="utf-8")
    return p


class ValidateWaveConfigTests(unittest.TestCase):
    def test_fails_when_discovery_primary_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(tmp, "wave_id: WAVE-001\nenvironment: DEV\n")
            result = validate_wave_config(cfg)
            self.assertFalse(result.is_valid)
            self.assertTrue(any("primary" in e for e in result.errors))

    def test_fails_when_discovery_fallback_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                "wave_id: WAVE-001\nenvironment: DEV\ndiscovery_owner_primary: discovery-scout\n",
            )
            result = validate_wave_config(cfg)
            self.assertFalse(result.is_valid)
            self.assertTrue(any("fallback" in e for e in result.errors))

    def test_passes_with_valid_discovery_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)
            self.assertEqual([], result.errors)

    def test_warns_when_primary_and_fallback_are_same(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: discovery-scout\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)   # warnings don't fail
            self.assertTrue(len(result.warnings) > 0)

    def test_project_name_requires_wave_context_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "projects" / "wave-demo"
            project_root.mkdir(parents=True)
            cfg = _write_config(
                str(project_root),
                (
                    "wave_id: WAVE-DEMO\n"
                    "project_name: wave-demo\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                ),
            )

            result = validate_wave_config(cfg)

            self.assertFalse(result.is_valid)
            self.assertTrue(any("project-config.yaml" in error for error in result.errors))
            self.assertTrue(any("agent-task-config.yaml" in error for error in result.errors))

    def test_project_paths_resolve_from_project_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "projects" / "wave-demo"
            context_root = project_root / "context"
            context_root.mkdir(parents=True)
            (context_root / "project-config.yaml").write_text("project_name: wave-demo\n")
            (context_root / "agent-task-config.yaml").write_text("project_name: wave-demo\n")
            cfg = _write_config(
                str(project_root),
                (
                    "wave_id: WAVE-DEMO\n"
                    "project_name: wave-demo\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                ),
            )

            result = validate_wave_config(cfg)

            self.assertTrue(result.is_valid, result.errors)

    def test_fails_when_file_not_found(self) -> None:
        result = validate_wave_config(Path("/nonexistent/wave-config.yaml"))
        self.assertFalse(result.is_valid)

    # B-008 tests
    def test_fails_when_prod_wave_missing_runbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: PROD\n"
                    "dry_run: false\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertFalse(result.is_valid)
            self.assertTrue(any("runbook" in e.lower() for e in result.errors))

    def test_passes_when_prod_wave_has_valid_runbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # Create the runbook file
            runbook = Path(tmp) / "runbook.md"
            runbook.write_text("# Runbook", encoding="utf-8")
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: PROD\n"
                    "dry_run: false\n"
                    "runbook_path: runbook.md\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)

    def test_dry_run_prod_does_not_require_runbook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: PROD\n"
                    "dry_run: true\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)

    def test_powercenter_source_platform_accepted(self) -> None:
        """powercenter deve ser aceito como source.type válido."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: powercenter\n"
                    "  connectors: [xml-export-parser]\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)
            self.assertFalse(any("FAIL" in str(result) for _ in [1]))

    def test_informatica_alias_accepted(self) -> None:
        """'informatica' deve ser aceito como alias de powercenter."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: informatica\n"
                    "  connectors: [pmrep-cli]\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)
            self.assertFalse(any("FAIL" in str(result) for _ in [1]))

    def test_powercenter_without_connectors_gives_warning(self) -> None:
        """wave-config com powercenter sem source.connectors deve gerar WARNING."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: powercenter\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)
            self.assertTrue(any("connectors" in w for w in result.warnings))

    def test_spark_generic_source_platform_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: spark_generic\n"
                    "  legacy_path: project/legacy/legacy-hospital-dw/\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)

    def test_spark_generic_aliases_accepted(self) -> None:
        for alias in ("spark", "mixed", "sqlserver", "mssql"):
            with tempfile.TemporaryDirectory() as tmp:
                cfg = _write_config(
                    tmp,
                    (
                        "wave_id: WAVE-001\n"
                        "environment: DEV\n"
                        "discovery_owner_primary: discovery-scout\n"
                        "discovery_owner_fallback: inventory-scout\n"
                        "source:\n"
                        f"  type: {alias}\n"
                        "  legacy_path: project/legacy/x/\n"
                    ),
                )
                result = validate_wave_config(cfg)
                self.assertTrue(result.is_valid, f"alias {alias} rejected")

    def test_spark_generic_without_legacy_path_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: spark_generic\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)
            self.assertTrue(any("legacy_path" in w for w in result.warnings))

    def test_synapse_source_platform_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: synapse\n"
                    "  legacy_path: project/legacy/synapse-workspace/\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)

    def test_azure_synapse_alias_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _write_config(
                tmp,
                (
                    "wave_id: WAVE-001\n"
                    "environment: DEV\n"
                    "discovery_owner_primary: discovery-scout\n"
                    "discovery_owner_fallback: inventory-scout\n"
                    "source:\n"
                    "  type: azure_synapse\n"
                    "  legacy_path: project/legacy/synapse-workspace/\n"
                ),
            )
            result = validate_wave_config(cfg)
            self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()
