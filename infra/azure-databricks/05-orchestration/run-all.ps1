# run-all.ps1 - Orquestrador completo - Executa todo o pipeline Databricks
# Este script executa todas as etapas do pipeline

param(
    [switch]$SkipProvisioning,
    [switch]$SkipConfig,
    [switch]$SkipDDL,
    [switch]$SkipIngestion,
    [switch]$IngestOnly,
    [string]$ConfigFile = "..\01-provision-azure\config.template.json"
)

$ErrorActionPreference = "Stop"

$global:ExecutionLog = @()
$global:StartTime = Get-Date

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

function Log-Step {
    param(
        [string]$Step,
        [string]$Status,
        [string]$Details
    )
    
    $global:ExecutionLog += [PSCustomObject]@{
        Step = $Step
        Status = $Status
        Details = $Details
        Timestamp = Get-Date
    }
}

function Execute-Module {
    param(
        [string]$ModuleName,
        [string]$ModulePath,
        [scriptblock]$ScriptBlock
    )
    
    Write-Header "MODULO: $ModuleName"
    
    $moduleStart = Get-Date
    
    try {
        & $ScriptBlock
        
        $duration = ((Get-Date) - $moduleStart).TotalSeconds
        Write-Success "$ModuleName concluido em $([math]::Round($duration, 2))s"
        Log-Step -Step $ModuleName -Status "SUCCESS" -Details "Duracao: $([math]::Round($duration, 2))s"
        
        return $true
    }
    catch {
        $duration = ((Get-Date) - $moduleStart).TotalSeconds
        Write-ErrorMsg "$ModuleName falhou: $_"
        Log-Step -Step $ModuleName -Status "FAILED" -Details $_.Exception.Message
        
        return $false
    }
}

# ============================================================================
# BANNER
# ============================================================================

Clear-Host

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "     AZURE DATABRICKS INTEGRATION - FULL PIPELINE" -ForegroundColor Cyan
Write-Host ""
Write-Host "          Avanade Core - Data Engineering" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Inicio da execucao: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "============================================================================" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# VALIDACOES INICIAIS
# ============================================================================

if ($IngestOnly) {
    Write-Step "Modo: Ingestao apenas"
    $SkipProvisioning = $true
    $SkipConfig = $true
    $SkipDDL = $true
}

# Carrega .env automaticamente no inicio
$envFile = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Step "Configuracoes carregadas do .env"
    
    # Auto-skip config e provisioning se credenciais existem
    if ($env:DATABRICKS_HOST -and $env:DATABRICKS_TOKEN) {
        if (-not $SkipProvisioning) {
            Write-Step "Workspace ja configurado - pulando provisionamento"
            $SkipProvisioning = $true
            Log-Step -Step "Provisionamento" -Status "SKIPPED" -Details "Workspace ja existe"
        }
        if (-not $SkipConfig) {
            Write-Success "Credenciais Databricks configuradas"
            $SkipConfig = $true
            Log-Step -Step "Credenciais" -Status "SKIPPED" -Details "Carregadas do .env"
        }
    }
}

# ============================================================================
# MODULO 1: PROVISIONAMENTO DO AZURE DATABRICKS
# ============================================================================

if (-not $SkipProvisioning) {
    $success = Execute-Module -ModuleName "Provisionamento Azure Databricks" -ModulePath "..\01-provision-azure" -ScriptBlock {
        
        Push-Location "..\01-provision-azure"
        
        try {
            if (-not (Test-Path "config.template.json")) {
                throw "Arquivo config.template.json nao encontrado!"
            }
            
            .\provision-databricks.ps1
            
            if ($LASTEXITCODE -ne 0) {
                throw "Provisionamento falhou com codigo: $LASTEXITCODE"
            }
        }
        finally {
            Pop-Location
        }
    }
    
    if (-not $success) {
        Write-ErrorMsg "Pipeline abortado: Provisionamento falhou"
        exit 1
    }
} else {
    Write-Step "Pulando provisionamento (workspace existente)"
    Log-Step -Step "Provisionamento" -Status "SKIPPED" -Details "Usar workspace existente"
}

