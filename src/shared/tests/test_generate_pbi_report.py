"""
test_generate_pbi_report.py — DMF v3 · Bianca (bi-semantic)

Testa a API real de scripts/generate_pbi_report.py (arquitetura TMDL/PBIP).
Substitui a versão anterior, que importava uma API model.bim inexistente
(build_table_*, build_model_bim, build_report_json, write_pbip_structure).
"""

import json

import pytest

from scripts.generate_pbi_report import (
    _TABLE_REGISTRY,
    _build_table_tmdl,
    _m_literal,
    _make_m_partition,
    generate,
    load_metrics,
    resolve_wave_id,
    write_report,
    write_semantic_model,
)

SAMPLE = {
    "schema_version": "1.0",
    "exported_at": "2026-06-17T17:45:00Z",
    "wave_summary": [{"wave_id": "WAVE-TEST", "overall_pct": 72.5,
                      "tables_migrated": 12, "tables_total": 20,
                      "tables_pct": 60.0, "pipelines_migrated": 5,
                      "pipelines_total": 8, "pipelines_pct": 62.5,
                      "avg_pipeline_time_minutes": 14.2,
                      "tables_remaining": 8, "backlog_pct": 40.0,
                      "gb_remaining": 30.0, "wave_estimate_accuracy": 96.2,
                      "environment": "DEV",
                      "recorded_at": "2026-06-17T17:40:00Z", "notes": None}],
    "estimate_comparison": [{"wave_id": "WAVE-TEST", "entity": "orders",
                             "estimated_rows": 1000000, "actual_rows": 980000,
                             "delta": -20000, "delta_pct": -2.0,
                             "accuracy_pct": 98.0, "environment": "DEV",
                             "recorded_at": "2026-06-17T17:40:00Z", "notes": None}],
    "gate_status": [{"wave_id": "WAVE-TEST", "gate": 1,
                     "phase_status": "COMPLETE", "artifacts_present": 5,
                     "artifacts_total": 5, "artifacts_pct": 100.0,
                     "tasks_completed": 10, "tasks_total": 10,
                     "tasks_pct": 100.0, "avg_task_time_minutes": 8.5,
                     "gate_score": 88.0, "environment": "DEV",
                     "recorded_at": "2026-06-17T17:40:00Z", "notes": None}],
    "gate_metrics": [{"wave_id": "WAVE-TEST", "gate": 1, "tests_rate": 0.92,
                      "dq_score": 0.89, "row_parity": 0.98,
                      "rejection_rate": 0.05, "rework_count": 1,
                      "rework_time_min": 30.0, "environment": "DEV",
                      "recorded_at": "2026-06-17T17:41:00Z", "notes": None}],
    "benchmarks": [{"wave_id": "WAVE-TEST", "entity": "orders",
                    "rows_processed": 1000000, "rows_per_second": 16666.67,
                    "bytes_processed": 500000000, "throughput_gb_per_day": 670.55,
                    "total_volume": "0.4657 GB", "table_size": "2.5 GB",
                    "avg_table_size": "1.4 GB", "duration_seconds": 60,
                    "status": "PASS", "environment": "DEV",
                    "recorded_at": "2026-06-17T17:42:00Z", "notes": None}],
    "reconciliation": [{"wave_id": "WAVE-TEST", "entity": "orders",
                        "status": "PASS", "source_count": 1000000,
                        "target_count": 1000000, "count_mismatch": False,
                        "checksum_mismatch": False,
                        "environment": "DEV",
                        "recorded_at": "2026-06-17T17:43:00Z", "notes": None}],
    "mismatch_categories": [{"wave_id": "WAVE-TEST", "category": "missing_rows", "count": 2,
                             "environment": "DEV", "recorded_at": "2026-06-17T17:43:00Z", "notes": None}],
    "inventory": [{"wave_id": "WAVE-TEST", "tables_total": 20,
                   "tables_migrated": 12, "pipelines_total": 8,
                   "pipelines_migrated": 5, "avg_table_size_gb": 2.4,
                   "total_volume_gb": 48.0, "data_accuracy_pct": 99.9,
                   "auto_validated_pct": 92.0, "migration_ready_pct": 88.0,
                   "simple_pct": 60.0, "complex_pct": 40.0,
                   "environment": "DEV",
                   "recorded_at": "2026-06-17T17:44:00Z", "notes": None}],
    "complexity_distribution": [{"wave_id": "WAVE-TEST", "complexity": "LOW", "value": 5,
                                 "environment": "DEV", "recorded_at": "2026-06-17T17:44:00Z", "notes": None}],
    "other_metrics": [],
}


