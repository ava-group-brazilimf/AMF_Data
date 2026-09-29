#!/usr/bin/env python3
"""
===============================================================================
DATABRICKS - EXECUCAO DE SQL VIA API
===============================================================================
Descricao: Executa comandos SQL no Databricks usando a SQL API
Autor: Avanade Core - Data Engineering Agents
Data: 2026-02-04
===============================================================================
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# ==============================================================================
# CONFIGURACAO
# ==============================================================================

# Carrega variaveis de ambiente
load_dotenv()

# Credenciais Databricks
# COMO OBTER:
# 1. DATABRICKS_HOST: URL do workspace (https://adb-123456789.azuredatabricks.net)
#    - Copie do portal Azure ou do arquivo databricks-workspace-info.json
# 2. DATABRICKS_TOKEN: Personal Access Token
#    - User Settings -> Developer -> Access Tokens -> Generate New Token
DATABRICKS_HOST = os.getenv('DATABRICKS_HOST')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')

# SQL Warehouse ID (opcional, para execucao via SQL API)
# COMO OBTER:
# 1. Acesse: {DATABRICKS_HOST}/sql/warehouses
# 2. Clique no SQL Warehouse desejado
# 3. Copie o ID da URL (formato: /sql/warehouses/{warehouse_id})
SQL_WAREHOUSE_ID = os.getenv('DATABRICKS_SQL_WAREHOUSE_ID')

# ==============================================================================
# FUNCOES AUXILIARES
# ==============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message: str):
    print(f"\n{Colors.CYAN}+{'=' * 67}+{Colors.ENDC}")
    print(f"{Colors.CYAN}|  {message:<65}|{Colors.ENDC}")
    print(f"{Colors.CYAN}+{'=' * 67}+{Colors.ENDC}\n")

def print_step(message: str):
    print(f"{Colors.YELLOW}> {message}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}[OK] {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}[X] {message}{Colors.ENDC}")

# ==============================================================================
# VALIDACOES
# ==============================================================================

def validate_credentials() -> bool:
    """Valida se as credenciais estao configuradas"""
    
    if not DATABRICKS_HOST:
        print_error("DATABRICKS_HOST nao configurado!")
        print(f"{Colors.YELLOW}Configure a variavel de ambiente ou crie arquivo .env{Colors.ENDC}")
        return False
    
    if not DATABRICKS_TOKEN:
        print_error("DATABRICKS_TOKEN nao configurado!")
        print(f"{Colors.YELLOW}Configure a variavel de ambiente ou crie arquivo .env{Colors.ENDC}")
        return False
    
    return True

# ==============================================================================
# DATABRICKS API
# ==============================================================================

def execute_sql_statement(sql: str, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executa um comando SQL via Databricks SQL API
    
    Args:
        sql: Comando SQL a ser executado
        warehouse_id: ID do SQL Warehouse (opcional)
    
    Returns:
        Resultado da execucao
    """
    
    # Usa warehouse_id fornecido ou da env
    wh_id = warehouse_id or SQL_WAREHOUSE_ID
    
    if not wh_id:
        print_error("SQL_WAREHOUSE_ID nao configurado!")
        print(f"{Colors.YELLOW}Configure a variavel DATABRICKS_SQL_WAREHOUSE_ID{Colors.ENDC}")
        return {"error": "No warehouse ID"}
    
    # API endpoint
    url = f"{DATABRICKS_HOST}/api/2.0/sql/statements/"
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "warehouse_id": wh_id,
        "statement": sql,
        "wait_timeout": "30s"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print_error(f"Erro na requisicao: {e}")
        if hasattr(e.response, 'text'):
            print(f"{Colors.RED}Resposta: {e.response.text}{Colors.ENDC}")
        return {"error": str(e)}

