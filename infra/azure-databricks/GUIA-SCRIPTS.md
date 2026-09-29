# Azure Databricks Integration - Guia Completo de Scripts

Este documento descreve todos os scripts disponíveis para integração com Azure Databricks, suas funções e como executá-los.

---

## Configuração Atual

Seu ambiente está configurado com:

| Variável | Valor |
|----------|-------|
| **DATABRICKS_HOST** | `adb-7405607395070159.19.azuredatabricks.net` |
| **DATABRICKS_HTTP_PATH** | `/sql/1.0/warehouses/6e43216f1e93cb7c` |
| **DATABRICKS_SQL_WAREHOUSE_ID** | `6e43216f1e93cb7c` |

---

## Passo a Passo de Execução

### Opção 1: Execução Completa (Recomendado para primeira vez)

```powershell
cd azure-databricks-integration\05-orchestration
.\run-all.ps1
```

### Opção 2: Execução Modular (Etapas individuais)

```powershell
# Passo 1: Criar Schemas e Tabelas
cd azure-databricks-integration\03-database-setup
.\execute-ddl.ps1

# Passo 2: Ingerir dados
cd ..\04-data-ingestion
pip install -r requirements.txt
python ingest-from-csv-universal.py --file "..\..\data-engineer-exec-agent\Files\green_tripdata_2021-04.csv" --table bronze.taxi_trips_raw
```

### Opção 3: Execução Rápida (Apenas Ingestão)

```powershell
cd azure-databricks-integration\05-orchestration
.\run-all.ps1 -IngestOnly
```

---

## Estrutura de Diretórios

```
azure-databricks-integration/
├── .env                          # Suas credenciais (configurado!)
├── 01-provision-azure/           # Provisionamento do workspace
├── 02-configure-databricks/      # Configuração do CLI e SQL Warehouse
├── 03-database-setup/            # Scripts SQL (schemas e tabelas)
├── 04-data-ingestion/            # Scripts Python de ingestão
└── 05-orchestration/             # Orquestradores (run-all, run-modular)
```

---

## Descrição Detalhada dos Scripts

### 01-provision-azure/

| Script | Descrição | Como Executar |
|--------|-----------|---------------|
| **provision-databricks.ps1** | Provisiona um novo workspace Azure Databricks via Azure CLI | `.\provision-databricks.ps1` |
| **config.template.json** | Template de configuração para provisionamento | Editar antes de executar provision-databricks.ps1 |

#### Exemplo de Execução:
```powershell
cd 01-provision-azure
# Edite config.template.json com suas configurações
.\provision-databricks.ps1
```

---

### 02-configure-databricks/

| Script | Descrição | Como Executar |
|--------|-----------|---------------|
| **setup-databricks-cli.ps1** | Instala e configura o Databricks CLI com autenticação | `.\setup-databricks-cli.ps1` |
| **create-sql-warehouse.ps1** | Cria um SQL Warehouse no Databricks via API | `.\create-sql-warehouse.ps1` |

#### Exemplo de Execução:
```powershell
cd 02-configure-databricks

# Configurar CLI (interativo)
.\setup-databricks-cli.ps1

# Ou com parâmetros
.\setup-databricks-cli.ps1 -WorkspaceUrl "https://adb-xxx.azuredatabricks.net" -Token "dapi..."

# Criar SQL Warehouse
.\create-sql-warehouse.ps1 -Name "meu-warehouse" -ClusterSize "Small"
```

---

### 03-database-setup/

| Script | Descrição | Como Executar |
|--------|-----------|---------------|
| **create-schemas.sql** | Cria schemas Medallion (Bronze, Silver, Gold, Reference) | Via execute-ddl.ps1 |
| **create-tables.sql** | Cria tabelas para pipeline de dados de táxis NYC | Via execute-ddl.ps1 |
| **execute-ddl.ps1** | Executa os scripts SQL no Databricks | `.\execute-ddl.ps1` |

#### Exemplo de Execução:
```powershell
cd 03-database-setup

# Executar todos os DDLs
.\execute-ddl.ps1

# Executar apenas um arquivo específico
.\execute-ddl.ps1 -SqlFile "create-schemas.sql"
```

#### Schemas Criados:
- **bronze** - Dados brutos (raw data)
- **silver** - Dados limpos e validados
- **gold** - Dados agregados para BI
- **reference** - Tabelas de referência (lookup)

---

### 04-data-ingestion/

| Script | Descrição | Como Executar |
|--------|-----------|---------------|
| **ingest-from-csv.py** | Ingere dados de arquivos CSV para Databricks | `python ingest-from-csv.py --file <arquivo> --table <tabela>` |
| **ingest-from-csv-universal.py** | Versão universal (Azure + Community Edition) | `python ingest-from-csv-universal.py --file <arquivo> --table <tabela>` |
| **ingest-from-json.py** | Ingere dados de arquivos JSON para Databricks | `python ingest-from-json.py --file <arquivo> --table <tabela>` |
| **ingest-from-api.py** | Consome dados de APIs REST e insere no Databricks | `python ingest-from-api.py --url <api_url> --table <tabela>` |
| **execute-sql-via-api.py** | Executa queries SQL diretamente via API | `python execute-sql-via-api.py --query "SELECT * FROM tabela"` |
| **requirements.txt** | Dependências Python | `pip install -r requirements.txt` |

