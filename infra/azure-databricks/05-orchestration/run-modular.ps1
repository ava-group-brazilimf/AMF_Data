<#
.SYNOPSIS
    Orquestrador modular - Executa módulos selecionados

.DESCRIPTION
    Este script permite executar módulos específicos do pipeline

.EXAMPLE
    .\run-modular.ps1 -Module Provision
    Executa apenas provisionamento

.EXAMPLE
    .\run-modular.ps1 -Module Config,DDL
    Executa configuração e criação de tabelas

.EXAMPLE
    .\run-modular.ps1 -Module All
    Executa tudo (equivalente a run-all.ps1)
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Provision", "Config", "DDL", "Ingest", "All")]
    [string[]]$Module
)

$ErrorActionPreference = "Stop"

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES
# ══════════════════════════════════════════════════════════════════════════════

function Write-Header {
    param([string]$Message)
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Message" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

# ══════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO
# ══════════════════════════════════════════════════════════════════════════════

Write-Header "Azure Databricks - Execução Modular"

# Se "All", executa run-all.ps1
if ($Module -contains "All") {
    Write-Host "Executando pipeline completo..." -ForegroundColor Yellow
    .\run-all.ps1
    exit $LASTEXITCODE
}

# Executa módulos selecionados
foreach ($mod in $Module) {
    switch ($mod) {
        "Provision" {
            Write-Header "Módulo: Provisionamento"
            Push-Location "..\01-provision-azure"
            .\provision-databricks.ps1
            Pop-Location
        }
        
        "Config" {
            Write-Header "Módulo: Configuração CLI"
            Push-Location "..\02-configure-databricks"
            .\setup-databricks-cli.ps1
            Pop-Location
        }
        
        "DDL" {
            Write-Header "Módulo: Criação de Tabelas"
            Push-Location "..\03-database-setup"
            .\execute-ddl.ps1
            Pop-Location
        }
        
        "Ingest" {
            Write-Header "Módulo: Ingestão de Dados"
            Push-Location "..\04-data-ingestion"
            
            # Instala dependências
            pip install -q -r requirements.txt
            
            # Ingere CSVs
            $csvFiles = Get-ChildItem "..\..\Files\*.csv"
            foreach ($csv in $csvFiles) {
                python ingest-from-csv.py --file $csv.FullName --table bronze.taxi_trips_raw
            }
            
            Pop-Location
        }
    }
}

Write-Header "Execução modular concluída!"
