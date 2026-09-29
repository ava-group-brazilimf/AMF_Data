"""
wave_status_tracker.py
Consolidates wave status across all three gates: artifact completeness,
gate scores, and overall readiness.

Consumes validate_gate_requirements() for artifact checks and provides
a unified status view per wave.

Usage:
    from scripts.wave_status_tracker import WaveStatusTracker

    tracker = WaveStatusTracker(wave_id="WAVE-001")
    tracker.set_gate_artifacts(1, present=5, total=5)
    tracker.set_gate_artifacts(2, present=4, total=5)
    tracker.set_gate_artifacts(3, present=0, total=8)
    tracker.set_gate_score(1, 88.0)
    print(tracker.summary())
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PhaseStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


@dataclass
class GateStatus:
    gate: int
    artifacts_present: int = 0
    artifacts_total: int = 0
    gate_score: float | None = None

    
    tasks_completed: int = 0
    tasks_total: int = 0
    total_time_seconds: float = 0.0

    @property
    def artifacts_pct(self) -> float:
        if self.artifacts_total == 0:
            return 0.0
        return round(self.artifacts_present / self.artifacts_total * 100, 1)

    @property
    def phase_status(self) -> PhaseStatus:
        if self.artifacts_present == 0:
            return PhaseStatus.NOT_STARTED
        if self.artifacts_present < self.artifacts_total:
            return PhaseStatus.IN_PROGRESS
        if self.gate_score is not None and self.gate_score < 70.0:
            return PhaseStatus.BLOCKED
        return PhaseStatus.COMPLETE
    
    @property
    def tasks_pct(self) -> float:
        if self.tasks_total == 0:
            return 0.0
        return round(self.tasks_completed / self.tasks_total * 100, 1)
    
    
    @property
    def avg_task_time_seconds(self) -> float:
        if self.tasks_completed == 0:
            return 0.0
        return round(self.total_time_seconds / self.tasks_completed, 2)
    
    @property
    def avg_task_time_minutes(self) -> float:
        return round(self.avg_task_time_seconds / 60, 2)
    

@dataclass
class WaveStatusSummary:
    wave_id: str
    gates: list[GateStatus]
    overall_pct: float
    tables_migrated: int = 0
    tables_total: int = 0
    pipelines_migrated: int = 0
    pipelines_total: int = 0
    total_pipeline_time_seconds: float = 0.0
    gb_total: float = 0.0
    gb_migrated: float = 0.0

    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


    @property
    def tables_pct(self) -> float:
        if self.tables_total == 0:
            return 0.0
        return round(self.tables_migrated / self.tables_total * 100, 1)
    
    @property
    def pipelines_pct(self) -> float:
        if self.pipelines_total == 0:
            return 0.0
        return round(self.pipelines_migrated / self.pipelines_total * 100, 1)
    
    
    @property
    def avg_pipeline_time_seconds(self) -> float:
        if self.pipelines_migrated == 0:
            return 0.0
        return round(self.total_pipeline_time_seconds / self.pipelines_migrated, 2)

    @property   
    def avg_pipeline_time_minutes(self) -> float:
        return round(self.avg_pipeline_time_seconds / 60, 2)

    @property
    def tables_remaining(self) -> int:
        """Quantidade de tabelas ainda não migradas."""
        return max(0, self.tables_total - self.tables_migrated)

    @property
    def backlog_pct(self) -> float:
        """% do escopo que ainda falta migrar."""
        if self.tables_total == 0:
            return 0.0
        return round(self.tables_remaining / self.tables_total * 100, 1)

    @property
    def gb_remaining(self) -> float:
        """Volume em GB ainda não migrado."""
        return round(max(0.0, self.gb_total - self.gb_migrated), 2)
    
    def __str__(self) -> str:
        lines = [
            f"Wave Status: {self.wave_id}  (overall: {self.overall_pct:.0f}%)",
            f"Tables: {self.tables_migrated}/{self.tables_total} ({self.tables_pct}%)",
            f"Pipelines: {self.pipelines_migrated}/{self.pipelines_total} ({self.pipelines_pct}%)"
        ]
        for g in self.gates:
            score_str = f"score={g.gate_score:.1f}" if g.gate_score is not None else "score=N/A"
            lines.append(
                f"  Gate {g.gate}: {g.phase_status.value}  "
                f"artifacts={g.artifacts_present}/{g.artifacts_total} ({g.artifacts_pct}%)  "
                f"{score_str}  "
                f"tasks={g.tasks_completed}/{g.tasks_total} ({g.tasks_pct}%) "
                f"avg_time={g.avg_task_time_minutes} min/task  "
                f"tables={self.tables_migrated}/{self.tables_total} ({self.tables_pct}%) "
            )
        return "\n".join(lines)


class WaveStatusTracker:
    """Tracks per-gate artifact completion and scores for a migration wave."""

    def __init__(self, wave_id: str) -> None:
        self.wave_id = wave_id
        self._gates: dict[int, GateStatus] = {
            1: GateStatus(gate=1),
            2: GateStatus(gate=2),
            3: GateStatus(gate=3),
        }
        
        self.tables_migrated = 0
        self.tables_total = 0
        self.pipelines_migrated = 0
        self.pipelines_total = 0
        self.total_pipeline_time_seconds = 0.0
        



    def set_gate_artifacts(self, gate: int, present: int, total: int) -> None:
        if gate not in self._gates:
            raise ValueError(f"Invalid gate: {gate}. Must be 1, 2, or 3.")
        self._gates[gate].artifacts_present = present
        self._gates[gate].artifacts_total = total

    def set_gate_score(self, gate: int, score: float) -> None:
        if gate not in self._gates:
            raise ValueError(f"Invalid gate: {gate}. Must be 1, 2, or 3.")
        self._gates[gate].gate_score = score

    def set_gate_tasks(self, gate: int, completed: int, total: int):
        if gate not in self._gates:
            raise ValueError(f"Invalid gate: {gate}. Must be 1, 2, or 3.")
            
        self._gates[gate].tasks_completed = completed
        self._gates[gate].tasks_total = total

    def set_gate_time(self, gate: int, total_time_seconds: float):
        if gate not in self._gates:
            raise ValueError(f"Invalid gate: {gate}. Must be 1, 2, or 3.")
        
        self._gates[gate].total_time_seconds = total_time_seconds

    def set_wave_tables(self, migrated: int, total: int):
        self.tables_migrated = migrated
        self.tables_total = total    

    def set_wave_pipelines(self, migrated: int, total: int):
        self.pipelines_migrated = migrated
        self.pipelines_total = total

    def set_wave_pipeline_time(self, total_time_seconds: float):
        self.total_pipeline_time_seconds = total_time_seconds


    def summary(self) -> WaveStatusSummary:
        gates = [self._gates[g] for g in sorted(self._gates)]
        total_artifacts = sum(g.artifacts_total for g in gates)
        present_artifacts = sum(g.artifacts_present for g in gates)
        overall_pct = (
            round(present_artifacts / total_artifacts * 100, 1)
            if total_artifacts > 0
            else 0.0
        )
        return WaveStatusSummary(
            wave_id=self.wave_id,
            gates=gates,
            overall_pct=overall_pct,
            tables_migrated=self.tables_migrated,
            tables_total=self.tables_total,
            pipelines_migrated=self.pipelines_migrated,
            pipelines_total=self.pipelines_total,
            total_pipeline_time_seconds=self.total_pipeline_time_seconds
        )
@dataclass
class EstimateComparison:
    entity: str
    estimated_rows: int
    actual_rows: int

    @property
    def delta(self) -> int:
        """Positivo = veio MAIS que o estimado. Negativo = veio MENOS."""
        return self.actual_rows - self.estimated_rows

    @property
    def delta_pct(self) -> float:
        if self.estimated_rows == 0:
            return 0.0
        return round(self.delta / self.estimated_rows * 100, 1)

    @property
    def accuracy_pct(self) -> float:
        """Acurácia da estimativa: 100% = estimou exato, 0% = errou por 100% ou mais."""
        if self.estimated_rows == 0:
            return 0.0
        error = abs(self.delta) / self.estimated_rows
        return round(max(0.0, (1 - error)) * 100, 1)


def wave_estimate_accuracy(comparisons: list[EstimateComparison]) -> float:
    """Acurácia média da wave — média simples das acurácias por entidade."""
    measured = [c for c in comparisons if c.estimated_rows > 0]
    if not measured:
        return 0.0
    return round(sum(c.accuracy_pct for c in measured) / len(measured), 1)


def compare_estimates(
    wave_config_entities: list[dict],
    actuals: dict[str, int],
) -> list[EstimateComparison]:
    """Cruza estimated_rows do wave-config com rows_processed do registry.

    Entidades sem valor realizado ficam com actual_rows=0 (ainda não migradas).
    """
    result = []
    for ent in wave_config_entities:
        name = ent["name"]
        result.append(EstimateComparison(
            entity=name,
            estimated_rows=ent.get("estimated_rows", 0),
            actual_rows=actuals.get(name, 0),
        ))
    return result


def format_estimate_table(comparisons: list[EstimateComparison]) -> str:
    """Formata a comparação estimado x realizado como tabela markdown."""
    lines = [
        "| Entidade | Estimado | Realizado | Delta | Delta % |",
        "|---|---:|---:|---:|---:|",
    ]
    for c in comparisons:
        lines.append(
            f"| {c.entity} | {c.estimated_rows:,} | {c.actual_rows:,} "
            f"| {c.delta:+,} | {c.delta_pct:+.1f}% |"
        )
    return "\n".join(lines)
