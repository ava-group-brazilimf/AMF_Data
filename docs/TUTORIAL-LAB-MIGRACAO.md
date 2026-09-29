# Tutorial Lab — Migração End-to-End com os Agentes

> **Tipo:** Tutorial — aprenda fazendo uma migração real do zero ao Gate 3
> **Público:** Estagiários e novos membros do time sem experiência prévia com o projeto
> **Tempo estimado:** 3–4 horas (incluindo leitura e interação com os agentes)
> **Pré-requisito:** [PLAYBOOK-ONBOARDING.md](PLAYBOOK-ONBOARDING.md) concluído (ambiente configurado, `203 passed, 2 skipped`)

---

## O que você vai aprender

Ao final deste tutorial você terá executado uma migração completa simulada:

1. Clonado um repositório ETL público como "sistema legado"
2. Usado **9 agentes** para conduzir o ciclo UPSTREAM → MIDSTREAM → DOWNSTREAM
3. Calculado e registrado os **3 GateScores** obrigatórios
4. Produzido os artefatos reais de cada gate

Não existe resposta errada aqui. O objetivo é sentir o fluxo, aprender os comandos e entender o que cada agente produz.

---

## Seção 1 — Escolha o Repositório Legado

O repositório que você vai clonar simula o **sistema de origem** da migração. Você vai tratá-lo como se fosse um legado real que precisa ser descoberto, mapeado e migrado.

