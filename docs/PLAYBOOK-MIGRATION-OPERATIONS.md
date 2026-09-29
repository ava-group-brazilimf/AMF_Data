# Playbook de Operação de Migração

> **Tipo:** How-to Guide — operação completa de uma migration wave do início ao fim  
> **Público:** Migration Coordinator, Data Engineer, Downstream Executor  
> **Pré-requisito:** Ambiente configurado (ver [PLAYBOOK-ONBOARDING.md](PLAYBOOK-ONBOARDING.md))

---

## Visão Geral do Fluxo

```

PRÉ-MIGRAÇÃO          GATE 1                GATE 2                GATE 3            PÓS-MIGRAÇÃO
──────────────    ──────────────────    ──────────────────    ──────────────────    ──────────────
Setup wave    →   Discovery + Design →  Architecture +      → Execution +        → Retrospectiva
Kickoff           STTM + DQ Rules       Data Model            Reconciliation        Improvement
                  ↓                     ↓                     ↓
                  GateScore >= 0.85     GateScore >= 0.85     GateScore >= 0.85
                  (ou aprovado c/ res.) (ou aprovado c/ res.) (ou aprovado c/ res.)

```

**Regra de ouro:** nenhuma fase pode avançar sem GateScore calculado e decisão de aprovação registrada.

```

GateScore = 0.35 × Completude + 0.25 × Qualidade + 0.20 × RiscoResidual + 0.20 × Reconciliação

```

| Faixa de Score | Decisão | Ação |
| --- | --- | --- |

| >= 0.85 | Aprovado | Avançar para próxima fase |
| 0.70 – 0.84 | Aprovado com ressalvas | Avançar registrando open items obrigatórios |
| < 0.70 | Bloqueado | Corrigir e re-submeter ao gate |

---

## Fase 0 — Pré-Migração: Kickoff da Wave

**Objetivo:** registrar o escopo, atribuir discovery owner e criar uma raiz operacional única para a wave.

### Passo 0.1 — Criar a raiz da wave

Use sempre `projects/{project_name}/`. Não use a pasta `project/` na raiz nem
pastas de output locais dos agentes.

```powershell
$project = "migration-northwind"
Copy-Item projects/_template "projects/$project" -Recurse
New-Item "projects/$project/outputs/upstream" -ItemType Directory -Force
New-Item "projects/$project/outputs/midstream" -ItemType Directory -Force
New-Item "projects/$project/outputs/downstream" -ItemType Directory -Force
New-Item "projects/$project/outputs/summary" -ItemType Directory -Force
```

**Saídas esperadas:**

- `projects/migration-northwind/wave-config.yaml` preenchido
- `context/project-config.yaml` e `context/agent-task-config.yaml` preenchidos
- Estrutura `outputs/{upstream,midstream,downstream,summary}` criada

Os três YAMLs devem declarar exatamente `project_name: "migration-northwind"`.
No `wave-config.yaml`, declare também:

```yaml
context_base_path: "projects/{project_name}/context"
outputs_base_path: "projects/{project_name}/outputs"
```

### Passo 0.2 — Validar o wave-config.yaml

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_wave_config `
    projects\migration-northwind\wave-config.yaml

```

Resultado esperado: `Wave config validation: PASS`. Não prossiga com warnings de
`project_name` ausente nem com erros de arquivos de contexto.

### Passo 0.3 — Assign discovery owner

**Regra operacional:** cada wave deve ter exatamente 1 discovery owner primário definido antes de iniciar Gate 1. O `inventory-scout` só entra como fallback se houver critério documentado.

Registre no `wave-config.yaml`:

```yaml
discovery_owner_primary: "discovery-scout"   # primário obrigatório
discovery_owner_fallback: "inventory-scout"  # somente por exceção

```

### Passo 0.4 — Iniciar a wave

Abra o `migration-coordinator` e informe o caminho explícito da configuração:

