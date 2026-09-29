# 🚀 Guia de Início Rápido - Azure Databricks Integration

Este guia te levará do zero até ter dados ingeridos no Databricks em **menos de 30 minutos**.

---

## ⚡ Quick Start (3 passos)

### 1️⃣ Instale as Ferramentas

```powershell
# Azure CLI
winget install Microsoft.AzureCLI

# Python 3.11
winget install Python.Python.3.11

# Databricks CLI (após instalar Python)
pip install databricks-cli

# Reinicie o terminal após as instalações
```

### 2️⃣ Execute o Pipeline Completo

```powershell
# Entre no diretório de orquestração
cd azure-databricks-integration/05-orchestration

# Execute tudo de uma vez
.\run-all.ps1
```

O script irá:
- ✅ Criar o workspace Databricks no Azure
- ✅ Configurar autenticação
- ✅ Criar schemas e tabelas
- ✅ Ingerir dados automaticamente

### 3️⃣ Acesse o Databricks

Após a execução, acesse a URL do workspace que será exibida no terminal.

---

## 🔧 Configuração Manual (se preferir controle total)

### Passo 1: Configure o Azure CLI

```powershell
# Login no Azure
az login

# Liste suas subscriptions
az account list --output table

# Defina a subscription ativa
az account set --subscription "<SUBSCRIPTION_ID>"
```

### Passo 2: Provisione o Workspace

```powershell
cd azure-databricks-integration/01-provision-azure

# Edite o arquivo config.template.json
notepad config.template.json
# Substitua 'SUBSTITUA_PELO_SEU_SUBSCRIPTION_ID' pelo seu ID real

# Execute o provisionamento
.\provision-databricks.ps1
```

### Passo 3: Configure o Databricks CLI

```powershell
cd ..\02-configure-databricks

# Execute o script de configuração
.\setup-databricks-cli.ps1

# Você será solicitado a fornecer:
# - Workspace URL (pode ser detectada automaticamente)
# - Personal Access Token (gere no Databricks)
```

**Como gerar o token:**
1. Acesse seu workspace Databricks
2. Clique no ícone do usuário (canto superior direito)
3. User Settings → Developer → Access Tokens
4. Generate New Token
5. Copie o token (aparece apenas UMA vez!)

### Passo 4: Crie as Tabelas

```powershell
cd ..\03-database-setup

# Faz upload dos scripts SQL
.\execute-ddl.ps1

# OU execute via Python API (requer SQL Warehouse)
cd ..\04-data-ingestion
pip install -r requirements.txt
python execute-sql-via-api.py
```

### Passo 5: Ingira os Dados

```powershell
cd ..\04-data-ingestion

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
# Crie arquivo .env na raiz do projeto:
notepad ..\..\..\.env

# Adicione:
# DATABRICKS_HOST=adb-xxxxx.azuredatabricks.net
# DATABRICKS_TOKEN=dapi...
# DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx

# Ingira CSV
python ingest-from-csv.py --file ..\..\Files\green_tripdata_2021-04.csv --table bronze.taxi_trips_raw

# Ingira JSON
python ingest-from-json.py --file ..\..\Files\payment_type_array.json --table reference.payment_types

# Ingira de API externa
python ingest-from-api.py --api-url "https://api.exemplo.com/data" --table bronze.external_data
```

---

## 🎯 Casos de Uso Comuns

### Uso 1: Executar Tudo Automaticamente

```powershell
cd azure-databricks-integration/05-orchestration
.\run-all.ps1
```

### Uso 2: Pular Provisionamento (workspace já existe)

```powershell
.\run-all.ps1 -SkipProvisioning
```

### Uso 3: Apenas Ingestão de Dados

```powershell
.\run-all.ps1 -IngestOnly
```

### Uso 4: Executar Módulos Específicos

```powershell
# Apenas provisionamento
.\run-modular.ps1 -Module Provision

# Configuração e DDL
.\run-modular.ps1 -Module Config,DDL

# Apenas ingestão
.\run-modular.ps1 -Module Ingest
```

---

## 🐛 Troubleshooting

### Erro: "Azure CLI not found"

```powershell
winget install Microsoft.AzureCLI
# Reinicie o terminal
```

### Erro: "Databricks authentication failed"

```powershell
# Reconfigure o CLI
cd azure-databricks-integration/02-configure-databricks
.\setup-databricks-cli.ps1
```

### Erro: "SQL Warehouse not found"

1. Acesse: https://<seu-workspace>.azuredatabricks.net/sql/warehouses
2. Crie um SQL Warehouse (ou inicie um existente)
3. Copie o HTTP Path
4. Configure: `$env:DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/xxxxx"`

### Erro: "Table already exists"

```sql
-- Execute no Databricks SQL Editor
DROP TABLE IF EXISTS bronze.taxi_trips_raw;
```

### Python: "Module not found"

```powershell
cd azure-databricks-integration/04-data-ingestion
pip install -r requirements.txt
```

---

## 📚 Recursos Adicionais

- **README Principal**: [README.md](README.md)
- **Documentação Azure Databricks**: https://learn.microsoft.com/azure/databricks/
- **Databricks SQL Reference**: https://docs.databricks.com/sql/language-manual/

---

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs de execução no terminal
2. Consulte a [documentação completa](README.md)
3. Revise as [variáveis de ambiente](.env.example)

---

*Powered by Avanade™ Core - Data Engineering Agents*