@pytest.fixture
def metrics_file(tmp_path):
    """metrics_registry.json em disco, para exercitar load_metrics/generate."""
    p = tmp_path / "metrics_registry.json"
    p.write_text(json.dumps(SAMPLE, ensure_ascii=False), encoding="utf-8")
    return p


# -- load_metrics / resolve_wave_id -------------------------------------------

def test_load_metrics_roundtrip(metrics_file):
    data = load_metrics(metrics_file)
    assert data["schema_version"] == "1.0"
    assert data["wave_summary"][0]["wave_id"] == "WAVE-TEST"


def test_resolve_wave_id():
    assert resolve_wave_id(SAMPLE, None) == "WAVE-TEST"
    assert resolve_wave_id(SAMPLE, "WAVE-TEST") == "WAVE-TEST"
    with pytest.raises(ValueError):
        resolve_wave_id(SAMPLE, "WAVE-INEXISTENTE")


def test_resolve_wave_id_sem_wave_summary():
    with pytest.raises(ValueError):
        resolve_wave_id({"wave_summary": []}, None)


# -- Definicoes de tabela (_TABLE_REGISTRY) -----------------------------------

def test_registry_completo():
    nomes = [t[0] for t in _TABLE_REGISTRY]
    assert nomes == ["WaveSummary", "EstimateComparison", "GateStatus",
                     "GateMetrics", "Benchmarks", "Reconciliation",
                     "MismatchCategories", "Inventory",
                     "ComplexityDistribution"]


@pytest.mark.parametrize("tname,def_fn,key,lb", _TABLE_REGISTRY)
def test_definicoes_de_tabela(tname, def_fn, key, lb):
    cols, msrs = def_fn()
    assert cols, f"{tname} deve declarar colunas"
    # Inventory e uma tabela de dados sem medidas — msrs vazio e valido
    assert isinstance(msrs, list)
    assert all("name" in c and "dataType" in c for c in cols)
    assert all(len(m) == 2 for m in msrs)
    assert key in SAMPLE, f"chave '{key}' ausente no SAMPLE"
    col_names = {c["name"] for c in cols}
    assert "wave_id" in col_names


@pytest.mark.parametrize("tname,def_fn,key,lb", _TABLE_REGISTRY)
def test_medidas_referenciam_a_propria_tabela(tname, def_fn, key, lb):
    _, msrs = def_fn()
    for nome, dax in msrs:
        assert tname in dax, f"medida '{nome}' de {tname} nao referencia a tabela"


def test_reconciliation_has_errors_per_million_measure():
    _, msrs = _TABLE_REGISTRY[5][1]()
    names = [name for name, _ in msrs]
    assert "Errors per Million" in names

    dax = next(dax for name, dax in msrs if name == "Errors per Million")
    assert "MismatchCategories[count]" in dax
    assert "Reconciliation[source_count]" in dax
    assert "DIVIDE(" in dax
    assert "1000000" in dax


def test_report_page_recon_has_errors_per_million_card(tmp_path):
    rpt = tmp_path / "WAVE-TEST.Report"
    write_report(rpt, "WAVE-TEST", dry_run=False)

    visuals = []
    for visual_dir in (rpt / "definition" / "pages" / "page_recon" / "visuals").iterdir():
        if visual_dir.is_dir():
            visuals.append(json.loads((visual_dir / "visual.json").read_text(encoding="utf-8")))

    card_refs = []
    for visual in visuals:
        q = visual.get("visual", {}).get("query", {})
        if visual.get("visual", {}).get("visualType") == "card":
            props = q.get("queryState", {}).get("Values", {}).get("projections", [])
            for projection in props:
                if isinstance(projection, dict):
                    card_refs.append(projection.get("queryRef"))

    assert any(ref == "Reconciliation.Errors per Million" for ref in card_refs)


# -- Geracao da expressao M ---------------------------------------------------

def test_m_literal():
    assert _m_literal(None, "string") == "null"
    assert _m_literal(None, "int64") == "null"
    assert _m_literal(True, "boolean") == "true"
    assert _m_literal(False, "boolean") == "false"
    assert _m_literal(42, "int64") == "42"
    assert _m_literal(1.5, "double") == "1.5"
    assert _m_literal("orders", "string") == '"orders"'