# ============================================================================
# MODULO 2: VERIFICACAO DE CREDENCIAIS (.env)
# ============================================================================

if (-not $SkipConfig) {
    $success = Execute-Module -ModuleName "Verificacao de Credenciais" -ModulePath ".." -ScriptBlock {
        
        # Carrega .env
        $envFile = "..\.env"
        if (Test-Path $envFile) {
            Write-Step "Carregando configuracoes do .env..."
            
            Get-Content $envFile | ForEach-Object {
                if ($_ -match '^([^#=]+)=(.*)$') {
                    $key = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    [Environment]::SetEnvironmentVariable($key, $value, "Process")
                }
            }
            
            if ($env:DATABRICKS_HOST -and $env:DATABRICKS_TOKEN) {
                Write-Success "Credenciais carregadas do .env"
                Write-Host "  Host: $env:DATABRICKS_HOST" -ForegroundColor Gray
            } else {
                throw "DATABRICKS_HOST ou DATABRICKS_TOKEN nao encontrados no .env"
            }
        } else {
            throw "Arquivo .env nao encontrado! Crie o arquivo com as credenciais."
        }
    }
    
    if (-not $success) {
        Write-ErrorMsg "Pipeline abortado: Credenciais nao configuradas"
        exit 1
    }
} else {
    Write-Step "Pulando verificacao de credenciais"
    Log-Step -Step "Credenciais" -Status "SKIPPED" -Details "Ja configuradas"
}

# ============================================================================
# MODULO 3: CRIACAO DE SCHEMAS E TABELAS (DDL)
# ============================================================================

if (-not $SkipDDL) {
    $success = Execute-Module -ModuleName "Criacao de Schemas e Tabelas" -ModulePath "..\03-database-setup" -ScriptBlock {
        
        Push-Location "..\03-database-setup"
        
        try {
            Write-Step "Executando scripts DDL..."
            
            $pythonAvailable = Get-Command python -ErrorAction SilentlyContinue
            
            if ($pythonAvailable) {
                Write-Step "Instalando dependencias Python..."
                pip install -q -r ..\04-data-ingestion\requirements.txt
                
                if ($env:DATABRICKS_HOST -and $env:DATABRICKS_TOKEN) {
                    Write-Step "Executando DDL via Python API..."
                    python ..\04-data-ingestion\execute-sql-via-api.py
                    
                    if ($LASTEXITCODE -ne 0) {
                        throw "Execucao de DDL falhou"
                    }
                } else {
                    Write-Step "Fazendo upload dos scripts SQL para o workspace..."
                    .\execute-ddl.ps1
                    
                    Write-Host ""
                    Write-Host "ATENCAO: Scripts SQL foram carregados no workspace Databricks." -ForegroundColor Yellow
                    Write-Host "Voce precisara executa-los manualmente via SQL Editor." -ForegroundColor Yellow
                    Write-Host ""
                }
            } else {
                Write-Step "Python nao encontrado. Fazendo upload dos scripts..."
                .\execute-ddl.ps1
            }
        }
        finally {
            Pop-Location
        }
    }
    
    if (-not $success) {
        Write-ErrorMsg "Pipeline abortado: Criacao de tabelas falhou"
        exit 1
    }
} else {
    Write-Step "Pulando criacao de tabelas"
    Log-Step -Step "DDL" -Status "SKIPPED" -Details "Tabelas ja existem"
}

# ============================================================================
# MODULO 4: INGESTAO DE DADOS
# ============================================================================

