# 🔄 Azure Databricks vs Databricks Community Edition

## 📊 Comparação Detalhada

| Aspecto | Azure Databricks | Databricks Community Edition |
|---------|------------------|------------------------------|
| **Provisionamento** | Requer Azure subscription | Sem custo, signup direto |
| **Autenticação** | Azure AD + Personal Access Token | Email/senha + PAT |
| **Compute** | SQL Warehouses, Clusters escaláveis | 1 cluster pequeno fixo |
| **Storage** | DBFS + Azure Storage integrado | DBFS limitado (10GB) |
| **Custo** | Pay-as-you-go (DBUs) | **100% Grátis** |
| **Recursos** | Ilimitado (conforme $$$) | Limitado (15GB RAM) |
| **APIs** | ✅ Mesmas APIs SQL/REST | ✅ Mesmas APIs SQL/REST |
| **SQL Syntax** | ✅ Idêntico | ✅ Idêntico |
| **Delta Lake** | ✅ Suportado | ✅ Suportado |
| **Notebooks** | ✅ Sim | ✅ Sim |
| **Jobs/Scheduling** | ✅ Sim | ❌ Não disponível |
| **Unity Catalog** | ✅ Sim (Premium) | ❌ Não disponível |

---

## ✅ Boa Notícia: Os Scripts Funcionam em AMBOS!

**A maior parte do código é compatível!** Apenas a **autenticação** e **provisionamento** mudam.

### O Que É Idêntico

✅ Scripts SQL (`create-schemas.sql`, `create-tables.sql`)  
✅ Scripts Python de ingestão (`ingest-from-csv.py`, `ingest-from-json.py`)  
✅ Arquitetura Medallion (Bronze/Silver/Gold)  
✅ Databricks SQL Connector  
✅ APIs REST  

### O Que Muda

❌ **Módulo 1** (Provisionamento) - Não precisa no Community Edition  
⚠️ **Módulo 2** (Configuração) - Processo diferente de autenticação  

---

## 🚀 Como Usar com Databricks Community Edition

### Passo 1: Criar Conta (Se ainda não tem)

1. Acesse: https://community.cloud.databricks.com/
2. Clique em "Sign Up"
3. Use sua conta Google
4. Confirme o email

### Passo 2: Obter Credenciais

#### 2.1 Workspace URL
- Após login, sua URL será algo como:
  ```
  https://community.cloud.databricks.com/
  ```

#### 2.2 Personal Access Token
1. Acesse: https://community.cloud.databricks.com/
2. User Settings → Developer → Access Tokens
3. Generate New Token
4. Lifetime: 90 dias
5. **Copie o token** (aparece apenas UMA vez!)

#### 2.3 Cluster/Warehouse Path
No Community Edition:
1. Acesse "Compute" → Clique no cluster (geralmente "Community Cluster")
2. Copie o Cluster ID (ou use o cluster HTTP path se disponível)

**IMPORTANTE:** Community Edition não tem SQL Warehouses dedicados, apenas clusters.

### Passo 3: Configurar Variáveis de Ambiente

Crie arquivo `.env` na raiz do projeto:

```env
# Databricks Community Edition Configuration
DATABRICKS_HOST=community.cloud.databricks.com
DATABRICKS_TOKEN=dapi_seu_token_aqui

# Para Community Edition, você vai precisar do Cluster ID
DATABRICKS_CLUSTER_ID=seu_cluster_id_aqui

# SQL Warehouse não existe no Community, deixe em branco ou use cluster HTTP path
DATABRICKS_HTTP_PATH=/sql/1.0/endpoints/seu_cluster_id
```

### Passo 4: Executar Scripts (Sem Provisionamento)

```powershell
# Pule o módulo de provisionamento e configuração do Azure
cd azure-databricks-integration

# Opção A: Execute apenas DDL e Ingestão
cd 05-orchestration
.\run-all.ps1 -SkipProvisioning -SkipConfig

# Opção B: Execute módulos específicos
cd ..\03-database-setup
# Upload manual dos SQLs via Databricks UI

cd ..\04-data-ingestion
pip install -r requirements.txt
python ingest-from-csv.py --file ..\..\Files\green_tripdata_2021-04.csv --table bronze.taxi_trips_raw
```

---

