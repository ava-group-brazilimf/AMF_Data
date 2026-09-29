# 📊 Arquitetura da Solução - Azure Databricks Integration

## 🏗️ Visão Geral da Arquitetura

```mermaid
flowchart TB
    subgraph External["🌐 FONTES EXTERNAS"]
        CSV[📄 Arquivos CSV]
        JSON[📋 Arquivos JSON]
        API[🔌 APIs REST]
    end
    
    subgraph Azure["☁️ MICROSOFT AZURE"]
        subgraph Provisioning["1️⃣ PROVISIONAMENTO"]
            AzCLI[Azure CLI]
            RG[Resource Group]
            DBW[Databricks Workspace]
            
            AzCLI -->|Cria| RG
            RG -->|Contém| DBW
        end
        
        subgraph Databricks["2️⃣ DATABRICKS"]
            subgraph Compute["Compute"]
                SQLWare[SQL Warehouse]
                Cluster[Clusters]
            end
            
            subgraph Storage["3️⃣ STORAGE (Medallion)"]
                Bronze[(🥉 Bronze Layer<br/>Raw Data)]
                Silver[(🥈 Silver Layer<br/>Cleansed Data)]
                Gold[(🥇 Gold Layer<br/>Aggregated Data)]
                Ref[(📚 Reference<br/>Lookup Tables)]
            end
            
            subgraph Processing["ETL Pipeline"]
                DDL[DDL Scripts<br/>Create Tables]
                Ingest[Ingestion Scripts<br/>Load Data]
                Transform[Transformation<br/>Bronze → Silver → Gold]
            end
        end
    end
    
    subgraph Local["💻 AMBIENTE LOCAL"]
        Scripts[PowerShell Scripts]
        Python[Python Scripts]
        Config[Configuration Files]
    end
    
    CSV -->|ingest-from-csv.py| Bronze
    JSON -->|ingest-from-json.py| Ref
    API -->|ingest-from-api.py| Bronze
    
    Scripts -->|Provision| Provisioning
    Scripts -->|Configure| Databricks
    Python -->|Execute| DDL
    Python -->|Run| Ingest
    
    Bronze -->|Cleanse| Silver
    Silver -->|Aggregate| Gold
    
    SQLWare -->|Query| Storage
    Cluster -->|Process| Processing
    
    Gold -->|Consume| BI[📈 Power BI / Dashboards]
    
    style Bronze fill:#cd7f32
    style Silver fill:#c0c0c0
    style Gold fill:#ffd700
    style Ref fill:#4a90e2
```

---

## 🔄 Fluxo de Execução

### Modo Completo (run-all.ps1)

```mermaid
sequenceDiagram
    participant User
    participant RunAll as run-all.ps1
    participant Provision as provision-databricks.ps1
    participant Config as setup-databricks-cli.ps1
    participant DDL as execute-ddl.ps1
    participant Ingest as ingest-*.py
    participant Databricks as Azure Databricks
    
    User->>RunAll: Execute
    
    rect rgb(200, 220, 240)
    Note over RunAll,Provision: FASE 1: Provisionamento
    RunAll->>Provision: Execute Module 1
    Provision->>Databricks: Create Workspace
    Databricks-->>Provision: Workspace Created
    Provision-->>RunAll: ✓ Success
    end
    
    rect rgb(220, 240, 220)
    Note over RunAll,Config: FASE 2: Configuração
    RunAll->>Config: Execute Module 2
    Config->>User: Prompt for Token
    User-->>Config: Provide Token
    Config->>Config: Configure CLI
    Config-->>RunAll: ✓ Success
    end
    
    rect rgb(240, 220, 200)
    Note over RunAll,DDL: FASE 3: Criação de Schemas
    RunAll->>DDL: Execute Module 3
    DDL->>Databricks: Upload SQL Scripts
    Databricks->>Databricks: Create Schemas & Tables
    DDL-->>RunAll: ✓ Success
    end
    
    rect rgb(240, 200, 220)
    Note over RunAll,Ingest: FASE 4: Ingestão
    RunAll->>Ingest: Execute Module 4
    loop For each data source
        Ingest->>Databricks: Insert Data
        Databricks-->>Ingest: Rows Inserted
    end
    Ingest-->>RunAll: ✓ Success
    end
    
    RunAll-->>User: Pipeline Complete ✅
```

