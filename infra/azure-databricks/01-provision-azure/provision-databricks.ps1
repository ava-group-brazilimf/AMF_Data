<#
.SYNOPSIS
    Provisiona um Azure Databricks workspace via Azure CLI

.DESCRIPTION
    Este script cria automaticamente:
    - Resource Group (se não existir)
    - Azure Databricks workspace
    - Configurações de rede (opcional)

.NOTES
    Pré-requisitos:
    - Azure CLI instalado: winget install Microsoft.AzureCLI
    - Login no Azure: az login
    - Permissões de Contributor na subscription

.EXAMPLE
    .\provision-databricks.ps1
    Provisiona usando config.template.json

.EXAMPLE
    .\provision-databricks.ps1 -ConfigFile custom-config.json
    Usa arquivo de configuração personalizado
#>

param(
    [string]$ConfigFile = "config.template.json",
    [switch]$WhatIf  # Mostra o que seria feito sem executar
)

$ErrorActionPreference = "Stop"

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

function Write-Header {
    param([string]$Message)
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Message" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "► $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# ══════════════════════════════════════════════════════════════════════════════
# VALIDAÇÕES INICIAIS
# ══════════════════════════════════════════════════════════════════════════════

Write-Header "Azure Databricks - Provisionamento Automatizado"

# Verifica se Azure CLI está instalado
Write-Step "Verificando Azure CLI..."
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Success "Azure CLI $($azVersion.'azure-cli') detectado"
} catch {
    Write-Error "Azure CLI não encontrado!"
    Write-Host "Instale com: winget install Microsoft.AzureCLI" -ForegroundColor Yellow
    exit 1
}

# Verifica se está logado no Azure
Write-Step "Verificando autenticação Azure..."
$account = az account show 2>$null
if (-not $account) {
    Write-Error "Não autenticado no Azure!"
    Write-Host "Execute: az login" -ForegroundColor Yellow
    exit 1
}

$accountInfo = $account | ConvertFrom-Json
Write-Success "Autenticado como: $($accountInfo.user.name)"
Write-Host "Subscription Ativa: $($accountInfo.name) ($($accountInfo.id))" -ForegroundColor Gray

# ══════════════════════════════════════════════════════════════════════════════
# CARREGA CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

Write-Step "Carregando configuração de $ConfigFile..."

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Arquivo $ConfigFile não encontrado!"
    Write-Host @"
Crie o arquivo com o formato:
{
  "subscriptionId": "SEU_SUBSCRIPTION_ID",
  "resourceGroup": "rg-databricks-dev",
  "location": "eastus2",
  "workspaceName": "dbw-data-engineering",
  "pricingTier": "premium"
}
"@ -ForegroundColor Yellow
    exit 1
}

$config = Get-Content $ConfigFile | ConvertFrom-Json

# Validações
if ($config.subscriptionId -like "*SUBSTITUA*") {
    Write-Error "Configure o subscriptionId em $ConfigFile!"
    Write-Host @"
Para obter seu Subscription ID:
1. Execute: az account list --output table
2. Copie o 'SubscriptionId' desejado
3. Substitua em $ConfigFile
"@ -ForegroundColor Yellow
    exit 1
}

Write-Success "Configuração carregada:"
Write-Host "  Resource Group: $($config.resourceGroup)" -ForegroundColor Gray
Write-Host "  Location: $($config.location)" -ForegroundColor Gray
Write-Host "  Workspace: $($config.workspaceName)" -ForegroundColor Gray
Write-Host "  Pricing Tier: $($config.pricingTier)" -ForegroundColor Gray

# ══════════════════════════════════════════════════════════════════════════════
# DEFINE SUBSCRIPTION ATIVA
# ══════════════════════════════════════════════════════════════════════════════

Write-Step "Definindo subscription ativa..."
az account set --subscription $config.subscriptionId
if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao definir subscription!"
    exit 1
}
Write-Success "Subscription definida: $($config.subscriptionId)"

# ══════════════════════════════════════════════════════════════════════════════
# CRIA RESOURCE GROUP (se não existir)
# ══════════════════════════════════════════════════════════════════════════════

