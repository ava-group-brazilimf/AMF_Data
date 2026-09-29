-- ==============================================================================
-- DATABRICKS - CRIACAO DE SCHEMAS (MEDALLION ARCHITECTURE)
-- ==============================================================================
-- Descricao: Cria schemas para arquitetura Medallion (Bronze, Silver, Gold)
-- Autor: Avanade Core - Data Engineering Agents
-- Data: 2026-02-04
-- ==============================================================================

-- Bronze Layer: Dados brutos (raw data)
CREATE SCHEMA IF NOT EXISTS bronze
COMMENT 'Bronze Layer - Raw data ingested from source systems';

-- Silver Layer: Dados limpos e validados
CREATE SCHEMA IF NOT EXISTS silver
COMMENT 'Silver Layer - Cleansed and validated data';

-- Gold Layer: Dados agregados e prontos para consumo
CREATE SCHEMA IF NOT EXISTS gold
COMMENT 'Gold Layer - Business-level aggregations and analytics';

-- Reference Layer: Dados de referencia (lookup tables)
CREATE SCHEMA IF NOT EXISTS reference
COMMENT 'Reference data - Lookup tables and master data';