### Modo Modular (run-modular.ps1)

```mermaid
flowchart LR
    User[👤 User] --> Choice{Escolha o Módulo}
    
    Choice -->|Provision| M1[1️⃣ Provisionar Workspace]
    Choice -->|Config| M2[2️⃣ Configurar CLI]
    Choice -->|DDL| M3[3️⃣ Criar Tabelas]
    Choice -->|Ingest| M4[4️⃣ Ingerir Dados]
    Choice -->|All| M5[🚀 Executar Tudo]
    
    M1 --> Done1[✅ Workspace Criado]
    M2 --> Done2[✅ CLI Configurado]
    M3 --> Done3[✅ Tabelas Criadas]
    M4 --> Done4[✅ Dados Ingeridos]
    M5 --> Done5[✅ Pipeline Completo]
    
    style M1 fill:#e3f2fd
    style M2 fill:#e8f5e9
    style M3 fill:#fff3e0
    style M4 fill:#fce4ec
    style M5 fill:#f3e5f5
```

---

## 📁 Estrutura de Diretórios

```
azure-databricks-integration/
│
├── 01-provision-azure/              # Módulo de Provisionamento
│   ├── config.template.json         # Configuração do workspace
│   ├── provision-databricks.ps1     # Script de criação
│   └── databricks-workspace-info.json  # Info do workspace (gerado)
│
├── 02-configure-databricks/         # Módulo de Configuração
│   └── setup-databricks-cli.ps1     # Configura autenticação
│
├── 03-database-setup/               # Módulo de DDL
│   ├── create-schemas.sql           # Cria Bronze, Silver, Gold, Reference
│   ├── create-tables.sql            # Cria todas as tabelas
│   └── execute-ddl.ps1              # Upload e execução
│
├── 04-data-ingestion/               # Módulo de Ingestão
│   ├── requirements.txt             # Dependências Python
│   ├── execute-sql-via-api.py       # Executa SQL via API
│   ├── ingest-from-csv.py           # Ingere CSVs
│   ├── ingest-from-json.py          # Ingere JSONs
│   └── ingest-from-api.py           # Ingere de APIs REST
│
├── 05-orchestration/                # Módulo de Orquestração
│   ├── run-all.ps1                  # 🚀 Pipeline completo
│   └── run-modular.ps1              # Execução modular
│
├── .env.example                     # Template de variáveis
├── .gitignore                       # Proteção de credenciais
├── README.md                        # Documentação completa
├── QUICKSTART.md                    # Guia rápido
└── ARCHITECTURE.md                  # Este arquivo
```

---

## 🔐 Segurança e Credenciais

### Fluxo de Autenticação

```mermaid
flowchart TB
    subgraph Local["💻 Local"]
        User[👤 Usuário]
        Script[Script PowerShell/Python]
        EnvFile[.env File]
    end
    
    subgraph Azure["☁️ Azure"]
        AzureAD[Azure AD]
        DBWorkspace[Databricks Workspace]
    end
    
    User -->|az login| AzureAD
    AzureAD -->|Token| User
    
    User -->|Gera PAT| DBWorkspace
    DBWorkspace -->|Personal Access Token| User
    
    User -->|Configura| EnvFile
    EnvFile -->|Lê credenciais| Script
    
    Script -->|Autenticado| DBWorkspace
    
    style EnvFile fill:#ffebee,stroke:#c62828,stroke-width:3px
    style AzureAD fill:#e3f2fd
    style DBWorkspace fill:#fff3e0
```

### ⚠️ Arquivos que NUNCA devem ser commitados

```
❌ .env                           # Credenciais reais
❌ .databrickscfg                 # Config do CLI
❌ databricks-workspace-info.json # Info do workspace
❌ *.token                        # Tokens de acesso
```

