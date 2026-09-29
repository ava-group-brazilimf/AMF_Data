"""
validate_gate3_artifacts.py
B-006 — validates Gate 3 artifact package (downstream wave output) before
production promotion.

Also supports Gate 1 and Gate 2 via validate_gate_requirements(gate, path).

Usage (standalone):
    python -m scripts.validate_gate3_artifacts <wave_output_dir>
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Canonical artifact requirements (mirrors orchestrator core-config.yaml) ---

GATE_3_REQUIRED: list[str] = [
    "ddl/",
    "etl/",
    "tests/",
    "documentation/",
    "wave-report.md",
    "documentation/execution-runbook.md",
    "documentation/quality-gate-evidence.md",
    "documentation/reconciliation-evidence.md",
    "downstream/bi/",      
]

GATE_2_REQUIRED: list[str] = [
    "architecture.md",
    "data-model.md",
    "decisions.md",
    "dq-rules.md",
    "monitoring-spec.md",
]

# Canonical Gate 1 artifact paths, relative to <wave>/outputs/upstream/.
# _check_path also accepts the flat basename at root (legacy waves) and a
# one-level subfolder match, so pre-existing structures keep validating.
GATE_1_REQUIRED: list[str] = [
    "strategy/problem-statement.md",
    "strategy/kpis.md",
    "analysis/analytical-questions.md",
    "sttm/sttm.md",
    "analysis/dq-initial.md",
]

# AST Engine artifacts validated per gate (only when canonical-model.json is present)
# Gate 1: canonical-model.json structure only
# Gate 2: adds lineage + sttm (full AST pipeline output)
# Gate 3: adds generated-code/ directory
GATE_1_AST_ARTIFACTS: list[str] = [
    "canonical-model.json",
]

GATE_2_AST_ARTIFACTS: list[str] = [
    "canonical-model.json",
    "column-lineage.json",
    "sttm.md",
]

GATE_3_AST_ARTIFACTS: list[str] = [
    "canonical-model.json",
    "column-lineage.json",
    "sttm.md",
    "generated-code/",
]

GATE_REQUIRED: dict[int, list[str]] = {
    1: GATE_1_REQUIRED,
    2: GATE_2_REQUIRED,
    3: GATE_3_REQUIRED,
}


@dataclass
class ValidationResult:
    is_valid: bool
    missing: list[str] = field(default_factory=list)
    present: list[str] = field(default_factory=list)
    gate: int = 3

    def __str__(self) -> str:
        lines = [f"Gate {self.gate} validation: {'PASS' if self.is_valid else 'FAIL'}"]
        for p in self.present:
            lines.append(f"  ✓  {p}")
        for m in self.missing:
            lines.append(f"  ✗  {m}  (MISSING)")
        return "\n".join(lines)


def _check_path(root: Path, artifact: str) -> bool:
    """Return True if *artifact* exists under root.  Trailing '/' = directory.

    Resolution order (first hit wins):
      1. Exact relative path        -> root/strategy/problem-statement.md
      2. Flat basename at root      -> root/problem-statement.md (legacy waves)
      3. Basename in any 1st-level subfolder -> root/*/problem-statement.md
    Directories (trailing '/') use exact match only.
    """
    clean = artifact.rstrip("/")
    is_dir = artifact.endswith("/")

    if (root / clean).exists():
        return True
    if is_dir:
        return False

    basename = Path(clean).name

    if (root / basename).exists():
        return True

    try:
        for child in root.iterdir():
            if child.is_dir() and (child / basename).exists():
                return True
    except (FileNotFoundError, PermissionError):
        pass

    return False


def validate_gate_requirements(gate: int, artifact_root: Path) -> ValidationResult:
    """Generic gate validator for gate 1, 2, or 3."""
    required = GATE_REQUIRED.get(gate, [])
    missing: list[str] = []
    present: list[str] = []
    for artifact in required:
        if _check_path(artifact_root, artifact):
            present.append(artifact)
        else:
            missing.append(artifact)
    return ValidationResult(is_valid=len(missing) == 0, missing=missing, present=present, gate=gate)


def validate_ast_artifacts(gate: int, artifact_root: Path) -> ValidationResult:
    """
    Validate AST Engine artifacts for the given gate.

    AST artifacts are optional enrichments — validation PASSES if the
    canonical-model.json is absent (not yet generated) but FAILS if it is
    present and malformed (missing required keys).
    """
    _AST_GATE_MAP: dict[int, list[str]] = {
        1: GATE_1_AST_ARTIFACTS,
        2: GATE_2_AST_ARTIFACTS,
        3: GATE_3_AST_ARTIFACTS,
    }
    ast_artifacts = _AST_GATE_MAP.get(gate, [])
    canonical_path = artifact_root / "canonical-model.json"

    # If canonical-model.json is absent, AST gate is not applicable
    if not canonical_path.exists():
        return ValidationResult(is_valid=True, present=[], missing=[], gate=gate)

    missing: list[str] = []
    present: list[str] = []

    # Validate canonical-model.json has required top-level keys
    try:
        import json
        data = json.loads(canonical_path.read_text(encoding="utf-8"))
        required_keys = {"pipeline_id", "pipeline_name", "source_platform"}
        for key in required_keys:
            artifact_key = f"canonical-model.json[{key}]"
            if key in data:
                present.append(artifact_key)
            else:
                missing.append(artifact_key)
    except Exception as exc:  # noqa: BLE001
        missing.append(f"canonical-model.json (invalid JSON: {exc})")

    # Check for other AST artifacts
    for artifact in ast_artifacts:
        if artifact == "canonical-model.json":
            continue  # Already validated above
        if _check_path(artifact_root, artifact):
            present.append(artifact)
        else:
            missing.append(artifact)

    return ValidationResult(is_valid=len(missing) == 0, missing=missing, present=present, gate=gate)


def validate_gate3_requirements(wave_root: Path) -> ValidationResult:
    """Convenience wrapper: validate Gate 3 (downstream wave) artifacts."""
    return validate_gate_requirements(3, wave_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate gate artifact package before production promotion"
    )
    parser.add_argument("path", help="Wave output directory to validate")
    parser.add_argument("--gate", type=int, default=3, choices=[1, 2, 3], help="Gate number (default: 3)")
    args = parser.parse_args(argv)

    result = validate_gate_requirements(args.gate, Path(args.path).resolve())
    print(result)
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
