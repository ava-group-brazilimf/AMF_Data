"""
test_validate_ast_artifacts.py — Tests for Gate AST artifact validation (Trilha 9)
"""
import json
import pytest
from pathlib import Path

from src.shared.scripts.validate_gate3_artifacts import validate_ast_artifacts


class TestValidateASTArtifacts:
    def test_passes_when_no_canonical_model(self, tmp_path):
        """AST validation should pass when canonical-model.json doesn't exist yet."""
        result = validate_ast_artifacts(1, tmp_path)
        assert result.is_valid is True

    def test_passes_with_valid_canonical_model(self, tmp_path):
        model = {
            "pipeline_id": "pip1",
            "pipeline_name": "orders",
            "source_platform": "SQL Server",
            "target_platform": "Fabric",
        }
        (tmp_path / "canonical-model.json").write_text(json.dumps(model), encoding="utf-8")
        result = validate_ast_artifacts(1, tmp_path)
        assert result.is_valid is True

    def test_fails_with_missing_required_key(self, tmp_path):
        # Missing source_platform
        model = {"pipeline_id": "pip1", "pipeline_name": "orders"}
        (tmp_path / "canonical-model.json").write_text(json.dumps(model), encoding="utf-8")
        result = validate_ast_artifacts(1, tmp_path)
        assert result.is_valid is False
        assert any("source_platform" in m for m in result.missing)

    def test_fails_with_invalid_json(self, tmp_path):
        (tmp_path / "canonical-model.json").write_text("NOT JSON", encoding="utf-8")
        result = validate_ast_artifacts(1, tmp_path)
        assert result.is_valid is False

    def test_passes_for_gate_2_without_canonical(self, tmp_path):
        result = validate_ast_artifacts(2, tmp_path)
        assert result.is_valid is True

    def test_passes_for_gate_3_without_canonical(self, tmp_path):
        result = validate_ast_artifacts(3, tmp_path)
        assert result.is_valid is True

    def test_gate_returns_correct_gate_number(self, tmp_path):
        result = validate_ast_artifacts(2, tmp_path)
        assert result.gate == 2

    def test_canonical_model_key_in_present(self, tmp_path):
        model = {
            "pipeline_id": "pip1",
            "pipeline_name": "orders",
            "source_platform": "SSIS",
        }
        (tmp_path / "canonical-model.json").write_text(json.dumps(model), encoding="utf-8")
        result = validate_ast_artifacts(1, tmp_path)
        assert any("pipeline_id" in p for p in result.present)

    def test_sttm_and_lineage_detected_when_present(self, tmp_path):
        model = {
            "pipeline_id": "pip1",
            "pipeline_name": "orders",
            "source_platform": "SSIS",
        }
        (tmp_path / "canonical-model.json").write_text(json.dumps(model), encoding="utf-8")
        (tmp_path / "column-lineage.json").write_text("{}", encoding="utf-8")
        (tmp_path / "sttm.md").write_text("# STTM", encoding="utf-8")
        # Gate 2 is when lineage + sttm are expected
        result = validate_ast_artifacts(2, tmp_path)
        assert "column-lineage.json" in result.present
        assert "sttm.md" in result.present