## 🛠️ Adaptação dos Scripts

### Alteração Necessária: `ingest-from-csv.py`

O Community Edition usa **Cluster** em vez de **SQL Warehouse**. Vou criar uma versão adaptada:

```python
# Detecta automaticamente o tipo de ambiente
import os
from databricks import sql

# Tenta usar SQL Warehouse primeiro (Azure Databricks)
http_path = os.getenv('DATABRICKS_HTTP_PATH')

# Se não tiver, usa Cluster ID (Community Edition)
if not http_path or http_path == '':
    cluster_id = os.getenv('DATABRICKS_CLUSTER_ID')
    if cluster_id:
        http_path = f'/sql/1.0/endpoints/{cluster_id}'
    else:
        raise ValueError("Configure DATABRICKS_HTTP_PATH ou DATABRICKS_CLUSTER_ID")

# Conexão funciona igual
connection = sql.connect(
    server_hostname=DATABRICKS_HOST,
    http_path=http_path,
    access_token=DATABRICKS_TOKEN
)
```

---

## 📋 Checklist: Azure vs Community Edition

### Para Azure Databricks (Seu código atual)
- [x] Azure subscription
- [x] Azure CLI instalado
- [x] Executar `.\run-all.ps1` completo
- [x] SQL Warehouse provisionado

### Para Databricks Community Edition (Alternativa grátis)
- [x] Conta criada em community.cloud.databricks.com
- [x] Personal Access Token gerado
- [x] Cluster ID copiado
- [x] Pular módulos 1 e 2
- [x] Executar apenas DDL e Ingestão

---

## ⚠️ Limitações do Community Edition

### O Que NÃO Funciona

❌ **Provisionamento automatizado** (Módulo 1)  
❌ **Jobs agendados** - Você precisa executar manualmente  
❌ **SQL Warehouses** - Apenas 1 cluster pequeno  
❌ **Unity Catalog** - Sem governança avançada  
❌ **Múltiplos clusters** - Apenas 1 cluster fixo  
❌ **Storage ilimitado** - Máximo 10GB DBFS  

### O Que Funciona Perfeitamente

✅ **Todos os scripts SQL** - Idêntico  
✅ **Ingestão de dados** - Python funciona igual  
✅ **Arquitetura Medallion** - Bronze/Silver/Gold  
✅ **Notebooks** - Para explorar dados  
✅ **Delta Lake** - Suportado  
✅ **Aprendizado** - Perfeito para testes!  

---

## 🎯 Recomendação

### Use Community Edition para:
- ✅ **Aprender** Databricks
- ✅ **Testar** seus scripts
- ✅ **Desenvolver** pipelines
- ✅ **Prototipar** soluções

### Use Azure Databricks para:
- ✅ **Produção** com dados reais
- ✅ **Escala** (grandes volumes)
- ✅ **Automação** (jobs agendados)
- ✅ **Integração** com Azure (Storage, Key Vault, etc)

---

## 🚀 Quick Start: Community Edition

```powershell
# 1. Configure .env
echo "DATABRICKS_HOST=community.cloud.databricks.com" > .env
echo "DATABRICKS_TOKEN=dapi_seu_token" >> .env
echo "DATABRICKS_CLUSTER_ID=seu_cluster_id" >> .env

# 2. Instale dependências
cd azure-databricks-integration/04-data-ingestion
pip install -r requirements.txt

# 3. Execute SQL manualmente no Databricks UI
# - Copie conteúdo de create-schemas.sql
# - Copie conteúdo de create-tables.sql
# - Execute no SQL Editor

# 4. Ingira dados
python ingest-from-csv.py \
  --file ..\..\Files\green_tripdata_2021-04.csv \
  --table bronze.taxi_trips_raw
```

---

## 💡 Dica: Workflow Híbrido

**Melhor estratégia:**

1. **Desenvolva** no Community Edition (grátis)
2. **Teste** seus scripts e queries
3. **Valide** a arquitetura Medallion
4. **Migre** para Azure Databricks quando:
   - Precisar de mais recursos
   - Quiser automatizar (jobs)
   - For para produção

**Os scripts funcionam em ambos sem alteração!** 🎉

---

## 🔧 Criando Versão Adaptada

Vou criar scripts alternativos para Community Edition...
