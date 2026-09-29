# insert-warehouse.ps1 - Configura SQL Warehouse e Insere Dados
# Este script cria/configura um SQL Warehouse e depois executa a ingestao de dados

param(
    [string]$WarehouseName = "warehousePadrao",
    [ValidateSet("2X-Small", "X-Small", "Small", "Medium", "Large")]
    [string]$WarehouseSize = "2X-Small",
    [int]$AutoStopMinutes = 10,
    [switch]$SkipWarehouse,
    [switch]$SkipInsertion,
    [string]$Table = "bronze.taxi_trips_raw"
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

# ============================================================================
# FUNCOES AUXILIARES
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "> $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[X] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Gray
}

function Load-EnvFile {
    $envPath = Join-Path $ScriptRoot "..\.env"
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^([^#=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
        return $envPath
    }
    return $null
}

function Update-EnvFile {
    param(
        [string]$EnvPath,
        [string]$Key,
        [string]$Value
    )
    
    $content = Get-Content $EnvPath
    $updated = $false
    
    $newContent = $content | ForEach-Object {
        if ($_ -match "^$Key=") {
            $updated = $true
            "$Key=$Value"
        } else {
            $_
        }
    }
    
    if (-not $updated) {
        $newContent += "$Key=$Value"
    }
    
    $newContent | Set-Content $EnvPath -Encoding UTF8
}

# ============================================================================
# BANNER
# ============================================================================

Clear-Host

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "     DATABRICKS WAREHOUSE + DATA INSERTION" -ForegroundColor Cyan
Write-Host ""
Write-Host "     Avanade Core - Data Engineering" -ForegroundColor Cyan
Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script ira:" -ForegroundColor Gray
Write-Host "  1. Criar/configurar um SQL Warehouse no Databricks" -ForegroundColor Gray
Write-Host "  2. Criar schemas e tabelas (DDL)" -ForegroundColor Gray
Write-Host "  3. Ingerir dados da pasta Files" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# CARREGAR CONFIGURACOES
# ============================================================================

Write-Step "Carregando configuracoes..."

$envPath = Load-EnvFile

if (-not $envPath) {
    Write-ErrorMsg "Arquivo .env nao encontrado!"
    Write-Host ""
    Write-Host "Crie o arquivo .env com as credenciais:" -ForegroundColor Yellow
    Write-Host "  DATABRICKS_HOST=https://adb-xxx.azuredatabricks.net" -ForegroundColor Gray
    Write-Host "  DATABRICKS_TOKEN=dapi..." -ForegroundColor Gray
    exit 1
}

if (-not $env:DATABRICKS_HOST -or -not $env:DATABRICKS_TOKEN) {
    Write-ErrorMsg "DATABRICKS_HOST e DATABRICKS_TOKEN sao obrigatorios no .env!"
    exit 1
}

# Normaliza host (remove https:// para API calls)
$databricksHost = $env:DATABRICKS_HOST -replace "^https?://", ""
$databricksToken = $env:DATABRICKS_TOKEN

Write-Success "Configuracoes carregadas"
Write-Info "Host: $databricksHost"

# ============================================================================
# ETAPA 1: CRIAR/CONFIGURAR SQL WAREHOUSE
# ============================================================================

if (-not $SkipWarehouse) {
    Write-Header "Etapa 1: Configurar SQL Warehouse"
    
    $headers = @{
        "Authorization" = "Bearer $databricksToken"
        "Content-Type" = "application/json"
    }
    
    # Verificar conexao
    Write-Step "Verificando conexao com Databricks..."
    
    try {
        $testUrl = "https://$databricksHost/api/2.0/clusters/spark-versions"
        $response = Invoke-RestMethod -Uri $testUrl -Headers $headers -Method Get
        Write-Success "Conexao estabelecida!"
    } catch {
        Write-ErrorMsg "Falha na conexao: $_"
        exit 1
    }
    
    # Listar warehouses existentes
    Write-Step "Verificando SQL Warehouses existentes..."
    
    $warehousesUrl = "https://$databricksHost/api/2.0/sql/warehouses"
    
    try {
        $existingWarehouses = Invoke-RestMethod -Uri $warehousesUrl -Headers $headers -Method Get
        
        $existingWarehouse = $null
        
        if ($existingWarehouses.warehouses) {
            Write-Info "SQL Warehouses encontrados:"
            
            foreach ($wh in $existingWarehouses.warehouses) {
                $statusColor = switch ($wh.state) {
                    "RUNNING" { "Green" }
                    "STOPPED" { "Yellow" }
                    "STARTING" { "Cyan" }
                    default { "Gray" }
                }
                Write-Host "  - $($wh.name) [$($wh.state)]" -ForegroundColor $statusColor
                
                if ($wh.name -eq $WarehouseName) {
                    $existingWarehouse = $wh
                }
            }
            Write-Host ""
        }
        
        if ($existingWarehouse) {
            Write-Info "Warehouse '$WarehouseName' ja existe (ID: $($existingWarehouse.id))"
            
            # Atualizar .env com o ID do warehouse
            $httpPath = "/sql/1.0/warehouses/$($existingWarehouse.id)"
            Update-EnvFile -EnvPath $envPath -Key "DATABRICKS_HTTP_PATH" -Value $httpPath
            Update-EnvFile -EnvPath $envPath -Key "DATABRICKS_SQL_WAREHOUSE_ID" -Value $existingWarehouse.id
            
            [Environment]::SetEnvironmentVariable("DATABRICKS_HTTP_PATH", $httpPath, "Process")
            [Environment]::SetEnvironmentVariable("DATABRICKS_SQL_WAREHOUSE_ID", $existingWarehouse.id, "Process")
            
            # Iniciar warehouse se estiver parado
            if ($existingWarehouse.state -eq "STOPPED") {
                Write-Step "Iniciando warehouse..."
                
                $startUrl = "https://$databricksHost/api/2.0/sql/warehouses/$($existingWarehouse.id)/start"
                Invoke-RestMethod -Uri $startUrl -Headers $headers -Method Post | Out-Null
                
                Write-Info "Aguardando warehouse iniciar (sem limite de tempo)..."
                Write-Info "Pressione Ctrl+C para cancelar"
                
                $waited = 0
                
                do {
                    Start-Sleep -Seconds 10
                    $waited += 10
                    
                    $statusUrl = "https://$databricksHost/api/2.0/sql/warehouses/$($existingWarehouse.id)"
                    $status = Invoke-RestMethod -Uri $statusUrl -Headers $headers -Method Get
                    
                    $minutes = [math]::Floor($waited / 60)
                    $seconds = $waited % 60
                    Write-Host "  Status: $($status.state) (${minutes}m ${seconds}s)" -ForegroundColor Gray
                    
                } while ($status.state -ne "RUNNING")
                
                Write-Success "Warehouse iniciado!"
            }
            
            Write-Success "Warehouse configurado: $($existingWarehouse.id)"
            
        } else {
            # Criar novo warehouse
            Write-Step "Criando novo SQL Warehouse '$WarehouseName' (Serverless)..."
            
            $warehouseConfig = @{
                name = $WarehouseName
                cluster_size = $WarehouseSize
                min_num_clusters = 1
                max_num_clusters = 1
                auto_stop_mins = $AutoStopMinutes
                enable_serverless_compute = $true
                channel = @{ name = "CHANNEL_NAME_CURRENT" }
            } | ConvertTo-Json -Depth 10
            
            try {
                $newWarehouse = Invoke-RestMethod -Uri $warehousesUrl -Headers $headers -Method Post -Body $warehouseConfig
                
                Write-Success "Warehouse criado com sucesso!"
                Write-Info "ID: $($newWarehouse.id)"
                Write-Info "HTTP Path: /sql/1.0/warehouses/$($newWarehouse.id)"
                
                # Atualizar .env
                $httpPath = "/sql/1.0/warehouses/$($newWarehouse.id)"
                Update-EnvFile -EnvPath $envPath -Key "DATABRICKS_HTTP_PATH" -Value $httpPath
                Update-EnvFile -EnvPath $envPath -Key "DATABRICKS_SQL_WAREHOUSE_ID" -Value $newWarehouse.id
                
                [Environment]::SetEnvironmentVariable("DATABRICKS_HTTP_PATH", $httpPath, "Process")
                [Environment]::SetEnvironmentVariable("DATABRICKS_SQL_WAREHOUSE_ID", $newWarehouse.id, "Process")
                
                # Aguardar warehouse iniciar
                Write-Info "Aguardando warehouse iniciar (sem limite de tempo)..."
                Write-Info "Pressione Ctrl+C para cancelar"
                
                $waited = 0
                
                do {
                    Start-Sleep -Seconds 10
                    $waited += 10
                    
                    $statusUrl = "https://$databricksHost/api/2.0/sql/warehouses/$($newWarehouse.id)"
                    $status = Invoke-RestMethod -Uri $statusUrl -Headers $headers -Method Get
                    
                    $minutes = [math]::Floor($waited / 60)
                    $seconds = $waited % 60
                    Write-Host "  Status: $($status.state) (${minutes}m ${seconds}s)" -ForegroundColor Gray
                    
                } while ($status.state -ne "RUNNING")
                
                Write-Success "Warehouse pronto para uso!"
                
            } catch {
                Write-ErrorMsg "Falha ao criar warehouse: $_"
                exit 1
            }
        }
        
    } catch {
        Write-ErrorMsg "Erro ao listar warehouses: $_"
        exit 1
    }
    
} else {
    Write-Step "Pulando configuracao de warehouse"
}

# ============================================================================
# ETAPA 2: CRIAR SCHEMAS E TABELAS (DDL)
# ============================================================================

Write-Header "Etapa 2: Criar Schemas e Tabelas"

$ddlPath = Join-Path $ScriptRoot "..\04-data-ingestion"

Push-Location $ddlPath

try {
    Write-Step "Instalando dependencias Python..."
    pip install -q -r requirements.txt 2>$null
    
    Write-Step "Executando DDL via API..."
    python execute-sql-via-api.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Schemas e tabelas criados!"
    } else {
        Write-ErrorMsg "Alguns comandos DDL falharam (nao-fatal)"
    }
} catch {
    Write-ErrorMsg "Erro ao executar DDL: $_"
}