def test_m_literal_escapa_aspas_e_barras():
    assert _m_literal('a"b', "string") == '"a\\"b"'
    assert _m_literal("a\\b", "string") == '"a\\\\b"'


def test_make_m_partition_com_linhas():
    cols, _ = _TABLE_REGISTRY[0][1]()
    rows = SAMPLE["wave_summary"]
    m = _make_m_partition("WaveSummary", cols, rows)
    assert m.startswith("let")
    assert "Table.FromRecords(" in m
    assert "Table.TransformColumnTypes(" in m
    assert m.rstrip().endswith("ChangedTypes")
    assert 'wave_id="WAVE-TEST"' in m
    assert "notes=null" in m
    assert "Int64.Type" in m


def test_make_m_partition_sem_linhas():
    cols, _ = _TABLE_REGISTRY[0][1]()
    m = _make_m_partition("WaveSummary", cols, [])
    assert "#table(" in m
    assert "Table.FromRecords(" not in m
    assert "Table.TransformColumnTypes(" in m


# -- TMDL ---------------------------------------------------------------------

def test_build_table_tmdl():
    tname, def_fn, key, lb = _TABLE_REGISTRY[0]
    cols, msrs = def_fn()
    tmdl = _build_table_tmdl(tname, cols, msrs, SAMPLE[key], lb)

    assert tmdl.startswith(f"table '{tname}'")
    assert "lineageTag:" in tmdl
    for nome, _dax in msrs:
        assert f"measure '{nome}'" in tmdl
    for c in cols:
        assert f"\tcolumn {c['name']}" in tmdl
        assert f"sourceColumn: {c['name']}" in tmdl
    assert f"partition '{tname}-Partition' = m" in tmdl
    assert "mode: import" in tmdl
    assert "annotation PBI_ResultType = Table" in tmdl


# -- write_semantic_model / write_report --------------------------------------

def test_write_semantic_model(tmp_path):
    sm = tmp_path / "WAVE-TEST.SemanticModel"
    write_semantic_model(sm, SAMPLE, "WAVE-TEST", dry_run=False)

    assert (sm / ".platform").exists()
    assert (sm / "definition.pbism").exists()
    assert (sm / "definition" / "model.tmdl").exists()
    assert (sm / "definition" / "database.tmdl").exists()
    assert (sm / "definition" / "diagramLayout.json").exists()

    for tname, *_ in _TABLE_REGISTRY:
        f = sm / "definition" / "tables" / f"{tname}.tmdl"
        assert f.exists(), f"{tname}.tmdl nao gerado"
        assert f.read_text(encoding="utf-8").startswith(f"table '{tname}'")

    model = (sm / "definition" / "model.tmdl").read_text(encoding="utf-8")
    for tname, *_ in _TABLE_REGISTRY:
        assert f"ref table '{tname}'" in model

    platform = json.loads((sm / ".platform").read_text(encoding="utf-8"))
    assert platform["metadata"]["type"] == "SemanticModel"


def test_write_semantic_model_filtra_por_wave(tmp_path):
    data = json.loads(json.dumps(SAMPLE))
    outra = json.loads(json.dumps(SAMPLE["wave_summary"][0]))
    outra["wave_id"] = "WAVE-OUTRA"
    data["wave_summary"].append(outra)

    sm = tmp_path / "WAVE-TEST.SemanticModel"
    write_semantic_model(sm, data, "WAVE-TEST", dry_run=False)

    tmdl = (sm / "definition" / "tables" / "WaveSummary.tmdl").read_text(encoding="utf-8")
    assert "WAVE-TEST" in tmdl
    assert "WAVE-OUTRA" not in tmdl


def test_write_semantic_model_dry_run(tmp_path):
    sm = tmp_path / "WAVE-TEST.SemanticModel"
    write_semantic_model(sm, SAMPLE, "WAVE-TEST", dry_run=True)
    assert not sm.exists(), "dry_run nao deve escrever em disco"


def test_write_semantic_model_preserves_real_rows_for_content_tables(tmp_path):
    sm = tmp_path / "WAVE-TEST.SemanticModel"
    write_semantic_model(sm, SAMPLE, "WAVE-TEST", dry_run=False)

    estimate_tmdl = (sm / "definition" / "tables" / "EstimateComparison.tmdl").read_text(encoding="utf-8")
    assert "orders" in estimate_tmdl
    assert "estimated_rows" in estimate_tmdl
    assert "actual_rows" in estimate_tmdl

    complexity_tmdl = (sm / "definition" / "tables" / "ComplexityDistribution.tmdl").read_text(encoding="utf-8")
    assert "LOW" in complexity_tmdl
    assert "value=5" in complexity_tmdl

    mismatch_tmdl = (sm / "definition" / "tables" / "MismatchCategories.tmdl").read_text(encoding="utf-8")
    assert "missing_rows" in mismatch_tmdl
    assert "count=2" in mismatch_tmdl


