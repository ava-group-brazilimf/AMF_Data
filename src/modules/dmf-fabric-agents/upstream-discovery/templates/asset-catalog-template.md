# Asset Catalog Template

**Project:** [Project Name]  
**Scanned:** [Date]  
**Repository:** [Path]  
**Scout Version:** 1.0.0

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Total Pipelines/Jobs** | [count] |
| **Total Data Sources** | [count] |
| **Total Datasets** | [count] |
| **Scheduled Jobs** | [count] |
| **Configuration Files** | [count] |

---

## 1. Pipelines & Jobs

### Summary by Technology

| Technology | Count | Status Distribution |
|------------|-------|---------------------|
| Azure Data Factory | - | Active: X, Inactive: Y |
| Databricks | - | Active: X, Inactive: Y |
| Apache Airflow | - | Active: X, Inactive: Y |
| SAP BODS | - | Active: X, Inactive: Y |
| SSIS | - | Active: X, Inactive: Y |
| **TOTAL** | - | Active: X, Inactive: Y |

### Detailed Catalog

| ID | Name | Technology | Status | File Path | Schedule | Owner |
|----|------|------------|--------|-----------|----------|-------|
| P001 | [Pipeline Name] | ADF | Active | pipelines/sales.json | Daily | [Team] |
| P002 | [Pipeline Name] | Databricks | Active | notebooks/etl_orders.py | Hourly | [Team] |
| P003 | [Pipeline Name] | Airflow | Inactive | dags/legacy_dag.py | - | [Team] |
| ... | ... | ... | ... | ... | ... | ... |

---

## 2. Data Sources

### Summary by Type

| Type | Count | Examples |
|------|-------|----------|
| SQL Server | - | Sales DB, HR DB |
| Oracle | - | ERP DB |
| PostgreSQL | - | CRM DB |
| Azure SQL | - | Staging DB |
| REST API | - | Salesforce API, SAP API |
| File System | - | CSV files, JSON files |
| Cloud Storage | - | Azure Blob, S3 |
| **TOTAL** | - | - |

### Detailed Catalog

| ID | Name | Type | Connection Reference | Environment | Status |
|----|------|------|---------------------|-------------|--------|
| DS001 | SQL_Server_SalesDB | SQL Server | LinkedService_SQL | Production | Active |
| DS002 | API_Salesforce | REST API | LinkedService_SFDC | Production | Active |
| DS003 | Blob_RawFiles | Azure Blob | LinkedService_Blob | Production | Active |
| ... | ... | ... | ... | ... | ... |

---

## 3. Datasets

### Summary by Location

| Location Type | Count | Examples |
|--------------|-------|----------|
| Database Tables | - | fact_sales, dim_customer |
| Views | - | vw_sales_summary |
| Files (CSV) | - | sales_data.csv |
| Files (Parquet) | - | orders.parquet |
| Files (JSON) | - | customer_data.json |
| **TOTAL** | - | - |

### Detailed Catalog