if (-not $SkipIngestion) {
    $success = Execute-Module -ModuleName "Ingestao de Dados" -ModulePath "..\04-data-ingestion" -ScriptBlock {
        
        Push-Location "..\04-data-ingestion"
        
        try {
            Write-Step "Instalando dependencias Python..."
            pip install -q -r requirements.txt
            
            # Corrigido: caminho correto para Files
            $filesPath = Join-Path $PSScriptRoot "..\Files"
            $csvFiles = Get-ChildItem "$filesPath\*.csv" -ErrorAction SilentlyContinue
            
            if ($csvFiles) {
                Write-Step "Encontrados $($csvFiles.Count) arquivo(s) CSV para ingestao"
                
                foreach ($csvFile in $csvFiles) {
                    Write-Step "Ingerindo: $($csvFile.Name)"
                    
                    python ingest-from-csv.py --file $csvFile.FullName --table "bronze.taxi_trips_raw" --mode append
                    
                    if ($LASTEXITCODE -eq 0) {
                        Write-Success "Arquivo ingerido: $($csvFile.Name)"
                    } else {
                        Write-ErrorMsg "Falha ao ingerir: $($csvFile.Name)"
                    }
                }
            } else {
                Write-Step "Nenhum arquivo CSV encontrado em $filesPath"
                Write-Host "Voce pode ingerir dados manualmente:" -ForegroundColor Yellow
                Write-Host "  python ingest-from-csv.py --file <caminho> --table bronze.taxi_trips_raw" -ForegroundColor Gray
            }
            
            $jsonFiles = Get-ChildItem "$filesPath\*.json" -ErrorAction SilentlyContinue
            
            if ($jsonFiles) {
                Write-Step "Encontrados $($jsonFiles.Count) arquivo(s) JSON"
                
                $paymentTypeFile = $jsonFiles | Where-Object { $_.Name -like "*payment_type*" }
                
                if ($paymentTypeFile) {
                    Write-Step "Ingerindo payment types..."
                    python ingest-from-json.py --file $paymentTypeFile.FullName --table "reference.payment_types" --mode overwrite
                }
            }
        }
        finally {
            Pop-Location
        }
    }
    
    if (-not $success) {
        Write-ErrorMsg "Ingestao de dados falhou (nao-fatal)"
    }
} else {
    Write-Step "Pulando ingestao de dados"
    Log-Step -Step "Ingestao" -Status "SKIPPED" -Details "Dados serao ingeridos manualmente"
}

# ============================================================================
# RESUMO DA EXECUCAO
# ============================================================================

$totalDuration = ((Get-Date) - $global:StartTime).TotalSeconds

Write-Host ""
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "                        PIPELINE CONCLUIDO" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green

Write-Host ""
Write-Host "RESUMO DA EXECUCAO:" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

foreach ($logEntry in $global:ExecutionLog) {
    $statusColor = switch ($logEntry.Status) {
        "SUCCESS" { "Green" }
        "FAILED" { "Red" }
        "SKIPPED" { "Yellow" }
        default { "Gray" }
    }
    
    $statusIcon = switch ($logEntry.Status) {
        "SUCCESS" { "[OK]" }
        "FAILED" { "[X]" }
        "SKIPPED" { "[--]" }
        default { "[.]" }
    }
    
    Write-Host "$statusIcon $($logEntry.Step): " -NoNewline
    Write-Host $logEntry.Status -ForegroundColor $statusColor -NoNewline
    Write-Host " - $($logEntry.Details)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Tempo total de execucao: $([math]::Round($totalDuration, 2))s" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PROXIMOS PASSOS
# ============================================================================

Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------------" -ForegroundColor Cyan

$infoFile = "..\01-provision-azure\databricks-workspace-info.json"
if (Test-Path $infoFile) {
    $workspaceInfo = Get-Content $infoFile | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "1. Acesse seu Databricks workspace:" -ForegroundColor Yellow
    Write-Host "   $($workspaceInfo.workspaceUrl)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Verifique as tabelas criadas:" -ForegroundColor Yellow
    Write-Host "   - bronze.taxi_trips_raw" -ForegroundColor Gray
    Write-Host "   - silver.taxi_trips" -ForegroundColor Gray
    Write-Host "   - gold.daily_trips_summary" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Execute transformacoes Bronze -> Silver -> Gold" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "1. Configure variaveis de ambiente (se ainda nao fez):" -ForegroundColor Yellow
    Write-Host "   DATABRICKS_HOST=<workspace-url>" -ForegroundColor Gray
    Write-Host "   DATABRICKS_TOKEN=<token>" -ForegroundColor Gray
    Write-Host "   DATABRICKS_HTTP_PATH=<sql-warehouse-http-path>" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Execute modulos individualmente conforme necessario" -ForegroundColor Yellow
    Write-Host ""
}

Write-Header "Pipeline finalizado!"

exit 0
