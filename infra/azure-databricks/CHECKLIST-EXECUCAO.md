# Checklist de Execucao - Azure Databricks Integration

## Pre-requisitos
- [x] Arquivo .env configurado
- [x] DATABRICKS_HOST: adb-7405607395070159.19.azuredatabricks.net
- [x] DATABRICKS_TOKEN: configurado
- [x] DATABRICKS_HTTP_PATH: /sql/1.0/warehouses/6e43216f1e93cb7c
- [x] SQL Warehouse: Criado e operacional

---

## Passo 1: Instalar Dependencias Python
```powershell
cd azure-databricks-integration\04-data-ingestion
pip install -r requirements.txt
```
Status: [ ] Concluido

---

## Passo 2: Criar Schemas e Tabelas
```powershell
cd azure-databricks-integration\03-database-setup
.\execute-ddl.ps1
```
Status: [ ] Concluido

---

## Passo 3: Ingerir Dados CSV
```powershell
cd azure-databricks-integration\04-data-ingestion

# Arquivo 1: Abril 2021
python ingest-from-csv-universal.py --file "..\..\data-engineer-exec-agent\Files\green_tripdata_2021-04.csv" --table bronze.taxi_trips_raw

# Arquivo 2: Maio 2021
python ingest-from-csv-universal.py --file "..\..\data-engineer-exec-agent\Files\green_tripdata_2021-05.csv" --table bronze.taxi_trips_raw

# Arquivo 3: Junho 2021
python ingest-from-csv-universal.py --file "..\..\data-engineer-exec-agent\Files\green_tripdata_2021-06.csv" --table bronze.taxi_trips_raw
```
Status: [ ] Concluido

---

## Passo 4: Ingerir Dados JSON (Tabelas de Referencia)
```powershell
# Payment Types
python ingest-from-json.py --file "..\..\data-engineer-exec-agent\Files\payment_type_array.json" --table reference.payment_types

# Rate Codes
python ingest-from-json.py --file "..\..\data-engineer-exec-agent\Files\rate_code.json" --table reference.rate_codes
```
Status: [ ] Concluido

---

## Passo 5: Verificar Dados Ingeridos
```powershell
python execute-sql-via-api.py --query "SELECT COUNT(*) as total FROM bronze.taxi_trips_raw"
```
Status: [ ] Concluido

---

## ALTERNATIVA: Executar Tudo de Uma Vez

```powershell
cd azure-databricks-integration\05-orchestration
.\run-all.ps1 -SkipProvisioning
```

---

## Resumo dos Scripts

| Etapa | Script | Funcao |
|-------|--------|--------|
| 1 | run-all.ps1 | Orquestrador completo |
| 2 | run-modular.ps1 | Orquestrador modular |
| 3 | execute-ddl.ps1 | Executa DDL (schemas/tabelas) |
| 4 | ingest-from-csv-universal.py | Ingere CSV (Azure + Community) |
| 5 | ingest-from-json.py | Ingere JSON |
| 6 | ingest-from-api.py | Ingere de API REST |
| 7 | execute-sql-via-api.py | Executa queries SQL |
| 8 | create-sql-warehouse.ps1 | Cria SQL Warehouse |
| 9 | setup-databricks-cli.ps1 | Configura CLI |
