"""
performance_benchmark.py
B-010 — Production-like performance benchmark stage for migration waves.

Computes rows/second for an entity load and compares against a baseline.
Produces a BenchmarkReport that must be present before production promotion.

Usage:
    from scripts.performance_benchmark import BenchmarkRun, run_benchmark

    run = BenchmarkRun(
        wave_id="WAVE-001",
        entity="orders",
        rows_processed=1_000_000,
        duration_seconds=60.0,
        baseline_rows_per_second=10_000.0,
        bytes_processed=500_000_000    
        
    )
    report = run_benchmark(run)
    print(report)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class BenchmarkStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"



@dataclass
class BenchmarkRun:
    wave_id: str
    entity: str
    rows_processed: int
    duration_seconds: float
    baseline_rows_per_second: float
    bytes_processed: int
    # Optional tolerance: how far below baseline is acceptable (default 10%)
    tolerance_pct: float = 0.10
    table_size_bytes: int | None = None
    avg_table_size_bytes: int | None = None

    


@dataclass
class BenchmarkReport:
    wave_id: str
    entity: str
    rows_processed: int
    rows_per_second: float
    baseline_rows_per_second: float
    tolerance_pct: float
    status: BenchmarkStatus
    delta_pct: float          # (actual - baseline) / baseline

    bytes_processed: int  
    duration_seconds: float

    table_size_bytes: int | None = None
    avg_table_size_bytes: int | None = None
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
   
    
    @property
    def throughput_gb_per_day(self) -> float:
        bytes_per_sec = self.bytes_processed / self.duration_seconds
        return round(bytes_per_sec * 86_400 / 1_073_741_824, 4)
    
    @property
    def bytes_per_second(self) -> float:
        return round(self.bytes_processed / self.duration_seconds, 2)
    
    @property
    def total_volume_gb(self) -> float:
        return round(self.bytes_processed / 1_073_741_824, 4)

    @property
    def processing_time_per_gb(self) -> float:
        """Segundos necessários para processar 1 GB — permite comparar waves de tamanhos diferentes."""
        if self.bytes_processed == 0:
            return 0.0
        gb = self.bytes_processed / 1_073_741_824
        return round(self.duration_seconds / gb, 2)

    @property
    def total_volume_tb(self) -> float:
        return round(self.bytes_processed / 1_099_511_627_776, 4)

    @property
    def duration_minutes(self) -> float:
        """Expõe duração em minutos para o KPI de tempo médio por pipeline."""
        return round(self.duration_seconds / 60, 2)
    
    @property
    def total_volume(self) -> str:
        return (
            f"{self.total_volume_tb} TB"
            if self.total_volume_tb >= 1
            else f"{self.total_volume_gb} GB"
        )
    

    @property
    def table_size_gb(self) -> str:
        if self.table_size_bytes is None:
            return "N/A"
        
        gb = self.table_size_bytes / 1_073_741_824
        return f"{round(gb, 4)} GB"



    @property
    def avg_table_size(self) -> str:
        if self.avg_table_size_bytes is None:
            return "N/A"
        
        gb = self.avg_table_size_bytes / 1_073_741_824
        
        return f"{round(gb, 4)} GB"


    def __str__(self) -> str:
        sign = "+" if self.delta_pct >= 0 else ""
        return (
            f"Benchmark [{self.entity} / {self.wave_id}]: {self.status.value}\n"
            f"  Table Size : {self.table_size_gb}\n" 
            f"  Avg Table Size : {self.avg_table_size}\n"
            f"  Total Rows : {self.rows_processed:,}\n"
            f"  Actual     : {self.rows_per_second:,.1f} rows/s\n"
            f"  Baseline   : {self.baseline_rows_per_second:,.1f} rows/s\n"
            f"  Delta      : {sign}{self.delta_pct:.1%}\n"
            f"  Throughput : {self.throughput_gb_per_day} GB/day\n"
            f"  Volume Total : {self.total_volume}\n"
            f"  Tolerance  : -{self.tolerance_pct:.0%}"
        )


def run_benchmark(run: BenchmarkRun) -> BenchmarkReport:
    """Execute benchmark calculation for a single entity load."""

    if run.rows_processed <= 0:
        raise ValueError(f"rows_processed must be > 0, got {run.rows_processed}")
    
    if run.duration_seconds <= 0:
        raise ValueError(f"duration_seconds must be > 0, got {run.duration_seconds}")
    
    if run.bytes_processed <= 0:
        raise ValueError(f"bytes_processed must be > 0, got {run.bytes_processed}")
    

    actual = run.rows_processed / run.duration_seconds
    delta = (actual - run.baseline_rows_per_second) / run.baseline_rows_per_second
    minimum = run.baseline_rows_per_second * (1.0 - run.tolerance_pct)
    status = BenchmarkStatus.PASS if actual >= minimum else BenchmarkStatus.FAIL

    return BenchmarkReport(
        wave_id=run.wave_id,
        entity=run.entity,
        table_size_bytes=run.table_size_bytes,
        avg_table_size_bytes=run.avg_table_size_bytes,
        rows_processed=run.rows_processed,
        rows_per_second=round(actual, 2),
        baseline_rows_per_second=run.baseline_rows_per_second,
        tolerance_pct=run.tolerance_pct,
        status=status,
        delta_pct=round(delta, 4),
        bytes_processed=run.bytes_processed,        
        duration_seconds=run.duration_seconds

    )


def lead_time_by_entity(reports: list[BenchmarkReport]) -> list[tuple[str, float]]:
    """Lead time em minutos por entidade, do mais lento para o mais rápido.

    Usa a property duration_minutes já exposta em BenchmarkReport (não recalcula a partir de duration_seconds).
    Retorna uma lista de tuplas (entity, duration_minutes) ordenada do maior para o menor.
    """
    pairs = [(r.entity, r.duration_minutes) for r in reports]
    return sorted(pairs, key=lambda p: p[1], reverse=True)
