# Architecture Document Template

# Data Architecture Document

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataArchitect  
**Version:** 1.0

---

## Executive Summary

{2-3 paragraph summary of the architecture approach}

**Architecture Pattern:** {Lakehouse / Data Warehouse / Hybrid}  
**Primary Technology:** {technology}  
**Target Environment:** {cloud/on-premise/hybrid}

---

## Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  SOURCES │───▶│ LANDING  │───▶│  BRONZE  │───▶│  SILVER  │───▶ GOLD │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    ORCHESTRATION & MONITORING                   │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    SECURITY & GOVERNANCE                        │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **{principle_1}**: {description}
2. **{principle_2}**: {description}
3. **{principle_3}**: {description}

---

## Data Layers

### Landing Layer (Raw)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Raw data ingestion, source fidelity |
| **Format** | {Parquet / Delta / CSV} |
| **Retention** | {30 days / configurable} |
| **Access** | ETL processes only |
| **Naming** | `lnd_{source}_{entity}` |

### Bronze Layer (Cleansed)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Cleansed, typed, deduplicated |
| **Format** | {Delta / Parquet} |
| **Retention** | {90 days} |
| **Access** | ETL + Advanced Users |
| **Naming** | `brz_{domain}_{entity}` |

### Silver Layer (Curated)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Business logic, joined, enriched |
| **Format** | {Delta} |
| **Retention** | {1 year} |
| **Access** | Analytics, Data Science |
| **Naming** | `slv_{domain}_{entity}` |

### Gold Layer (Aggregated)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Consumption-ready, aggregated |
| **Format** | {Delta / Semantic Model} |
| **Retention** | {Permanent} |
| **Access** | BI, Reporting, End Users |
| **Naming** | `gld_{domain}_{subject}` |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Storage | {Azure Data Lake / S3 / GCS} | Raw and processed data |
| Processing | {Spark / Databricks / Synapse} | ETL and transformations |
| Orchestration | {ADF / Airflow / Prefect} | Pipeline scheduling |
| Serving | {Delta / SQL Endpoint / Synapse} | Query access |
| BI | {Power BI / Tableau / Looker} | Visualization |
| Governance | {Unity Catalog / Purview} | Metadata and access |

---

## Data Flow

### Ingestion Flow

| Source | Type | Method | Frequency | SLA |
|--------|------|--------|-----------|-----|
| {source_1} | {DB/API/File} | {method} | {freq} | {sla} |
| {source_2} | {type} | {method} | {freq} | {sla} |

### Transformation Flow

```
Landing ──▶ [Clean] ──▶ Bronze ──▶ [Enrich] ──▶ Silver ──▶ [Aggregate] ──▶ Gold
```

---

## Security Architecture

### Access Control

| Layer | Access Level | Method |
|-------|--------------|--------|
| Landing | ETL Service | Service Principal |
| Bronze | ETL + Advanced Users | AAD Groups |
| Silver | Analytics Team | AAD Groups + RLS |
| Gold | All Authorized | AAD + RLS |

### Data Protection

- **Encryption at Rest**: {method}
- **Encryption in Transit**: {method}
- **Key Management**: {approach}

---

## Scalability

| Metric | Current | Expected Growth |
|--------|---------|-----------------|
| Data Volume | {X GB} | {Y% per year} |
| Daily Records | {X records} | {Y% per year} |
| Concurrent Users | {X} | {Y} |

---

## Monitoring & Operations

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Pipeline Success Rate | % of successful runs | < 99% |
| Data Freshness | Time since last update | > SLA |
| Query Performance | P95 latency | > 5s |

---

## Disaster Recovery

| Metric | Target |
|--------|--------|
| **RTO** | {time} |
| **RPO** | {time} |
| **Backup Frequency** | {frequency} |

---

## Architecture Decisions

See `decisions.md` for detailed ADRs.

---

*Document generated by DataArchitect Agent*
