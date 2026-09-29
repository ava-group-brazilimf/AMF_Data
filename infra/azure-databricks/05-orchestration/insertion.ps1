# insertion.ps1 - Script de Ingestao de Dados para Azure Databricks
# Este script le arquivos da pasta Files e insere no Databricks
# Se a pasta Files estiver vazia, inicia jornada para conexao com SQL Server

param(
    [string]$Table = "bronze.taxi_trips_raw",
    [ValidateSet("append", "overwrite")]
    [string]$Mode = "append",
    [int]$BatchSize = 1000,
    [switch]$Force
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
        return $true
    }
    return $false
}

# ============================================================================
# BANNER
# ============================================================================

Clear-Host

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "     DATABRICKS DATA INSERTION" -ForegroundColor Cyan
Write-Host ""
Write-Host "     Avanade Core - Data Engineering" -ForegroundColor Cyan
Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# CARREGAR CONFIGURACOES
# ============================================================================

Write-Step "Carregando configuracoes..."

if (-not (Load-EnvFile)) {
    Write-ErrorMsg "Arquivo .env nao encontrado!"
    Write-Host ""
    Write-Host "Crie o arquivo .env com as credenciais:" -ForegroundColor Yellow
    Write-Host "  DATABRICKS_HOST=https://adb-xxx.azuredatabricks.net" -ForegroundColor Gray
    Write-Host "  DATABRICKS_TOKEN=dapi..." -ForegroundColor Gray
    Write-Host "  DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxx" -ForegroundColor Gray
    exit 1
}

if (-not $env:DATABRICKS_HOST -or -not $env:DATABRICKS_TOKEN) {
    Write-ErrorMsg "Credenciais Databricks nao configuradas no .env!"
    exit 1
}

Write-Success "Configuracoes carregadas"
Write-Info "Host: $env:DATABRICKS_HOST"

# ============================================================================
# VERIFICAR PASTA FILES
# ============================================================================

$filesPath = Join-Path $ScriptRoot "..\Files"

if (-not (Test-Path $filesPath)) {
    New-Item -ItemType Directory -Path $filesPath -Force | Out-Null
    Write-Info "Pasta Files criada: $filesPath"
}

$csvFiles = Get-ChildItem "$filesPath\*.csv" -ErrorAction SilentlyContinue
$jsonFiles = Get-ChildItem "$filesPath\*.json" -ErrorAction SilentlyContinue
$allFiles = @()
if ($csvFiles) { $allFiles += $csvFiles }
if ($jsonFiles) { $allFiles += $jsonFiles }

# ============================================================================
# JORNADA DE CONEXAO SQL (se pasta vazia)
# ============================================================================

if ($allFiles.Count -eq 0) {
    Write-Header "Pasta Files vazia - Conexao com SQL Server"
    
    Write-Host "Nenhum arquivo encontrado na pasta Files." -ForegroundColor Yellow
    Write-Host "Vamos conectar a uma base de dados SQL Server para extrair dados." -ForegroundColor Yellow
    Write-Host ""
    
    # Coleta informacoes de conexao
    Write-Host "=== CONFIGURACAO DA CONEXAO SQL SERVER ===" -ForegroundColor Cyan
    Write-Host ""
    
    $sqlServer = Read-Host "Servidor SQL (ex: servidor.database.windows.net)"
    if (-not $sqlServer) {
        Write-ErrorMsg "Servidor SQL e obrigatorio!"
        exit 1
    }
    
    $sqlDatabase = Read-Host "Nome do Banco de Dados"
    if (-not $sqlDatabase) {
        Write-ErrorMsg "Nome do banco e obrigatorio!"
        exit 1
    }
    
    $sqlUser = Read-Host "Usuario"
    if (-not $sqlUser) {
        Write-ErrorMsg "Usuario e obrigatorio!"
        exit 1
    }
    
    $sqlPassword = Read-Host "Senha" -AsSecureString
    $sqlPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sqlPassword)
    )
    
    Write-Host ""
    Write-Host "=== OPCOES DE EXTRACAO ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Extrair tabela completa" -ForegroundColor Gray
    Write-Host "2. Executar query customizada" -ForegroundColor Gray
    Write-Host "3. Listar tabelas disponiveis" -ForegroundColor Gray
    Write-Host ""
    
    $option = Read-Host "Escolha uma opcao (1-3)"
    
    # Monta connection string
    $connectionString = "Server=$sqlServer;Database=$sqlDatabase;User Id=$sqlUser;Password=$sqlPasswordPlain;TrustServerCertificate=True;"
    
    Write-Step "Conectando ao SQL Server..."
    
    try {
        $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
        $connection.Open()
        Write-Success "Conexao estabelecida com sucesso!"
        
        switch ($option) {
            "1" {
                # Extrair tabela completa
                $tableName = Read-Host "Nome da tabela (ex: dbo.Clientes)"
                $query = "SELECT * FROM $tableName"
                $outputFile = Join-Path $filesPath "$($tableName.Replace('.', '_')).csv"
            }
            "2" {
                # Query customizada
                Write-Host "Digite a query SQL (termine com ponto-e-virgula e pressione Enter):" -ForegroundColor Yellow
                $query = Read-Host "Query"
                $outputFile = Join-Path $filesPath "query_result_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
            }
            "3" {
                # Listar tabelas
                $query = "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME"
                
                $command = New-Object System.Data.SqlClient.SqlCommand($query, $connection)
                $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($command)
                $dataTable = New-Object System.Data.DataTable
                $adapter.Fill($dataTable)
                
                Write-Host ""
                Write-Host "Tabelas disponiveis:" -ForegroundColor Cyan
                Write-Host "--------------------" -ForegroundColor Cyan
                
                foreach ($row in $dataTable.Rows) {
                    Write-Host "  $($row.TABLE_SCHEMA).$($row.TABLE_NAME)" -ForegroundColor Gray
                }
                
                Write-Host ""
                $tableName = Read-Host "Escolha uma tabela para extrair"
                $query = "SELECT * FROM $tableName"
                $outputFile = Join-Path $filesPath "$($tableName.Replace('.', '_')).csv"
            }
            default {
                Write-ErrorMsg "Opcao invalida!"
                $connection.Close()
                exit 1
            }
        }
        
        Write-Step "Executando query e extraindo dados..."
        
        $command = New-Object System.Data.SqlClient.SqlCommand($query, $connection)
        $command.CommandTimeout = 300  # 5 minutos
        $adapter = New-Object System.Data.SqlClient.SqlDataAdapter($command)
        $dataTable = New-Object System.Data.DataTable
        $rowCount = $adapter.Fill($dataTable)
        
        Write-Success "Extraidos $rowCount registros"
        
        # Exporta para CSV
        Write-Step "Exportando para CSV..."
        $dataTable | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
        
        Write-Success "Arquivo salvo: $outputFile"
        
        $connection.Close()
        
        # Atualiza lista de arquivos
        $csvFiles = Get-ChildItem "$filesPath\*.csv" -ErrorAction SilentlyContinue
        $allFiles = @()
        if ($csvFiles) { $allFiles += $csvFiles }
        
    } catch {
        Write-ErrorMsg "Erro na conexao SQL: $_"
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
        exit 1
    }
}

