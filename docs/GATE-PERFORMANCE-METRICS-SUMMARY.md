# Gate Performance Metrics — Implemented Solution

## 📍 Solution Overview

The `gate_performance_metrics.py` module was implemented with the goal of standardizing the recording, persistence, and availability of performance metrics per gate throughout pipeline executions (waves).
The solution consolidates key quality and observability indicators into a structured and versionable dataset, including:

### Observability Metrics
- Validation metrics: `tests_rate`, `dq_score`, `row_parity`
- Failure and rework metrics: `rejection_rate`, `rework_count`, `rework_time_min`

---

## 📦 What Was Created

### 1. **Main Module** — `gate_performance_metrics.py`
📁 **Location:** `src/shared/scripts/gate_performance_metrics.py`

**Features:**
- ✅ Persists metrics in JSON Lines (`.jsonl`) format  
- ✅ Automatically reloads historical data  
- ✅ Exports to CSV (ready for Excel, Tableau, Power BI, Grafana)  
- ✅ Exports to JSON (for APIs and web tools)  
- ✅ Aggregations by gate (min/max/avg)  
- ✅ Queries by wave, by gate  
- ✅ Summary reports  

**Main functions:**
```python
registry = GatePerformanceRegistry("path/to/metrics.jsonl")
registry.record(metric)                    # Records a new metric
registry.get_by_gate(gate)                 # Filter by gate
registry.get_by_wave(wave_id)              # Filter by wave
registry.aggregate_by_gate(gate)           # Aggregations
registry.export_csv("output.csv")          # Export to CSV
registry.export_json("output.json")        # Export to JSON
registry.summary_report()                  # Textual report
```

---

### 2. **Complete Tests** — `test_gate_performance_metrics.py`
✅ Automated tests validate the module behavior  
📁 **Location:** `src/shared/tests/test_gate_performance_metrics.py`
```bash
# Run tests
python -m pytest src/shared/tests/test_gate_performance_metrics.py -v
```

---

### 3. **Usage Documentation** — `GATE-PERFORMANCE-METRICS-USAGE.md`
📁 **Location:** `docs/GATE-PERFORMANCE-METRICS-USAGE.md`

Contains:
- Basic usage examples
- Integration with `gate_score_report.py`
- Use cases (dashboards, alerts, comparisons)
- Full API
- Recommended file structure

---

### 4. **Executable Example** — `register_gate_metrics_example.py`
📁 **Location:** `samples/register_gate_metrics_example.py`

Ready-to-run script demonstrating:
- Register metrics for WAVE-001 (all 3 gates)
- Export to CSV
- Export to JSON
- Generate reports

```bash
# Run example
python src/shared/samples/register_gate_metrics_example.py
```

## 📊 Saída do Exemplo Prático

### CSV Gerado (Pronto para Dashboard)
```csv
wave_id,gate,tests_rate,dq_score,row_parity,rejection_rate,rework_count,rework_time_min,recorded_at,environment,notes
```

### JSON Gerado (Estruturado)
```json
{
  "total_metrics": 3,
  "exported_at": "2026-06-08T17:32:43.034766+00:00",
  "metrics": [
    {
      "wave_id": "WAVE-001",
      "gate": 1,
      "tests_rate": 0.80,
      "dq_score": 0.75,
      "row_parity": 0.86,
      "rejection_rate": 0.33,
      "rework_count": 2,
      "rework_time_min": 90.0,
      "recorded_at": "2026-06-08T17:32:43.016779+00:00",
      "environment": "DEV",
      "notes": null
    },
    {
      "wave_id": "WAVE-001",
      "gate": 2,
      "tests_rate": 0.87,
      "dq_score": 0.82,
      "row_parity": 0.90,
      "rejection_rate": 0.97,
      "rework_count": 1,
      "rework_time_min": 15.0,
      "recorded_at": "2026-06-08T17:35:00+00:00",
      "environment": "UAT",
      "notes": null
    },
    {
      "wave_id": "WAVE-001",
      "gate": 3,
      "tests_rate": 0.90,
      "dq_score": 0.87,
      "row_parity": 0.98,
      "rejection_rate": 1.00,
      "rework_count": 0,
      "rework_time_min": 0.0,
      "recorded_at": "2026-06-08T17:40:00+00:00",
      "environment": "PROD",
      "notes": null
    }
  ]
}

```

## 🚀 How to Use Immediately

### Option 1: Use the Example Script
```bash
python src/shared/samples/register_gate_metrics_example.py

```

Generates files in:
- `projects/sample-migration/outputs/summary/gate_performance_metrics.jsonl`
- `projects/sample-migration/outputs/summary/gate_metrics.csv`
- `projects/sample-migration/outputs/summary/gate_metrics.json`

