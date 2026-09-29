# setup-databricks-cli.ps1 - Configura o Databricks CLI com autenticacao via token

param(
    [string]$WorkspaceUrl,
    [string]$Token,
    [string]$ProfileName = "DEFAULT"
)

$ErrorActionPreference = "Stop"

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

# ============================================================================
# VALIDACOES INICIAIS
# ============================================================================

Write-Header "Databricks CLI - Configuracao de Autenticacao"

# Verifica Python
Write-Step "Verificando Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python detectado: $pythonVersion"
} catch {
    Write-ErrorMsg "Python nao encontrado!"
    Write-Host "Instale com: winget install Python.Python.3.11" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# INSTALA DATABRICKS CLI
# ============================================================================

Write-Step "Verificando Databricks CLI..."
try {
    $databricksVersion = databricks --version 2>&1
    Write-Success "Databricks CLI ja instalado: $databricksVersion"
} catch {
    Write-Step "Instalando Databricks CLI..."
    pip install databricks-cli
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Databricks CLI instalado com sucesso!"
    } else {
        Write-ErrorMsg "Falha na instalacao!"
        exit 1
    }
}

# ============================================================================
# OBTER WORKSPACE URL
# ============================================================================

if (-not $WorkspaceUrl) {
    $infoFile = "..\01-provision-azure\databricks-workspace-info.json"
    if (Test-Path $infoFile) {
        $workspaceInfo = Get-Content $infoFile | ConvertFrom-Json
        $WorkspaceUrl = $workspaceInfo.workspaceUrl
        Write-Host "> URL do workspace detectada: $WorkspaceUrl" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "====================================================================" -ForegroundColor Yellow
        Write-Host "  COMO OBTER A URL DO WORKSPACE" -ForegroundColor Yellow
        Write-Host "====================================================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Acesse o portal Azure: https://portal.azure.com" -ForegroundColor Gray
        Write-Host "2. Navegue ate seu Databricks workspace" -ForegroundColor Gray
        Write-Host "3. Copie a 'Workspace URL' (formato: https://adb-123456789.azuredatabricks.net)" -ForegroundColor Gray
        Write-Host ""
        
        $WorkspaceUrl = Read-Host "Digite a URL do workspace"
    }
}

# Normaliza URL
if (-not $WorkspaceUrl.StartsWith("https://")) {
    $WorkspaceUrl = "https://$WorkspaceUrl"
}

# ============================================================================
# OBTER TOKEN
# ============================================================================

if (-not $Token) {
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Yellow
    Write-Host "  COMO GERAR UM PERSONAL ACCESS TOKEN" -ForegroundColor Yellow
    Write-Host "====================================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Acesse: $WorkspaceUrl" -ForegroundColor Gray
    Write-Host "2. Clique no icone do usuario (canto superior direito)" -ForegroundColor Gray
    Write-Host "3. User Settings -> Developer" -ForegroundColor Gray
    Write-Host "4. Access Tokens -> Generate New Token" -ForegroundColor Gray
    Write-Host "5. Defina:" -ForegroundColor Gray
    Write-Host "   - Comment: Databricks CLI - Data Migration" -ForegroundColor Gray
    Write-Host "   - Lifetime: 90 dias (recomendado)" -ForegroundColor Gray
    Write-Host "6. Clique em Generate" -ForegroundColor Gray
    Write-Host "7. IMPORTANTE: Copie o token (ele aparece apenas UMA vez!)" -ForegroundColor Gray
    Write-Host ""
    
    $Token = Read-Host "Digite o Personal Access Token"
}

# ============================================================================
# CONFIGURA DATABRICKS CLI
# ============================================================================

Write-Step "Configurando perfil '$ProfileName'..."

$env:DATABRICKS_HOST = $WorkspaceUrl
$env:DATABRICKS_TOKEN = $Token

# Escreve arquivo de configuracao
$configContent = "[DEFAULT]`nhost = $WorkspaceUrl`ntoken = $Token"
$configContent | Out-File -FilePath "$env:USERPROFILE\.databrickscfg" -Encoding UTF8 -Force

Write-Success "Configuracao salva em: $env:USERPROFILE\.databrickscfg"

# ============================================================================
# TESTA CONECTIVIDADE
# ============================================================================

Write-Step "Testando conectividade..."

try {
    $workspaces = databricks workspace list / 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Conexao estabelecida com sucesso!"
        Write-Host "  Workspace URL: $WorkspaceUrl" -ForegroundColor Gray
        Write-Host "  Autenticacao: Token valido" -ForegroundColor Gray
    } else {
        Write-ErrorMsg "Falha na conexao!"
        Write-Host $workspaces -ForegroundColor Red
        exit 1
    }
} catch {
    Write-ErrorMsg "Erro ao testar conectividade: $_"
    exit 1
}

# ============================================================================
# SALVA VARIAVEIS DE AMBIENTE (OPCIONAL)
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR VARIAVEIS DE AMBIENTE (OPCIONAL)" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

$saveEnv = Read-Host "Deseja criar arquivo .env para uso em scripts Python? (s/N)"

if ($saveEnv -eq "s" -or $saveEnv -eq "S") {
    $envContent = "# Databricks Configuration`nDATABRICKS_HOST=$WorkspaceUrl`nDATABRICKS_TOKEN=$Token"
    
    $envFile = "..\..\.env"
    $envContent | Out-File -FilePath $envFile -Encoding UTF8 -Force
    Write-Success "Arquivo .env criado: $envFile"
    Write-Host "  IMPORTANTE: Adicione '.env' ao .gitignore!" -ForegroundColor Red
}

# ============================================================================
# PROXIMOS PASSOS
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  PROXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] Databricks CLI configurado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Yellow
Write-Host "  databricks workspace list /               # Listar workspace" -ForegroundColor Gray
Write-Host "  databricks clusters list                  # Listar clusters" -ForegroundColor Gray
Write-Host "  databricks fs ls dbfs:/                   # Listar arquivos DBFS" -ForegroundColor Gray
Write-Host ""
Write-Host "Proximas etapas:" -ForegroundColor Yellow
Write-Host "  1. Criar schemas e tabelas:" -ForegroundColor Gray
Write-Host "     cd ..\03-database-setup" -ForegroundColor Gray
Write-Host "     .\execute-ddl.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Ingerir dados:" -ForegroundColor Gray
Write-Host "     cd ..\04-data-ingestion" -ForegroundColor Gray
Write-Host "     python ingest-from-csv.py" -ForegroundColor Gray
Write-Host ""

Write-Header "Configuracao concluida!"