def execute_sql_file(file_path: Path, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executa um arquivo SQL completo
    
    Args:
        file_path: Caminho para o arquivo SQL
        warehouse_id: ID do SQL Warehouse
    
    Returns:
        Estatisticas de execucao
    """
    
    print_step(f"Executando arquivo: {file_path.name}")
    
    # Le o arquivo SQL
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Divide por comandos (separados por ponto-e-virgula)
    commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
    
    results = {
        "file": file_path.name,
        "total_commands": len(commands),
        "success": 0,
        "errors": 0,
        "details": []
    }
    
    for i, cmd in enumerate(commands, 1):
        # Remove comentarios inline primeiro
        clean_cmd = '\n'.join([line for line in cmd.split('\n') 
                                if not line.strip().startswith('--')])
        
        # Ignora comandos vazios
        if not clean_cmd.strip():
            continue
        
        print(f"  Comando {i}/{len(commands)}...", end=' ')
        
        result = execute_sql_statement(clean_cmd, warehouse_id)
        
        if "error" in result or result.get("status", {}).get("state") == "FAILED":
            results["errors"] += 1
            error_msg = result.get("status", {}).get("error", {}).get("message", str(result.get("error")))
            print(f"{Colors.RED}[X] Erro: {error_msg}{Colors.ENDC}")
            results["details"].append({
                "command": i,
                "status": "error",
                "message": error_msg
            })
        else:
            results["success"] += 1
            print(f"{Colors.GREEN}[OK]{Colors.ENDC}")
            results["details"].append({
                "command": i,
                "status": "success"
            })
    
    return results

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Funcao principal"""
    
    print_header("Databricks SQL Executor (via API)")
    
    # Valida credenciais
    if not validate_credentials():
        sys.exit(1)
    
    print_success(f"Host: {DATABRICKS_HOST}")
    print_success(f"Token: {'*' * 20}{DATABRICKS_TOKEN[-4:]}")
    
    # Diretorio de scripts SQL
    sql_dir = Path("../03-database-setup")
    
    if not sql_dir.exists():
        print_error(f"Diretorio nao encontrado: {sql_dir}")
        sys.exit(1)
    
    # Arquivos SQL na ordem correta
    sql_files = [
        sql_dir / "create-schemas.sql",
        sql_dir / "create-tables.sql"
    ]
    
    # Verifica se SQL Warehouse esta configurado
    if not SQL_WAREHOUSE_ID:
        print_error("SQL Warehouse ID nao configurado!")
        print(f"\n{Colors.YELLOW}Para executar SQL, voce precisa de um SQL Warehouse ativo:{Colors.ENDC}")
        print(f"1. Acesse: {DATABRICKS_HOST}/sql/warehouses")
        print(f"2. Crie ou inicie um SQL Warehouse")
        print(f"3. Copie o ID e configure: DATABRICKS_SQL_WAREHOUSE_ID")
        print(f"\nOu forneca o ID como argumento:")
        print(f"  python execute-sql-via-api.py --warehouse-id <ID>")
        sys.exit(1)
    
    # Executa cada arquivo
    total_success = 0
    total_errors = 0
    
    for sql_file in sql_files:
        if not sql_file.exists():
            print_error(f"Arquivo nao encontrado: {sql_file}")
            continue
        
        results = execute_sql_file(sql_file, SQL_WAREHOUSE_ID)
        
        total_success += results["success"]
        total_errors += results["errors"]
        
        print(f"  Resultado: {results['success']} sucesso(s), {results['errors']} erro(s)\n")
    
    # Resumo final
    print_header("Resumo da Execucao")
    print(f"  Total de comandos executados com sucesso: {Colors.GREEN}{total_success}{Colors.ENDC}")
    print(f"  Total de erros: {Colors.RED}{total_errors}{Colors.ENDC}")
    
    if total_errors == 0:
        print_success("\nTodos os scripts foram executados com sucesso!")
    else:
        print_error(f"\n{total_errors} erro(s) encontrado(s). Revise os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