✅ **Use sempre:** `.env.example` como template (sem credenciais reais)

---

## 🎯 Camadas de Dados (Medallion Architecture)

### Bronze Layer 🥉
- **Objetivo:** Dados brutos (raw data)
- **Características:**
  - Cópia exata da fonte
  - Sem transformações
  - Metadados de ingestão adicionados
- **Exemplo:** `bronze.taxi_trips_raw`

### Silver Layer 🥈
- **Objetivo:** Dados limpos e validados
- **Características:**
  - Validações de qualidade aplicadas
  - Dados tipados corretamente
  - Campos calculados
- **Exemplo:** `silver.taxi_trips`

### Gold Layer 🥇
- **Objetivo:** Dados agregados para consumo
- **Características:**
  - Métricas de negócio
  - Agregações e resumos
  - Otimizado para BI
- **Exemplo:** `gold.daily_trips_summary`

### Reference Layer 📚
- **Objetivo:** Dados de referência
- **Características:**
  - Lookup tables
  - Dimensões
  - Master data
- **Exemplo:** `reference.payment_types`

---

## 🚀 Performance e Escalabilidade

### Estratégias de Otimização

| Aspecto | Estratégia | Implementação |
|---------|------------|---------------|
| **Ingestão** | Batch processing | Lotes de 1000 registros |
| **Storage** | Delta Lake | Todas as tabelas usam `USING delta` |
| **Compute** | SQL Warehouse | Execução serverless |
| **Particionamento** | Por data | `PARTITION BY (trip_date)` |
| **Z-Ordering** | Colunas frequentes | `OPTIMIZE ... ZORDER BY (pickup_location_id)` |

### Escalabilidade

```mermaid
graph LR
    A[Small<br/>< 1GB] -->|Auto-scaling| B[Medium<br/>1-100GB]
    B -->|Auto-scaling| C[Large<br/>100GB-1TB]
    C -->|Auto-scaling| D[X-Large<br/>> 1TB]
    
    style A fill:#e8f5e9
    style B fill:#fff3e0
    style C fill:#ffebee
    style D fill:#f3e5f5
```

---

## 📊 Monitoramento e Observabilidade

### Métricas Recomendadas

```mermaid
pie title "Distribuição de Monitoramento"
    "Query Performance" : 30
    "Data Quality" : 25
    "Ingestion Metrics" : 20
    "Cost Optimization" : 15
    "Security & Compliance" : 10
```

### Dashboards Sugeridos

1. **Pipeline Health**
   - Taxa de sucesso de ingestões
   - Latência de processamento
   - Erros por fonte

2. **Data Quality**
   - Registros validados vs. rejeitados
   - Percentual de nulls por coluna
   - Anomalias detectadas

3. **Cost Analysis**
   - DBU consumption por dia
   - Storage growth
   - Query costs

---

## 🔄 Integração com CI/CD

### GitHub Actions Example

```yaml
name: Databricks Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r 04-data-ingestion/requirements.txt
      
      - name: Ingest data
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HTTP_PATH: ${{ secrets.DATABRICKS_HTTP_PATH }}
        run: |
          python 04-data-ingestion/ingest-from-csv.py \
            --file data/latest.csv \
            --table bronze.taxi_trips_raw \
            --mode append
```

---

## 🎓 Próximos Passos

### Curto Prazo (1-2 semanas)
- [ ] Implementar transformações Silver → Gold
- [ ] Criar notebooks de análise exploratória
- [ ] Configurar alertas de Data Quality

### Médio Prazo (1-2 meses)
- [ ] Implementar Unity Catalog (governança)
- [ ] Criar dashboards Power BI
- [ ] Automatizar via Azure Data Factory

### Longo Prazo (3-6 meses)
- [ ] Implementar ML pipelines
- [ ] Streaming data com Delta Live Tables
- [ ] Multi-cloud deployment

---

*Powered by Avanade™ Core - Data Engineering Agents*
