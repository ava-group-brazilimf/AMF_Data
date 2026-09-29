#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
DATABRICKS - INGESTÃO DE DADOS DE API REST
═══════════════════════════════════════════════════════════════════════════════
Descrição: Consome dados de APIs REST e insere no Databricks
Autor: Avanade Core - Data Engineering Agents
Data: 2026-02-04
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import pandas as pd
from dotenv import load_dotenv
from databricks import sql

# Carrega configuração
load_dotenv()

DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '').replace('https://', '').replace('http://', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH')

# ══════════════════════════════════════════════════════════════════════════════
# API CLIENT
# ══════════════════════════════════════════════════════════════════════════════

def fetch_from_api(
    api_url: str,
    method: str = 'GET',
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Consome dados de uma API REST
    
    Args:
        api_url: URL da API
        method: Método HTTP (GET, POST, etc)
        headers: Headers HTTP (para autenticação, etc)
        params: Query parameters
        data: Body data (para POST)
    
    Returns:
        Lista de registros
    """
    
    print(f"► Consumindo API: {api_url}")
    
    try:
        response = requests.request(
            method=method,
            url=api_url,
            headers=headers,
            params=params,
            json=data,
            timeout=30
        )
        
        response.raise_for_status()
        
        json_data = response.json()
        
        # Detecta estrutura
        if isinstance(json_data, list):
            records = json_data
        elif isinstance(json_data, dict):
            # Tenta extrair array de diferentes estruturas comuns
            if 'data' in json_data:
                records = json_data['data']
            elif 'results' in json_data:
                records = json_data['results']
            elif 'items' in json_data:
                records = json_data['items']
            else:
                # Objeto único
                records = [json_data]
        else:
            records = []
        
        print(f"✓ API respondeu com {len(records)} registros")
        
        return records
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Erro ao consumir API: {e}")
        return []

# ══════════════════════════════════════════════════════════════════════════════
# INGESTÃO
# ══════════════════════════════════════════════════════════════════════════════

def ingest_api_to_databricks(
    api_url: str,
    table_name: str,
    api_headers: Optional[Dict[str, str]] = None,
    mode: str = 'append'
) -> dict:
    """
    Ingere dados de API REST para Databricks
    """
    
    # Fetch dados da API
    records = fetch_from_api(api_url, headers=api_headers)
    
    if not records:
        print("✗ Nenhum registro obtido da API")
        return {"success": False, "error": "No records"}
    
    # Converte para DataFrame
    df = pd.DataFrame(records)
    
    # Adiciona metadados
    df['_ingestion_timestamp'] = datetime.now()
    df['_source_api'] = api_url
    
    print(f"► Preparando {len(df)} registros para ingestão")
    
    # Conecta ao Databricks
    print("► Conectando ao Databricks...")
    
    try:
        connection = sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        
        cursor = connection.cursor()
        
        # Limpa tabela se mode = overwrite
        if mode == 'overwrite':
            cursor.execute(f"DELETE FROM {table_name}")
        
        # Insere dados
        print(f"► Inserindo {len(df)} registros...")
        
        inserted = 0
        for _, row in df.iterrows():
            columns = ', '.join(row.index)
            values = ', '.join([
                'NULL' if pd.isna(val) else 
                f"'{str(val).replace("'", "''")}'" if isinstance(val, str) else 
                str(val)
                for val in row
            ])
            
            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            
            try:
                cursor.execute(insert_sql)
                inserted += 1
            except Exception as e:
                print(f"✗ Erro: {e}")
        
        cursor.close()
        connection.close()
        
        print(f"✓ Ingestão concluída: {inserted} registros inseridos")
        
        return {"success": True, "rows_inserted": inserted}
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        return {"success": False, "error": str(e)}

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Ingere dados de API para Databricks')
    parser.add_argument('--api-url', type=str, required=True, help='URL da API REST')
    parser.add_argument('--table', type=str, required=True, help='Tabela de destino')
    parser.add_argument('--api-key', type=str, help='API Key (Authorization header)')
    parser.add_argument('--mode', type=str, default='append', choices=['append', 'overwrite'])
    
    args = parser.parse_args()
    
    # Prepara headers se API key fornecida
    headers = None
    if args.api_key:
        headers = {"Authorization": f"Bearer {args.api_key}"}
    
    result = ingest_api_to_databricks(
        api_url=args.api_url,
        table_name=args.table,
        api_headers=headers,
        mode=args.mode
    )
    
    if not result.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    # Exemplo de uso:
    # python ingest-from-api.py \
    #   --api-url "https://api.example.com/v1/data" \
    #   --table "bronze.external_data" \
    #   --api-key "your-api-key"
    
    main()
