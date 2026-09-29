# 🔷 Azure Databricks Integration - Módulos Autônomos

**Versão:** 1.0  
**Data:** 4 de Fevereiro de 2026  
**Objetivo:** Provisionamento automatizado e ingestão de dados no Azure Databricks

---

## 📋 Visão Geral

Esta solução fornece módulos **independentes e reutilizáveis** para:

1. ✅ Provisionar Azure Databricks workspace via Azure CLI
2. ✅ Configurar autenticação e Databricks CLI
3. ✅ Criar schemas e tabelas automaticamente
4. ✅ Ingerir dados de fontes externas (CSV, JSON, APIs) no Databricks
5. ✅ Executar tudo integrado com um único comando

---

## 🏗️ Arquitetura

```
azure-databricks-integration/
│
├── 01-provision-azure/
│   ├── provision-databricks.ps1          # Cria workspace no Azure
│   ├── config.template.json              # Template de configuração
│   └── README.md                         # Instruções específicas
│
├── 02-configure-databricks/
│   ├── setup-databricks-cli.ps1          # Configura Databricks CLI
│   ├── generate-token.ps1                # Gera Personal Access Token
│   └── README.md
│
├── 03-database-setup/
│   ├── create-schemas.sql                # DDL para schemas
│   ├── create-tables.sql                 # DDL para tabelas
│   ├── execute-ddl.ps1                   # Executa SQL no Databricks
│   └── README.md
│
├── 04-data-ingestion/
│   ├── ingest-from-csv.py                # Ingere dados de CSV
│   ├── ingest-from-json.py               # Ingere dados de JSON
│   ├── ingest-from-api.py                # Ingere dados de API REST
│   ├── requirements.txt                  # Dependências Python
│   └── README.md
│
├── 05-orchestration/
│   ├── run-all.ps1                       # 🚀 Executa tudo integrado
│   ├── run-modular.ps1                   # Executa módulos selecionados
│   └── README.md
│
└── README.md                             # Este arquivo
```

---

## 📦 Pré-requisitos

### Ferramentas Necessárias

| Ferramenta | Versão | Como Instalar |
|------------|--------|---------------|
| Azure CLI | >= 2.50 | `winget install Microsoft.AzureCLI` |
| Databricks CLI | >= 0.18 | `pip install databricks-cli` |
| Python | >= 3.9 | `winget install Python.Python.3.11` |
| PowerShell | >= 7.0 | Já incluído no Windows |

### Credenciais Azure

Você precisará de:
- **Subscription ID** do Azure
- **Resource Group** (será criado se não existir)
- Permissões de **Contributor** na subscription

---

## 🚀 Guia de Uso Rápido

### Opção 1: Execução Integrada (Recomendado)

Execute tudo com um único comando:

```powershell
cd azure-databricks-integration/05-orchestration
.\run-all.ps1
```

Isso executará:
1. ✅ Provisionamento do workspace
2. ✅ Configuração do Databricks CLI
3. ✅ Criação de schemas e tabelas
4. ✅ Ingestão de dados de exemplo

### Opção 2: Execução Modular

Execute apenas os módulos desejados:

```powershell
# Apenas provisionar
.\01-provision-azure\provision-databricks.ps1

# Apenas configurar CLI
.\02-configure-databricks\setup-databricks-cli.ps1

# Apenas criar tabelas
.\03-database-setup\execute-ddl.ps1

# Apenas ingerir dados
python .\04-data-ingestion\ingest-from-csv.py
```

---

## 🔐 Gestão de Credenciais

### 1. Azure CLI - Login

```powershell
# Login interativo (abre navegador)
az login

# Ou login com Service Principal (CI/CD)
az login --service-principal `
  --username $env:AZURE_CLIENT_ID `
  --password $env:AZURE_CLIENT_SECRET `
  --tenant $env:AZURE_TENANT_ID

# Definir subscription ativa
az account set --subscription "<SUBSCRIPTION_ID>"
```

### 2. Databricks - Token de Acesso

```powershell
# Opção A: Gerar token via script (requer workspace já criado)
.\02-configure-databricks\generate-token.ps1

# Opção B: Gerar manualmente
# 1. Acesse: https://<workspace-url>/
# 2. User Settings → Developer → Access Tokens → Generate New Token
# 3. Copie o token (aparece apenas uma vez!)
```

### 3. Armazenar Credenciais Seguramente

```powershell
# Criar arquivo .env (nunca commitar!)
echo "DATABRICKS_HOST=https://adb-123456789.azuredatabricks.net" > .env
echo "DATABRICKS_TOKEN=dapi123456789..." >> .env

# Ou usar variáveis de ambiente
$env:DATABRICKS_HOST = "https://adb-123456789.azuredatabricks.net"
$env:DATABRICKS_TOKEN = "dapi123456789..."
```

---

## 📊 Fluxo de Ingestão de Dados

### Fontes Suportadas

| Fonte | Script | Descrição |
|-------|--------|-----------|
| CSV Local | `ingest-from-csv.py` | Lê CSVs da pasta `Files/` |
| JSON Local | `ingest-from-json.py` | Lê arquivos JSON |
| API REST | `ingest-from-api.py` | Consome APIs externas |
| Azure Blob | `ingest-from-blob.py` | (Futuro) Storage Account |

### Exemplo: Ingerir CSV

```python
python 04-data-ingestion/ingest-from-csv.py \
  --file ../Files/green_tripdata_2021-04.csv \
  --table bronze.taxi_trips \
  --mode append
```

---

## 🛠️ Personalização

### Configurar Parâmetros

Edite `01-provision-azure/config.template.json`:

```json
{
  "subscriptionId": "SEU_SUBSCRIPTION_ID",
  "resourceGroup": "rg-databricks-dev",
  "location": "eastus2",
  "workspaceName": "dbw-data-engineering",
  "pricingTier": "premium"
}
```

### Adaptar Schemas

Edite `03-database-setup/create-tables.sql` conforme seu modelo de dados.

---

## ⚠️ Segurança

### ✅ Boas Práticas

- ✅ Nunca commitar arquivos `.env` ou tokens
- ✅ Usar Azure Key Vault em produção
- ✅ Rotacionar tokens a cada 90 dias
- ✅ Aplicar RBAC no Databricks workspace

### ❌ Evitar

- ❌ Hardcoded credentials em scripts
- ❌ Tokens com validade "sem expiração"
- ❌ Compartilhar Personal Access Tokens

---

## 📈 Próximos Passos

Após a configuração inicial:

1. **Adaptar para seus dados:** Edite scripts de ingestão
2. **Agendar execuções:** Use Azure DevOps Pipelines ou GitHub Actions
3. **Monitorar:** Integre com Azure Monitor ou Databricks Jobs
4. **Governança:** Aplique Unity Catalog (se Premium)

---

## 🆘 Troubleshooting

### Erro: "Azure CLI not found"

```powershell
# Instale o Azure CLI
winget install Microsoft.AzureCLI

# Reinicie o terminal
```

### Erro: "Databricks authentication failed"

```powershell
# Verifique se o token está correto
databricks workspace list

# Reconfigure o CLI
databricks configure --token
```

### Erro: "Table already exists"

```sql
-- Use DROP TABLE IF EXISTS no SQL
DROP TABLE IF EXISTS bronze.taxi_trips;
CREATE TABLE bronze.taxi_trips (...);
```

---

## 📞 Suporte

Para dúvidas sobre este módulo:
- 📧 Email: data-engineering@avanade.com
- 📚 Docs: Ver `Docs/GUIA-DE-USO-AGENTES.md`

---

*Powered by Avanade™ Core - Data Engineering Agents*
