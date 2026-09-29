# ⚡ Guia Rápido: Testar no Community Edition

**Tempo:** 10 minutos  
**Custo:** R$ 0,00 (100% grátis)

---

## 🎯 Objetivo

Testar os scripts no **Databricks Community Edition** antes de usar Azure Databricks.

---

## 📝 Passo a Passo

### 1. Criar Conta (2 minutos)

1. Acesse: https://community.cloud.databricks.com/
2. Clique em **"Sign Up"**
3. Use sua **conta Google**
4. Confirme o email

✅ Pronto! Você já tem um workspace Databricks grátis.

---

### 2. Obter Credenciais (3 minutos)

#### 2.1 Personal Access Token

1. Após login, clique no **ícone do usuário** (canto superior direito)
2. **User Settings** → **Developer**
3. **Access Tokens** → **Generate New Token**
4. Configure:
   - **Comment:** "Data Migration Test"
   - **Lifetime:** 90 dias
5. Clique em **"Generate"**
6. **COPIE O TOKEN IMEDIATAMENTE** (aparece apenas UMA vez!)

#### 2.2 Cluster ID

1. No menu lateral, clique em **"Compute"**
2. Você verá um cluster (geralmente "Community Cluster")
3. Clique no cluster
4. Na URL, copie o ID: `https://community.cloud.databricks.com/#setting/clusters/XXXX-XXXXXX-XXXXXXXX/configuration`
5. O Cluster ID é: `XXXX-XXXXXX-XXXXXXXX`

---

### 3. Configurar Ambiente Local (2 minutos)

#### 3.1 Crie arquivo `.env`

Na raiz do projeto, crie o arquivo `.env`:

```env
# Databricks Community Edition
DATABRICKS_HOST=community.cloud.databricks.com
DATABRICKS_TOKEN=dapi_seu_token_copiado_aqui
DATABRICKS_CLUSTER_ID=seu_cluster_id_aqui
```

#### 3.2 Instale Dependências Python

```powershell
cd azure-databricks-integration/04-data-ingestion
pip install -r requirements.txt
```

---

### 4. Criar Tabelas (3 minutos)

**Opção A: Manual (mais fácil para Community Edition)**

1. Acesse: https://community.cloud.databricks.com/
2. Vá em **SQL** (menu lateral) ou **Workspace**
3. Crie um **novo SQL Notebook**
4. Copie e cole o conteúdo de:
   - `03-database-setup/create-schemas.sql`
   - `03-database-setup/create-tables.sql`
5. Execute os comandos (Shift + Enter ou botão "Run")

**Opção B: Via Script (se tiver SQL Warehouse configurado)**

```powershell
cd azure-databricks-integration/04-data-ingestion
python execute-sql-via-api.py
```

---

### 5. Ingerir Dados (2 minutos)

```powershell
cd azure-databricks-integration/04-data-ingestion

# Use o script UNIVERSAL (detecta automaticamente o ambiente)
python ingest-from-csv-universal.py \
  --file ..\..\Files\green_tripdata_2021-04.csv \
  --table bronze.taxi_trips_raw \
  --mode append
```

✅ Pronto! Seus dados estão no Databricks!

---

## 🎉 Verificar Resultados

### No SQL Editor

1. Vá em **SQL** → **SQL Editor**
2. Execute:

```sql
-- Ver schemas criados
SHOW SCHEMAS;

-- Ver tabelas
SHOW TABLES IN bronze;

-- Contar registros
SELECT COUNT(*) FROM bronze.taxi_trips_raw;

-- Ver primeiras linhas
SELECT * FROM bronze.taxi_trips_raw LIMIT 10;
```

### Em Notebook

1. Crie um **novo Notebook** (Python ou SQL)
2. Execute:

```python
# Python
df = spark.table("bronze.taxi_trips_raw")
display(df.limit(10))
```

ou

```sql
-- SQL
SELECT * FROM bronze.taxi_trips_raw LIMIT 10;
```

---

## 🔄 Migrar para Azure Databricks (Quando Quiser)

Quando precisar de mais recursos ou quiser automatizar:

### Passo 1: Altere o `.env`

```env
# Mude de Community para Azure
DATABRICKS_HOST=adb-xxxxx.azuredatabricks.net  # Seu workspace Azure
DATABRICKS_TOKEN=dapi_novo_token_azure
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx  # SQL Warehouse
```

### Passo 2: Execute os Mesmos Scripts

```powershell
# Os scripts funcionam EXATAMENTE IGUAL!
python ingest-from-csv-universal.py \
  --file ..\..\Files\green_tripdata_2021-04.csv \
  --table bronze.taxi_trips_raw
```

**🎯 Zero alterações no código!** Os scripts detectam automaticamente o ambiente.

---

## 📊 Comparação de Workflow

### Community Edition (Grátis)
```
1. Criar conta (2 min)
2. Gerar token (1 min)
3. Criar .env (1 min)
4. Criar tabelas manualmente no SQL Editor (3 min)
5. Ingerir dados com Python (2 min)
```
**Total:** ~10 minutos | **Custo:** R$ 0

### Azure Databricks (Pago)
```
1. Executar run-all.ps1 (15-20 min)
   - Provisiona workspace
   - Configura tudo automaticamente
   - Cria tabelas
   - Ingere dados
```
**Total:** ~20 minutos | **Custo:** ~R$ 50-100/mês (variável)

---

## ⚠️ Diferenças Importantes

| Aspecto | Community Edition | Azure Databricks |
|---------|-------------------|------------------|
| **Setup** | Manual (10 min) | Automatizado (20 min) |
| **Custo** | Grátis | Pago |
| **Limite de Dados** | 10GB | Ilimitado |
| **Compute** | 1 cluster pequeno | Múltiplos clusters |
| **Jobs Agendados** | ❌ Não | ✅ Sim |
| **SQL Warehouses** | ❌ Não | ✅ Sim |
| **Scripts Python** | ✅ Funciona | ✅ Funciona |
| **Scripts SQL** | ✅ Funciona | ✅ Funciona |

---

## 💡 Dica Pro

**Workflow Recomendado:**

1. **Desenvolva** no Community Edition (grátis)
   - Teste queries SQL
   - Valide transformações
   - Ajuste scripts Python

2. **Migre** para Azure quando:
   - Tiver dados > 10GB
   - Precisar de automação (jobs)
   - Quiser integrar com Azure Storage/Key Vault
   - For para produção

3. **Use o mesmo código** em ambos!
   - Apenas mude o `.env`
   - Scripts detectam automaticamente o ambiente

---

## 🆘 Troubleshooting Rápido

### Erro: "Cluster not found"
- Verifique se o cluster está **iniciado** (clique em "Start" no Compute)

### Erro: "Authentication failed"
- Gere um novo token (pode ter expirado)
- Verifique se copiou o token completo

### Erro: "Table not found"
- Execute os SQLs de criação de tabelas primeiro no SQL Editor

### Erro: "Module not found"
- Execute: `pip install -r requirements.txt`

---

## 📚 Próximos Passos

Após testar no Community Edition:

1. ✅ Validar que os scripts funcionam
2. ✅ Ajustar para seus dados específicos
3. ✅ Criar notebooks de análise
4. ✅ Decidir se precisa migrar para Azure (produção)

---

**🎉 Parabéns! Você está rodando Databricks gratuitamente!**

*Quando precisar escalar, basta mudar 3 linhas no `.env` e rodar no Azure.* 🚀