# ============================================================================
# INSTALAR DEPENDENCIAS PYTHON
# ============================================================================

Write-Step "Verificando dependencias Python..."

$ingestionPath = Join-Path $ScriptRoot "..\04-data-ingestion"
Push-Location $ingestionPath

try {
    pip install -q -r requirements.txt 2>$null
    Write-Success "Dependencias Python instaladas"
} catch {
    Write-ErrorMsg "Falha ao instalar dependencias Python"
}

# ============================================================================
# INGESTAO DE ARQUIVOS CSV
# ============================================================================

Write-Header "Ingestao de Dados"

$csvFiles = Get-ChildItem "$filesPath\*.csv" -ErrorAction SilentlyContinue

if ($csvFiles) {
    Write-Info "Encontrados $($csvFiles.Count) arquivo(s) CSV"
    Write-Host ""
    
    $totalRows = 0
    $successCount = 0
    $errorCount = 0
    
    foreach ($csvFile in $csvFiles) {
        Write-Step "Processando: $($csvFile.Name)"
        
        $startTime = Get-Date
        
        python ingest-from-csv.py --file $csvFile.FullName --table $Table --mode $Mode --batch-size $BatchSize
        
        $duration = ((Get-Date) - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Ingerido: $($csvFile.Name) ($([math]::Round($duration, 1))s)"
            $successCount++
        } else {
            Write-ErrorMsg "Falha: $($csvFile.Name)"
            $errorCount++
        }
        
        Write-Host ""
    }
    
    Write-Header "Resumo da Ingestao"
    Write-Host "  Arquivos processados: $($csvFiles.Count)" -ForegroundColor White
    Write-Host "  Sucesso: " -NoNewline; Write-Host $successCount -ForegroundColor Green
    Write-Host "  Erros: " -NoNewline; Write-Host $errorCount -ForegroundColor Red
    
} else {
    Write-ErrorMsg "Nenhum arquivo CSV encontrado para ingestao!"
}

# ============================================================================
# INGESTAO DE ARQUIVOS JSON (Reference Data)
# ============================================================================

$jsonFiles = Get-ChildItem "$filesPath\*.json" -ErrorAction SilentlyContinue

if ($jsonFiles) {
    Write-Header "Ingestao de Dados de Referencia (JSON)"
    
    foreach ($jsonFile in $jsonFiles) {
        Write-Step "Processando: $($jsonFile.Name)"
        
        # Determina tabela de destino baseado no nome do arquivo
        $targetTable = switch -Wildcard ($jsonFile.Name) {
            "*payment*" { "reference.payment_types" }
            "*rate*" { "reference.rate_codes" }
            "*trip_type*" { "reference.trip_types" }
            default { "reference.lookup_data" }
        }
        
        python ingest-from-json.py --file $jsonFile.FullName --table $targetTable --mode overwrite
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Ingerido: $($jsonFile.Name) -> $targetTable"
        } else {
            Write-ErrorMsg "Falha: $($jsonFile.Name)"
        }
    }
}

Pop-Location

# ============================================================================
# FINALIZACAO
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "  Ingestao Concluida!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para verificar os dados no Databricks:" -ForegroundColor Yellow
Write-Host "  SELECT COUNT(*) FROM $Table;" -ForegroundColor Gray
Write-Host ""
