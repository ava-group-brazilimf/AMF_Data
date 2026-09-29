# Gate Performance Metrics — Example of Use

This document shows how to use `gate_performance_metrics.py` to log and query score metrics for each gate.

## 🚀 Basic Example: Logging Metrics of a Wave

```python
from scripts.gate_performance_metrics import (
    GatePerformanceMetric,
    GatePerformanceRegistry,
)

# Initialize registry (creates file if it doesn't exist)
registry = GatePerformanceRegistry(
    "projects/meu-projeto/outputs/summary/gate_performance_metrics.jsonl"
)

# Log Gate 1 metrics
metric_gate1 = GatePerformanceMetric(
    wave_id="WAVE-001",
    gate=1,
    tests_rate=0.80,    
    dq_score=0.75,      
    row_parity=0.86,    
    rejection_rate=0.33,
    rework_count=2,
    rework_time_min=90,
    environment="DEV"
)
registry.record(metric_gate1)

# Register Gate 2
metric_gate2 = GatePerformanceMetric(
    wave_id="WAVE-001",
    gate=2,
    tests_rate=0.87,
    dq_score=0.82,
    row_parity=0.90,
    rejection_rate=0.97,
    rework_count=1,
    rework_time_min=15,
    environment="UAT"
)
registry.record(metric_gate2)

# Register Gate 3
metric_gate3 = GatePerformanceMetric(
    wave_id="WAVE-001",
    gate=3,
    tests_rate=0.90,
    dq_score=0.87,
    row_parity=0.98,
    rejection_rate=1.00,
    rework_count=0,
    rework_time_min=0,
    environment="PROD"
)
registry.record(metric_gate3)
```

## 📊 Example: Export to Dashboard

```python
# Export as CSV (for Excel, Tableau, Power BI, etc)
registry.export_csv("outputs/metrics/gate_metrics.csv")

# Export as JSON (for APIs and web tools)
registry.export_json("outputs/metrics/gate_metrics.json")

# Print summarized report
print(registry.summary_report())
```

**CSV Output** (ready for dashboard):
```csv
wave_id,gate,tests_rate,dq_score,row_parity,rejection_rate,rework_count,rework_time_min,recorded_at,environment,notes
WAVE-001,1,0.8000,0.7500,0.8600,0.3300,2,90.00,2026-06-08T10:30:00+00:00,DEV,
WAVE-001,2,0.8700,0.8200,0.9000,0.9700,1,15.00,2026-06-08T10:35:00+00:00,UAT,
WAVE-001,3,0.9000,0.8700,0.9800,1.0000,0,0.00,2026-06-08T10:40:00+00:00,PROD,
WAVE-002,1,0.8200,0.7600,0.8700,0.3300,2,90.00,2026-06-09T14:10:00+00:00,DEV,
WAVE-002,2,0.8800,0.8300,0.9100,0.9700,1,15.00,2026-06-09T14:15:00+00:00,UAT,
WAVE-002,3,0.9100,0.8800,0.9900,1.0000,0,0.00,2026-06-09T14:20:00+00:00,PROD,
```

## 🔍 Example: Query Historical Data

```python
# Reload registry from existing file
registry = GatePerformanceRegistry("outputs/metrics/gate_performance_metrics.jsonl")

# Get all metrics of a specific gate
gate2_metrics = registry.get_by_gate(gate=2)
print(f"Total waves in Gate 2: {len(gate2_metrics)}")

# Get metrics from a specific wave
wave001_metrics = registry.get_by_wave("WAVE-001")
print(f"WAVE-001 metrics (all gates): {wave001_metrics}")

# Aggregations by gate
agg_gate2 = registry.aggregate_by_gate(gate=2)
print(f"\nGate 2 Statistics:")
print(f"  Waves: {agg_gate2.total_waves}")
print(f"  Tests Rate (avg): {agg_gate2.avg_tests_rate:.1%}")
print(f"  DQ Score (avg):   {agg_gate2.avg_dq_score:.1%}")
print(f"  Row Parity (avg): {agg_gate2.avg_row_parity:.1%}")

# Fast averages
avg_dq_gate1 = registry.average_dq_by_gate(gate=1)
print(f"\nGate 1 - Average DQ Score: {avg_dq_gate1:.1%}")
```

## 🔗 Integration with `gate_score_report.py`

To automate the registration when calculating the GateScore:

