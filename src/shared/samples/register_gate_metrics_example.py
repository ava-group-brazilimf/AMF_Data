#!/usr/bin/env python
"""
Example: Register gate performance metrics from a real migration wave

This script demonstrates how to:
1. Collect gate metrics from WAVE-001
2. Record them to the persistent registry
3. Export to CSV for dashboard consumption
4. Generate summary report

Run with:
    python -m samples.register_gate_metrics_example
    
Or from root:
    python samples/register_gate_metrics_example.py
"""

import sys
from pathlib import Path

# Add src directory to Python path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root / "src"))

from shared.scripts.metrics_registry import (
    GatePerformanceMetric,
    GatePerformanceRegistry,
)


def main(output_dir: Path = Path("projects/sample-migration/outputs/summary")):
    """Example workflow for registering gate metrics."""
        
    print("Gate Performance Metrics — Registration Example\n")
    
    # Setup paths
    output_dir.mkdir(parents=True, exist_ok=True)
    
    registry_file = output_dir / "gate_performance_metrics.jsonl"
    csv_export = output_dir / "gate_metrics.csv"
    json_export = output_dir / "gate_metrics.json"

    if registry_file.exists():
        registry_file.unlink()  # Remove existing registry for clean slate in this example
    
    print(f"Registry file: {registry_file}")
    print(f"CSV export:   {csv_export}")
    print(f"JSON export:  {json_export}\n")
    
    # Initialize registry (loads existing data if present)
    registry = GatePerformanceRegistry(registry_file)
    
    # Example: Register metrics for WAVE-001 across all 3 gates
    # (These are the values from your request)
    wave_metrics = [
        {
            "wave_id": "WAVE-001",
            "gate": 1,
            "tests_rate": 0.80,
            "dq_score": 0.75,
            "row_parity": 0.86,
            "rejection_rate": 0.33,
            "rework_count": 2,
            "rework_time_min": 90,
            "environment": "DEV",
        },
        {
            "wave_id": "WAVE-001",
            "gate": 2,
            "tests_rate": 0.87,
            "dq_score": 0.82,
            "row_parity": 0.90,
            "rejection_rate": 0.97,
            "rework_count": 1,
            "rework_time_min": 15,
            "environment": "UAT",
        },
        {
            "wave_id": "WAVE-001",
            "gate": 3,
            "tests_rate": 0.90,
            "dq_score": 0.87,
            "row_parity": 0.98,
            "rejection_rate": 1.00,
            "rework_count": 0,
            "rework_time_min": 0,
            "environment": "PROD",
        },
    ]
    
    print("📝 Recording metrics for WAVE-001:")
    for data in wave_metrics:
        metric = GatePerformanceMetric(**data)
        registry.record(metric)
        print(f"  ✓ Gate {data['gate']}: tests={data['tests_rate']:.1%}, "
              f"dq={data['dq_score']:.1%}, parity={data['row_parity']:.1%}, "
              f"rejection={data['rejection_rate']:.1%}, rework={data['rework_count']}x/{data['rework_time_min']}m")
    
    print("\nMetrics recorded successfully\n")
    
    # Example: Query the data back
    print("Retrieving recorded metrics:")
    all_metrics = registry.get_by_wave("WAVE-001")
    print(f"  Found {len(all_metrics)} gate records for WAVE-001\n")
    
    # Example: Export to CSV for dashboard
    print("Exporting to CSV...")
    registry.export_csv(csv_export)
    print(f"  ✓ CSV ready at {csv_export}\n")
    
    # Example: Export to JSON
    print("Exporting to JSON...")
    registry.export_json(json_export)
    print(f"  ✓ JSON ready at {json_export}\n")
    
    # Example: Generate summary
    print("Summary Report:")
    print(registry.summary_report())
    print()
    
    # Example: Query by gate with aggregation
    print("\nGate Aggregations:")
    for gate in [1, 2, 3]:
        agg = registry.aggregate_by_gate(gate)
        if agg:
            print(f"\n  Gate {gate}:")
            print(f"    Waves recorded: {agg.total_waves}")
            print(f"    Tests Rate:  {agg.avg_tests_rate:.1%} (range: {agg.min_tests_rate:.1%}–{agg.max_tests_rate:.1%})")
            print(f"    DQ Score:    {agg.avg_dq_score:.1%} (range: {agg.min_dq_score:.1%}–{agg.max_dq_score:.1%})")
            print(f"    Row Parity:  {agg.avg_row_parity:.1%} (range: {agg.min_row_parity:.1%}–{agg.max_row_parity:.1%})")
            print(f"    Rejection:   {agg.avg_rejection_rate:.1%} (range: {agg.min_rejection_rate:.1%}–{agg.max_rejection_rate:.1%})")
            print(f"    Rework Count:{agg.avg_rework_count:.1f} (range: {agg.min_rework_count:.0f}–{agg.max_rework_count:.0f})")
            print(f"    Rework Time: {agg.avg_rework_time_min:.1f} min (range: {agg.min_rework_time_min:.1f}–{agg.max_rework_time_min:.1f} min)")
    
    print("\n\nExample complete!")
    print("\nNext steps:")
    print("  1. Open the CSV file in Excel or your BI tool")
    print("  2. Set up automated exports in your CI/CD pipeline")
    print("  3. Connect your dashboard to the CSV or JSON export")


if __name__ == "__main__":
    main()
