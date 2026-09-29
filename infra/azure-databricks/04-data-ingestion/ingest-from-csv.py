#!/usr/bin/env python3
"""
===============================================================================
DATABRICKS - INGESTAO DE DADOS DE CSV
===============================================================================
Descricao: Le arquivos CSV locais e insere no Databricks (tabela Bronze)
Autor: Avanade Core - Data Engineering Agents
Data: 2026-02-04
===============================================================================
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

# ==============================================================================
# CONFIGURACAO
# ==============================================================================

load_dotenv()

# Credenciais Databricks
DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '').replace('https://', '').replace('http://', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH')

# ==============================================================================
# FUNCOES AUXILIARES
# ==============================================================================

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

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

def validate_config() -> bool:
    """Valida configuracao"""
    
    if not DATABRICKS_HOST:
        print_error("DATABRICKS_HOST nao configurado!")
        return False
    
    if not DATABRICKS_TOKEN:
        print_error("DATABRICKS_TOKEN nao configurado!")
        return False
    
    if not DATABRICKS_HTTP_PATH:
        print_error("DATABRICKS_HTTP_PATH nao configurado!")
        print(f"{Colors.YELLOW}Configure o HTTP Path do SQL Warehouse{Colors.ENDC}")
        print(f"Formato: /sql/1.0/warehouses/xxxxx")
        return False
    
    return True

# ==============================================================================
# INGESTAO DE DADOS
# ==============================================================================

def ingest_csv_to_databricks(
    csv_path: Path,
    table_name: str,
    mode: str = 'append',
    batch_size: int = 1000
) -> dict:
    """
    Ingere dados de CSV para o Databricks
    
    Args:
        csv_path: Caminho para o arquivo CSV
        table_name: Nome da tabela de destino (ex: bronze.taxi_trips_raw)
        mode: 'append' ou 'overwrite'
        batch_size: Tamanho do lote para insercao
    
    Returns:
        Estatisticas da ingestao
    """
    
    print_step(f"Lendo arquivo CSV: {csv_path.name}")
    
    # Le o CSV
    try:
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Converte colunas de data se existirem
        date_columns = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        print_success(f"CSV carregado: {len(df)} linhas, {len(df.columns)} colunas")
    except Exception as e:
        print_error(f"Erro ao ler CSV: {e}")
        return {"success": False, "error": str(e)}
    
    # Adiciona metadados de ingestao
    df['_ingestion_timestamp'] = datetime.now()
    df['_source_file'] = csv_path.name
    
    # Conecta ao Databricks
    print_step("Conectando ao Databricks...")
    
    try:
        connection = sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        
        cursor = connection.cursor()
        print_success("Conexao estabelecida")
        
        # Limpa tabela se mode = overwrite
        if mode == 'overwrite':
            print_step(f"Limpando tabela {table_name}...")
            cursor.execute(f"DELETE FROM {table_name}")
            print_success("Tabela limpa")
        
        # Insere dados em lotes
        print_step(f"Inserindo {len(df)} linhas em lotes de {batch_size}...")
        
        inserted_rows = 0
        errors = 0
        
        # Pega nomes das colunas
        columns = list(df.columns)
        columns_str = ', '.join(columns)
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                # Converte valores para formato SQL
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, str):
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    elif isinstance(val, (datetime, pd.Timestamp)):
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    else:
                        values.append(str(val))
                
                values_str = ', '.join(values)
                
                insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
                
                try:
                    cursor.execute(insert_sql)
                    inserted_rows += 1
                except Exception as e:
                    errors += 1
                    if errors < 10:
                        print_error(f"Erro na linha {inserted_rows + errors}: {e}")
            
            # Progresso
            progress = min(i + batch_size, len(df))
            pct = (progress / len(df)) * 100
            print(f"  Progresso: {progress}/{len(df)} linhas ({pct:.1f}%)")
        
        cursor.close()
        connection.close()
        
        print_success(f"Ingestao concluida: {inserted_rows} linhas inseridas, {errors} erros")
        
        return {
            "success": True,
            "rows_inserted": inserted_rows,
            "errors": errors,
            "source_file": csv_path.name,
            "table": table_name
        }
    
    except Exception as e:
        print_error(f"Erro durante ingestao: {e}")
        return {"success": False, "error": str(e)}

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description='Ingere CSV para Databricks')
    parser.add_argument('--file', type=str, help='Caminho para o arquivo CSV')
    parser.add_argument('--table', type=str, default='bronze.taxi_trips_raw', 
                        help='Tabela de destino (default: bronze.taxi_trips_raw)')
    parser.add_argument('--mode', type=str, default='append', choices=['append', 'overwrite'],
                        help='Modo de insercao (default: append)')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Tamanho do lote (default: 1000)')
    
    args = parser.parse_args()
    
    print_header("Databricks CSV Ingestion")
    
    # Valida configuracao
    if not validate_config():
        print(f"\n{Colors.YELLOW}Configure as variaveis de ambiente no arquivo .env:{Colors.ENDC}")
        print(f"  DATABRICKS_HOST=adb-xxxxx.azuredatabricks.net")
        print(f"  DATABRICKS_TOKEN=dapi...")
        print(f"  DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx")
        sys.exit(1)
    
    # Define arquivo CSV
    if args.file:
        csv_path = Path(args.file)
    else:
        csv_path = Path("../Files/green_tripdata_2021-04.csv")
    
    if not csv_path.exists():
        print_error(f"Arquivo nao encontrado: {csv_path}")
        print(f"\n{Colors.YELLOW}Use: python ingest-from-csv.py --file <caminho-do-csv>{Colors.ENDC}")
        sys.exit(1)
    
    # Executa ingestao
    result = ingest_csv_to_databricks(
        csv_path=csv_path,
        table_name=args.table,
        mode=args.mode,
        batch_size=args.batch_size
    )
    
    # Resumo
    print_header("Resumo da Ingestao")
    
    if result.get("success"):
        print_success(f"Arquivo: {result['source_file']}")
        print_success(f"Tabela: {result['table']}")
        print_success(f"Linhas inseridas: {result['rows_inserted']}")
        if result['errors'] > 0:
            print_error(f"Erros: {result['errors']}")
    else:
        print_error(f"Falha na ingestao: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