```text
[Selecione: migration-coordinator]
> *start-wave
wave_config_path: projects/migration-northwind/wave-config.yaml
```

O coordenador deve carregar os dois arquivos de `context/` antes da primeira
delegação e fixar todos os outputs em `projects/migration-northwind/outputs/`.

**Checklist de saída da Fase 0:**

- [ ] Nome e ID da wave definidos

- [ ] Escopo de entidades listado

- [ ] Discovery owner atribuído

- [ ] `wave-config.yaml` válido (teste com script)
- [ ] `project_name` idêntico na pasta e nos três YAMLs
- [ ] Dois arquivos de contexto carregados
- [ ] `outputs_base_path` e `context_base_path` resolvidos dentro da pasta da wave
- [ ] Wave iniciada com `wave_config_path` explícito

---

## Fase 1 — UPSTREAM: Discovery e Gate 1

**Objetivo:** catalogar o ambiente legado, mapear dependências, definir estratégia e produzir todos os artefatos obrigatórios do Gate 1 (incluindo trilha AST quando aplicável).

**Agentes desta fase:** `discovery-scout`, `data-strategist`, `business-analyst`, `logic-extractor`

---

### Passo 1.1 — Discovery do ambiente legado

```

[Selecione: discovery-scout]
> *scan-repo
Fonte: SQL Server 2019, banco: NORTHWIND_PROD
Schemas a escanear: dbo, sales

> *classify
Classifique todos os objetos encontrados por complexidade (Low/Medium/High)

> *map-dependencies
Mostre o DAG de dependências das entidades no escopo da WAVE-002

> *estimate-volume
Estime volumes para: Customers, OrderHeaders, OrderLines

```

**Saídas esperadas:**

- `inventory-report.md` — catálogo completo de objetos com complexidade

- Diagrama Mermaid de dependências

- Estimativa de volume por entidade

---

### Passo 1.2 — Problem statement e KPIs

```

[Selecione: data-strategist]
> *define-problem
Projeto: WAVE-002 — migração de entidades transacionais do ERP legado
Motorista de negócio: consolidar dados de pedidos no destino

> *create-kpis
Baseado no problem statement da WAVE-002

```

**Saídas esperadas:**

- `gate1-problem-statement.md`

- `gate1-kpis.md` — 5 KPIs com owners e targets

---

### Passo 1.3 — STTM e regras de DQ

```

[Selecione: business-analyst]
> Criar STTM para: Customers, OrderHeaders, OrderLines
  Fonte: SQL Server (dbo)
  Destino: destino conforme arquitetura definida

> Definir regras de DQ:
  - CustomerID: NOT NULL, único
  - OrderDate: NOT NULL, deve ser >= 2000-01-01
  - TotalAmount: deve ser > 0

```

**Saídas esperadas:**

- `sttm.md` — Source-to-Target Mapping por entidade

- `dq-rules.md` — regras de qualidade com severidade

- `data-dictionary.md`

---

### Passo 1.4 — Extração de lógica de negócio (se houver código legado)

```

[Selecione: logic-extractor]
> *extract-logic
Alvo: stored procedures de cálculo de frete e desconto
Path: /legacy-code/stored-procedures/

> *classify-logic
Separe: lógica de negócio vs lógica de infraestrutura

> *extract-ast
Tipo: SQL ou SSIS
Path: /legacy-code/
Plataforma alvo: (informe a plataforma)

```

**Saídas esperadas:**

- `business-rules.md` — regras de negócio documentadas

- `logic-map.md` — mapeamento de lógica para destino

- `canonical-model.json` — modelo canônico extraído via AST

- `column-lineage.json` — lineage coluna-a-coluna

- `sttm.md` — STTM derivado/atualizado automaticamente

---

### Passo 1.5 — Validar score de Gate 1

Calcule o GateScore e registre a decisão:

```

[Selecione: migration-coordinator]
> *gate1-validate
Wave: WAVE-002

```