def test_write_report(tmp_path):
    rpt = tmp_path / "WAVE-TEST.Report"
    write_report(rpt, "WAVE-TEST", dry_run=False)

    assert (rpt / ".platform").exists()
    assert (rpt / "definition.pbir").exists()
    assert (rpt / "definition" / "report.json").exists()
    assert (rpt / "definition" / "version.json").exists()

    pages_json = rpt / "definition" / "pages" / "pages.json"
    assert pages_json.exists()
    pages = json.loads(pages_json.read_text(encoding="utf-8"))
    assert pages["pageOrder"] == ["page_exec", "page_gate", "page_estimates",
                                  "page_quality", "page_complexity",
                                  "page_recon", "page_mismatch",
                                  "page_bench"]
    assert pages["activePageName"] == "page_exec"

    for folder in pages["pageOrder"]:
        pg = rpt / "definition" / "pages" / folder
        assert (pg / "page.json").exists()
        visuais = list((pg / "visuals").glob("*/visual.json"))
        assert visuais, f"pagina {folder} sem visuais"
        for v in visuais:
            json.loads(v.read_text(encoding="utf-8"))

    report = json.loads((rpt / "definition" / "report.json").read_text(encoding="utf-8"))
    anot = {a["name"]: a["value"] for a in report["annotations"]}
    assert anot["DMF_WaveId"] == "WAVE-TEST"


def test_write_report_dry_run(tmp_path):
    rpt = tmp_path / "WAVE-TEST.Report"
    write_report(rpt, "WAVE-TEST", dry_run=True)
    assert not rpt.exists()


# -- generate() — end-to-end --------------------------------------------------

def test_generate_end_to_end(metrics_file, tmp_path):
    out = tmp_path / "bi"
    pbip_root = generate(metrics_path=metrics_file, output_dir=out,
                         wave_filter="WAVE-TEST")

    assert pbip_root.exists()
    assert pbip_root.name == "WAVE-TEST.pbip"
    assert (pbip_root / "WAVE-TEST.pbip").exists()
    assert (pbip_root / ".gitignore").exists()

    sm_dirs = [d for d in pbip_root.iterdir()
               if d.is_dir() and d.name.endswith(".SemanticModel")]
    rp_dirs = [d for d in pbip_root.iterdir()
               if d.is_dir() and d.name.endswith(".Report")]
    assert len(sm_dirs) == 1
    assert len(rp_dirs) == 1

    assert (sm_dirs[0] / "definition" / "tables" / "WaveSummary.tmdl").exists()
    assert (rp_dirs[0] / "definition" / "pages" / "pages.json").exists()

    pbir = json.loads((rp_dirs[0] / "definition.pbir").read_text(encoding="utf-8"))
    alvo = (rp_dirs[0] / pbir["datasetReference"]["byPath"]["path"]).resolve()
    assert alvo == sm_dirs[0].resolve(), (
        f"definition.pbir aponta para {alvo}, "
        f"mas o SemanticModel esta em {sm_dirs[0]}"
    )


def test_generate_wave_inexistente(metrics_file, tmp_path):
    with pytest.raises(ValueError):
        generate(metrics_path=metrics_file, output_dir=tmp_path / "bi",
                 wave_filter="WAVE-NAO-EXISTE")


def test_generate_dry_run(metrics_file, tmp_path):
    out = tmp_path / "bi"
    generate(metrics_path=metrics_file, output_dir=out,
             wave_filter="WAVE-TEST", dry_run=True)
    assert not out.exists(), "dry_run nao deve escrever em disco"


def test_generate_sobrescreve_execucao_anterior(metrics_file, tmp_path):
    out = tmp_path / "bi"
    pbip_root = generate(metrics_path=metrics_file, output_dir=out,
                         wave_filter="WAVE-TEST")
    sujeira = pbip_root / "residuo.txt"
    sujeira.write_text("stale", encoding="utf-8")

    generate(metrics_path=metrics_file, output_dir=out, wave_filter="WAVE-TEST")
    assert not sujeira.exists(), "geracao deve limpar o diretorio anterior"
