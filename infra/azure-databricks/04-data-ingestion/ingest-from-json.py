#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
DATABRICKS - INGESTÃO DE DADOS DE JSON
═══════════════════════════════════════════════════════════════════════════════
Descrição: Lê arquivos JSON locais e insere no Databricks
Autor: Avanade Core - Data Engineering Agents
Data: 2026-02-04
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from dotenv import load_dotenv
from databricks import sql

# Carrega configuração
load_dotenv()

DATABRICKS_HOST = os.getenv('DATABRICKS_HOST', '').replace('https://', '').replace('http://', '')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH')

# ══════════════════════════════════════════════════════════════════════════════
# INGESTÃO JSON
# ══════════════════════════════════════════════════════════════════════════════

def ingest_json_to_databricks(
    json_path: Path,
    table_name: str,
    mode: str = 'append'
) -> dict:
    """
    Ingere dados de JSON para Databricks
    
    Suporta:
    - JSON Lines (cada linha é um objeto)
    - Array de objetos
    - Objeto único
    """
    
    print(f"► Lendo arquivo JSON: {json_path.name}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            # Tenta detectar o formato
            first_char = f.read(1)
            f.seek(0)
            
            if first_char == '[':
                # Array de objetos
                data = json.load(f)
            elif first_char == '{':
                # Pode ser objeto único ou JSON Lines
                content = f.read()
                try:
                    # Tenta como objeto único
                    data = [json.loads(content)]
                except:
                    # Tenta como JSON Lines
                    data = [json.loads(line) for line in content.split('\n') if line.strip()]
            else:
                raise ValueError("Formato JSON não reconhecido")
        
        # Converte para DataFrame
        df = pd.DataFrame(data)
        
        # Adiciona metadados
        df['_ingestion_timestamp'] = datetime.now()
        df['_source_file'] = json_path.name
        
        print(f"✓ JSON carregado: {len(df)} registros, {len(df.columns)} campos")
        
        # Conecta ao Databricks
        print("► Conectando ao Databricks...")
        
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
    parser = argparse.ArgumentParser(description='Ingere JSON para Databricks')
    parser.add_argument('--file', type=str, required=True, help='Caminho para o arquivo JSON')
    parser.add_argument('--table', type=str, required=True, help='Tabela de destino')
    parser.add_argument('--mode', type=str, default='append', choices=['append', 'overwrite'])
    
    args = parser.parse_args()
    
    json_path = Path(args.file)
    
    if not json_path.exists():
        print(f"✗ Arquivo não encontrado: {json_path}")
        sys.exit(1)
    
    result = ingest_json_to_databricks(json_path, args.table, args.mode)
    
    if not result.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    main()