**Checklist mínimo do Gate 1 (artefatos obrigatórios):**

- [ ] `inventory-report.md` — completo

- [ ] `gate1-problem-statement.md` — aprovado

- [ ] `gate1-kpis.md` — 5 KPIs com owners

- [ ] `sttm.md` — todas as entidades mapeadas

- [ ] `dq-rules.md` — regras com severidade

- [ ] Discovery owner registrado no `wave-config.yaml`

- [ ] (Se trilha AST) `canonical-model.json` válido (chaves mínimas: `pipeline_id`, `pipeline_name`, `source_platform`)

**Decisão de gate:** registre em `gate1-decision.md` com score, aprovadores e open items (se houver).

---

## Fase 2 — MIDSTREAM: Design e Gate 2

**Objetivo:** definir arquitetura, modelo de dados, políticas de governança, código gerado e validado.

**Agentes desta fase:** `data-architect`, `data-modeler`, `data-steward`, `code-generator`, `quality-gate`, `security-compliance`

---

### Passo 2.1 — Arquitetura de dados

```

[Selecione: data-architect]
> *design-architecture
Wave: WAVE-002
Entidades: Customers, OrderHeaders, OrderLines
Camadas: Bronze / Silver / Gold
Plataforma: (informe a plataforma alvo)

```

**Saídas esperadas:**

- `architecture.md` — decisões de arquitetura, padrões de zona, particionamento

- `decisions.md` — ADRs das decisões técnicas (Architecture Decision Records)

- `monitoring-spec.md` — especificação de observabilidade e SLOs

---

### Passo 2.2 — Modelo de dados

```

[Selecione: data-modeler]
> *create-model
Baseado no STTM e na arquitetura definida para WAVE-002

> *review-granularity
Confirme granularidade e chave de partição para OrderHeaders

```

**Saídas esperadas:**

- `data-model.md` — modelo lógico com entidades, atributos, tipos, PKs/FKs

- Diagrama ER (Mermaid)

---

### Passo 2.3 — Governança e catálogo

```

[Selecione: data-steward]
> *catalog
Registre todas as entidades da WAVE-002 no catálogo de dados

> *define-policies
Defina políticas de acesso e retenção para Customers (dados pessoais)

```

**Saídas esperadas:**

- Entradas de catálogo por entidade

- Políticas de acesso e retenção documentadas

---

### Passo 2.4 — Geração de DDL/ETL

```

[Selecione: code-generator]
> *generate-ddl
Baseado no data-model.md da WAVE-002

> *generate-etl
Gerar ETL para: Bronze → Silver → Gold
Padrão: incremental com watermark por OrderDate

> *generate-from-ast
Input: canonical-model.json
Plataformas: fabric, databricks, airflow

```

**Saídas esperadas:**

- `ddl/` — scripts de criação das tabelas no destino

- `etl/` — scripts de carga por camada

- `generated-code/fabric/`, `generated-code/databricks/`, `generated-code/airflow/` (quando usar AST)

---

### Passo 2.5 — Validação de qualidade do código

```

[Selecione: quality-gate]
> *validate-code
Path: ddl/, etl/
Wave: WAVE-002

> *score
Calcule o GateScore de qualidade para WAVE-002

```

**Saídas esperadas:**

- `quality-gate-evidence.md` — scoring por dimensão, status de aprovação, open items

---

### Passo 2.6 — Compliance e PII

```

[Selecione: security-compliance]
> *detect-pii
Entidades: Customers
Campos em análise: CustomerName, Email, Phone, Address

> *masking-rules
Defina estratégia de masking por ambiente (DEV/HML/PROD)

```

**Saídas esperadas:**

- `security-compliance-report.md` — PII detectados, status de masking, recomendações

---

### Passo 2.7 — Validar score de Gate 2

**Checklist mínimo do Gate 2 (artefatos obrigatórios):**