| # | Repositório | Sistema Legado Simulado | Nível | Recomendado Para |
|---|---|---|---|---|
| **1** | [cloudera-labs/envelope](https://github.com/cloudera-labs/envelope) | Pipelines Spark sobre HDFS (ordens financeiras FIX, eventos, JSON) | Avançado | Quem já conhece Spark |
| **2** | [phucvn16409/build-etl-using-ssis](https://github.com/phucvn16409/build-etl-using-ssis) | **AdventureWorks 2019 — varejo de bicicletas (SSIS + SQL Server)** | **Iniciante** | **✅ Recomendado para este lab** |
| **3** | [Stefen-Taime/ETL-Data-Pipeline-RDBMS-TO-HDFS](https://github.com/Stefen-Taime/ETL-Data-Pipeline-RDBMS-TO-HDFS-using-Airflow-Apache-Sqoop-Spark-Postgres-and-Hive) | PostgreSQL → HDFS (Airflow + Sqoop + Spark + Hive) | Intermediário | Quem quer cenário big data |
| **4** | [pregismond/etl-data-pipelines-with-shell-airflow-kafka](https://github.com/pregismond/etl-data-pipelines-with-shell-airflow-kafka) | Pedágios multi-formato (CSV + TSV + fixed-width) + streaming Kafka | Intermediário | Quem quer explorar formatos distintos |
| **5** | [fermat01/Building-streaming-ETL-Data-pipeline](https://github.com/fermat01/Building-streaming-ETL-Data-pipeline) | Streaming em tempo real — Kafka + Spark + Minio/S3 | Avançado | Quem quer cenário streaming |
| **6** | [yennanliu/spark-etl-pipeline](https://github.com/yennanliu/spark-etl-pipeline) | ETL batch/streaming Spark Scala — pageviews, S3, Hive | Avançado | Quem tem experiência com Scala |
| **7** | [ddgope/Data-Pipelines-with-Airflow](https://github.com/ddgope/Data-Pipelines-with-Airflow) | Sparkify — plataforma de música (S3 → Redshift) | Intermediário | Quem quer cenário cloud AWS |
| **8** | [qwshen/spark-etl-framework](https://github.com/qwshen/spark-etl-framework) | ETL genérico Spark YAML/JSON — multi-jobs e UDFs | Avançado | Quem quer framework extensível |
| **9** | [SETL-Framework/setl](https://github.com/SETL-Framework/setl) | Framework Scala Spark — Factories e SparkRepositories | Avançado | Quem trabalha com Scala |
| **10** | [mboccenti/ETL-and-Data-Pipelines-with-Shell-Airflow-and-Kafka](https://github.com/mboccenti/ETL-and-Data-Pipelines-with-Shell-Airflow-and-Kafka) | Shell + Airflow DAGs + Kafka streaming — batch e real-time | Intermediário | Quem quer cobrir ambas modalidades |

### Por que o repositório #2 (AdventureWorks/SSIS)?

Este tutorial usa o repositório **#2** como exemplo principal porque:
- Usa SQL Server — a fonte mais comum em projetos de migração enterprise
- Entidades conhecidas: `Customer`, `Product`, `SalesOrder`, `SalesOrderDetail`
- Inclui staging area, DW e pacotes SSIS — cenário realista de "meu legado é SSIS"
- Zero infraestrutura de cloud necessária para acompanhar o lab

> **Usando outro repositório?** Os prompts funcionam para qualquer um — basta trocar os nomes de entidades e tipo de fonte. A [Seção 8](#seção-8--adaptando-os-prompts-para-outros-repositórios) mostra como adaptar.

---

## Seção 2 — Setup Inicial

### Passo 2.1 — Clone os dois repositórios

Abra um terminal PowerShell e execute:

```powershell
# Clone ou abra o projeto Data Migration Factory (se já não estiver aberto)
cd "Data-Migration v3"

# Clone o legado dentro da raiz canônica da wave
git clone https://github.com/phucvn16409/build-etl-using-ssis projects/wave-lab-adventureworks/legacy
```

### Passo 2.2 — Ative o ambiente Python

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest src/shared/tests/ -q    # deve mostrar: 283 passed, 2 skipped (confirma ambiente OK)
```

### Passo 2.2a — (Opcional) Ative o Headroom para economia de tokens

O Headroom comprime o contexto enviado aos agentes, economizando 30–60% de tokens LLM. É especialmente útil em inventários grandes (>500KB).

```powershell
# Instalar (com a venv ativa)
pip install "headroom-ai[mcp,code]>=0.27.0"

# Verificar
headroom --version    # deve retornar 0.27.0+
```

Com o Headroom instalado:
- O task `*scan-repo` comprime automaticamente arquivos >500KB (Step 2.1a)
- O task `*generate-inventory` comprime o `inventory-enriched.json` (Step 4a)
- Os scripts `gate_score_report.py`, `kpi_dashboard_report.py` e `reconciliation_checks.py` oferecem funções `_compressed()` que reduzem o payload passado aos agentes

> **Sem o Headroom?** Tudo funciona normalmente — os agentes recebem o conteúdo completo sem compressão. A economia de tokens é um bônus, não um requisito.

### Passo 2.3 — Crie a estrutura da wave em projects/

A partir da raiz do projeto (não mude de diretório — todos os comandos seguintes usam caminhos relativos à raiz):

```powershell
# Cria a hierarquia padrão de projeto dentro de projects/
python -c "
import os
dirs = [
    'projects/wave-lab-adventureworks/context',
    'projects/wave-lab-adventureworks/outputs/upstream',
    'projects/wave-lab-adventureworks/outputs/midstream',
    'projects/wave-lab-adventureworks/outputs/downstream/ddl',
    'projects/wave-lab-adventureworks/outputs/downstream/etl',
    'projects/wave-lab-adventureworks/outputs/downstream/tests',
    'projects/wave-lab-adventureworks/outputs/summary'
]
[os.makedirs(d, exist_ok=True) for d in dirs]
print('Wave structure created')
"
```

> **Regra:** não use `project/` na raiz nem pastas locais dos agentes. Contexto e
> outputs desta execução pertencem exclusivamente a `projects/wave-lab-adventureworks/`.

### Passo 2.4 — Crie o wave-config.yaml e os arquivos de contexto

Crie o arquivo `projects/wave-lab-adventureworks/wave-config.yaml` com o conteúdo abaixo:

```yaml
wave_id: WAVE-LAB-001
wave_name: "AdventureWorks Sales Migration — Lab Tutorial"
project_name: "wave-lab-adventureworks"
context_base_path: "projects/{project_name}/context"
outputs_base_path: "projects/{project_name}/outputs"
environment: DEV
dry_run: true

discovery_owner_primary: "discovery-scout"
discovery_owner_fallback: "inventory-scout"

source:
  type: sqlserver
  legacy_path: "projects/wave-lab-adventureworks/legacy"
  database: AdventureWorks2019
  schema: Sales

entities:
  - name: "Customer"
    tier: STANDARD
    source_system: "SQL Server / AdventureWorks SSIS"
    target_layer: "gold"
    estimated_rows: 19820

  - name: "SalesOrder"
    tier: CRITICAL
    source_system: "SQL Server / AdventureWorks SSIS"
    target_layer: "gold"
    estimated_rows: 31465

  - name: "SalesOrderDetail"
    tier: CRITICAL
    source_system: "SQL Server / AdventureWorks SSIS"
    target_layer: "gold"
    estimated_rows: 121317

  - name: "Product"
    tier: STANDARD
    source_system: "SQL Server / AdventureWorks SSIS"
    target_layer: "gold"
    estimated_rows: 504

target_platform: "(destino a definir — ex: Databricks, Fabric, Snowflake)"

gate_thresholds:
  gate_1: 80.0
  gate_2: 85.0
  gate_3: 85.0

approvers:
  gate_1: "data-strategist"
  gate_2: "data-architect"
  gate_3: "migration-coordinator"
```

Crie `projects/wave-lab-adventureworks/context/project-config.yaml`:

```yaml
project_name: "wave-lab-adventureworks"
source_platform: "sqlserver"
target_platform: "(destino a definir)"
legacy_technology: "ssis"
trace_id: ""
scope_modules: "all"
outputs_base_path: "projects/{project_name}/outputs"
context_base_path: "projects/{project_name}/context"
```

Em seguida, crie `projects/wave-lab-adventureworks/context/agent-task-config.yaml` para rastreabilidade da execução:

```yaml
trace_id: ""                  # Deixe em branco — o migration-coordinator preenche ao iniciar a wave
project_name: "wave-lab-adventureworks"
scope_modules:
  - upstream-discovery
  - midstream-design
  - midstream-quality
  - downstream-execution
  - core-coordination
agent_sequence:
  - discovery-scout
  - data-strategist
  - business-analyst
  - logic-extractor
  - data-architect
  - data-modeler
  - data-steward
  - code-generator
  - quality-gate
  - security-compliance
  - downstream-executor
  - reconciliation
  - self-healing
  - documentation
  - migration-coordinator
max_retries: 2
timeout_minutes: 120
human_gates: [gate_1, gate_2, gate_3]
```

> **Checklist de pré-kickoff:** antes de continuar, revise `src/shared/checklists/pre-kickoff.md` para garantir que todos os itens de setup estão completos.

### Passo 2.5 — Valide o wave-config

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_wave_config `
  projects\wave-lab-adventureworks\wave-config.yaml
```

Resultado esperado: `Wave config validation: PASS`.

### Passo 2.6 — Inicie a wave com o contexto resolvido

```text
[Selecione: migration-coordinator]
> *start-wave
wave_config_path: projects/wave-lab-adventureworks/wave-config.yaml
```

Antes de delegar ao `discovery-scout`, o coordenador deve carregar os dois YAMLs
de `context/` e fixar o output em `projects/wave-lab-adventureworks/outputs/`.

---

## Seção 3 — Fase UPSTREAM: Discovery

**Objetivo desta fase:** mapear o sistema legado (o repositório que você clonou), entender o que existe e produzir os artefatos obrigatórios do Gate 1.

**Agentes desta fase:** `discovery-scout` → `data-strategist` → `business-analyst`

---

### Passo 3.1 — Abra o VS Code com os dois projetos

```powershell
# Em um terminal, abra o VS Code na raiz do Data Migration Factory
code "c:\path\to\Data-Migration v3"
```

Abra também a pasta `legacy-etl-lab` como segundo workspace para consulta do código legado.

---

### Passo 3.2 — Ative o discovery-scout

**No Copilot Chat, selecione: `discovery-scout`**

Cole o prompt abaixo e pressione Enter:

```
*scan-repo
Estou analisando um sistema legado de ETL baseado em SSIS e SQL Server.
Repositório de referência: https://github.com/phucvn16409/build-etl-using-ssis
Dataset: AdventureWorks 2019 (varejo de bicicletas)
Schemas relevantes: Sales, Production

Entidades em escopo:
- Sales.Customer (dados de clientes)
- Sales.SalesOrderHeader (cabeçalho de pedidos)
- Sales.SalesOrderDetail (itens de pedido)
- Production.Product (catálogo de produtos)

A pipeline legada usa pacotes SSIS com staging area e carga para DW.
Preciso de um inventário completo dos objetos ETL.
```

**O que esperar:** o agente vai gerar um `inventory-report.md` com a lista de objetos, tecnologia identificada e primeiras observações sobre complexidade.

---

### Passo 3.3 — Classifique a complexidade

Ainda no `discovery-scout`, cole:

```
*classify
Com base no inventário gerado, classifique cada entidade por complexidade de migração:
- Customer: leitura simples, sem transformações complexas
- SalesOrderHeader: tem cálculos de subtotal, tax, freight
- SalesOrderDetail: tem cálculo de LineTotal = UnitPrice * OrderQty * (1 - UnitPriceDiscount)
- Product: tabela de referência, baixa volatilidade

Use o critério Low / Medium / High.
```

---

### Passo 3.4 — Mapeie as dependências

```
*map-dependencies
Mapeie o DAG de dependências entre as entidades do escopo:
- SalesOrderDetail depende de SalesOrderHeader (FK: SalesOrderID)
- SalesOrderHeader depende de Customer (FK: CustomerID)
- SalesOrderDetail depende de Product (FK: ProductID)

Gere o diagrama de dependências em formato Mermaid.
```

**Artefato esperado ao final do Passo 3.4:**
- `inventory-report.md` com objetos catalogados
- Diagrama de dependências (DAG)
- Classificação Low/Medium/High por entidade

---

### Passo 3.5 — Defina o problem statement

**No Copilot Chat, selecione: `data-strategist`**

```
*define-problem
Projeto: WAVE-LAB-001 — Migração AdventureWorks Sales para plataforma moderna
Contexto: pipeline SSIS legada em SQL Server com manutenção cara e sem suporte a analytics em tempo real
Motorista de negócio: modernizar a plataforma de dados de vendas para reduzir TCO e habilitar analytics avançado
Escopo: 4 entidades (Customer, SalesOrder, SalesOrderDetail, Product), ambiente DEV
Stakeholders: time de dados, time de vendas, TI
Salve o resultado como problem-statement.md em outputs/upstream/strategy/ (nome exato - o validador do Gate 1 verifica).
```

---

### Passo 3.6 — Defina os KPIs da wave

```
*create-kpis
Baseado no problem statement recém criado para WAVE-LAB-001.
Inclua KPIs relacionados a:
- Completude da migração (zero perda de registros)
- Integridade dos dados (checksums)
- Performance (tempo de carga)
- Qualidade (regras DQ atendidas)
- Rollback readiness
Salve o resultado como kpis.md em outputs/upstream/strategy/.
```

---

### Passo 3.7 — Crie o STTM

**No Copilot Chat, selecione: `business-analyst`**

```
Criar STTM (Source-to-Target Mapping) para as entidades da WAVE-LAB-001:

ENTIDADE 1: Customer
- Fonte: Sales.Customer (SQL Server AdventureWorks)
- Destino: gold.dim_customer
- Campos principais: CustomerID, PersonID, StoreID, TerritoryID, AccountNumber, ModifiedDate
- Transformações: AccountNumber pode precisar de normalização

ENTIDADE 2: SalesOrderHeader
- Fonte: Sales.SalesOrderHeader
- Destino: gold.fact_sales_order
- Campos principais: SalesOrderID, CustomerID, OrderDate, DueDate, ShipDate, SubTotal, TaxAmt, Freight, TotalDue, Status
- Transformações: TotalDue = SubTotal + TaxAmt + Freight (precisa validação)

ENTIDADE 3: SalesOrderDetail
- Fonte: Sales.SalesOrderDetail
- Destino: gold.fact_sales_order_detail
- Campos principais: SalesOrderDetailID, SalesOrderID, ProductID, OrderQty, UnitPrice, UnitPriceDiscount, LineTotal
- Transformações: LineTotal = UnitPrice * OrderQty * (1 - UnitPriceDiscount) — deve ser re-calculado no destino

ENTIDADE 4: Product
- Fonte: Production.Product
- Destino: gold.dim_product
- Campos principais: ProductID, Name, ProductNumber, MakeFlag, FinishedGoodsFlag, Color, StandardCost, ListPrice, ProductLine, Class
- Transformações: nenhuma transformação crítica
```

---

### Passo 3.7a — Defina as perguntas analíticas

Ainda no `business-analyst`:

```
*analytical-questions
Defina as perguntas analíticas que a WAVE-LAB-001 deve responder após a migração:
- Quais clientes geram maior receita por território?
- Qual a evolução mensal de vendas por linha de produto?
- Qual o ticket médio por pedido e por canal?
- Quais produtos têm maior margem (ListPrice - StandardCost)?

Salve o resultado como analytical-questions.md em outputs/upstream/analysis/.
```

> Este artefato é OBRIGATÓRIO no Gate 1 - o validador oficial reprova sem ele.

---

### Passo 3.8 — Defina as regras de DQ

Ainda no `business-analyst`:

```
Definir regras de DQ para as entidades da WAVE-LAB-001:

Customer:
- CustomerID: NOT NULL, único, inteiro positivo
- AccountNumber: NOT NULL, formato AW + 8 dígitos

SalesOrderHeader:
- SalesOrderID: NOT NULL, único
- CustomerID: NOT NULL, deve existir em Customer
- OrderDate: NOT NULL, deve ser anterior a DueDate
- TotalDue: deve ser igual a SubTotal + TaxAmt + Freight (tolerância de ±0.01)
- Status: valores válidos: 1=In process, 2=Approved, 3=Backordered, 4=Rejected, 5=Shipped, 6=Cancelled

SalesOrderDetail:
- SalesOrderDetailID: NOT NULL, único
- SalesOrderID: NOT NULL, deve existir em SalesOrderHeader
- ProductID: NOT NULL, deve existir em Product
- OrderQty: deve ser > 0
- UnitPrice: deve ser >= 0
- LineTotal: deve ser calculado corretamente (UnitPrice * OrderQty * (1 - UnitPriceDiscount))

Salve o resultado como dq-initial.md em outputs/upstream/analysis/ (não use o nome do artefato governado de Gate 2 - o validador do Gate 1 procura dq-initial.md).
```

**Artefatos esperados ao final da Fase UPSTREAM (nomes e pastas EXATOS - o validador oficial verifica ambos):**
- `outputs/upstream/strategy/problem-statement.md`
- `outputs/upstream/strategy/kpis.md`
- `outputs/upstream/analysis/analytical-questions.md`
- `outputs/upstream/sttm/sttm.md`
- `outputs/upstream/analysis/dq-initial.md`

---

## Seção 4 — Gate 1: Validação

### Passo 4.1 — Rode o validador oficial de artefatos

Antes de pedir o GateScore ao agente, valide a estrutura com o script oficial -
é ele que decide se os artefatos existem:

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate1_artifacts projects\wave-lab-adventureworks\outputs\upstream
```

**Resultado esperado:** `Gate 1 validation: PASS` com os 5 artefatos ✓.
Se algum aparecer como MISSING, volte ao passo que o gera (a mensagem mostra o
path esperado) - não avance com artefato faltando.

### Passo 4.1b — Peça o GateScore ao agente

**No Copilot Chat, selecione: `migration-coordinator`**

```
*gate1-validate
Wave: WAVE-LAB-001
O validador oficial retornou PASS para os 5 artefatos do Gate 1
(strategy/problem-statement.md, strategy/kpis.md,
analysis/analytical-questions.md, sttm/sttm.md, analysis/dq-initial.md).

Avalie o conteúdo dos artefatos e calcule o GateScore nas 4 dimensões
(Completude, Qualidade, Risco residual, Reconciliação - para Reconciliação,
avalie o PLANO de reconciliação, pois dry_run=true não executa carga).
Indique se estamos APPROVED para avançar ao MIDSTREAM.
```

### Passo 4.2 — Calcule o GateScore via script

```powershell
python -m scripts.gate_score_report `
  --completude 0.90 `
  --qualidade 0.85 `
  --risco 0.80 `
  --reconciliacao 0.75
```

> **Nota:** use os valores que o agente sugerir no passo anterior. O threshold é SEMPRE o `gate_thresholds.gate_1` do seu `wave-config.yaml` (0.80 neste lab) - se encontrar outro valor citado em qualquer workflow, o `wave-config.yaml` prevalece.

### Passo 4.3 — Registre a decisão do Gate 1

Crie o arquivo `projects/wave-lab-adventureworks/outputs/summary/gate1-decision.md`:

```markdown
# Gate 1 Decision — WAVE-LAB-001

**Data:** [preencha com a data atual]
**GateScore:** [preencha com o score calculado]
**Decisão:** APPROVED / APPROVED WITH CAVEATS / BLOCKED

## Aprovadores
- Gate 1: data-strategist (nome: [seu nome])

## Open Items (se CAVEATS)
- [ ] [liste os open items se houver]

## Artefatos Validados
- [x] inventory-report.md
- [x] outputs/upstream/strategy/problem-statement.md
- [x] outputs/upstream/strategy/kpis.md
- [x] outputs/upstream/analysis/analytical-questions.md
- [x] outputs/upstream/sttm/sttm.md
- [x] outputs/upstream/analysis/dq-initial.md
```

**✅ Gate 1 concluído — você pode avançar para o MIDSTREAM.**

---

## Seção 5 — Fase MIDSTREAM: Design

**Objetivo desta fase:** projetar a arquitetura, o modelo de dados e gerar o código DDL/ETL que vai executar a migração.

**Agentes desta fase:** `data-architect` → `data-modeler` → `data-steward` → `code-generator` → `quality-gate` → `security-compliance`

---

### Passo 5.1 — Projete a arquitetura

**No Copilot Chat, selecione: `data-architect`**

```
*design-architecture
Wave: WAVE-LAB-001
Fonte: SQL Server AdventureWorks 2019 (Sales schema)
Destino: (informe a plataforma que você está usando — ex: Databricks Delta Lake, Apache Parquet local, ou diga "genérico")

Entidades em escopo:
- Customer (STANDARD) → dim_customer
- SalesOrderHeader (CRITICAL) → fact_sales_order
- SalesOrderDetail (CRITICAL) → fact_sales_order_detail
- Product (STANDARD) → dim_product

Estratégia de carga sugerida: full load para dimensões, incremental por OrderDate para fatos
Zonas: Bronze (raw), Silver (cleansed + validated), Gold (dimensional model)
Inclua decisões sobre particionamento e estratégia de reprocessamento.
```

---

### Passo 5.2 — Registre as decisões de arquitetura

```
*adr
Registre uma Architecture Decision Record para:
Decisão: usar full load para Customer e Product (tabelas pequenas, baixa volatilidade)
Decisão: usar incremental por OrderDate para SalesOrderHeader e SalesOrderDetail
Motivo: os fatos têm >100k linhas e crescem diariamente — full load seria custoso em produção
Consequência: precisamos de watermark control na camada Gold
```

---

### Passo 5.3 — Defina o modelo lógico

**No Copilot Chat, selecione: `data-modeler`**

```
*create-model
Crie o modelo lógico dimensional para a WAVE-LAB-001:

Tabelas de dimensão:
- dim_customer: customer_sk (surrogate key), customer_id (natural key), account_number, territory_id, store_id, modified_date
- dim_product: product_sk, product_id, name, product_number, color, standard_cost, list_price, product_line, class, make_flag

Tabelas de fato:
- fact_sales_order: order_sk, sales_order_id, customer_sk (FK), order_date, due_date, ship_date, status, sub_total, tax_amt, freight, total_due
- fact_sales_order_detail: detail_sk, sales_order_id, sales_order_detail_id, product_sk (FK), order_qty, unit_price, unit_price_discount, line_total

Granularidade:
- fact_sales_order: 1 linha por pedido (SalesOrderID)
- fact_sales_order_detail: 1 linha por item do pedido (SalesOrderDetailID)

Gere o diagrama ER em Mermaid.
```

---

### Passo 5.4 — Crie os contratos de dados

```
*data-contracts
Gere contratos de dados YAML para as 4 entidades da WAVE-LAB-001.
Inclua para cada entidade:
- campos com tipos, nullable e PII flag
- regras de qualidade (completeness, uniqueness, row_parity)
- owner: data-steward
- tier conforme wave-config (CRITICAL para fatos, STANDARD para dimensões)
```

---

### Passo 5.5 — Governança e catálogo

**No Copilot Chat, selecione: `data-steward`**

```
*catalog
Registre as seguintes entidades no catálogo de dados da WAVE-LAB-001:
- dim_customer: dados de clientes AdventureWorks, fonte Sales.Customer
- fact_sales_order: pedidos de venda, fonte Sales.SalesOrderHeader
- fact_sales_order_detail: itens de pedido, fonte Sales.SalesOrderDetail
- dim_product: catálogo de produtos, fonte Production.Product

Para cada entidade: descrição, owner (time de dados), classificação (PII: sim/não), frequência de atualização.
```

```
*detect-pii
Analise as entidades da WAVE-LAB-001 para campos com PII:
- dim_customer: verificar se PersonID ou campos derivados contêm dados pessoais
- fact_sales_order: verificar ShipToAddressID, BillToAddressID
- dim_product: sem PII esperado
- fact_sales_order_detail: sem PII esperado

Indique quais campos precisam de masking em DEV/HML.
```

> **Atenção:** se o agente detectar PII, mude para `security-compliance` no próximo passo.

---

### Passo 5.6 — Compliance e masking (se houver PII)

**No Copilot Chat, selecione: `security-compliance`**

```
*masking-rules
Entidades com PII detectado na WAVE-LAB-001:
- dim_customer: PersonID pode ser associado a dados pessoais de pessoa física

Defina a estratégia de masking por ambiente:
- DEV: hash SHA-256 para PersonID
- HML: hash SHA-256 para PersonID  
- PROD: dado real (produção tem controle de acesso)
```

---

### Passo 5.7 — Gere o código DDL

**No Copilot Chat, selecione: `code-generator`**

```
*generate-ddl
Gere os scripts DDL para as 4 entidades da WAVE-LAB-001 baseado no data-model.md:

Plataforma: (informe sua plataforma — ex: "SQL genérico ANSI", "Databricks SQL", "PostgreSQL")

DDL necessário:
1. CREATE TABLE gold.dim_customer com surrogate key, natural key e campos conforme modelo
2. CREATE TABLE gold.dim_product com surrogate key e campos conforme modelo
3. CREATE TABLE gold.fact_sales_order com surrogate key, FKs para dimensões e métricas
4. CREATE TABLE gold.fact_sales_order_detail com surrogate key, FKs e métricas

Inclua:
- PRIMARY KEY e FOREIGN KEY constraints
- Comentários por coluna
- NOT NULL constraints conforme regras de DQ
```

---

### Passo 5.8 — Gere o código ETL

```
*generate-etl
Gere os scripts ETL para a WAVE-LAB-001 com as seguintes camadas:

BRONZE (extração raw):
- Extrair Customer, SalesOrderHeader, SalesOrderDetail, Product do SQL Server (ou CSV do repo legado)
- Salvar como raw sem transformação

SILVER (limpeza e validação):
- Aplicar regras de DQ: NOT NULL, ranges válidos, referential integrity
- Calcular LineTotal = UnitPrice * OrderQty * (1 - UnitPriceDiscount) e comparar com valor fonte
- Validar TotalDue = SubTotal + TaxAmt + Freight (tolerância ±0.01)
- Rejeitar registros inválidos para quarentena

GOLD (dimensional model):
- Popular dim_customer com surrogate key gerada
- Popular dim_product com surrogate key gerada
- Popular fact_sales_order com lookup de customer_sk
- Popular fact_sales_order_detail com lookup de product_sk e order_sk

Plataforma: (informe a mesma do DDL)
```

---

### Passo 5.9 — Valide o código gerado

**No Copilot Chat, selecione: `quality-gate`**

```
*validate-code
Valide os scripts DDL e ETL gerados para WAVE-LAB-001:

Critérios a verificar:
1. DDL: todas as PKs definidas? FKs corretas? NOT NULL onde esperado?
2. ETL Bronze: extração completa de todos os campos do STTM?
3. ETL Silver: todas as regras de DQ aplicadas?
4. ETL Gold: surrogate keys geradas corretamente? Lookups de FK implementados?
5. Cobertura de testes: existe teste para o cálculo de LineTotal?

Indique violações com severidade (CRITICAL / WARNING / INFO).
```

```
*score
Calcule o score de qualidade do código para WAVE-LAB-001.
Dimensões: completude do STTM coberto, regras DQ implementadas, estrutura DDL correta.
```

**Artefatos esperados ao final da Fase MIDSTREAM:**
- `architecture.md`
- `decisions.md` (ADRs)
- `data-model.md` (com diagrama ER)
- `data-contracts.md`
- Regras de DQ governadas pelo data-steward
- `security-compliance-report.md`
- `ddl/` (scripts DDL)
- `etl/` (scripts ETL bronze/silver/gold)
- `quality-gate-evidence.md`

---

## Seção 6 — Gate 2: Validação

**No Copilot Chat, selecione: `migration-coordinator`**

### Passo 6.1 — Valide os artefatos do Gate 2

```
*gate2-validate
Wave: WAVE-LAB-001

Artefatos produzidos:
- architecture.md ✓
- decisions.md ✓
- data-model.md ✓
- data-contracts.md ✓
- monitoring-spec.md (se gerado)
- security-compliance-report.md ✓
- ddl/ ✓ (4 scripts)
- etl/ ✓ (bronze + silver + gold)
- quality-gate-evidence.md ✓

Calcule o GateScore e indique se estamos APPROVED para avançar ao DOWNSTREAM.
```

### Passo 6.2 — Calcule via script

```powershell
python -m scripts.gate_score_report `
  --completude 0.92 `
  --qualidade 0.88 `
  --risco 0.82 `
  --reconciliacao 0.80
```

### Passo 6.3 — Registre a decisão do Gate 2

Crie `projects/wave-lab-adventureworks/outputs/summary/gate2-decision.md` com a mesma estrutura do Gate 1.

**✅ Gate 2 concluído — você pode avançar para o DOWNSTREAM.**

---

## Seção 7 — Fase DOWNSTREAM: Execução

**Objetivo desta fase:** executar os scripts gerados, reconciliar os dados e documentar a entrega.

**Agentes desta fase:** `downstream-executor` → `reconciliation` → `self-healing` (se erros) → `documentation`

---

### Passo 7.1 — Crie o runbook de execução

**No Copilot Chat, selecione: `downstream-executor`**

```
*create-runbook
Crie o execution-runbook para WAVE-LAB-001:

Ambiente: DEV (dry_run: true)
Ordem de execução:
1. DDL: criar tabelas gold.dim_customer, gold.dim_product, gold.fact_sales_order, gold.fact_sales_order_detail
2. ETL Bronze: extrair dados do SQL Server / repositório legado
3. ETL Silver: aplicar DQ e transformações
4. ETL Gold: popular modelo dimensional

Rollback plan:
- DROP TABLE se DDL falhar
- Truncar tabelas e re-executar se ETL falhar em Silver ou Gold
- Condição de aborto: se row count divergir > 1% do esperado

Aprovação necessária antes de executar em PROD.
```

---

### Passo 7.2 — Execute em modo dry-run

```
*dry-run
Execute o dry-run da WAVE-LAB-001:

Simule a execução nesta sequência e aponte riscos:
1. Criação das tabelas DDL no schema gold
2. Carga Bronze: Customer (19.820 linhas esperadas), Product (504), SalesOrderHeader (31.465), SalesOrderDetail (121.317)
3. Carga Silver: aplicação das regras DQ
4. Carga Gold: dimensional model completo

Identifique:
- Dependências de dados que podem quebrar a ordem de execução
- Campos com risco de truncamento (varchar muito curto)
- Riscos de performance (tabelas sem índice definido)
```

---

### Passo 7.3 — Reconcilie os dados

**No Copilot Chat, selecione: `reconciliation`**

```
*row-count
Valide a paridade de row count para WAVE-LAB-001:

Contagens esperadas (fonte AdventureWorks):
- Customer: 19.820 registros fonte → deve ter 19.820 no dim_customer
- Product: 504 registros fonte → deve ter 504 no dim_product
- SalesOrderHeader: 31.465 registros fonte → deve ter 31.465 no fact_sales_order
- SalesOrderDetail: 121.317 registros fonte → deve ter 121.317 no fact_sales_order_detail

Tolerância: 0% para dimensões (full load), 0% para fatos (dry-run)
```

```
*checksum
Valide a integridade dos campos financeiros críticos para WAVE-LAB-001:

fact_sales_order:
- SUM(TotalDue) fonte deve ser igual ao SUM(total_due) destino
- SUM(SubTotal) fonte deve ser igual ao SUM(sub_total) destino

fact_sales_order_detail:
- SUM(LineTotal) fonte deve ser igual ao SUM(line_total) destino
- SUM(OrderQty) fonte deve ser igual ao SUM(order_qty) destino

Gere evidência de reconciliação por entidade (PASS / FAIL com delta se FAIL).
```

```
*schema-diff
Compare o schema fonte vs destino para as 4 entidades:

Para cada entidade, verifique:
- Todos os campos do STTM foram criados no destino?
- Tipos de dados são compatíveis?
- Constraints NOT NULL estão aplicadas?
- Há campos novos no destino não previstos no STTM?
```

---

### Passo 7.4 — Se houver erros: auto-diagnóstico

**No Copilot Chat, selecione: `self-healing`**

```
*diagnose
Erro encontrado durante a reconciliação da WAVE-LAB-001:
[cole aqui o erro ou divergência encontrada]

Por exemplo:
"SUM(LineTotal) no destino difere do fonte em R$ 0.03 — 3 registros com UnitPriceDiscount = NULL convertido para 0"

Execute root cause analysis e sugira a correção.
```

```
*reflect
Avalie a correção aplicada para o erro de LineTotal na WAVE-LAB-001.
Dimensões: Correctness, Safety, Idiomatic, Learnability.
```

---

### Passo 7.5 — Documente a entrega

**No Copilot Chat, selecione: `documentation`**

```
*wave-report
Gere o wave-report completo para WAVE-LAB-001:

Informações da wave:
- Entidades migradas: Customer (19.820), Product (504), SalesOrder (31.465), SalesOrderDetail (121.317)
- Ambiente: DEV, dry_run: true
- Gate 1 score: [seu score]
- Gate 2 score: [seu score]
- Reconciliação: [PASS/FAIL com detalhes]
- Problemas encontrados: [liste se houver]
- Lições aprendidas: [o que você aprendeu neste lab]

Inclua seções: resumo executivo, artefatos produzidos, evidências de reconciliação, open items.
```

```
*data-lineage
Documente a lineagem de dados da WAVE-LAB-001:
- Sales.Customer → bronze.customer_raw → silver.customer_clean → gold.dim_customer
- Sales.SalesOrderHeader → bronze.sales_order_raw → silver.sales_order_clean → gold.fact_sales_order
- Sales.SalesOrderDetail → bronze.sales_order_detail_raw → silver.sales_order_detail_clean → gold.fact_sales_order_detail
- Production.Product → bronze.product_raw → silver.product_clean → gold.dim_product
```

**Artefatos esperados ao final da Fase DOWNSTREAM:**
- `execution-runbook.md`
- `reconciliation-evidence.md`
- `wave-report.md`
- `data-lineage.md`

---

## Seção 8 — Gate 3: Validação Final

**No Copilot Chat, selecione: `migration-coordinator`**

### Passo 8.1 — Valide os artefatos do Gate 3

```
*gate3-validate
Wave: WAVE-LAB-001

Pacote Gate 3 produzido:
- ddl/ ✓ (4 scripts executados)
- etl/ ✓ (bronze + silver + gold)
- tests/ (preencha se gerou testes)
- documentation/ ✓ (wave-report, runbook, lineage)
- wave-report.md ✓
- reconciliation-evidence.md ✓
- execution-runbook.md ✓

Calcule o GateScore final e indique se a wave está APPROVED para promoção.
```

### Passo 8.2 — Valide via script

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.validate_gate3_artifacts `
  projects\wave-lab-adventureworks\outputs\downstream
```

### Passo 8.3 — Calcule o GateScore final

```powershell
.\.venv\Scripts\python.exe -m src.shared.scripts.gate_score_report `
  --completude 0.95 `
  --qualidade 0.90 `
  --risco 0.85 `
  --reconciliacao 0.90
```

### Passo 8.4 — Registre a decisão final

Crie `projects/wave-lab-adventureworks/outputs/summary/gate3-decision.md`.

**🎉 Gate 3 concluído — WAVE-LAB-001 entregue!**

---

## Seção 9 — Retrospectiva (Opcional, mas Recomendada)

**No Copilot Chat, selecione: `iteration-improvement`**

```
*retrospective
Conduza a retrospectiva da WAVE-LAB-001:

O que funcionou bem:
- [anote o que você aprendeu que funcionou]

O que pode melhorar:
- [anote onde travou ou ficou confuso]

Dúvidas que surgiram:
- [liste suas dúvidas]

Sugestões para o próximo lab:
- [o que você faria diferente na próxima wave]
```

```
*kpi-review
Revise os KPIs definidos no Gate 1 para WAVE-LAB-001:
- Completude: atingiu 100% das entidades migradas?
- Integridade: checksums PASS em todas as entidades?
- Performance: o dry-run completou dentro do tempo esperado?
- Qualidade: regras DQ atendidas?
```

---

## Seção 9.1 — (Opcional) Verificar Economia de Tokens com Headroom

Se você instalou o Headroom no Passo 2.2a, pode verificar a economia real de tokens que ocorreu durante o lab.

### Passo 9.1.1 — Verifique as métricas de compressão

```powershell
headroom perf
```

Se ainda não há dados (proxy não estava rodando), você pode testar manualmente:

```powershell
# Comprimir um artefato do lab para ver a redução
headroom compress projects/wave-lab-adventureworks/outputs/upstream/inventory-report.md
```

### Passo 9.1.2 — Teste a compressão programática

```python
# Teste as funções _compressed() dos scripts de governança
from scripts.gate_score_report import generate_gate_score_report_compressed

scores = {
    "completude": 0.95,
    "qualidade": 0.90,
    "risco_residual": 0.85,
    "reconciliacao": 0.90
}
result = generate_gate_score_report_compressed(scores, wave_id="WAVE-LAB-001")

# Se Headroom está instalado, result terá {"_headroom_compressed": True, "content": ...}
# Se não está instalado, retorna o relatório normal
print(type(result), "— compressed" if isinstance(result, dict) and result.get("_headroom_compressed") else "— full")
```

### Passo 9.1.3 — Entenda onde a economia acontece

| Ponto de Integração | O que é comprimido | Savings Típico |
|---|---|---|
| `*scan-repo` Step 2.1a | Arquivos fonte >500KB | 40–60% |
| `*generate-inventory` Step 4a | `inventory-enriched.json` | 40–60% |
| `gate_score_report.py` | Relatórios de gate passados entre agentes | 25–40% |
| `reconciliation_checks.py` | Datasets com >50 colunas de discrepância | 30–50% |
| `kpi_dashboard_report.py` | Dashboards KPI com muitas entidades | 30–45% |

> **Dica:** Para waves com muitas entidades (>10), o Headroom pode economizar milhares de tokens por interação de agente. Em produção, rode `headroom proxy` durante toda a wave para medir savings reais.

---

## Seção 10 — Adaptando os Prompts para Outros Repositórios

Se você escolheu um repositório diferente, substitua os valores abaixo nos prompts:

| Campo | AdventureWorks (#2) | Sparkify Airflow (#7) | RDBMS→HDFS (#3) | Toll Roads (#4) |
|---|---|---|---|---|
| **Fonte** | SQL Server / SSIS | S3 + JSON logs | PostgreSQL | CSV + TSV + fixed-width |
| **Entidades** | Customer, SalesOrder, SalesOrderDetail, Product | songs, events, artists, users | [conforme repo] | toll_records, vehicle, operator |
| **Destino sugerido** | Delta Lake / DW genérico | Redshift / Delta Lake | Hive / Delta Lake | Delta Lake |
| **Carga** | Full load dims, incremental fatos | Incremental por timestamp | Full load | Incremental |
| **DQ crítica** | LineTotal = UnitPrice * OrderQty | userid NOT NULL, page = NextSong | [conforme repo] | amount > 0, timestamp válido |
| **Schema fonte** | Sales, Production | stagingevents, stagingsongs | public | toll_data |

**Adaptação para Sparkify (#7):**
```
*scan-repo
Repositório: https://github.com/ddgope/Data-Pipelines-with-Airflow
Sistema legado: plataforma de streaming musical Sparkify
Fonte: S3 (logs JSON de eventos de usuário + metadados de músicas via Airflow → Redshift)
Entidades: staging_events, staging_songs, users, songs, artists, time, songplays
```

**Adaptação para RDBMS→HDFS (#3):**
```
*scan-repo
Repositório: https://github.com/Stefen-Taime/ETL-Data-Pipeline-RDBMS-TO-HDFS-... 
Sistema legado: PostgreSQL com pipeline Airflow + Sqoop + Spark → Hive
Fonte: PostgreSQL (tabelas relacionais)
Destino: HDFS/Hive
Tech stack legado: Sqoop para extração, Spark para transformação, Hive como destino
```

---

## Checklist de Conclusão do Lab

### UPSTREAM ✅
- [ ] Repositório legado clonado e explorado
- [ ] `wave-config.yaml` criado e validado (`validate_wave_config.py`)
- [ ] `inventory-report.md` gerado (discovery-scout)
- [ ] Diagrama de dependências (DAG) gerado
- [ ] `outputs/upstream/strategy/problem-statement.md` criado (data-strategist)
- [ ] `outputs/upstream/strategy/kpis.md` criado (data-strategist)
- [ ] `outputs/upstream/analysis/analytical-questions.md` criado (business-analyst)
- [ ] `outputs/upstream/sttm/sttm.md` criado (business-analyst)
- [ ] `outputs/upstream/analysis/dq-initial.md` criado (business-analyst)
- [ ] Gate 1 score calculado e registrado em `outputs/summary/gate1-decision.md`

### MIDSTREAM ✅
- [ ] `architecture.md` criado (data-architect)
- [ ] `decisions.md` com ADRs criado (data-architect)
- [ ] `data-model.md` com diagrama ER criado (data-modeler)
- [ ] `data-contracts.md` criado (data-modeler)
- [ ] PII detectado e masking definido (security-compliance)
- [ ] Scripts DDL gerados (code-generator)
- [ ] Scripts ETL bronze/silver/gold gerados (code-generator)
- [ ] `quality-gate-evidence.md` criado (quality-gate)
- [ ] Gate 2 score calculado e registrado em `outputs/summary/gate2-decision.md`

### DOWNSTREAM ✅
- [ ] `execution-runbook.md` criado (downstream-executor)
- [ ] Dry-run executado e riscos documentados
- [ ] Row count reconciliado (reconciliation)
- [ ] Checksums financeiros validados
- [ ] Schema diff realizado
- [ ] Erros diagnosticados e corrigidos (self-healing, se necessário)
- [ ] `wave-report.md` gerado (documentation)
- [ ] `data-lineage.md` gerado (documentation)
- [ ] Gate 3 score calculado e registrado em `outputs/summary/gate3-decision.md`

### PÓS-WAVE ✅
- [ ] Retrospectiva conduzida (iteration-improvement)
- [ ] Próximos passos definidos

---

## Estrutura de Pastas Esperada ao Final

```text
projects/wave-lab-adventureworks/
├── wave-config.yaml
├── context/
│   ├── project-config.yaml
│   ├── agent-task-config.yaml       ← trace_id e sequência de agentes
│   └── shared-context.md
│
└── outputs/
    ├── upstream/                    ← artefatos Gate 1
    │   ├── inventory-report.md
    │   ├── strategy/
    │   │   ├── problem-statement.md
    │   │   └── kpis.md
    │   ├── analysis/
    │   │   ├── analytical-questions.md
    │   │   └── dq-initial.md
    │   └── sttm/
    │       └── sttm.md
    │
    ├── midstream/                   ← artefatos Gate 2
    │   ├── architecture.md
    │   ├── decisions.md
    │   ├── data-model.md
    │   ├── data-contracts.md
    │   ├── monitoring-spec.md
    │   ├── security-compliance-report.md
    │   ├── quality-gate-evidence.md
    │   ├── ddl/
    │   │   ├── dim_customer.sql
    │   │   ├── dim_product.sql
    │   │   ├── fact_sales_order.sql
    │   │   └── fact_sales_order_detail.sql
    │   └── etl/
    │       ├── bronze_extract.py
    │       ├── silver_transform.py
    │       └── gold_load.py
    │
    ├── downstream/                  ← artefatos Gate 3
    │   ├── execution-runbook.md
    │   ├── reconciliation-evidence.md
    │   ├── wave-report.md
    │   ├── data-lineage.md
    │   └── changelog.md
    │
    └── summary/                     ← decisões de gate
        ├── gate1-decision.md
        ├── gate2-decision.md
        └── gate3-decision.md
```

---

## Próximos Passos

| Objetivo | O que fazer |
|---|---|
| Aprofundar no método | Leia [PLAYBOOK-MIGRATION-OPERATIONS.md](PLAYBOOK-MIGRATION-OPERATIONS.md) — versão operacional completa |
| Ver todos os comandos disponíveis | Consulte [COPILOT-AGENTS-GUIDE.md](COPILOT-AGENTS-GUIDE.md) — referência completa |
| Entender as permissões por agente | Leia [OPERATING-MODEL-CANVAS-v2.md](OPERATING-MODEL-CANVAS-v2.md) |
| Repetir com outro repositório | Use a [Seção 10](#seção-10--adaptando-os-prompts-para-outros-repositórios) deste documento |
| Executar uma wave real | Siga [PLAYBOOK-MIGRATION-OPERATIONS.md](PLAYBOOK-MIGRATION-OPERATIONS.md) com dados reais |
