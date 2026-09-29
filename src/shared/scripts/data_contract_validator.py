"""
data_contract_validator.py
Declarative data contract validation for migration entities.

A data contract is a YAML file describing quality expectations for an entity:
owner, tier, schema fields with types, and quality rules. This validator
checks that contracts are well-formed and evaluates measured metrics against
the declared expectations using quality_thresholds.py.

Usage:
    from scripts.data_contract_validator import (
        DataContract, load_contract, validate_contract_schema,
        evaluate_contract,
    )

    contract = load_contract(Path("contracts/orders.yaml"))
    schema_result = validate_contract_schema(contract)
    eval_result = evaluate_contract(contract, measured_completeness=0.99, ...)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class FieldSpec:
    name: str
    dtype: str
    nullable: bool = True
    pii: bool = False
    description: str = ""


@dataclass
class QualityExpectation:
    metric: str          # completeness | uniqueness | freshness | row_parity | dq_score
    operator: str        # >=, <=, ==, >
    threshold: float


@dataclass
class DataContract:
    """Declarative data contract for a migration entity."""
    entity: str
    version: str = "1.0"
    owner: str = ""
    tier: str = "STANDARD"         # CRITICAL | STANDARD | REFERENCE
    description: str = ""
    fields: list[FieldSpec] = field(default_factory=list)
    quality: list[QualityExpectation] = field(default_factory=list)
    sla_freshness_hours: float | None = None


VALID_TIERS = {"CRITICAL", "STANDARD", "REFERENCE"}
VALID_OPERATORS = {">=", "<=", "==", ">", "<"}
VALID_METRICS = {"completeness", "uniqueness", "freshness", "row_parity", "dq_score", "null_rate"}
VALID_DTYPES = {"string", "int", "bigint", "float", "double", "decimal", "boolean", "date", "timestamp", "binary"}

REQUIRED_CONTRACT_KEYS = {"entity", "owner", "tier", "fields"}


@dataclass
class ContractViolation:
    rule: str
    detail: str


@dataclass
class ContractSchemaResult:
    """Result of validating the contract YAML structure itself."""
    entity: str
    valid: bool
    violations: list[ContractViolation] = field(default_factory=list)

    def __str__(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        lines = [f"Contract [{self.entity}]: {status}"]
        for v in self.violations:
            lines.append(f"  - {v.rule}: {v.detail}")
        return "\n".join(lines)


@dataclass
class QualityCheckResult:
    metric: str
    expected: str       # e.g. ">= 0.99"
    actual: float
    passed: bool


@dataclass
class ContractEvalResult:
    """Result of evaluating measured metrics against contract expectations."""
    entity: str
    passed: bool
    checks: list[QualityCheckResult] = field(default_factory=list)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"Contract Eval [{self.entity}]: {status}"]
        for c in self.checks:
            mark = "✓" if c.passed else "✗"
            lines.append(f"  {mark} {c.metric}: {c.actual} (expected {c.expected})")
        return "\n".join(lines)


def load_contract(path: Path) -> DataContract:
    """Load a data contract from a YAML file."""
    if not HAS_YAML:
        raise ImportError("pyyaml is required: pip install pyyaml")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return parse_contract(raw)


def parse_contract(raw: dict[str, Any]) -> DataContract:
    """Parse a raw dict (from YAML) into a DataContract."""
    fields = []
    for f in raw.get("fields", []):
        fields.append(FieldSpec(
            name=f["name"],
            dtype=f.get("dtype", f.get("type", "string")),
            nullable=f.get("nullable", True),
            pii=f.get("pii", False),
            description=f.get("description", ""),
        ))

    quality = []
    for q in raw.get("quality", []):
        quality.append(QualityExpectation(
            metric=q["metric"],
            operator=q.get("operator", ">="),
            threshold=float(q["threshold"]),
        ))

    return DataContract(
        entity=raw.get("entity", "unknown"),
        version=str(raw.get("version", "1.0")),
        owner=raw.get("owner", ""),
        tier=raw.get("tier", "STANDARD").upper(),
        description=raw.get("description", ""),
        fields=fields,
        quality=quality,
        sla_freshness_hours=raw.get("sla_freshness_hours"),
    )


def validate_contract_schema(contract: DataContract) -> ContractSchemaResult:
    """Validate that a data contract has correct structure and values."""
    violations: list[ContractViolation] = []

    if not contract.entity or contract.entity == "unknown":
        violations.append(ContractViolation("entity", "Entity name is required"))

    if not contract.owner:
        violations.append(ContractViolation("owner", "Owner is required"))

    if contract.tier not in VALID_TIERS:
        violations.append(ContractViolation(
            "tier", f"Invalid tier '{contract.tier}'. Must be one of {VALID_TIERS}",
        ))

    if not contract.fields:
        violations.append(ContractViolation("fields", "At least one field is required"))

    for f in contract.fields:
        if not f.name:
            violations.append(ContractViolation("field_name", "Field name cannot be empty"))
        if f.dtype.lower() not in VALID_DTYPES:
            violations.append(ContractViolation(
                "field_dtype", f"Field '{f.name}' has invalid dtype '{f.dtype}'. Valid: {VALID_DTYPES}",
            ))

    for q in contract.quality:
        if q.metric not in VALID_METRICS:
            violations.append(ContractViolation(
                "quality_metric", f"Invalid metric '{q.metric}'. Valid: {VALID_METRICS}",
            ))
        if q.operator not in VALID_OPERATORS:
            violations.append(ContractViolation(
                "quality_operator", f"Invalid operator '{q.operator}'. Valid: {VALID_OPERATORS}",
            ))

    return ContractSchemaResult(
        entity=contract.entity,
        valid=len(violations) == 0,
        violations=violations,
    )


def _compare(actual: float, operator: str, threshold: float) -> bool:
    """Apply comparison operator."""
    ops = {
        ">=": lambda a, t: a >= t,
        "<=": lambda a, t: a <= t,
        "==": lambda a, t: abs(a - t) < 1e-9,
        ">": lambda a, t: a > t,
        "<": lambda a, t: a < t,
    }
    return ops[operator](actual, threshold)


def evaluate_contract(
    contract: DataContract,
    **measured_metrics: float,
) -> ContractEvalResult:
    """Evaluate measured metrics against contract quality expectations.

    Args:
        contract: The data contract to evaluate against.
        **measured_metrics: Metric name → actual measured value.
            Example: completeness=0.99, row_parity=1.0, dq_score=0.97

    Returns:
        ContractEvalResult with per-check pass/fail.
    """
    checks: list[QualityCheckResult] = []
    all_pass = True

    for expectation in contract.quality:
        actual = measured_metrics.get(expectation.metric)
        if actual is None:
            checks.append(QualityCheckResult(
                metric=expectation.metric,
                expected=f"{expectation.operator} {expectation.threshold}",
                actual=0.0,
                passed=False,
            ))
            all_pass = False
            continue

        passed = _compare(actual, expectation.operator, expectation.threshold)
        checks.append(QualityCheckResult(
            metric=expectation.metric,
            expected=f"{expectation.operator} {expectation.threshold}",
            actual=actual,
            passed=passed,
        ))
        if not passed:
            all_pass = False

    return ContractEvalResult(
        entity=contract.entity,
        passed=all_pass,
        checks=checks,
    )