- [ ] `architecture.md`

- [ ] `data-model.md`

- [ ] `decisions.md`

- [ ] `dq-rules.md` (refinado com novas regras do design)

- [ ] `monitoring-spec.md`

- [ ] `quality-gate-evidence.md` — status PASS/FAIL explícito

- [ ] `security-compliance-report.md`

- [ ] (Se trilha AST) `column-lineage.json` e `sttm.md` presentes

**Decisão de gate:** registre em `gate2-decision.md` com score, aprovadores e open items.

---

## Fase 3 — DOWNSTREAM: Execução e Gate 3

**Objetivo:** executar a wave no ambiente real, reconciliar dados, publicar evidências, emitir runbook.

**Agentes desta fase:** `downstream-executor`, `reconciliation`, `self-healing`, `documentation`

---

### Passo 3.1 — Revisão pré-execução: dry run

**Antes de qualquer execução real, sempre execute dry run primeiro:**

```

[Selecione: downstream-executor]
> *dry-run
Wave: WAVE-002

```

Verifique:

- Nenhum erro de sintaxe nos DDLs

- ETL sem dependências ausentes

- Permissões confirmadas no destino

---

### Passo 3.2 — Criar execution-runbook

**O `execution-runbook.md` é obrigatório antes do non-dry run.**

```

[Selecione: downstream-executor]
> *create-runbook
Wave: WAVE-002
Incluir: passos de execução, rollback plan, pontos de checkpoint, responsáveis

```

Revise e assine o runbook antes de avançar.

---

### Passo 3.3 — Execução real da wave

```

[Selecione: downstream-executor]
> *execute-wave
Wave: WAVE-002
Modo: incremental

```

**Durante a execução monitore:**

- Logs de carga por entidade

- Erros imediatos (early fail)

- Volume de registros processados vs esperado

---

### Passo 3.4 — Diagnóstico de falhas (se houver)

Se a execução falhar em qualquer ponto:

```

[Selecione: self-healing]
> *diagnose
Wave: WAVE-002
Erro reportado: [cole a mensagem de erro aqui]

> *apply-fix
Aplique a correção sugerida e re-execute o step com falha

```

**Saídas esperadas:**

- `error-pattern-log.md` — padrão identificado e solução aplicada

- Registro do aprendizado para waves futuras

---

### Passo 3.5 — Reconciliação de dados

O módulo `reconciliation_checks.py` suporta dois modos de operação. Escolha o modo adequado ao seu ambiente:

#### Modo DISCONNECTED (padrão — sem conexão live)

Use quando dados são exportados previamente como CSV ou fornecidos como listas Python:

```python
# Opção A: listas in-memory
from scripts.reconciliation_checks import reconcile_checksums

report = reconcile_checksums(
    entity="OrderHeaders",
    source_rows=[{"id": 1, "amount": 500}, ...],  # extraído manualmente
    target_rows=[{"id": 1, "amount": 500}, ...],  # extraído do destino
)

# Opção B: arquivos CSV exportados
from scripts.reconciliation_checks import reconcile_from_sources, ReconciliationMode
from pathlib import Path

report = reconcile_from_sources(
    entity="OrderHeaders",
    source_loader=Path("exports/source_orderheaders.csv"),
    target_loader=Path("exports/target_orderheaders.csv"),
    mode=ReconciliationMode.DISCONNECTED,
)
print(report)  # Reconciliation [OrderHeaders] (DISCONNECTED): PASS
```

#### Modo CONNECTED (adaptadores callable — acesso direto ao banco)

Use quando há conectividade direta com os sistemas fonte e destino. Forneça funções (callables) que retornam `list[dict]`:

```python
from scripts.reconciliation_checks import reconcile_from_sources, ReconciliationMode

def fetch_source_orders():
    # usa qualquer biblioteca: pyodbc, psycopg2, spark, REST, etc.
    return source_db.execute("SELECT * FROM OrderHeaders").fetchall()

def fetch_target_orders():
    return target_db.execute("SELECT * FROM OrderHeaders").fetchall()

report = reconcile_from_sources(
    entity="OrderHeaders",
    source_loader=fetch_source_orders,
    target_loader=fetch_target_orders,
    mode=ReconciliationMode.CONNECTED,
)
print(report.status)  # PASS ou FAIL
```

#### Via agente

```

[Selecione: reconciliation]
> *row-count
Wave: WAVE-002
Entidades: Customers, OrderHeaders, OrderLines

> *checksum
Entidades de alto risco: OrderHeaders (financeiro)

> *schema-diff
Compare schema fonte vs destino para todas as entidades da wave

```

**Saídas esperadas:**

- `reconciliation-evidence.md` — row counts, checksums, schema diffs, status PASS/FAIL

- Entidades com desvio registradas com severidade

---

### Passo 3.6 — Publicar documentação da wave

```

[Selecione: documentation]
> *wave-report
Wave: WAVE-002
Inclua: sumário executivo, artefatos produzidos, GateScore, desvios, lições aprendidas

> *runbook-update
Atualize o execution-runbook com as lições da execução real

```

**Saídas esperadas:**

- `wave-report.md` — relatório completo de entrega

- `execution-runbook.md` (versão final atualizada)

- `data-lineage.md` (se aplicável)

---

### Passo 3.7 — Validar score de Gate 3

**Checklist mínimo do Gate 3 (pacote de entrega obrigatório):**

- [ ] `ddl/` — scripts executados com sucesso

- [ ] `etl/` — scripts executados com sucesso

- [ ] `tests/` — testes de integração passando

- [ ] `documentation/` — wave-report, runbook, lineage

- [ ] `reconciliation-evidence.md` — PASS com row count e checksum

- [ ] `quality-gate-evidence.md` — PASS explícito

- [ ] (Se trilha AST) `generated-code/` presente com os artefatos da plataforma alvo

**Decisão de gate:** registre em `gate3-decision.md` com score, aprovadores e data de go-live.

---

## Fase 4 — Pós-Migração: Retrospectiva e Melhoria

**Objetivo:** aprender com a wave executada, melhorar o processo para a próxima.

### Passo 4.1 — Execução do improvement cycle

```

[Selecione: iteration-improvement]
> *retrospective
Wave: WAVE-002
Pontos positivos, negativos e ações de melhoria

> *update-patterns
Registre novos padrões de erro e soluções encontradas

```

### Passo 4.2 — Atualizar KPIs do projeto

Calcule e registre no dashboard do projeto:

- Gate first-pass approval rate

- Lead time discovery → wave package executável

- Rollback rate desta wave

- Reconciliation mismatch rate

- MTTR (se houve falha)

### Passo 4.3 — Preparar próxima wave

- Revise `inventory-report.md` para identificar próximas entidades

- Crie novo `wave-config.yaml` para a próxima wave

- Volte ao **Passo 0.1** com o aprendizado desta wave

---

## Otimização de Tokens com Headroom (Opcional)

Para waves com muitos artefatos ou inventários grandes (>500KB), o **Headroom** reduz significativamente o custo de tokens LLM ao comprimir contexto antes de passar para os agentes.

### Quando usar

| Cenário | Benefício Estimado |
| --- | --- |
| `inventory-enriched.json` > 500KB | 40–60% menos tokens no Gate 1 |
| Relatórios de reconciliação com > 50 colunas | 30–50% menos tokens |
| Gate Score Reports detalhados | 25–40% menos tokens |
| KPI dashboards com muitas entidades | 30–45% menos tokens |

### Como funciona na operação

Os scripts de governança detectam automaticamente se o Headroom está instalado:

