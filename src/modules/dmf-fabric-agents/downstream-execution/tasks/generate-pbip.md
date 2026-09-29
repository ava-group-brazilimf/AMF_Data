# Task: generate-pbip

## Objetivo
Gerar um projeto Power BI `.pbip` com dados embutidos a partir de
`metrics_registry.json`, sem configurar fonte de dados ao abrir no Power BI Desktop.

## Pre-condicoes
- `metrics_registry.json` deve existir em `projects/{project-name}/outputs/summary/`
- Gate 3 deve estar `IN_PROGRESS` ou `COMPLETE`

## Como descobrir o wave_id

Leia o campo `wave_id` do primeiro item de `wave_summary` no
`metrics_registry.json`.

```powershell
python -c "import json, pathlib, sys; files = sorted(pathlib.Path('projects').glob('*/outputs/summary/metrics_registry.json')); sys.exit('metrics_registry.json nao encontrado em nenhum projeto') if not files else None; data = json.loads(files[0].read_text(encoding='utf-8')); print(data['wave_summary'][0]['wave_id'])"
```

## Execucao padrao

```powershell
python -m src.shared.scripts.generate_pbi_report `
    --metrics "projects/<project-name>/outputs/summary/metrics_registry.json" `
    --output  "projects/<project-name>/outputs/downstream/bi" `
    --wave    "WAVE-001"
```

## Smoke test rapido (sem artefatos reais)

Se ainda nao existir `metrics_registry.json` no projeto, gere um arquivo sintetico:

```powershell
New-Item -ItemType Directory -Force -Path tmp | Out-Null
python -c "import json, pathlib; p = pathlib.Path('tmp/metrics_registry.json'); d = {'schema_version':'1.0','exported_at':'2026-07-30T00:00:00Z','wave_summary':[{'wave_id':'WAVE-001','overall_pct':80.0,'tables_migrated':8,'tables_total':10,'tables_pct':80.0,'pipelines_migrated':4,'pipelines_total':5,'pipelines_pct':80.0,'avg_pipeline_time_minutes':12.5,'environment':'DEV','recorded_at':'2026-07-30T00:00:00Z','notes':None}],'gate_status':[],'gate_metrics':[],'benchmarks':[],'reconciliation':[],'inventory':[],'other_metrics':[]}; p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')"
python -m src.shared.scripts.generate_pbi_report `
    --metrics "tmp/metrics_registry.json" `
    --output  "tmp/bi" `
    --wave    "WAVE-001"
```

Saida esperada:
- `tmp/bi/WAVE-001.pbip/WAVE-001.pbip`
- `tmp/bi/WAVE-001.pbip/.SemanticModel/`
- `tmp/bi/WAVE-001.pbip/.Report/`

## Observacoes
- O parametro `--compile-pbix` nao faz mais parte do script.
- O fluxo oficial gera `.pbip`; se precisar de `.pbix`, abra o `.pbip` no Power BI Desktop e salve/exporte.