| ID | Name | Type | Location | Est. Row Count | Last Modified |
|----|------|------|----------|----------------|---------------|
| DT001 | fact_sales | Table | SQL_DW/dbo.fact_sales | 10M | 2026-02-01 |
| DT002 | dim_customer | Table | SQL_DW/dbo.dim_customer | 1.2M | 2026-01-15 |
| DT003 | sales_raw | CSV | Blob/raw/sales/*.csv | 5M | 2026-02-10 |
| ... | ... | ... | ... | ... | ... |

---

## 4. Scheduled Jobs

### Summary by Frequency

| Frequency | Count | Examples |
|-----------|-------|----------|
| Real-time/Streaming | - | Event-driven pipelines |
| Hourly | - | High-frequency ETL |
| Daily | - | Standard batch jobs |
| Weekly | - | Aggregation jobs |
| Monthly | - | Reporting jobs |
| On-demand | - | Manual/Ad-hoc |
| **TOTAL** | - | - |

### Detailed Catalog

| ID | Job Name | Technology | Schedule | Trigger Type | Status |
|----|----------|------------|----------|--------------|--------|
| J001 | SalesIngestion | ADF | Daily 2:00 AM | Time | Active |
| J002 | OrdersProcessing | Databricks | Hourly | Time | Active |
| J003 | WeeklyAggregate | Airflow | Weekly Sun 6:00 AM | Cron | Active |
| ... | ... | ... | ... | ... | ... |

---

## 5. Configuration Files

### Summary by Type

| Type | Count | Location |
|------|-------|----------|
| Connection Strings (.properties) | - | /config/ |
| Environment Variables (.env) | - | /config/ |
| YAML Configs (.yaml) | - | /config/, /airflow/ |
| JSON Configs (.json) | - | /config/, /adf/ |
| XML Configs (.xml) | - | /config/, /bods/ |
| Terraform (.tf) | - | /infrastructure/ |
| **TOTAL** | - | - |

### Detailed Catalog

| ID | File Name | Type | Environment | Contains Secrets | Status |
|----|-----------|------|-------------|------------------|--------|
| CF001 | database.properties | Properties | Production | ⚠️ Yes (vault refs) | Active |
| CF002 | airflow.cfg | INI | Production | ✅ No | Active |
| CF003 | app-config.yaml | YAML | All | ⚠️ Yes (vault refs) | Active |
| ... | ... | ... | ... | ... | ... |

---

## 6. Dependencies & Relationships

### Critical Dependencies

| Source | Depends On | Type | Impact |
|--------|-----------|------|--------|
| Pipeline: SalesIngestion | DataSource: SQL_SalesDB | READ | High |
| Pipeline: SalesIngestion | Dataset: staging_sales | WRITE | High |
| Pipeline: OrdersETL | Pipeline: SalesIngestion | SEQUENTIAL | Medium |
| ... | ... | ... | ... |

---

## 7. External Dependencies

### Third-Party Services

| Service | Purpose | Used By | Status |
|---------|---------|---------|--------|
| Azure Key Vault | Secrets management | All pipelines | Active |
| Azure DevOps | CI/CD | Deployment | Active |
| Salesforce API | Customer data | Sales pipelines | Active |
| SAP API | ERP data | Finance pipelines | Active |
| ... | ... | ... | ... |

### External Libraries

| Library | Version | Language | Used By |
|---------|---------|----------|---------|
| pyspark | 3.3.0 | Python | Databricks jobs |
| pandas | 1.5.2 | Python | Data processing |
| sqlalchemy | 1.4.41 | Python | DB connections |
| ... | ... | ... | ... |

---

## 8. Dead Code & Unused Assets

### Unused Pipelines

| Pipeline | Reason | Last Used | Recommendation |
|----------|--------|-----------|----------------|
| [Name] | No schedule | Never | Archive |
| [Name] | No references | 6 months ago | Archive |
| [Name] | Marked "backup" | 1 year ago | Delete |
| ... | ... | ... | ... |

### Unused Configurations

| Config File | Reason | Recommendation |
|------------|--------|----------------|
| old_config.properties | Superseded | Archive |
| backup.env | Not referenced | Delete |
| ... | ... | ... |

---

## 9. Red Flags & Issues

### Security Issues

| Issue | Location | Severity | Recommendation |
|-------|----------|----------|----------------|
| Hard-coded password | [file path], line X | 🔴 Critical | Move to Key Vault |
| Exposed API key | [file path], line Y | 🔴 Critical | Move to Key Vault |
| Weak connection string | [file path] | 🟡 Medium | Use managed identity |
| ... | ... | ... | ... |

### Technical Debt

| Issue | Location | Impact | Recommendation |
|-------|----------|--------|----------------|
| Monolithic notebook (2000+ lines) | [file path] | 🟡 Medium | Refactor into modules |
| No error handling | [pipeline] | 🟡 Medium | Add try-catch blocks |
| Hard-coded values | [file path] | 🟡 Medium | Use parameters |
| ... | ... | ... | ... |

---

## 10. Metadata

### Scan Details

| Attribute | Value |
|-----------|-------|
| **Scout Version** | 1.0.0 |
| **Scan Date** | [Date] |
| **Scan Duration** | [Duration] |
| **Repository Path** | [Path] |
| **Total Files Scanned** | [Count] |
| **Parse Success Rate** | [%] |
| **Technologies Detected** | [Count] |

### Quality Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Parse Success Rate | X% | > 95% | ✅ Pass |
| Credential Detection | 100% | 100% | ✅ Pass |
| Asset Coverage | X% | > 98% | ✅ Pass |
| Documentation Quality | X% | > 80% | ⚠️ Review |

---

## Next Steps

1. ✅ Review asset catalog with stakeholders
2. ⏭️ Handoff to BusinessAnalyst (Mary) for STTM creation
3. ⏭️ Address security red flags (hard-coded credentials)
4. ⏭️ Plan remediation for technical debt
5. ⏭️ Archive unused assets after approval

---

**Generated by:** InventoryScout Agent 🔍  
**Date:** [Timestamp]  
**Version:** 1.0.0
