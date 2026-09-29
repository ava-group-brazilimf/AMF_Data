"""
validate_gate2_artifacts.py
Convenience module — validates Gate 2 artifact package (MIDSTREAM design
outputs) before promoting to DOWNSTREAM.

Delegates to validate_gate_requirements(2, path) in validate_gate3_artifacts.

Required artifacts: architecture.md, data-model.md, decisions.md,
dq-rules.md, monitoring-spec.md

Usage (standalone):
    python -m scripts.validate_gate2_artifacts <artifact_dir>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.validate_gate3_artifacts import ValidationResult, validate_gate_requirements


def validate_gate2_artifacts(artifact_root: Path) -> ValidationResult:
    """Validate Gate 2 (MIDSTREAM) artifacts."""
    return validate_gate_requirements(2, artifact_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Gate 2 artifact package before DOWNSTREAM promotion"
    )
    parser.add_argument("path", help="Directory containing Gate 2 artifacts")
    args = parser.parse_args(argv)

    result = validate_gate2_artifacts(Path(args.path).resolve())
    print(result)
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