### Option 2: Use in Your Own Code
```python
from src.shared.scripts.gate_performance_metrics import (
    GatePerformanceMetric,
    GatePerformanceRegistry,
)

# Create registry
registry = GatePerformanceRegistry("projects/nome-projeto/outputs/summary/gate_performance_metrics.jsonl")


# Register a gate metric
metric = GatePerformanceMetric(
    wave_id="WAVE-001",
    gate=2,
    tests_rate=0.87,
    dq_score=0.82,
    row_parity=0.90,
    environment="UAT"
)

registry.record(metric)

# Export to dashboard
registry.export_csv("outputs/metrics/gate_metrics.csv")
```

### Option 3: Integrate with `gate_score_report.py`
After calculating the GateScore, automatically register:
```python
from src.shared.scripts.gate_score_report import generate_gate_score_report, GateScoreInput
from src.shared.scripts.gate_performance_metrics import GatePerformanceMetric, GatePerformanceRegistry

# Calculate score
gate_input = GateScoreInput(wave_id="WAVE-001", gate=2, ...)
gate_report = generate_gate_score_report(gate_input)

# Register metric
registry = GatePerformanceRegistry("path/to/registry.jsonl")
metric = GatePerformanceMetric(
    wave_id=gate_report.wave_id,
    gate=gate_report.gate,
    tests_rate=gate_report.tests_rate,
    dq_score=gate_report.dq_score,
    row_parity=gate_report.row_parity,
)
registry.record(metric)
```

---


## 🔗 Integration with Existing Files

| File | Relationship |
|------|-------------|
| `gate_score_report.py` | **Complementary** — Calculates the score; the new module **records** the metrics |
| `kpi_dashboard_report.py` | **Different** — Records execution KPIs (first-pass rate, rollback, MTTR, cycle time) and can also include AST KPIs (`ast_coverage`, `transformation_accuracy`, `code_generation_accuracy`); this module records **gate quality** KPIs |
| `gate{N}-decision.md` | **Integrated** — Gate decisions + scores; now you have **structured history** |

---

## 📁 File Structure

```
src/shared/scripts/
├── gate_score_report.py                      ← Calculates score
├── gate_performance_metrics.py               ← ✨ NEW: Records and persists metrics
├── GATE-PERFORMANCE-METRICS-USAGE.md         ← ✨ NEW: Full documentation

src/shared/tests/
├── test_gate_score_report.py                 ← Score tests
├── test_gate_performance_metrics.py          ← ✨ NEW

samples/
└── register_gate_metrics_example.py          ← ✨ NEW: Ready-to-use script

projects/sample-migration/outputs/summary/
├── gate_performance_metrics.jsonl            ← ✨ JSON Lines history
├── gate_metrics.csv                          ← ✨ Ready for Excel/BI
└── gate_metrics.json                         ← ✨ Structured backup
```
---

## ✅ Validation

Automated tests validate the main flows of the module:
```
test_record_single_metric .............. PASSED
test_get_by_gate ...................... PASSED
test_get_by_wave ...................... PASSED
test_aggregate_by_gate ................ PASSED
test_export_csv ....................... PASSED
test_export_json ...................... PASSED
test_persistence_reload ............... PASSED
test_summary_report ................... PASSED
```

---

## 🎯 Recommended Next Steps


### 1. **Immediate** — Test with your data
```bash
# Edit the example with your real data
nano samples/register_gate_metrics_example.py
python samples/register_gate_metrics_example.py

```

### 2. **Short Term** — Integrate with gates pipeline
Add this code after calculating each GateScore:
```python
registry.record(GatePerformanceMetric(...))
registry.export_csv("outputs/metrics/gate_metrics.csv")
```

### 3. **Medium Term** — Connect dashboard
- Open `gate_metrics.csv` in Excel, Tableau, Power BI, or Grafana
- Set up automatic refresh (daily/weekly)
- Create alerts based on aggregations

### 4. **Long Term** — Trends
After 5+ recorded waves, analyze:
- Degradation trend by gate
- Performance comparison between environments
- Anomaly detection

---

## 📞 Support

**Q: Do the data persist between runs?**
A: Yes! The `.jsonl` file automatically accumulates history. Loading the registry reloads all the data.

**Q: Can I have multiple registries?**
A: Yes! Create as many instances as you need, each with a different file.

**Q: How do I integrate with my BI tool?**
A: Export to CSV and connect directly. Most BI tools read CSV automatically.

**Q: What if I have multiple projects/waves?**
A: Each project has its own registry. You can aggregate all the CSVs into a single dashboard.

---

## 🎉 Para usar comece com:
```bash
python src/shared/samples/register_gate_metrics_example.py
```
Depois abra os arquivos gerados em `projects/sample-migration/outputs/summary/`.

Sucesso! 🚀