```python
from scripts.gate_score_report import generate_gate_score_report, GateScoreInput
from scripts.gate_performance_metrics import (
    GatePerformanceMetric,
    GatePerformanceRegistry,
)

#`rejection_rate`, `rework_count`, and `rework_time_min` values should come from the execution process and not be manually set in production.

# Calculate GateScore
gate_input = GateScoreInput(
    wave_id="WAVE-001",
    gate=2,
    tests_passed=9,
    tests_total=10,
    dq_score=0.82,
    row_parity=0.90,
)
gate_report = generate_gate_score_report(gate_input)

# Automatically log the metrics
registry = GatePerformanceRegistry("outputs/metrics/gate_performance_metrics.jsonl")
metric = GatePerformanceMetric(
    wave_id=gate_report.wave_id,
    gate=gate_report.gate,
    tests_rate=gate_report.tests_rate,
    dq_score=gate_report.dq_score,
    row_parity=gate_report.row_parity,
    rejection_rate=0.33,
    rework_count=2,
    rework_time_min=90,
    environment="UAT"
)
registry.record(metric)

print(gate_report)  
```

## 📁 Recommended File Structure

```
projects/seu-projeto/
├── context/
│   ├── project-config.yaml
│   └── shared-context.md
├── outputs/
│   ├── upstream/
│   │   └── gate1-decision.md
│   ├── midstream/
│   │   └── gate2-decision.md
│   ├── downstream/
│   │   └── gate3-decision.md
│   └── summary/
│       └── gate_performance_metrics.jsonl   ← New: score history
└── metrics/
    ├── gate_metrics.csv                     ← To dashboards
    └── gate_metrics.json                    ← Structured backup
```

## 🎯 Use Cases

### Real-Time Dashboard

```python
# Scheduled script (cron/Azure Scheduler)
registry = GatePerformanceRegistry("outputs/metrics/gate_performance_metrics.jsonl")

# Export updated to dashboard
registry.export_csv("outputs/metrics/gate_metrics.csv")

# Send to dashboard API
import requests
metrics_json = registry.get_all()
requests.post("https://dashboard.interno/api/gate-metrics", json=metrics_json)
```

### Degradation Alerts

```python
# Monitor DQ score trend
agg = registry.aggregate_by_gate(gate=3)
if agg.avg_dq_score < 0.85:
    send_alert(f"Gate 3 DQ Score degraded to {agg.avg_dq_score:.1%}")
```

### Inter-Waves Comparison

```python
gate2_metrics = registry.get_by_gate(gate=2)
recent = gate2_metrics[:3]  # Last 3 waves

print("Last 3 waves - Gate 2:")
for m in recent:
    print(f"  {m.wave_id}: tests={m.tests_rate:.1%}, dq={m.dq_score:.1%}, parity={m.row_parity:.1%}")
```

## 🛠️ CLI Command for Test

```bash
python -c "
from scripts.gate_performance_metrics import GatePerformanceMetric, GatePerformanceRegistry
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmpdir:
    registry = GatePerformanceRegistry(Path(tmpdir) / 'test.jsonl')
    
    for gate in [1, 2, 3]:
        m = GatePerformanceMetric(
            wave_id='WAVE-001',
            gate=gate,
            tests_rate=0.80 + gate*0.05,
            dq_score=0.75 + gate*0.05,
            row_parity=0.85 + gate*0.05
        )
        registry.record(m)
    
    print(registry.summary_report())
"
```

## 📚 Full API

| Method | Description |
|--------|-------------|
| `record(metric)` | Records a new metric |
| `get_all()` | Returns all metrics |
| `get_by_gate(gate)` | Filters by gate (1, 2, 3) |
| `get_by_wave(wave_id)` | Filters by wave |
| `aggregate_by_gate(gate)` | Returns min/max/avg for the gate |
| `average_dq_by_gate(gate)` | Average DQ score for the gate |
| `average_tests_rate_by_gate(gate)` | Average tests_rate for the gate |
| `average_row_parity_by_gate(gate)` | Average row_parity for the gate |
| `average_rejection_rate_by_gate(gate)` | Average rejection_rate for the gate |
| `average_rework_count_by_gate(gate)` | Average rework_count for the gate |
| `average_rework_time_by_gate(gate)` | Average rework_time_min for the gate |
| `export_csv(path)` | Exports to CSV |
| `export_json(path)` | Exports to JSON |
| `summary_report()` | Generates a summarized textual report |

---

**Next steps**:
1. Integrate with your gate pipeline (call `registry.record()` after calculating each GateScore)
2. Export CSV daily to your dashboard (Tableau, Power BI, Grafana, etc.)
3. Configure alerts based on aggregations (`avg_dq_by_gate()`)