# execute-ddl.ps1 - Executa scripts SQL no Databricks via Python API

$ErrorActionPreference = "Stop"

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

Write-Header "Databricks SQL Executor"

# Carrega variaveis de ambiente do .env
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
    Write-Success "Configuracoes carregadas"
} else {
    Write-ErrorMsg "Arquivo .env nao encontrado!"
    exit 1
}

# Verifica variaveis necessarias
if (-not $env:DATABRICKS_HOST -or -not $env:DATABRICKS_TOKEN) {
    Write-ErrorMsg "DATABRICKS_HOST e DATABRICKS_TOKEN nao configuradas!"
    exit 1
}

Write-Success "Credenciais Databricks configuradas"

# Executa via Python API
Write-Header "Executando scripts SQL via Python API"

$pythonScript = "..\04-data-ingestion\execute-sql-via-api.py"
if (Test-Path $pythonScript) {
    Push-Location "..\04-data-ingestion"
    try {
        python execute-sql-via-api.py
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Scripts SQL executados com sucesso!"
        } else {
            Write-ErrorMsg "Falha na execucao dos scripts SQL"
            exit 1
        }
    } catch {
        Write-ErrorMsg "Erro ao executar scripts: $_"
        exit 1
    } finally {
        Pop-Location
    }
} else {
    Write-ErrorMsg "Script Python nao encontrado: $pythonScript"
    exit 1
}

Write-Header "Processo concluido!"
