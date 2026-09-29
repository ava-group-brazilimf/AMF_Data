#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
DATABRICKS - INGESTÃO UNIVERSAL (Azure + Community Edition)
═══════════════════════════════════════════════════════════════════════════════
Descrição: Detecta automaticamente o ambiente e conecta adequadamente
Suporta: Azure Databricks, Databricks Community Edition
Autor: Avanade Core - Data Engineering Agents
Data: 2026-02-04
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd
from dotenv import load_dotenv
from databricks import sql

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

load_dotenv()

# Credenciais Databricks (funciona para Azure e Community Edition)
# 
# PARA AZURE DATABRICKS:
# 1. DATABRICKS_HOST: adb-123456789.azuredatabricks.net (sem https://)
# 2. DATABRICKS_TOKEN: Personal Access Token (User Settings → Developer)
# 3. DATABRICKS_HTTP_PATH: /sql/1.0/warehouses/xxxxx (SQL Warehouse)
#
# PARA DATABRICKS COMMUNITY EDITION:
# 1. DATABRICKS_HOST: community.cloud.databricks.com
# 2. DATABRICKS_TOKEN: Personal Access Token (User Settings → Developer)
# 3. DATABRICKS_CLUSTER_ID: ID do cluster (em "Compute")
#    OU
#    DATABRICKS_HTTP_PATH: Se souber o HTTP path do cluster

DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '').replace('https://', '').replace('http://', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')

# ══════════════════════════════════════════════════════════════════════════════
# DETECÇÃO AUTOMÁTICA DE AMBIENTE
# ══════════════════════════════════════════════════════════════════════════════

def detect_environment():
    """
    Detecta automaticamente se está usando Azure Databricks ou Community Edition
    
    Returns:
        tuple: (environment_type, http_path)
    """
    
    host = DATABRICKS_HOST.lower()
    
    # Detecta Community Edition
    if 'community.cloud.databricks.com' in host:
        print("🌐 Ambiente detectado: Databricks Community Edition")
        
        # Tenta usar HTTP_PATH se fornecido
        http_path = os.getenv('DATABRICKS_HTTP_PATH')
        if http_path:
            return ('community', http_path)
        
        # Se não, tenta usar CLUSTER_ID
        cluster_id = os.getenv('DATABRICKS_CLUSTER_ID')
        if cluster_id:
            # Community Edition geralmente não tem SQL Warehouse, usa cluster endpoint
            http_path = f'/sql/1.0/endpoints/{cluster_id}'
            print(f"  Usando Cluster ID: {cluster_id}")
            return ('community', http_path)
        
        # Fallback: pede ao usuário
        print("\n⚠️ Configure uma das opções:")
        print("  DATABRICKS_CLUSTER_ID=<cluster-id>")
        print("  OU")
        print("  DATABRICKS_HTTP_PATH=<http-path>")
        return ('community', None)
    
    # Detecta Azure Databricks
    elif 'azuredatabricks.net' in host:
        print("☁️ Ambiente detectado: Azure Databricks")
        
        http_path = os.getenv('DATABRICKS_HTTP_PATH')
        if http_path:
            print(f"  Usando SQL Warehouse: {http_path}")
            return ('azure', http_path)
        
        print("\n⚠️ Configure DATABRICKS_HTTP_PATH para SQL Warehouse")
        return ('azure', None)
    
    # Ambiente desconhecido
    else:
        print(f"⚠️ Ambiente desconhecido: {host}")
        http_path = os.getenv('DATABRICKS_HTTP_PATH')
        return ('unknown', http_path)

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def print_header(message: str):
    print(f"\n{Colors.CYAN}╔{'═' * 67}╗{Colors.ENDC}")
    print(f"{Colors.CYAN}║  {message:<65}║{Colors.ENDC}")
    print(f"{Colors.CYAN}╚{'═' * 67}╝{Colors.ENDC}\n")

def print_step(message: str):
    print(f"{Colors.YELLOW}► {message}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

# ══════════════════════════════════════════════════════════════════════════════
# VALIDAÇÕES
# ══════════════════════════════════════════════════════════════════════════════

def validate_config() -> tuple:
    """Valida configuração e retorna (is_valid, env_type, http_path)"""
    
    if not DATABRICKS_HOST:
        print_error("DATABRICKS_HOST não configurado!")
        return (False, None, None)
    
    if not DATABRICKS_TOKEN:
        print_error("DATABRICKS_TOKEN não configurado!")
        return (False, None, None)
    
    env_type, http_path = detect_environment()
    
    if not http_path:
        print_error("HTTP Path ou Cluster ID não configurado!")
        return (False, env_type, None)
    
    return (True, env_type, http_path)

# ══════════════════════════════════════════════════════════════════════════════
# INGESTÃO DE DADOS (UNIVERSAL)
# ══════════════════════════════════════════════════════════════════════════════

def ingest_csv_to_databricks(
    csv_path: Path,
    table_name: str,
    http_path: str,
    mode: str = 'append',
    batch_size: int = 1000
) -> dict:
    """
    Ingere dados de CSV para o Databricks (Azure ou Community Edition)
    """
    
    print_step(f"Lendo arquivo CSV: {csv_path.name}")
    
    # Lê o CSV
    try:
        df = pd.read_csv(csv_path, parse_dates=['lpep_pickup_datetime', 'lpep_dropoff_datetime'])
        print_success(f"CSV carregado: {len(df)} linhas, {len(df.columns)} colunas")
    except Exception as e:
        print_error(f"Erro ao ler CSV: {e}")
        return {"success": False, "error": str(e)}
    
    # Adiciona metadados de ingestão
    df['_ingestion_timestamp'] = datetime.now()
    df['_source_file'] = csv_path.name
    
    # Conecta ao Databricks (funciona para ambos os ambientes)
    print_step("Conectando ao Databricks...")
    
    try:
        connection = sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=http_path,
            access_token=DATABRICKS_TOKEN
        )
        
        cursor = connection.cursor()
        print_success("Conexão estabelecida")
        
        # Limpa tabela se mode = overwrite
        if mode == 'overwrite':
            print_step(f"Limpando tabela {table_name}...")
            cursor.execute(f"DELETE FROM {table_name}")
            print_success("Tabela limpa")
        
        # Insere dados em lotes
        print_step(f"Inserindo {len(df)} linhas em lotes de {batch_size}...")
        
        inserted_rows = 0
        errors = 0
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                # Monta INSERT statement
                columns = ', '.join(row.index)
                
                # Converte valores para formato SQL
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, str):
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    elif isinstance(val, datetime):
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    else:
                        values.append(str(val))
                
                values_str = ', '.join(values)
                
                insert_sql = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({values_str})
                """
                
                try:
                    cursor.execute(insert_sql)
                    inserted_rows += 1
                except Exception as e:
                    errors += 1
                    if errors < 10:
                        print_error(f"Erro na linha {i}: {e}")
            
            # Progresso
            progress = min(i + batch_size, len(df))
            print(f"  Progresso: {progress}/{len(df)} linhas ({(progress/len(df)*100):.1f}%)")
        
        cursor.close()
        connection.close()
        
        print_success(f"Ingestão concluída: {inserted_rows} linhas inseridas, {errors} erros")
        
        return {
            "success": True,
            "rows_inserted": inserted_rows,
            "errors": errors,
            "source_file": csv_path.name,
            "table": table_name
        }
    
    except Exception as e:
        print_error(f"Erro durante ingestão: {e}")
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Ingere CSV para Databricks (Azure ou Community Edition)'
    )
    parser.add_argument('--file', type=str, help='Caminho para o arquivo CSV')
    parser.add_argument('--table', type=str, default='bronze.taxi_trips_raw', 
                        help='Tabela de destino (default: bronze.taxi_trips_raw)')
    parser.add_argument('--mode', type=str, default='append', choices=['append', 'overwrite'],
                        help='Modo de inserção (default: append)')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Tamanho do lote (default: 1000)')
    
    args = parser.parse_args()
    
    print_header("Databricks Universal CSV Ingestion")
    
    # Valida configuração
    is_valid, env_type, http_path = validate_config()
    
    if not is_valid:
        print(f"\n{Colors.YELLOW}Configure as variáveis de ambiente no arquivo .env:{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Para Azure Databricks:{Colors.ENDC}")
        print(f"  DATABRICKS_HOST=adb-xxxxx.azuredatabricks.net")
        print(f"  DATABRICKS_TOKEN=dapi...")
        print(f"  DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx")
        print(f"\n{Colors.CYAN}Para Databricks Community Edition:{Colors.ENDC}")
        print(f"  DATABRICKS_HOST=community.cloud.databricks.com")
        print(f"  DATABRICKS_TOKEN=dapi...")
        print(f"  DATABRICKS_CLUSTER_ID=<cluster-id>")
        sys.exit(1)
    
    print_success(f"Ambiente: {env_type}")
    print_success(f"Host: {DATABRICKS_HOST}")
    print_success(f"HTTP Path: {http_path}")
    
    # Define arquivo CSV
    if args.file:
        csv_path = Path(args.file)
    else:
        csv_path = Path("../../Files/green_tripdata_2021-04.csv")
    
    if not csv_path.exists():
        print_error(f"Arquivo não encontrado: {csv_path}")
        print(f"\n{Colors.YELLOW}Use: python ingest-from-csv-universal.py --file <caminho-do-csv>{Colors.ENDC}")
        sys.exit(1)
    
    # Executa ingestão
    result = ingest_csv_to_databricks(
        csv_path=csv_path,
        table_name=args.table,
        http_path=http_path,
        mode=args.mode,
        batch_size=args.batch_size
    )
    
    # Resumo
    print_header("Resumo da Ingestão")
    
    if result.get("success"):
        print_success(f"Arquivo: {result['source_file']}")
        print_success(f"Tabela: {result['table']}")
        print_success(f"Linhas inseridas: {result['rows_inserted']}")
        if result['errors'] > 0:
            print_error(f"Erros: {result['errors']}")
    else:
        print_error(f"Falha na ingestão: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
