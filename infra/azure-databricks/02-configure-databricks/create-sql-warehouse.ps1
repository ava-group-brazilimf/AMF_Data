<#
.SYNOPSIS
    Cria um SQL Warehouse no Azure Databricks via REST API

.DESCRIPTION
    Este script cria automaticamente um SQL Warehouse no seu workspace
    Azure Databricks usando a REST API oficial.

.PARAMETER Name
    Nome do SQL Warehouse (default: sql-warehouse-data-migration)

.PARAMETER ClusterSize
    Tamanho do cluster: 2X-Small, X-Small, Small, Medium, Large, X-Large, 2X-Large, 3X-Large, 4X-Large

.PARAMETER AutoStopMinutes
    Minutos de inatividade antes de auto-stop (default: 15)

.PARAMETER EnableServerless
    Se habilitado, usa Serverless SQL Warehouse

.EXAMPLE
    .\create-sql-warehouse.ps1

.EXAMPLE
    .\create-sql-warehouse.ps1 -Name "meu-warehouse" -ClusterSize "Small"
#>

param(
    [string]$Name = "sql-warehouse-data-migration",
    [ValidateSet("2X-Small", "X-Small", "Small", "Medium", "Large", "X-Large", "2X-Large", "3X-Large", "4X-Large")]
    [string]$ClusterSize = "X-Small",
    [int]$AutoStopMinutes = 15,
    [switch]$EnableServerless,
    [string]$EnvFile = "../.env"
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "[>] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERRO] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Gray
}

function Load-EnvFile {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        $altPath = Join-Path $PSScriptRoot "../.env"
        if (Test-Path $altPath) {
            $Path = $altPath
        } else {
            $azurePath = Join-Path $PSScriptRoot "../.env.azure"
            if (Test-Path $azurePath) {
                $Path = $azurePath
            } else {
                return $null
            }
        }
    }
    
    $envVars = @{}
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $eqIndex = $line.IndexOf("=")
            if ($eqIndex -gt 0) {
                $key = $line.Substring(0, $eqIndex).Trim()
                $value = $line.Substring($eqIndex + 1).Trim()
                $envVars.$key = $value
            }
        }
    }
    return $envVars
}

Write-Header "Azure Databricks - Criar SQL Warehouse"

Write-Step "Carregando configuracoes do arquivo .env..."

$envVars = Load-EnvFile -Path $EnvFile

if (-not $envVars -or -not $envVars.DATABRICKS_HOST -or -not $envVars.DATABRICKS_TOKEN) {
    Write-ErrorMsg "Arquivo .env nao encontrado ou incompleto!"
    Write-Host ""
    Write-Host "Para criar o SQL Warehouse, voce precisa configurar:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Copie o arquivo .env.azure.example para .env:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.azure.example .env" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Edite o arquivo .env com:" -ForegroundColor Yellow
    Write-Host "   - DATABRICKS_HOST (URL do workspace)" -ForegroundColor White
    Write-Host "   - DATABRICKS_TOKEN (Personal Access Token)" -ForegroundColor White
    Write-Host ""
    exit 1
}

$databricksHost = $envVars.DATABRICKS_HOST
$databricksToken = $envVars.DATABRICKS_TOKEN

$httpsPattern = "^https?://"
if ($databricksHost -match $httpsPattern) {
    $databricksHost = $databricksHost -replace $httpsPattern, ""
}

Write-Success "Configuracoes carregadas"
Write-Info "Workspace: $databricksHost"

Write-Step "Verificando conexao com Databricks..."

$headers = @{
    "Authorization" = "Bearer $databricksToken"
    "Content-Type" = "application/json"
}