```python
# gate_score_report.py — uso automático
from scripts.gate_score_report import generate_gate_score_report_compressed

# Se Headroom instalado: retorna dict comprimido (30-60% menos tokens)
# Se não instalado: retorna relatório normal sem compressão
report = generate_gate_score_report_compressed(scores, wave_id="WAVE-002")
```

```python
# reconciliation_checks.py — compressão para grandes datasets
from scripts.reconciliation_checks import reconcile_checksums_compressed

# Discrepâncias com >50 colunas são auto-comprimidas
result = reconcile_checksums_compressed(
    entity="OrderHeaders",
    source_checksums=source_data,
    target_checksums=target_data,
)
```

### Monitorar savings em produção

```powershell
# Iniciar o proxy para medir savings reais
headroom proxy

# Consultar métricas acumuladas
headroom perf
```

### Integração com agentes via MCP

Com o MCP server configurado em `.vscode/settings.json`, todos os agentes ganham acesso a:

- `headroom_compress` — comprimir artefatos antes de passar ao contexto
- `headroom_retrieve` — recuperar artefato original quando necessário
- `headroom_perf` — consultar métricas de economia

Os tasks `scan-repo` (Step 2.1a) e `generate-inventory` (Step 4a) já utilizam essas ferramentas automaticamente.

---

## Referência Rápida de Scripts de Governança

Execute os scripts Python para validações automatizadas durante a operação:

```powershell
# Ativar venv (sempre primeiro)
.\.venv\Scripts\Activate.ps1

# Validar configuração da wave
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_wave_config projects\migration-northwind\wave-config.yaml

# Verificar artefatos obrigatórios — Gate 1
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate1_artifacts projects\migration-northwind\outputs\upstream

# Verificar artefatos obrigatórios — Gate 2
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate2_artifacts projects\migration-northwind\outputs\midstream

# Verificar artefatos obrigatórios — Gate 3
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate3_artifacts projects\migration-northwind\outputs\downstream

# Contratos de dados
python -c "from scripts.data_contract_validator import load_contract, evaluate_contract; from pathlib import Path; c=load_contract(Path('contracts/orders.yaml')); print(evaluate_contract(c, completeness=0.99))"

# Status consolidado da wave
python -c "from scripts.wave_status_tracker import WaveStatusTracker; t=WaveStatusTracker('WAVE-002'); print(t.summary())"

# Rodar TODOS os testes de governança
.\.venv\Scripts\python.exe -m pytest src/shared/tests/ -q
# Esperado: todos os testes aprovados
```

Para a lista completa de scripts, consulte [src/shared/scripts/README.md](../src/shared/scripts/README.md).

---

## Referência de Decisão de Gate

| Situação | Ação |
| --- | --- |

| GateScore >= 0.85 | Aprovado — avançar imediatamente |
| GateScore 0.70–0.84 | Aprovado com ressalvas — registrar open items obrigatórios, definir prazo para fechamento |
| GateScore < 0.70 | Bloqueado — corrigir artefatos faltantes, recalcular score, re-submeter |
| Artefato obrigatório ausente | Bloqueador automático — não pode avançar independente do score |

---

## Referência de Documentos Relacionados

| Documento | Quando usar |
| --- | --- |

| [PRD-Agentic-Data-Migration-Factory.md](PRD-Agentic-Data-Migration-Factory.md) | Entender os requisitos e critérios de aceite do projeto |
| [COPILOT-AGENTS-GUIDE.md](COPILOT-AGENTS-GUIDE.md) | Referência completa de comandos por agente |
| [OPERATING-MODEL-CANVAS-v2.md](OPERATING-MODEL-CANVAS-v2.md) | Papéis, permissões e modelo operacional |
| [SKILLS-BLUEPRINT-BY-GATE.md](SKILLS-BLUEPRINT-BY-GATE.md) | Quais skills usar em cada gate |
| [PLAYBOOK-ONBOARDING.md](PLAYBOOK-ONBOARDING.md) | Setup inicial do ambiente e do projeto |
