# 🔧 Escolhendo seu Ambiente

Você tem **2 arquivos de configuração** separados para facilitar:

---

## 📁 Arquivos Disponíveis

### 1️⃣ Azure Databricks (Produção, Pago)
📄 **Arquivo:** [.env.azure.example](.env.azure.example)

**Use quando:**
- ✅ Tiver Azure subscription
- ✅ Precisar de mais de 10GB de dados
- ✅ Quiser automatizar com jobs agendados
- ✅ For ambiente de produção

**Custos:** ~R$ 50-100/mês (variável conforme uso)

---

### 2️⃣ Databricks Community Edition (Teste, Grátis)
📄 **Arquivo:** [.env.community.example](.env.community.example)

**Use quando:**
- ✅ Quiser testar sem custo
- ✅ Estiver aprendendo Databricks
- ✅ Tiver até 10GB de dados
- ✅ Não precisar de automação

**Custos:** 🆓 R$ 0,00 (100% grátis)

---

## 🚀 Como Usar

### Opção 1: Azure Databricks

```powershell
# 1. Copie o template Azure
cd azure-databricks-integration
copy .env.azure.example .env

# 2. Edite o .env e preencha:
#    - DATABRICKS_HOST (workspace URL do Azure)
#    - DATABRICKS_TOKEN (Personal Access Token)
#    - DATABRICKS_HTTP_PATH (SQL Warehouse)

# 3. Execute o pipeline completo
cd 05-orchestration
.\run-all.ps1
```

---

### Opção 2: Community Edition

```powershell
# 1. Copie o template Community
cd azure-databricks-integration
copy .env.community.example .env

# 2. Crie conta em: https://community.cloud.databricks.com/

# 3. Edite o .env e preencha:
#    - DATABRICKS_TOKEN (Personal Access Token)
#    - DATABRICKS_CLUSTER_ID (ID do cluster)

# 4. Crie tabelas manualmente no SQL Editor do Databricks
#    (copie/cole os SQLs de 03-database-setup/)

# 5. Ingira dados
cd 04-data-ingestion
pip install -r requirements.txt
python ingest-from-csv-universal.py --file ..\..\Files\green_tripdata_2021-04.csv --table bronze.taxi_trips_raw
```

---

## 📊 Comparação Rápida

| Característica | Azure | Community |
|----------------|-------|-----------|
| **Setup** | [.env.azure.example](.env.azure.example) | [.env.community.example](.env.community.example) |
| **Variáveis necessárias** | 3 (HOST, TOKEN, HTTP_PATH) | 2 (TOKEN, CLUSTER_ID) |
| **Tempo de setup** | 20 min (automatizado) | 10 min (manual) |
| **Custo** | Pago | Grátis |
| **Limite de dados** | Ilimitado | 10GB |
| **Scripts SQL** | ✅ Funciona | ✅ Funciona |
| **Scripts Python** | ✅ Funciona | ✅ Funciona |
| **Jobs automáticos** | ✅ Sim | ❌ Não |

---

## 💡 Recomendação

### Workflow Ideal

```
1. TESTE no Community Edition (grátis)
   └─ Use: .env.community.example
   └─ Valide scripts
   └─ Aprenda sem custo

2. MIGRE para Azure (quando precisar)
   └─ Use: .env.azure.example
   └─ Mesmo código!
   └─ Apenas troque o .env
```

---

## 🔄 Migração entre Ambientes

**Para trocar de Community → Azure:**

```powershell
# Backup do .env atual
copy .env .env.community.backup

# Use o template Azure
copy .env.azure.example .env

# Edite com suas credenciais Azure
notepad .env
```

**Para trocar de Azure → Community:**

```powershell
# Backup do .env atual
copy .env .env.azure.backup

# Use o template Community
copy .env.community.example .env

# Edite com suas credenciais Community
notepad .env
```

---

## 📚 Documentação Detalhada

- **Azure Databricks:** Ver [README.md](README.md) e [QUICKSTART.md](QUICKSTART.md)
- **Community Edition:** Ver [COMMUNITY-EDITION.md](COMMUNITY-EDITION.md) e [QUICK-TEST-COMMUNITY.md](QUICK-TEST-COMMUNITY.md)

---

## 🆘 Troubleshooting

### Não sei qual usar?

**Comece com Community Edition** se:
- 🆓 Você quer testar grátis
- 📚 Está aprendendo Databricks
- 🧪 É ambiente de desenvolvimento/teste

**Use Azure Databricks** se:
- 💼 É projeto corporativo/produção
- 📈 Precisa de > 10GB de dados
- ⚙️ Quer automação (jobs, pipelines)

### Posso usar ambos?

**Sim!** Mantenha ambos os arquivos:
- `.env.azure.example` - Template para Azure
- `.env.community.example` - Template para Community
- `.env` - O que está ativo (não commitar no Git!)

Troque o `.env` conforme necessário.

---

*Escolha o template certo e comece a trabalhar! 🚀*
