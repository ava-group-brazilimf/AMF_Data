"""Tests for scripts/data_contract_validator.py"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.data_contract_validator import (
    DataContract,
    FieldSpec,
    QualityExpectation,
    ContractSchemaResult,
    ContractEvalResult,
    QualityCheckResult,
    parse_contract,
    validate_contract_schema,
    evaluate_contract,
    load_contract,
    _compare,
)

# Check if yaml is available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_CONTRACT_DICT = {
    "entity": "orders",
    "version": "1.0",
    "owner": "data-team",
    "tier": "CRITICAL",
    "description": "Orders fact table",
    "fields": [
        {"name": "order_id", "dtype": "bigint", "nullable": False, "pii": False},
        {"name": "customer_name", "dtype": "string", "nullable": True, "pii": True},
        {"name": "amount", "dtype": "decimal", "nullable": False},
        {"name": "created_at", "dtype": "timestamp"},
    ],
    "quality": [
        {"metric": "completeness", "operator": ">=", "threshold": 0.99},
        {"metric": "row_parity", "operator": ">=", "threshold": 1.0},
        {"metric": "dq_score", "operator": ">=", "threshold": 0.98},
    ],
    "sla_freshness_hours": 24.0,
}

MINIMAL_CONTRACT_DICT = {
    "entity": "lookups",
    "owner": "platform",
    "tier": "REFERENCE",
    "fields": [
        {"name": "code", "dtype": "string"},
    ],
}


# ---------------------------------------------------------------------------
# parse_contract
# ---------------------------------------------------------------------------

class TestParseContract:
    def test_full_contract(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        assert c.entity == "orders"
        assert c.tier == "CRITICAL"
        assert c.owner == "data-team"
        assert len(c.fields) == 4
        assert len(c.quality) == 3
        assert c.sla_freshness_hours == 24.0

    def test_minimal_contract(self):
        c = parse_contract(MINIMAL_CONTRACT_DICT)
        assert c.entity == "lookups"
        assert c.tier == "REFERENCE"
        assert len(c.fields) == 1
        assert len(c.quality) == 0

    def test_defaults(self):
        c = parse_contract({"fields": []})
        assert c.entity == "unknown"
        assert c.version == "1.0"
        assert c.tier == "STANDARD"

    def test_field_type_alias(self):
        data = {"entity": "t", "owner": "x", "tier": "STANDARD", "fields": [{"name": "a", "type": "int"}]}
        c = parse_contract(data)
        assert c.fields[0].dtype == "int"

    def test_pii_field(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        pii_fields = [f for f in c.fields if f.pii]
        assert len(pii_fields) == 1
        assert pii_fields[0].name == "customer_name"


# ---------------------------------------------------------------------------
# validate_contract_schema
# ---------------------------------------------------------------------------

class TestValidateContractSchema:
    def test_valid(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = validate_contract_schema(c)
        assert result.valid
        assert result.entity == "orders"
        assert len(result.violations) == 0

    def test_missing_entity(self):
        c = DataContract(entity="", owner="team", fields=[FieldSpec("a", "string")])
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "entity" in rules

    def test_missing_owner(self):
        c = DataContract(entity="test", owner="", fields=[FieldSpec("a", "string")])
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "owner" in rules

    def test_invalid_tier(self):
        c = DataContract(entity="test", owner="team", tier="INVALID", fields=[FieldSpec("a", "string")])
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "tier" in rules

    def test_no_fields(self):
        c = DataContract(entity="test", owner="team")
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "fields" in rules

    def test_invalid_dtype(self):
        c = DataContract(
            entity="test", owner="team",
            fields=[FieldSpec("a", "varchar")],
        )
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "field_dtype" in rules

    def test_invalid_quality_metric(self):
        c = DataContract(
            entity="test", owner="team",
            fields=[FieldSpec("a", "string")],
            quality=[QualityExpectation("invalid_metric", ">=", 0.9)],
        )
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "quality_metric" in rules

    def test_invalid_quality_operator(self):
        c = DataContract(
            entity="test", owner="team",
            fields=[FieldSpec("a", "string")],
            quality=[QualityExpectation("completeness", "~=", 0.9)],
        )
        result = validate_contract_schema(c)
        assert not result.valid
        rules = [v.rule for v in result.violations]
        assert "quality_operator" in rules

    def test_str_valid(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = validate_contract_schema(c)
        assert "VALID" in str(result)

    def test_str_invalid(self):
        c = DataContract(entity="", owner="")
        result = validate_contract_schema(c)
        assert "INVALID" in str(result)


# ---------------------------------------------------------------------------
# evaluate_contract
# ---------------------------------------------------------------------------

class TestEvaluateContract:
    def test_all_pass(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = evaluate_contract(c, completeness=0.995, row_parity=1.0, dq_score=0.99)
        assert result.passed
        assert result.entity == "orders"
        assert len(result.checks) == 3

    def test_one_fails(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = evaluate_contract(c, completeness=0.90, row_parity=1.0, dq_score=0.99)
        assert not result.passed
        failed = [ch for ch in result.checks if not ch.passed]
        assert len(failed) == 1
        assert failed[0].metric == "completeness"

    def test_missing_metric(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = evaluate_contract(c, completeness=0.99)
        assert not result.passed
        # row_parity and dq_score are missing → fail
        failed = [ch for ch in result.checks if not ch.passed]
        assert len(failed) == 2

    def test_no_quality_rules(self):
        c = parse_contract(MINIMAL_CONTRACT_DICT)
        result = evaluate_contract(c, completeness=0.99)
        assert result.passed  # No rules = vacuously true
        assert len(result.checks) == 0

    def test_str_pass(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = evaluate_contract(c, completeness=0.995, row_parity=1.0, dq_score=0.99)
        s = str(result)
        assert "PASS" in s
        assert "✓" in s

    def test_str_fail(self):
        c = parse_contract(VALID_CONTRACT_DICT)
        result = evaluate_contract(c, completeness=0.5, row_parity=0.5, dq_score=0.5)
        s = str(result)
        assert "FAIL" in s
        assert "✗" in s


# ---------------------------------------------------------------------------
# _compare
# ---------------------------------------------------------------------------

class TestCompare:
    def test_gte(self):
        assert _compare(0.99, ">=", 0.99)
        assert _compare(1.0, ">=", 0.99)
        assert not _compare(0.98, ">=", 0.99)

    def test_lte(self):
        assert _compare(0.01, "<=", 0.01)
        assert not _compare(0.02, "<=", 0.01)

    def test_eq(self):
        assert _compare(1.0, "==", 1.0)
        assert not _compare(1.1, "==", 1.0)

    def test_gt(self):
        assert _compare(1.1, ">", 1.0)
        assert not _compare(1.0, ">", 1.0)

    def test_lt(self):
        assert _compare(0.9, "<", 1.0)
        assert not _compare(1.0, "<", 1.0)


# ---------------------------------------------------------------------------
# load_contract (YAML file)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_YAML, reason="pyyaml not installed")
class TestLoadContract:
    def test_load_from_yaml(self, tmp_path):
        import yaml
        contract_path = tmp_path / "orders.yaml"
        contract_path.write_text(yaml.dump(VALID_CONTRACT_DICT), encoding="utf-8")
        c = load_contract(contract_path)
        assert c.entity == "orders"
        assert c.tier == "CRITICAL"
        assert len(c.fields) == 4

    def test_load_minimal(self, tmp_path):
        import yaml
        contract_path = tmp_path / "lookups.yaml"
        contract_path.write_text(yaml.dump(MINIMAL_CONTRACT_DICT), encoding="utf-8")
        c = load_contract(contract_path)
        assert c.entity == "lookups"