Pop-Location

# ============================================================================
# ETAPA 3: INGESTAO DE DADOS
# ============================================================================

if (-not $SkipInsertion) {
    Write-Header "Etapa 3: Ingestao de Dados"
    
    $filesPath = Join-Path $ScriptRoot "..\Files"
    $csvFiles = Get-ChildItem "$filesPath\*.csv" -ErrorAction SilentlyContinue
    
    if ($csvFiles) {
        Write-Info "Encontrados $($csvFiles.Count) arquivo(s) CSV"
        
        Push-Location $ddlPath
        
        foreach ($csvFile in $csvFiles) {
            Write-Step "Ingerindo: $($csvFile.Name)"
            
            $startTime = Get-Date
            
            python ingest-from-csv.py --file $csvFile.FullName --table $Table --mode append
            
            $duration = ((Get-Date) - $startTime).TotalSeconds
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Concluido: $($csvFile.Name) ($([math]::Round($duration, 1))s)"
            } else {
                Write-ErrorMsg "Falha: $($csvFile.Name)"
            }
        }
        
        Pop-Location
        
    } else {
        Write-ErrorMsg "Nenhum arquivo CSV encontrado em $filesPath"
        Write-Host ""
        Write-Host "Coloque arquivos CSV na pasta Files e execute novamente." -ForegroundColor Yellow
        Write-Host "Ou execute: .\insertion.ps1 para a jornada de conexao SQL" -ForegroundColor Yellow
    }
} else {
    Write-Step "Pulando ingestao de dados"
}

# ============================================================================
# RESUMO FINAL
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "  Pipeline Concluido!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuracao salva no .env:" -ForegroundColor Cyan
Write-Host "  DATABRICKS_HOST = $env:DATABRICKS_HOST" -ForegroundColor Gray
Write-Host "  DATABRICKS_HTTP_PATH = $env:DATABRICKS_HTTP_PATH" -ForegroundColor Gray
Write-Host "  DATABRICKS_SQL_WAREHOUSE_ID = $env:DATABRICKS_SQL_WAREHOUSE_ID" -ForegroundColor Gray
Write-Host ""
Write-Host "Acesse o Databricks:" -ForegroundColor Cyan
Write-Host "  $env:DATABRICKS_HOST" -ForegroundColor Gray
Write-Host ""
Write-Host "Queries de validacao:" -ForegroundColor Cyan
Write-Host "  SHOW SCHEMAS;" -ForegroundColor Gray
Write-Host "  SELECT COUNT(*) FROM $Table;" -ForegroundColor Gray
Write-Host ""
