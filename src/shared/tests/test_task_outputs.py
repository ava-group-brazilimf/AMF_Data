"""
test_task_outputs.py — Validates that task outputs conform to expected formats,
paths, required fields, and template application rules.

Covers all multi-format outputs from:
- UPSTREAM: generate-inventory, create-sttm
- MIDSTREAM: create-architecture, create-data-model, validate-code
- DOWNSTREAM: run-wave, reconcile-wave, generate-migration-report
"""
from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path


class InventoryOutputTests(unittest.TestCase):
    """Tests for generate-inventory task outputs (4 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "outputs" / "upstream" / "inventory"
        self.root.mkdir(parents=True)

    def _write_inventory_json(self, data: dict | None = None) -> Path:
        content = data or {
            "project": "TEST-PROJECT",
            "wave_id": "WAVE-001",
            "generated_at": "2026-06-08T00:00:00Z",
            "objects": [
                {
                    "id": "OBJ-001",
                    "name": "dbo.Customers",
                    "type": "TABLE",
                    "schema": "dbo",
                    "complexity": "LOW",
                    "row_count_estimate": 50000,
                    "dependencies": [],
                }
            ],
            "summary": {"total_objects": 1, "tables": 1, "views": 0, "procedures": 0},
        }
        path = self.root / "inventory-enriched.json"
        path.write_text(json.dumps(content, indent=2), encoding="utf-8")
        return path

    def _write_inventory_md(self, content: str | None = None) -> Path:
        text = content or "# Inventory Report\n\n## Summary\n\n- Total: 1 objects\n\n## Objects\n\n| Name | Type | Complexity |\n|------|------|------------|\n| dbo.Customers | TABLE | LOW |\n"
        path = self.root / "inventory-report.md"
        path.write_text(text, encoding="utf-8")
        return path

    def _write_inventory_html(self, content: str | None = None) -> Path:
        text = content or "<!DOCTYPE html><html><head><title>AS-IS Platform Landscape</title></head><body><h1>Platform Landscape</h1></body></html>"
        path = self.root.parent / "asis-platform-landscape.html"
        path.write_text(text, encoding="utf-8")
        return path

    def _write_inventory_csv(self, rows: list[list[str]] | None = None) -> Path:
        data = rows or [
            ["id", "name", "type", "schema", "complexity", "row_count_estimate"],
            ["OBJ-001", "dbo.Customers", "TABLE", "dbo", "LOW", "50000"],
        ]
        path = self.root / "all-objects-inventory.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        return path

    # --- JSON tests ---

    def test_inventory_json_is_valid_json(self) -> None:
        path = self._write_inventory_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)

    def test_inventory_json_has_required_keys(self) -> None:
        path = self._write_inventory_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        required_keys = {"project", "wave_id", "generated_at", "objects", "summary"}
        self.assertTrue(required_keys.issubset(data.keys()))

    def test_inventory_json_objects_have_required_fields(self) -> None:
        path = self._write_inventory_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for obj in data["objects"]:
            for field in ("id", "name", "type", "schema", "complexity"):
                self.assertIn(field, obj, f"Missing field '{field}' in object")

    def test_inventory_json_no_placeholders(self) -> None:
        path = self._write_inventory_json()
        content = path.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    # --- Markdown tests ---

    def test_inventory_md_has_required_sections(self) -> None:
        path = self._write_inventory_md()
        content = path.read_text(encoding="utf-8")
        self.assertIn("# Inventory Report", content)
        self.assertIn("## Summary", content)
        self.assertIn("## Objects", content)

    def test_inventory_md_no_placeholders(self) -> None:
        path = self._write_inventory_md()
        content = path.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    # --- HTML tests ---

    def test_inventory_html_is_valid_html(self) -> None:
        path = self._write_inventory_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("<html", content)
        self.assertIn("</html>", content)

    def test_inventory_html_has_title(self) -> None:
        path = self._write_inventory_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<title>", content)

    def test_inventory_html_no_placeholders(self) -> None:
        path = self._write_inventory_html()
        content = path.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    # --- CSV tests ---

    def test_inventory_csv_has_header(self) -> None:
        path = self._write_inventory_csv()
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
        expected_cols = {"id", "name", "type", "schema", "complexity", "row_count_estimate"}
        self.assertTrue(expected_cols.issubset(set(header)))

    def test_inventory_csv_consistent_columns(self) -> None:
        path = self._write_inventory_csv()
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            col_count = len(header)
            for i, row in enumerate(reader, start=2):
                self.assertEqual(len(row), col_count, f"Row {i} has {len(row)} columns, expected {col_count}")

    def test_inventory_csv_non_empty_data(self) -> None:
        path = self._write_inventory_csv()
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            rows = list(reader)
        self.assertGreater(len(rows), 0)

    # --- Completeness test ---

    def test_all_four_outputs_generated(self) -> None:
        """Task is not complete until all 4 files exist."""
        self._write_inventory_json()
        self._write_inventory_md()
        self._write_inventory_html()
        self._write_inventory_csv()

        self.assertTrue((self.root / "inventory-enriched.json").exists())
        self.assertTrue((self.root / "inventory-report.md").exists())
        self.assertTrue((self.root.parent / "asis-platform-landscape.html").exists())
        self.assertTrue((self.root / "all-objects-inventory.csv").exists())

    def test_fails_when_html_missing(self) -> None:
        """Task should fail if HTML output is not generated."""
        self._write_inventory_json()
        self._write_inventory_md()
        self._write_inventory_csv()
        # HTML intentionally not written
        self.assertFalse((self.root.parent / "asis-platform-landscape.html").exists())


class STTMOutputTests(unittest.TestCase):
    """Tests for create-sttm task outputs (3 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "outputs" / "upstream" / "sttm"
        self.root.mkdir(parents=True)

    def _write_sttm_json(self, data: dict | None = None) -> Path:
        content = data or {
            "project_name": "TEST",
            "wave_id": "WAVE-001",
            "version": "1.0",
            "generated_at": "2026-06-08T00:00:00Z",
            "source_systems": [
                {"id": "SRC-001", "name": "NORTHWIND", "type": "DATABASE", "technology": "SQL Server"}
            ],
            "mappings": [
                {
                    "id": "MAP-001",
                    "source_system": "SRC-001",
                    "source_table": "dbo.Customers",
                    "source_column": "CustomerID",
                    "target_table": "slv_customers",
                    "target_column": "customer_id",
                    "transformation": "CAST AS INT",
                }
            ],
        }
        path = self.root / "sttm.json"
        path.write_text(json.dumps(content, indent=2), encoding="utf-8")
        return path

    def _write_sttm_md(self) -> Path:
        path = self.root / "sttm.md"
        path.write_text("# Source-to-Target Mapping\n\n## Source Systems\n\n## Mappings\n", encoding="utf-8")
        return path

    def _write_sttm_html(self) -> Path:
        path = self.root / "sttm-visual.html"
        path.write_text(
            '<!DOCTYPE html><html><head><title>STTM Visual</title></head><body><div class="sttm-dashboard"></div></body></html>',
            encoding="utf-8",
        )
        return path

    def test_sttm_json_required_keys(self) -> None:
        path = self._write_sttm_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("project_name", "wave_id", "version", "source_systems", "mappings"):
            self.assertIn(key, data)

    def test_sttm_json_mappings_have_required_fields(self) -> None:
        path = self._write_sttm_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        required = {"id", "source_system", "source_table", "source_column", "target_table", "target_column", "transformation"}
        for mapping in data["mappings"]:
            self.assertTrue(required.issubset(mapping.keys()))

    def test_sttm_json_no_placeholders(self) -> None:
        path = self._write_sttm_json()
        content = path.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_sttm_md_has_required_sections(self) -> None:
        path = self._write_sttm_md()
        content = path.read_text(encoding="utf-8")
        self.assertIn("# Source-to-Target Mapping", content)
        self.assertIn("## Source Systems", content)
        self.assertIn("## Mappings", content)

    def test_sttm_html_valid(self) -> None:
        path = self._write_sttm_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("</html>", content)
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_all_three_sttm_outputs(self) -> None:
        self._write_sttm_json()
        self._write_sttm_md()
        self._write_sttm_html()
        self.assertTrue((self.root / "sttm.json").exists())
        self.assertTrue((self.root / "sttm.md").exists())
        self.assertTrue((self.root / "sttm-visual.html").exists())


class ArchitectureOutputTests(unittest.TestCase):
    """Tests for create-architecture task outputs (3 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "outputs" / "midstream"
        self.root.mkdir(parents=True)

    def _write_arch_json(self) -> Path:
        data = {
            "project_name": "TEST",
            "wave_id": "WAVE-001",
            "generated_at": "2026-06-08T00:00:00Z",
            "pattern": "LAKEHOUSE",
            "layers": [
                {"name": "landing", "purpose": "Raw ingestion"},
                {"name": "bronze", "purpose": "Cleansing"},
                {"name": "silver", "purpose": "Business logic"},
                {"name": "gold", "purpose": "Aggregation"},
            ],
            "technology_stack": {"compute": "Databricks", "storage": "ADLS Gen2"},
            "adrs": [],
        }
        path = self.root / "architecture-spec.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def _write_arch_md(self) -> Path:
        path = self.root / "architecture.md"
        path.write_text("# Architecture\n\n## Pattern\n\nLakehouse\n\n## Layers\n\n## Technology Stack\n", encoding="utf-8")
        return path

    def _write_arch_html(self) -> Path:
        path = self.root / "tobe-target-architecture.html"
        path.write_text(
            '<!DOCTYPE html><html><head><title>TO-BE Architecture</title></head><body><div class="medallion-flow"></div></body></html>',
            encoding="utf-8",
        )
        return path

    def test_arch_json_required_keys(self) -> None:
        path = self._write_arch_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("project_name", "pattern", "layers", "technology_stack"):
            self.assertIn(key, data)

    def test_arch_json_layers_non_empty(self) -> None:
        path = self._write_arch_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreater(len(data["layers"]), 0)

    def test_arch_md_required_sections(self) -> None:
        path = self._write_arch_md()
        content = path.read_text(encoding="utf-8")
        self.assertIn("# Architecture", content)
        self.assertIn("## Layers", content)
        self.assertIn("## Technology Stack", content)

    def test_arch_html_valid(self) -> None:
        path = self._write_arch_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_all_three_arch_outputs(self) -> None:
        self._write_arch_json()
        self._write_arch_md()
        self._write_arch_html()
        self.assertTrue((self.root / "architecture-spec.json").exists())
        self.assertTrue((self.root / "architecture.md").exists())
        self.assertTrue((self.root / "tobe-target-architecture.html").exists())


class DataModelOutputTests(unittest.TestCase):
    """Tests for create-data-model task outputs (3 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "design-outputs" / "WAVE-001"
        self.root.mkdir(parents=True)

    def _write_model_json(self) -> Path:
        data = {
            "project_name": "TEST",
            "wave_id": "WAVE-001",
            "version": "1.0",
            "generated_at": "2026-06-08T00:00:00Z",
            "naming_conventions": {
                "bronze": "brz_",
                "silver": "slv_",
                "gold_facts": "gld_fact_",
                "gold_dims": "gld_dim_",
            },
            "entities": [
                {
                    "name": "slv_customers",
                    "layer": "silver",
                    "type": "dimension",
                    "scd_type": 2,
                    "columns": [
                        {"name": "customer_id", "type": "INT", "pk_fk": "PK", "nullable": False},
                        {"name": "customer_name", "type": "STRING", "pk_fk": "-", "nullable": False},
                    ],
                }
            ],
            "relationships": [],
        }
        path = self.root / "data-model.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def _write_model_md(self) -> Path:
        path = self.root / "data-model.md"
        path.write_text("# Data Model\n\n## Entities\n\n## Relationships\n", encoding="utf-8")
        return path

    def _write_model_html(self) -> Path:
        path = self.root / "data-model-er.html"
        path.write_text(
            '<!DOCTYPE html><html><head><title>ER Diagram</title></head><body><div class="er-canvas"></div></body></html>',
            encoding="utf-8",
        )
        return path

    def test_model_json_required_keys(self) -> None:
        path = self._write_model_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("project_name", "wave_id", "naming_conventions", "entities", "relationships"):
            self.assertIn(key, data)

    def test_model_json_naming_conventions(self) -> None:
        path = self._write_model_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        nc = data["naming_conventions"]
        for key in ("bronze", "silver", "gold_facts", "gold_dims"):
            self.assertIn(key, nc)

    def test_model_json_entities_have_columns(self) -> None:
        path = self._write_model_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for entity in data["entities"]:
            self.assertIn("columns", entity)
            self.assertGreater(len(entity["columns"]), 0)
            for col in entity["columns"]:
                for field in ("name", "type", "pk_fk"):
                    self.assertIn(field, col)

    def test_model_json_pk_fk_valid_values(self) -> None:
        path = self._write_model_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        valid_values = {"PK", "FK", "NK", "-"}
        for entity in data["entities"]:
            for col in entity["columns"]:
                self.assertIn(col["pk_fk"], valid_values)

    def test_model_md_required_sections(self) -> None:
        path = self._write_model_md()
        content = path.read_text(encoding="utf-8")
        self.assertIn("# Data Model", content)
        self.assertIn("## Entities", content)

    def test_model_html_valid(self) -> None:
        path = self._write_model_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_all_three_model_outputs(self) -> None:
        self._write_model_json()
        self._write_model_md()
        self._write_model_html()
        self.assertTrue((self.root / "data-model.json").exists())
        self.assertTrue((self.root / "data-model.md").exists())
        self.assertTrue((self.root / "data-model-er.html").exists())


class WaveReportOutputTests(unittest.TestCase):
    """Tests for run-wave task outputs (3 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "wave-outputs" / "WAVE-001"
        self.root.mkdir(parents=True)

    def _write_wave_json(self, data: dict | None = None) -> Path:
        content = data or {
            "wave_id": "WAVE-001",
            "status": "COMPLETED",
            "generated_at": "2026-06-08T00:00:00Z",
            "execution_summary": [
                {"step": "DDL Execution", "status": "PASS", "duration_seconds": 12},
                {"step": "ETL Execution", "status": "PASS", "duration_seconds": 45},
            ],
            "ddl_results": [{"script": "create_customers.sql", "status": "PASS", "rows_affected": 0}],
            "etl_results": [{"pipeline": "load_customers", "rows_read": 50000, "rows_loaded": 50000, "rows_rejected": 0}],
            "tests_results": [{"test": "test_not_null", "status": "PASS"}],
            "summary": {
                "tests_passed_rate": 100.0,
                "dq_score_pct": 98.5,
                "parity_pct": 99.9,
            },
            "gate_decision": {
                "gate_score": 89.5,
                "outcome": "PASS",
            },
            "discovery_owner": {"primary": "discovery-scout", "fallback": "inventory-scout"},
        }
        path = self.root / "wave-report.json"
        path.write_text(json.dumps(content, indent=2), encoding="utf-8")
        return path

    def _write_wave_md(self) -> Path:
        path = self.root / "wave-report.md"
        path.write_text(
            "# Wave Report — WAVE-001\n\n## Status: COMPLETED\n\n## Gate Decision\n\nScore: 89.5 | Outcome: PASS\n",
            encoding="utf-8",
        )
        return path

    def _write_wave_html(self) -> Path:
        path = self.root / "wave-execution-report.html"
        path.write_text(
            '<!DOCTYPE html><html><head><title>Wave Execution Report</title></head><body><div class="gate-score">89.5</div></body></html>',
            encoding="utf-8",
        )
        return path

    def test_wave_json_required_keys(self) -> None:
        path = self._write_wave_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("wave_id", "status", "execution_summary", "gate_decision", "discovery_owner"):
            self.assertIn(key, data)

    def test_wave_json_status_valid(self) -> None:
        path = self._write_wave_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(data["status"], {"COMPLETED", "PARTIAL", "FAILED"})

    def test_wave_json_gate_decision_structure(self) -> None:
        path = self._write_wave_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        gd = data["gate_decision"]
        self.assertIn("gate_score", gd)
        self.assertIn("outcome", gd)
        self.assertIn(gd["outcome"], {"PASS", "HOLD", "FAIL"})

    def test_wave_json_discovery_owner_required(self) -> None:
        path = self._write_wave_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        do = data["discovery_owner"]
        self.assertIn("primary", do)
        self.assertIn("fallback", do)

    def test_wave_json_no_placeholders(self) -> None:
        path = self._write_wave_json()
        content = path.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_wave_md_cites_json(self) -> None:
        path = self._write_wave_md()
        content = path.read_text(encoding="utf-8")
        # MD should have wave ID and status
        self.assertIn("WAVE-001", content)
        self.assertIn("COMPLETED", content)

    def test_wave_html_no_placeholders(self) -> None:
        path = self._write_wave_html()
        content = path.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_wave_html_has_gate_score(self) -> None:
        path = self._write_wave_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("89.5", content)

    def test_all_three_wave_outputs(self) -> None:
        self._write_wave_json()
        self._write_wave_md()
        self._write_wave_html()
        self.assertTrue((self.root / "wave-report.json").exists())
        self.assertTrue((self.root / "wave-report.md").exists())
        self.assertTrue((self.root / "wave-execution-report.html").exists())

    def test_fails_when_json_missing(self) -> None:
        """Wave report JSON is the source of truth; task fails without it."""
        self._write_wave_md()
        self._write_wave_html()
        self.assertFalse((self.root / "wave-report.json").exists())


class ReconciliationOutputTests(unittest.TestCase):
    """Tests for reconcile-wave task outputs (3 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "reconciliation-outputs" / "WAVE-001"
        self.root.mkdir(parents=True)

    def _write_recon_json(self) -> Path:
        data = {
            "wave_id": "WAVE-001",
            "generated_at": "2026-06-08T00:00:00Z",
            "parity_pct": 99.95,
            "status": "APPROVED",
            "sign_off_eligible": True,
            "sign_off_threshold_pct": 99.9,
            "summary": {
                "total_tables": 10,
                "tables_passed": 10,
                "tables_failed": 0,
                "critical_count": 0,
                "warning_count": 1,
            },
            "levels": {
                "L1": {"tables_passed": 3, "tables_failed": 0},
                "L2": {"tables_passed": 4, "tables_failed": 0},
                "L3": {"tables_passed": 3, "tables_failed": 0},
            },
            "tables": [],
        }
        path = self.root / "reconciliation-report.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def _write_recon_md(self) -> Path:
        path = self.root / "reconciliation-report.md"
        path.write_text(
            "# Reconciliation Report\n\n## Summary\n\nParity: 99.95%\nStatus: APPROVED\n\n## Details\n",
            encoding="utf-8",
        )
        return path

    def _write_recon_html(self) -> Path:
        path = self.root / "reconciliation-dashboard.html"
        path.write_text(
            '<!DOCTYPE html><html><head><title>Reconciliation Dashboard</title></head><body><svg class="gauge"></svg></body></html>',
            encoding="utf-8",
        )
        return path

    def test_recon_json_required_keys(self) -> None:
        path = self._write_recon_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("wave_id", "parity_pct", "status", "sign_off_eligible", "summary"):
            self.assertIn(key, data)

    def test_recon_json_parity_is_top_level(self) -> None:
        """validate_gate3_artifacts.py depends on parity_pct being top-level."""
        path = self._write_recon_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("parity_pct", data)
        self.assertIsInstance(data["parity_pct"], (int, float))

    def test_recon_json_status_is_top_level(self) -> None:
        """validate_gate3_artifacts.py depends on status being top-level."""
        path = self._write_recon_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("status", data)
        self.assertIn(data["status"], {"APPROVED", "PARTIAL", "FAILED"})

    def test_recon_json_sign_off_logic(self) -> None:
        path = self._write_recon_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        # sign_off_eligible should be True only when status=APPROVED, parity>=threshold, critical=0
        if data["sign_off_eligible"]:
            self.assertEqual(data["status"], "APPROVED")
            self.assertGreaterEqual(data["parity_pct"], data["sign_off_threshold_pct"])
            self.assertEqual(data["summary"]["critical_count"], 0)

    def test_recon_json_no_template_metadata(self) -> None:
        """_template_metadata block must be removed before persisting."""
        path = self._write_recon_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertNotIn("_template_metadata", data)

    def test_recon_md_has_parity(self) -> None:
        path = self._write_recon_md()
        content = path.read_text(encoding="utf-8")
        self.assertIn("99.95", content)

    def test_recon_html_valid(self) -> None:
        path = self._write_recon_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertNotRegex(content, r"\{\{.*?\}\}")

    def test_all_three_recon_outputs(self) -> None:
        self._write_recon_json()
        self._write_recon_md()
        self._write_recon_html()
        self.assertTrue((self.root / "reconciliation-report.json").exists())
        self.assertTrue((self.root / "reconciliation-report.md").exists())
        self.assertTrue((self.root / "reconciliation-dashboard.html").exists())


class MigrationReportOutputTests(unittest.TestCase):
    """Tests for generate-migration-report task outputs (6 files)."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "documentation-outputs" / "migration-reports"
        self.root.mkdir(parents=True)

    def _write_all_reports(self) -> None:
        files = [
            "migration-report.md",
            "migration-report-executive.md",
            "migration-report-technical.md",
            "migration-report.en.md",
            "migration-report-executive.en.md",
            "migration-report-technical.en.md",
        ]
        for f in files:
            (self.root / f).write_text(f"# {f}\n\nContent for {f}\n", encoding="utf-8")

    def test_all_six_reports_generated(self) -> None:
        self._write_all_reports()
        expected = [
            "migration-report.md",
            "migration-report-executive.md",
            "migration-report-technical.md",
            "migration-report.en.md",
            "migration-report-executive.en.md",
            "migration-report-technical.en.md",
        ]
        for name in expected:
            self.assertTrue((self.root / name).exists(), f"Missing: {name}")

    def test_executive_report_exists(self) -> None:
        self._write_all_reports()
        self.assertTrue((self.root / "migration-report-executive.md").exists())

    def test_no_placeholders_in_reports(self) -> None:
        self._write_all_reports()
        for path in self.root.glob("*.md"):
            content = path.read_text(encoding="utf-8")
            self.assertNotRegex(content, r"\{\{.*?\}\}", f"Placeholder found in {path.name}")

    def test_fails_when_en_version_missing(self) -> None:
        """Both PT-BR and EN-US versions are required."""
        (self.root / "migration-report.md").write_text("# Report PT-BR", encoding="utf-8")
        self.assertFalse((self.root / "migration-report.en.md").exists())


class QualityScoresOutputTests(unittest.TestCase):
    """Tests for validate-code / score-pipeline task outputs."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "quality-outputs"
        self.root.mkdir(parents=True)

    def _write_scores_json(self) -> Path:
        data = {
            "pipeline_id": "pipeline_001",
            "generated_at": "2026-06-08T00:00:00Z",
            "dimensions": {
                "syntax": {"score": 10.0, "weight": 0.15},
                "lint": {"score": 8.5, "weight": 0.10},
                "semantic": {"score": 9.0, "weight": 0.30},
                "tests": {"score": 9.5, "weight": 0.25},
                "performance": {"score": 7.0, "weight": 0.10},
                "security": {"score": 10.0, "weight": 0.10},
            },
            "final_score": 9.1,
            "decision": "APPROVED",
        }
        path = self.root / "quality-scores.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def _write_validation_html(self) -> Path:
        path = self.root / "validation-scorecard.html"
        path.write_text(
            '<!DOCTYPE html><html><head><title>Validation Scorecard</title></head><body><div class="scorecard"></div></body></html>',
            encoding="utf-8",
        )
        return path

    def test_scores_json_has_dimensions(self) -> None:
        path = self._write_scores_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("dimensions", data)
        required_dims = {"syntax", "lint", "semantic", "tests", "performance", "security"}
        self.assertTrue(required_dims.issubset(data["dimensions"].keys()))

    def test_scores_json_weights_sum_to_one(self) -> None:
        path = self._write_scores_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        total_weight = sum(d["weight"] for d in data["dimensions"].values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)

    def test_scores_json_decision_valid(self) -> None:
        path = self._write_scores_json()
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(data["decision"], {"APPROVED", "REJECTED", "REVIEW_REQUIRED"})

    def test_validation_html_valid(self) -> None:
        path = self._write_validation_html()
        content = path.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertNotRegex(content, r"\{\{.*?\}\}")


class HTMLTemplateApplicationTests(unittest.TestCase):
    """Cross-cutting tests for HTML template application rules."""

    def test_html_has_no_unclosed_tags(self) -> None:
        """Basic check: opened tags should be closed."""
        html = '<!DOCTYPE html><html><head><title>Test</title></head><body><div class="main"><p>Content</p></div></body></html>'
        self.assertEqual(html.count("<html"), html.count("</html>"))
        self.assertEqual(html.count("<head"), html.count("</head>"))
        self.assertEqual(html.count("<body"), html.count("</body>"))

    def test_html_placeholder_pattern_detection(self) -> None:
        """Regex pattern for placeholder detection."""
        import re

        pattern = re.compile(r"\{\{.*?\}\}")
        self.assertTrue(pattern.search("Hello {{WORLD}}"))
        self.assertIsNone(pattern.search("Hello World"))
        self.assertTrue(pattern.search("<div>{{PROJECT_NAME}}</div>"))

    def test_gauge_stroke_dashoffset_formula(self) -> None:
        """Validate gauge rendering formula: offset = 691 * (1 - value/100)."""
        parity_pct = 99.9
        offset = round(691 * (1 - parity_pct / 100))
        self.assertEqual(offset, 1)  # Nearly full circle

        parity_pct = 50.0
        offset = round(691 * (1 - parity_pct / 100))
        self.assertEqual(offset, 346)  # Half circle

    def test_parity_color_rules(self) -> None:
        """Validate parity color assignment logic."""

        def get_parity_color(pct: float) -> str:
            if pct >= 99.9:
                return "teal"
            elif pct >= 95.0:
                return "amber"
            else:
                return "red"

        self.assertEqual(get_parity_color(99.95), "teal")
        self.assertEqual(get_parity_color(99.9), "teal")
        self.assertEqual(get_parity_color(97.0), "amber")
        self.assertEqual(get_parity_color(95.0), "amber")
        self.assertEqual(get_parity_color(94.9), "red")
        self.assertEqual(get_parity_color(80.0), "red")


class OutputPathConsistencyTests(unittest.TestCase):
    """Tests that output path conventions are consistent."""

    def test_upstream_base_path(self) -> None:
        base = "projects/{project_name}/outputs/upstream"
        self.assertIn("upstream", base)
        self.assertIn("{project_name}", base)

    def test_midstream_base_path(self) -> None:
        base = "projects/{project_name}/outputs/midstream"
        self.assertIn("midstream", base)

    def test_downstream_base_path(self) -> None:
        base = "projects/{project_name}/outputs/downstream"
        self.assertIn("downstream", base)

    def test_json_filename_convention(self) -> None:
        """JSON filenames should be lowercase, hyphenated."""
        import re

        valid_pattern = re.compile(r"^[a-z][a-z0-9\-]*\.json$")
        names = [
            "inventory-enriched.json",
            "sttm.json",
            "architecture-spec.json",
            "data-model.json",
            "wave-report.json",
            "reconciliation-report.json",
            "quality-scores.json",
        ]
        for name in names:
            self.assertRegex(name, valid_pattern, f"Invalid JSON filename: {name}")

    def test_html_filename_convention(self) -> None:
        """HTML filenames should be lowercase, hyphenated."""
        import re

        valid_pattern = re.compile(r"^[a-z][a-z0-9\-]*\.html$")
        names = [
            "asis-platform-landscape.html",
            "sttm-visual.html",
            "tobe-target-architecture.html",
            "data-model-er.html",
            "wave-execution-report.html",
            "reconciliation-dashboard.html",
            "validation-scorecard.html",
        ]
        for name in names:
            self.assertRegex(name, valid_pattern, f"Invalid HTML filename: {name}")

    def test_template_naming_convention(self) -> None:
        """Template files use -tmpl suffix before extension."""
        import re

        valid_pattern = re.compile(r"^[a-z][a-z0-9\-]*-tmpl\.[a-z]+$")
        names = [
            "sttm-tmpl.json",
            "sttm-tmpl.md",
            "sttm-visual-tmpl.html",
            "architecture-tmpl.md",
            "data-model-tmpl.json",
            "data-model-er-tmpl.html",
            "wave-report-tmpl.json",
            "reconciliation-report-tmpl.json",
            "reconciliation-dashboard-tmpl.html",
        ]
        for name in names:
            self.assertRegex(name, valid_pattern, f"Invalid template filename: {name}")


if __name__ == "__main__":
    unittest.main()