Write-Step "Verificando Resource Group..."
$rgExists = az group exists --name $config.resourceGroup
if ($rgExists -eq "false") {
    Write-Step "Criando Resource Group $($config.resourceGroup)..."
    
    if (-not $WhatIf) {
        az group create `
            --name $config.resourceGroup `
            --location $config.location `
            --tags Environment=$($config.tags.Environment) Project=$($config.tags.Project) ManagedBy=$($config.tags.ManagedBy)
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Resource Group criado!"
        } else {
            Write-Error "Falha ao criar Resource Group!"
            exit 1
        }
    } else {
        Write-Host "[WHATIF] Criaria Resource Group: $($config.resourceGroup)" -ForegroundColor Magenta
    }
} else {
    Write-Success "Resource Group já existe"
}

# ══════════════════════════════════════════════════════════════════════════════
# CRIA DATABRICKS WORKSPACE
# ══════════════════════════════════════════════════════════════════════════════

Write-Step "Verificando se workspace já existe..."
$workspaceExists = az databricks workspace show `
    --resource-group $config.resourceGroup `
    --name $config.workspaceName 2>$null

if ($workspaceExists) {
    Write-Success "Workspace já existe: $($config.workspaceName)"
    $workspace = $workspaceExists | ConvertFrom-Json
    Write-Host "  URL: $($workspace.workspaceUrl)" -ForegroundColor Gray
    Write-Host "  ID: $($workspace.id)" -ForegroundColor Gray
} else {
    Write-Step "Criando Azure Databricks workspace..."
    Write-Host "  Isso pode levar 5-10 minutos..." -ForegroundColor Gray
    
    if (-not $WhatIf) {
        # Cria o workspace
        $workspace = az databricks workspace create `
            --resource-group $config.resourceGroup `
            --name $config.workspaceName `
            --location $config.location `
            --sku $config.pricingTier `
            --tags Environment=$($config.tags.Environment) Project=$($config.tags.Project) ManagedBy=$($config.tags.ManagedBy) `
            --output json
        
        if ($LASTEXITCODE -eq 0) {
            $workspaceData = $workspace | ConvertFrom-Json
            Write-Success "Workspace criado com sucesso!"
            Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
            Write-Host "║  WORKSPACE CRIADO COM SUCESSO                                      ║" -ForegroundColor Green
            Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
            Write-Host "  Nome: $($workspaceData.name)" -ForegroundColor White
            Write-Host "  URL: https://$($workspaceData.workspaceUrl)" -ForegroundColor White
            Write-Host "  Resource ID: $($workspaceData.id)" -ForegroundColor Gray
            
            # Salva informações em arquivo
            $outputFile = "databricks-workspace-info.json"
            @{
                workspaceName = $workspaceData.name
                workspaceUrl = "https://$($workspaceData.workspaceUrl)"
                resourceId = $workspaceData.id
                resourceGroup = $config.resourceGroup
                location = $workspaceData.location
                sku = $workspaceData.sku.name
                createdAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            } | ConvertTo-Json | Out-File $outputFile
            
            Write-Host "`n✓ Informações salvas em: $outputFile" -ForegroundColor Green
        } else {
            Write-Error "Falha ao criar workspace!"
            exit 1
        }
    } else {
        Write-Host "[WHATIF] Criaria workspace: $($config.workspaceName)" -ForegroundColor Magenta
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# PRÓXIMOS PASSOS
# ══════════════════════════════════════════════════════════════════════════════

if (-not $WhatIf) {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  PRÓXIMOS PASSOS                                                   ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host @"

1. Acesse o workspace:
   https://$($workspaceData.workspaceUrl)

2. Gere um Personal Access Token:
   User Settings → Developer → Access Tokens → Generate New Token

3. Configure o Databricks CLI:
   cd ..\02-configure-databricks
   .\setup-databricks-cli.ps1

4. Ou execute tudo integrado:
   cd ..\05-orchestration
   .\run-all.ps1

"@ -ForegroundColor Yellow
}

Write-Header "Provisionamento concluído!"