try {
    $testUrl = "https://$databricksHost/api/2.0/clusters/spark-versions"
    $response = Invoke-RestMethod -Uri $testUrl -Headers $headers -Method Get
    Write-Success "Conexao com Databricks estabelecida!"
} catch {
    Write-ErrorMsg "Falha na conexao com Databricks!"
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique se:" -ForegroundColor Yellow
    Write-Host "  - O DATABRICKS_HOST esta correto" -ForegroundColor Yellow
    Write-Host "  - O DATABRICKS_TOKEN e valido e nao expirou" -ForegroundColor Yellow
    exit 1
}

Write-Step "Verificando SQL Warehouses existentes..."

$warehousesUrl = "https://$databricksHost/api/2.0/sql/warehouses"

try {
    $existingWarehouses = Invoke-RestMethod -Uri $warehousesUrl -Headers $headers -Method Get
    
    if ($existingWarehouses.warehouses) {
        Write-Info "SQL Warehouses encontrados:"
        foreach ($wh in $existingWarehouses.warehouses) {
            $status = $wh.state
            $statusColor = switch ($status) {
                "RUNNING" { "Green" }
                "STOPPED" { "Yellow" }
                "STARTING" { "Cyan" }
                "STOPPING" { "Yellow" }
                default { "Gray" }
            }
            Write-Host "  - $($wh.name) [ID: $($wh.id)] - " -NoNewline
            Write-Host $status -ForegroundColor $statusColor
        }
        
        $existing = $existingWarehouses.warehouses | Where-Object { $_.name -eq $Name }
        if ($existing) {
            Write-Host ""
            Write-Host "Ja existe um SQL Warehouse com o nome '$Name'" -ForegroundColor Yellow
            Write-Host "ID: $($existing.id)" -ForegroundColor Yellow
            Write-Host "HTTP Path: /sql/1.0/warehouses/$($existing.id)" -ForegroundColor Yellow
            
            $continue = Read-Host "Deseja criar um novo mesmo assim? (s/N)"
            if ($continue -ne "s" -and $continue -ne "S") {
                Write-Info "Operacao cancelada."
                exit 0
            }
        }
    } else {
        Write-Info "Nenhum SQL Warehouse encontrado. Sera criado o primeiro!"
    }
} catch {
    Write-Info "Nao foi possivel listar warehouses existentes. Continuando..."
}

Write-Step "Criando SQL Warehouse '$Name'..."

$warehouseConfig = @{
    name = $Name
    cluster_size = $ClusterSize
    auto_stop_mins = $AutoStopMinutes
    min_num_clusters = 1
    max_num_clusters = 1
    enable_photon = $true
    spot_instance_policy = "COST_OPTIMIZED"
    warehouse_type = if ($EnableServerless) { "PRO" } else { "CLASSIC" }
    enable_serverless_compute = $EnableServerless.IsPresent
    tags = @{
        custom_tags = @(
            @{ key = "Project"; value = "Data-Migration" }
            @{ key = "CreatedBy"; value = "PowerShell-Script" }
            @{ key = "CreatedAt"; value = (Get-Date -Format "yyyy-MM-dd") }
        )
    }
}

$body = $warehouseConfig | ConvertTo-Json -Depth 10

Write-Info "Configuracao:"
Write-Host "  - Nome: $Name" -ForegroundColor Gray
Write-Host "  - Tamanho: $ClusterSize" -ForegroundColor Gray
Write-Host "  - Auto-stop: $AutoStopMinutes minutos" -ForegroundColor Gray
Write-Host "  - Serverless: $($EnableServerless.IsPresent)" -ForegroundColor Gray
Write-Host "  - Photon: Habilitado" -ForegroundColor Gray

