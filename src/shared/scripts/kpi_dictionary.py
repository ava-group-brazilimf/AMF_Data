"""
kpi_dictionary.py
B-014 — KPI dictionary with ownership model.

Defines the canonical KPIs for the migration project (mirrors gate1-kpis.md
template). Each KPI has an ID, definition, owner agent, target, measurement
method, and reporting cadence.

The dictionary can be serialized to/from YAML for versioning and review.

Usage:
    from scripts.kpi_dictionary import KPIDictionary, KPI_DEFAULTS

    d = KPIDictionary(KPI_DEFAULTS)
    kpi = d.get("row_count_parity")
    print(kpi.definition)
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import yaml  # type: ignore
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


@dataclass
class KPIOwnership:
    owner_agent: str          # agent responsible for measuring
    business_owner: str       # human role that approves the target
    reporting_cadence: str    # e.g. "per wave", "daily", "wave"


@dataclass
class KPI:
    id: str
    name: str
    definition: str
    target: str
    measurement_method: str
    ownership: KPIOwnership


# ---------------------------------------------------------------------------
# Canonical KPI defaults (mirrors gate1-kpis.md)
# ---------------------------------------------------------------------------

KPI_DEFAULTS: list[KPI] = [
    KPI(
        id="row_count_parity",
        name="Row Count Parity",
        definition="Source rows = Target rows per entity after migration wave",
        target="100%",
        measurement_method="Reconciliation agent: count(*) source vs count(*) target per entity",
        ownership=KPIOwnership(
            owner_agent="reconciliation",
            business_owner="Data Owner",
            reporting_cadence="per wave",
        ),
    ),
    KPI(
        id="dq_score",
        name="Data Quality Score",
        definition="Percentage of records passing all defined DQ rules",
        target="≥ 98%",
        measurement_method="Quality Gate agent: DQ rule evaluation per entity tier",
        ownership=KPIOwnership(
            owner_agent="quality-gate",
            business_owner="Data Steward",
            reporting_cadence="per wave",
        ),
    ),
    KPI(
        id="migration_duration",
        name="Migration Duration",
        definition="Elapsed time from wave execution start to wave validated",
        target="TBD per wave SLA",
        measurement_method="Downstream Executor: execution log start/end timestamps",
        ownership=KPIOwnership(
            owner_agent="downstream-executor",
            business_owner="Technical Lead",
            reporting_cadence="per wave",
        ),
    ),
    KPI(
        id="first_pass_success_rate",
        name="First-Pass Success Rate",
        definition="Percentage of waves completed without rollback on first attempt",
        target="≥ 90%",
        measurement_method="Wave report: count waves with status=PASS / total waves",
        ownership=KPIOwnership(
            owner_agent="orchestrator",
            business_owner="Delivery Lead",
            reporting_cadence="per wave",
        ),
    ),
    KPI(
        id="mttr",
        name="Mean Time to Recover",
        definition="Mean elapsed time from wave failure detection to successful re-run",
        target="≤ 4 hours",
        measurement_method="Self-Healing agent: incident log start/resolution timestamps",
        ownership=KPIOwnership(
            owner_agent="self-healing",
            business_owner="Technical Lead",
            reporting_cadence="per incident",
        ),
    ),
]


# ---------------------------------------------------------------------------
# Dictionary wrapper
# ---------------------------------------------------------------------------

class KPIDictionary:
    def __init__(self, kpis: list[KPI]) -> None:
        self.kpis = kpis
        self._index: dict[str, KPI] = {k.id: k for k in kpis}

    def get(self, kpi_id: str) -> KPI:
        if kpi_id not in self._index:
            raise KeyError(f"KPI '{kpi_id}' not found in dictionary")
        return self._index[kpi_id]

    def to_yaml(self, path: Path) -> None:
        if not _YAML_AVAILABLE:
            raise RuntimeError("PyYAML is required: pip install pyyaml")
        data = {"kpis": [asdict(k) for k in self.kpis]}
        path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_kpi_dictionary(path: Path) -> KPIDictionary:
    """Load a KPI dictionary from a YAML file produced by KPIDictionary.to_yaml()."""
    if not _YAML_AVAILABLE:
        raise RuntimeError("PyYAML is required: pip install pyyaml")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    kpis: list[KPI] = []
    for item in raw.get("kpis", []):
        ownership_data = item.pop("ownership")
        ownership = KPIOwnership(**ownership_data)
        kpis.append(KPI(**item, ownership=ownership))
    return KPIDictionary(kpis)
