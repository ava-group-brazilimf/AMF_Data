"""Tests for B-014: KPI dictionary and ownership model."""
import unittest

from scripts.kpi_dictionary import (
    KPI,
    KPIOwnership,
    KPIDictionary,
    load_kpi_dictionary,
    KPI_DEFAULTS,
)


class KPIDictionaryTests(unittest.TestCase):
    def test_default_kpis_present(self) -> None:
        """Must contain the 5 KPIs defined in gate1-kpis.md template."""
        required = {
            "row_count_parity",
            "dq_score",
            "migration_duration",
            "first_pass_success_rate",
            "mttr",
        }
        ids = {k.id for k in KPI_DEFAULTS}
        self.assertTrue(required.issubset(ids), f"Missing: {required - ids}")

    def test_each_kpi_has_owner(self) -> None:
        for kpi in KPI_DEFAULTS:
            self.assertIsNotNone(kpi.ownership, f"{kpi.id} missing ownership")
            self.assertNotEqual("", kpi.ownership.owner_agent)

    def test_dictionary_lookup_by_id(self) -> None:
        d = KPIDictionary(KPI_DEFAULTS)
        kpi = d.get("row_count_parity")
        self.assertIsNotNone(kpi)
        self.assertEqual("row_count_parity", kpi.id)

    def test_dictionary_lookup_missing_raises(self) -> None:
        d = KPIDictionary(KPI_DEFAULTS)
        with self.assertRaises(KeyError):
            d.get("nonexistent_kpi")

    def test_load_from_yaml_round_trips(self) -> None:
        import tempfile, yaml
        from pathlib import Path
        d = KPIDictionary(KPI_DEFAULTS)
        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = Path(tmp) / "kpis.yaml"
            d.to_yaml(yaml_path)
            loaded = load_kpi_dictionary(yaml_path)
        self.assertEqual(len(KPI_DEFAULTS), len(loaded.kpis))

    def test_all_kpis_have_measurement_method(self) -> None:
        for kpi in KPI_DEFAULTS:
            self.assertNotEqual("", kpi.measurement_method, f"{kpi.id} missing measurement_method")


if __name__ == "__main__":
    unittest.main()
