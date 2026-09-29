"""
validate_gate1_artifacts.py
Convenience module — validates Gate 1 artifact package (UPSTREAM discovery
outputs) before promoting to MIDSTREAM.

Delegates to validate_gate_requirements(1, path) in validate_gate3_artifacts.

Required artifacts: strategy/problem-statement.md, strategy/kpis.md,
analysis/analytical-questions.md, sttm/sttm.md, analysis/dq-initial.md

Usage (standalone):
    python -m scripts.validate_gate1_artifacts <artifact_dir>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .validate_gate3_artifacts import ValidationResult, validate_gate_requirements


def validate_gate1_artifacts(artifact_root: Path) -> ValidationResult:
    """Validate Gate 1 (UPSTREAM) artifacts."""
    return validate_gate_requirements(1, artifact_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Gate 1 artifact package before MIDSTREAM promotion"
    )
    parser.add_argument("path", help="Directory containing Gate 1 artifacts")
    args = parser.parse_args(argv)

    result = validate_gate1_artifacts(Path(args.path).resolve())
    print(result)
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
