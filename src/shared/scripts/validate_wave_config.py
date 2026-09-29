"""
validate_wave_config.py
B-017 — Enforces that every wave config declares a primary AND fallback
discovery owner. Used by CI and by gate pre-checks.

Usage (standalone):
    python -m scripts.validate_wave_config <wave_config.yaml>
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml  # type: ignore
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


@dataclass
class WaveConfigValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"Wave config validation: {'PASS' if self.is_valid else 'FAIL'}"]
        for e in self.errors:
            lines.append(f"  ERROR   {e}")
        for w in self.warnings:
            lines.append(f"  WARNING {w}")
        return "\n".join(lines)


def _repository_root(config_path: Path) -> Path:
    """Return the repository root for configs stored below its projects folder."""
    for parent in config_path.resolve().parents:
        if parent.name == "projects":
            return parent.parent
    return config_path.resolve().parent


def resolve_project_paths(config_path: Path, config: dict) -> tuple[Path, Path] | None:
    """Resolve the canonical context and output roots declared by a wave config."""
    project_name = str(config.get("project_name") or "").strip()
    if not project_name:
        return None

    repository_root = _repository_root(config_path)
    values = {
        "project_name": project_name,
        "context": config.get("context_base_path", "projects/{project_name}/context"),
        "outputs": config.get("outputs_base_path", "projects/{project_name}/outputs"),
    }

    def resolve(value: object) -> Path:
        rendered = str(value).format(project_name=project_name)
        path = Path(rendered)
        return path.resolve() if path.is_absolute() else (repository_root / path).resolve()

    return resolve(values["context"]), resolve(values["outputs"])


def validate_wave_config(config_path: Path) -> WaveConfigValidationResult:
    """Validate discovery ownership and required fields in a wave YAML config.

    B-017: the wave config MUST contain:
      discovery_owner_primary   — string, non-empty
      discovery_owner_fallback  — string, non-empty, different from primary
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not config_path.exists():
        return WaveConfigValidationResult(
            is_valid=False,
            errors=[f"Config file not found: {config_path}"],
        )

    if not _YAML_AVAILABLE:
        return WaveConfigValidationResult(
            is_valid=False,
            errors=["PyYAML is not installed. Run: pip install pyyaml"],
        )

    try:
        with config_path.open(encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
    except Exception as exc:  # noqa: BLE001
        return WaveConfigValidationResult(is_valid=False, errors=[f"YAML parse error: {exc}"])

    # B-017 checks
    primary = config.get("discovery_owner_primary", "").strip()
    fallback = config.get("discovery_owner_fallback", "").strip()

    if not primary:
        errors.append("discovery_owner_primary is missing or empty (B-017)")
    if not fallback:
        errors.append("discovery_owner_fallback is missing or empty (B-017)")
    if primary and fallback and primary == fallback:
        warnings.append(
            f"discovery_owner_primary and fallback are both '{primary}'. "
            "They should be different agents."
        )

    # Runtime workspace checks: bind every configured wave to one context/output root.
    project_name = str(config.get("project_name") or "").strip()
    if not project_name:
        warnings.append(
            "project_name is not set; context and output paths cannot be resolved "
            "deterministically"
        )
    else:
        context_path, outputs_path = resolve_project_paths(config_path, config)  # type: ignore[misc]
        expected_project_root = (
            _repository_root(config_path) / "projects" / project_name
        ).resolve()
        for label, path in (("context_base_path", context_path), ("outputs_base_path", outputs_path)):
            if path != expected_project_root and expected_project_root not in path.parents:
                errors.append(
                    f"{label} resolves outside projects/{project_name}: {path}"
                )

        required_context = ("project-config.yaml", "agent-task-config.yaml")
        for filename in required_context:
            if not (context_path / filename).is_file():
                errors.append(
                    f"Required wave context file not found: {context_path / filename}"
                )

    # B-008: non-dry-run waves MUST reference a validated runbook
    is_dry_run = config.get("dry_run", False)
    environment = (config.get("environment") or "").strip().upper()
    if environment in ("UAT", "PROD") and not is_dry_run:
        runbook_path = config.get("runbook_path", "").strip()
        if not runbook_path:
            errors.append(
                "runbook_path is required for non-dry-run UAT/PROD waves (B-008). "
                "Set dry_run: true or provide a runbook_path."
            )
        else:
            # Resolve relative to config file directory
            resolved = (config_path.parent / runbook_path).resolve()
            if not resolved.exists():
                errors.append(
                    f"runbook_path '{runbook_path}' does not exist (B-008). "
                    "Ensure the execution runbook is present before running."
                )

    # Source platform validation
    ACCEPTED_SOURCE_PLATFORMS = [
        "hadoop", "cloudera",
        "ssis",
        "airflow",
        "informatica", "powercenter",
        "sap_bods", "bods",
        "spark_generic", "spark", "mixed", "sqlserver", "mssql",
        "synapse", "azure_synapse",
    ]

    source = config.get("source") or {}
    source_type = (source.get("type") or "").strip().lower() if isinstance(source, dict) else ""
    if source_type:
        if source_type not in ACCEPTED_SOURCE_PLATFORMS:
            errors.append(
                f"source.type '{source_type}' is not a supported platform. "
                f"Accepted: {ACCEPTED_SOURCE_PLATFORMS}"
            )
        # PowerCenter-specific: warn if connectors not specified
        if source_type in ("powercenter", "informatica") and not source.get("connectors"):
            warnings.append(
                "source.type is powercenter/informatica but source.connectors is not specified. "
                "Recommend: [pmrep-cli] or [xml-export-parser]"
            )
        # Generic Spark: warn if legacy_path not specified (file-based scan needs it)
        if source_type in ("spark_generic", "spark", "mixed", "sqlserver", "mssql") \
                and not source.get("legacy_path"):
            warnings.append(
                "source.type is spark_generic/mixed but source.legacy_path is not specified. "
                "File-based scan requires the repository path."
            )
        # Synapse: warn if export format not confirmed
        if source_type in ("synapse", "azure_synapse") and not source.get("legacy_path"):
            warnings.append(
                "source.type is synapse but source.legacy_path is not specified. "
                "Expected: path to workspace Git export (pipeline/, sqlscript/, ...)."
            )

    # Optional wave metadata checks
    if not config.get("wave_id"):
        warnings.append("wave_id is not set — recommended for audit traceability")
    if not environment:
        warnings.append("environment is not set (DEV/UAT/PROD)")

    return WaveConfigValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate wave config YAML (B-017: discovery owner enforcement)"
    )
    parser.add_argument("config", help="Path to wave config YAML file")
    args = parser.parse_args(argv)

    result = validate_wave_config(Path(args.config).resolve())
    print(result)
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