#### Exemplos de Execução:
```powershell
cd 04-data-ingestion

# Instalar dependências (primeira vez)
pip install -r requirements.txt

# Ingerir CSV
python ingest-from-csv-universal.py --file "..\..\data-engineer-exec-agent\Files\green_tripdata_2021-04.csv" --table bronze.taxi_trips_raw

# Ingerir JSON
python ingest-from-json.py --file "..\..\data-engineer-exec-agent\Files\payment_type_array.json" --table reference.payment_types

# Consumir de API
python ingest-from-api.py --url "https://api.exemplo.com/data" --table bronze.api_data

# Executar SQL
python execute-sql-via-api.py --query "SELECT COUNT(*) FROM bronze.taxi_trips_raw"
```

---

### 05-orchestration/

| Script | Descrição | Como Executar |
|--------|-----------|---------------|
| **run-all.ps1** | Executa TODO o pipeline completo | `.\run-all.ps1` |
| **run-modular.ps1** | Executa módulos selecionados | `.\run-modular.ps1 -Module <modulo>` |

#### run-all.ps1 - Parâmetros:
```powershell
# Execução completa
.\run-all.ps1

# Pular provisionamento (usar workspace existente)
.\run-all.ps1 -SkipProvisioning

# Pular configuração do CLI
.\run-all.ps1 -SkipConfig

# Pular criação de tabelas
.\run-all.ps1 -SkipDDL

# Executar apenas ingestão
.\run-all.ps1 -IngestOnly
```

#### run-modular.ps1 - Módulos Disponíveis:
```powershell
# Apenas provisionamento
.\run-modular.ps1 -Module Provision

# Apenas configuração
.\run-modular.ps1 -Module Config

# Apenas DDL (schemas e tabelas)
.\run-modular.ps1 -Module DDL

# Apenas ingestão
.\run-modular.ps1 -Module Ingest

# Múltiplos módulos
.\run-modular.ps1 -Module Config,DDL,Ingest

# Executar tudo
.\run-modular.ps1 -Module All
```

---

## Script Unificado (Extração + Inserção)

Sim! O script **`run-all.ps1`** automatiza todo o processo:

1. ✅ Provisionamento do workspace (opcional)
2. ✅ Configuração do CLI
3. ✅ Criação de schemas e tabelas
4. ✅ Ingestão de dados de múltiplas fontes

Para uma execução rápida apenas da ingestão:
```powershell
.\run-all.ps1 -IngestOnly
```

---

## Fluxo Recomendado

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PASSO A PASSO                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. CONFIGURAÇÃO (.env) ─────────────────────────────────── [✓ JÁ FEITO]   │
│     └─ Credenciais configuradas no arquivo .env                             │
│                                                                              │
│  2. CRIAR SCHEMAS E TABELAS ──────────────────────────────────────────────  │
│     │                                                                        │
│     └─ cd 03-database-setup                                                  │
│        .\execute-ddl.ps1                                                     │
│                                                                              │
│  3. INGERIR DADOS ────────────────────────────────────────────────────────  │
│     │                                                                        │
│     └─ cd 04-data-ingestion                                                  │
│        pip install -r requirements.txt                                       │
│        python ingest-from-csv-universal.py --file <arquivo> --table <tabela>│
│                                                                              │
│  OU EXECUTE TUDO DE UMA VEZ:                                                 │
│     │                                                                        │
│     └─ cd 05-orchestration                                                   │
│        .\run-all.ps1 -SkipProvisioning                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Arquivos de Dados Disponíveis

Os seguintes arquivos estão disponíveis para ingestão:

| Arquivo | Tipo | Localização |
|---------|------|-------------|
| green_tripdata_2021-04.csv | CSV | data-engineer-exec-agent/Files/ |
| green_tripdata_2021-05.csv | CSV | data-engineer-exec-agent/Files/ |
| green_tripdata_2021-06.csv | CSV | data-engineer-exec-agent/Files/ |
| payment_type_array.json | JSON | data-engineer-exec-agent/Files/ |
| rate_code.json | JSON | data-engineer-exec-agent/Files/ |
| trip_type.tsv | TSV | data-engineer-exec-agent/Files/ |

---

## Solução de Problemas

### Erro: "DATABRICKS_HOST incorreto"
- Verifique se o .env não contém parâmetros extras (como `/?o=xxx`)
- Formato correto: `adb-xxxx.xx.azuredatabricks.net`

### Erro: "SQL Warehouse não encontrado"
- Execute o script de criação: `.\create-sql-warehouse.ps1`
- Verifique o DATABRICKS_HTTP_PATH no .env

### Erro: "Token inválido"
- Gere um novo token no Databricks
- User Settings → Developer → Access Tokens

### Erro: "Dependências Python"
```powershell
cd 04-data-ingestion
pip install -r requirements.txt
```

---

## Comandos Rápidos

```powershell
# Testar conexão
cd azure-databricks-integration\04-data-ingestion
python -c "from dotenv import load_dotenv; import os; load_dotenv('../.env'); print('Host:', os.getenv('DATABRICKS_HOST'))"

# Executar query de teste
python execute-sql-via-api.py --query "SHOW SCHEMAS"

# Ingerir um arquivo CSV
python ingest-from-csv-universal.py --file "..\..\data-engineer-exec-agent\Files\green_tripdata_2021-04.csv" --table bronze.taxi_trips_raw

# Executar pipeline completo
cd ..\05-orchestration
.\run-all.ps1 -SkipProvisioning
```