try {
    $createUrl = "https://$databricksHost/api/2.0/sql/warehouses"
    $result = Invoke-RestMethod -Uri $createUrl -Headers $headers -Method Post -Body $body
    
    $warehouseId = $result.id
    
    Write-Success "SQL Warehouse criado com sucesso!"
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  INFORMACOES DO SQL WAREHOUSE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ID:        $warehouseId" -ForegroundColor White
    Write-Host "  Nome:      $Name" -ForegroundColor White
    Write-Host "  HTTP Path: /sql/1.0/warehouses/$warehouseId" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green
    
    Write-Step "Atualizando arquivo .env..."
    
    $envPath = Join-Path $PSScriptRoot "../.env"
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath -Raw
        
        $httpPathPattern = "DATABRICKS_HTTP_PATH=.*"
        if ($envContent -match "DATABRICKS_HTTP_PATH=") {
            $envContent = $envContent -replace $httpPathPattern, "DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/$warehouseId"
        }
        
        $warehouseIdPattern = "DATABRICKS_SQL_WAREHOUSE_ID=.*"
        if ($envContent -match "DATABRICKS_SQL_WAREHOUSE_ID=") {
            $envContent = $envContent -replace $warehouseIdPattern, "DATABRICKS_SQL_WAREHOUSE_ID=$warehouseId"
        }
        
        Set-Content -Path $envPath -Value $envContent
        Write-Success "Arquivo .env atualizado com as novas configuracoes!"
    } else {
        Write-Info "Arquivo .env nao encontrado para atualizacao automatica."
        Write-Host ""
        Write-Host "Adicione manualmente ao seu .env:" -ForegroundColor Yellow
        Write-Host "DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/$warehouseId" -ForegroundColor White
        Write-Host "DATABRICKS_SQL_WAREHOUSE_ID=$warehouseId" -ForegroundColor White
    }
    
    Write-Step "Aguardando inicializacao do SQL Warehouse..."
    Write-Info "Isso pode levar alguns minutos..."
    
    $maxWaitTime = 300
    $checkInterval = 10
    $elapsed = 0
    
    while ($elapsed -lt $maxWaitTime) {
        Start-Sleep -Seconds $checkInterval
        $elapsed += $checkInterval
        
        try {
            $statusUrl = "https://$databricksHost/api/2.0/sql/warehouses/$warehouseId"
            $statusResult = Invoke-RestMethod -Uri $statusUrl -Headers $headers -Method Get
            
            $state = $statusResult.state
            
            if ($state -eq "RUNNING") {
                Write-Host ""
                Write-Success "SQL Warehouse esta RUNNING e pronto para uso!"
                break
            } elseif ($state -eq "STOPPED") {
                Write-Host ""
                Write-Info "SQL Warehouse esta STOPPED (sera iniciado na primeira query)"
                break
            } else {
                Write-Host "`r[>] Status: $state... ($elapsed segundos)" -NoNewline -ForegroundColor Yellow
            }
        } catch {
            Write-Host "`r[>] Verificando status... ($elapsed segundos)" -NoNewline -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host ""
    Write-Header "SQL Warehouse Criado com Sucesso!"
    
    Write-Host "Proximos passos:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Para conectar via Python:" -ForegroundColor Yellow
    Write-Host "   from databricks import sql" -ForegroundColor Gray
    Write-Host "   connection = sql.connect(" -ForegroundColor Gray
    Write-Host "       server_hostname=`"$databricksHost`"," -ForegroundColor Gray
    Write-Host "       http_path=`"/sql/1.0/warehouses/$warehouseId`"," -ForegroundColor Gray
    Write-Host "       access_token=`"<seu-token>`"" -ForegroundColor Gray
    Write-Host "   )" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "2. Para acessar pelo portal:" -ForegroundColor Yellow
    Write-Host "   https://$databricksHost/sql/warehouses/$warehouseId" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "3. Para executar queries:" -ForegroundColor Yellow
    Write-Host "   https://$databricksHost/sql/editor" -ForegroundColor Gray
    
} catch {
    Write-ErrorMsg "Falha ao criar SQL Warehouse!"
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        try {
            $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Detalhes: $($errorBody.message)" -ForegroundColor Red
        } catch {
            Write-Host "Detalhes: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
    
    exit 1
}

Write-Host ""
Write-Success "Script concluido!"
