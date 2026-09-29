# ⚙️ Code Generation Best Practices

> **Agent:** Coda | **Reference:** Code generation standards and patterns for the AI-Agent Migration Factory™

---

## 1. PySpark Code Standards

### 1.1 Imports and Structure

```python
# Standard import ordering
# 1. Python standard library
from datetime import datetime
import logging

# 2. PySpark imports
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, lit, when, coalesce, trim, upper
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from pyspark.sql.window import Window

# 3. Delta Lake imports
from delta.tables import DeltaTable

# 4. Project-specific imports
from config import get_pipeline_config
```

### 1.2 Function Design

```python
def transform_customer_data(
    df_source: DataFrame,
    df_lookup: DataFrame,
    load_date: str
) -> DataFrame:
    """Transform raw customer data applying business rules.

    Args:
        df_source: Raw customer DataFrame from source system.
        df_lookup: Lookup table for region mapping.
        load_date: Processing date in YYYY-MM-DD format.

    Returns:
        Transformed DataFrame ready for Delta Lake write.

    Raises:
        ValueError: If df_source is empty.
        SchemaError: If required columns are missing.
    """
    if df_source.isEmpty():
        raise ValueError("Source DataFrame is empty — aborting transformation")

    # Apply transformations
    df_result = (
        df_source
        .withColumn("customer_name", trim(upper(col("raw_name"))))
        .withColumn("region", coalesce(col("region_code"), lit("UNKNOWN")))
        .withColumn("load_date", lit(load_date))
        .withColumn("processed_at", lit(datetime.now().isoformat()))
    )

    return df_result
```

### 1.3 Naming Conventions

| Element          | Convention              | Example                          |
|------------------|-------------------------|----------------------------------|
| Variables        | snake_case              | `df_customer`, `load_date`       |
| Functions        | snake_case              | `transform_customer_data()`      |
| Constants        | UPPER_SNAKE_CASE        | `MAX_RETRIES`, `DEFAULT_SCHEMA`  |
| Classes          | PascalCase              | `PipelineConfig`                 |
| DataFrames       | `df_` prefix            | `df_source`, `df_result`         |
| Temp views       | `tmp_` prefix           | `tmp_customer_staging`           |
| Delta tables     | `catalog.schema.table`  | `migration.curated.dim_customer` |

### 1.4 Error Handling

```python
try:
    df_result = transform_customer_data(df_source, df_lookup, load_date)
except ValueError as e:
    logger.error(f"Validation error: {e}")
    metrics["status"] = "FAILED"
    metrics["error"] = str(e)
    raise
except AnalysisException as e:
    logger.error(f"Spark analysis error: {e}")
    metrics["status"] = "FAILED"
    raise
except Exception as e:
    logger.error(f"Unexpected error in transform: {e}")
    metrics["status"] = "FAILED"
    raise
finally:
    metrics["end_time"] = datetime.now().isoformat()
    log_metrics(metrics)
```

---

## 2. Delta Lake Patterns

### 2.1 Write Operations

```python
# Overwrite (Full Load)
df_result.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("catalog.schema.table_name")

# Append (Incremental Load)
df_result.write \
    .format("delta") \
    .mode("append") \
    .saveAsTable("catalog.schema.table_name")

# Merge (Upsert) — see Delta Merge pattern below
```

### 2.2 MERGE (Upsert) Pattern

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forName(spark, "catalog.schema.dim_customer")

(delta_table.alias("target")
    .merge(
        df_updates.alias("source"),
        "target.customer_id = source.customer_id"
    )
    .whenMatchedUpdate(
        condition="source.updated_at > target.updated_at",
        set={
            "customer_name": "source.customer_name",
            "region": "source.region",
            "updated_at": "source.updated_at",
            "load_date": "source.load_date"
        }
    )
    .whenNotMatchedInsert(
        values={
            "customer_id": "source.customer_id",
            "customer_name": "source.customer_name",
            "region": "source.region",
            "created_at": "source.created_at",
            "updated_at": "source.updated_at",
            "load_date": "source.load_date"
        }
    )
    .execute()
)
```

### 2.3 SCD Type 2 Pattern

```python
# Step 1: Identify changes
df_changes = (
    df_source.alias("src")
    .join(df_target.alias("tgt"),
          (col("src.business_key") == col("tgt.business_key")) &
          (col("tgt.is_current") == lit(True)),
          "left")
    .where(
        col("tgt.business_key").isNull() |  # New records
        (col("src.hash_value") != col("tgt.hash_value"))  # Changed records
    )
)

# Step 2: Close existing records
(delta_table.alias("target")
    .merge(
        df_changes.alias("updates"),
        "target.business_key = updates.business_key AND target.is_current = true"
    )
    .whenMatchedUpdate(
        set={
            "is_current": lit(False),
            "effective_end_date": lit(datetime.now().isoformat()),
            "updated_at": lit(datetime.now().isoformat())
        }
    )
    .execute()
)

# Step 3: Insert new/changed records
df_new_records = (
    df_changes
    .withColumn("is_current", lit(True))
    .withColumn("effective_start_date", lit(datetime.now().isoformat()))
    .withColumn("effective_end_date", lit("9999-12-31"))
    .withColumn("surrogate_key", monotonically_increasing_id())
)
df_new_records.write.format("delta").mode("append").saveAsTable("catalog.schema.dim_table")
```

### 2.4 Table Maintenance

```sql
-- Optimize file sizes
OPTIMIZE catalog.schema.table_name;

-- Z-ORDER for query performance
OPTIMIZE catalog.schema.table_name ZORDER BY (customer_id, transaction_date);

-- Clean up old versions (retain 7 days)
VACUUM catalog.schema.table_name RETAIN 168 HOURS;

-- Analyze table statistics
ANALYZE TABLE catalog.schema.table_name COMPUTE STATISTICS FOR ALL COLUMNS;
```

---

## 3. Unit Testing

### 3.1 Test Structure

```python
"""Tests for pipeline: PL_CUSTOMER_MASTER
Generated by Coda ⚙️ — AI-Agent Migration Factory™
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from chispa.dataframe_comparer import assert_df_equality

# ---- Fixtures ----

@pytest.fixture(scope="session")
def spark():
    return (SparkSession.builder
            .master("local[2]")
            .appName("test_pl_customer_master")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.default.parallelism", "2")
            .getOrCreate())

@pytest.fixture
def sample_data(spark):
    data = [
        ("C001", "John Doe", "US", "2026-01-01"),
        ("C002", "Jane Smith", "BR", "2026-01-01"),
    ]
    schema = StructType([
        StructField("customer_id", StringType(), False),
        StructField("customer_name", StringType(), True),
        StructField("region", StringType(), True),
        StructField("load_date", StringType(), False),
    ])
    return spark.createDataFrame(data, schema)
```

### 3.2 Assertion Patterns

```python
# Schema assertion
def test_output_schema(spark, result_df):
    expected_fields = ["customer_id", "customer_name", "region", "load_date", "processed_at"]
    assert result_df.columns == expected_fields

# Row count
def test_row_count(spark, result_df, source_df):
    assert result_df.count() == source_df.count()

# Data quality
def test_no_nulls_in_key(spark, result_df):
    null_count = result_df.where(col("customer_id").isNull()).count()
    assert null_count == 0, f"Found {null_count} null customer_ids"

# DataFrame equality (using chispa)
def test_transformation_output(spark, result_df, expected_df):
    assert_df_equality(result_df, expected_df, ignore_row_order=True)
```

### 3.3 Edge Case Templates

```python
def test_empty_input(spark, transform_func):
    empty_df = spark.createDataFrame([], schema)
    with pytest.raises(ValueError, match="Source DataFrame is empty"):
        transform_func(empty_df)

def test_null_values(spark, transform_func):
    data = [("C001", None, None, "2026-01-01")]
    df = spark.createDataFrame(data, schema)
    result = transform_func(df)
    # Nulls should be replaced with defaults
    assert result.where(col("customer_name").isNull()).count() == 0

def test_duplicate_keys(spark, transform_func):
    data = [
        ("C001", "John", "US", "2026-01-01"),
        ("C001", "John Updated", "US", "2026-01-02"),
    ]
    df = spark.createDataFrame(data, schema)
    result = transform_func(df)
    # Should keep latest by load_date
    assert result.count() == 1
```

---

## 4. Job Configuration

### 4.1 Cluster Sizing Guide

| Data Volume    | Workers  | Node Type         | Memory/Node | Notes                    |
|---------------|----------|-------------------|-------------|--------------------------|
| < 1 GB        | 1–2      | Standard_DS3_v2   | 14 GB       | Dev/test workloads       |
| 1–10 GB       | 2–4      | Standard_DS4_v2   | 28 GB       | Standard batch           |
| 10–100 GB     | 4–8      | Standard_DS5_v2   | 56 GB       | Large batch              |
| 100 GB–1 TB   | 8–16     | Standard_E8s_v3   | 64 GB       | Memory-optimized         |
| > 1 TB        | 16–32    | Standard_E16s_v3  | 128 GB      | Heavy processing         |

### 4.2 Spark Configuration Standards

```json
{
  "spark_conf": {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.autoCompact.enabled": "true",
    "spark.sql.shuffle.partitions": "auto",
    "spark.databricks.io.cache.enabled": "true",
    "spark.sql.sources.partitionOverwriteMode": "dynamic"
  }
}
```

### 4.3 Retry and Timeout Strategy

| Pipeline Type    | Timeout    | Max Retries | Retry Interval |
|-----------------|------------|-------------|----------------|
| Simple ETL      | 30 min     | 2           | 5 min          |
| Complex Join    | 60 min     | 2           | 5 min          |
| SCD Type 2      | 90 min     | 1           | 10 min         |
| Full Load       | 120 min    | 1           | 10 min         |
| Streaming       | Continuous | 3           | 1 min          |

---

## 5. Performance Optimization

### 5.1 Join Optimization Decision Tree

```
Is small table < 10MB?
  ├─ YES → broadcast(small_table)
  └─ NO
      Is small table < 100MB?
        ├─ YES → broadcast if driver memory > 4GB
        └─ NO
            Is join key skewed?
              ├─ YES → salt the key + repartition
              └─ NO → SortMergeJoin (default)
```

### 5.2 Partition Strategy Guide

```
Is data time-series?
  ├─ YES
  │   Is data volume > 10GB/day?
  │     ├─ YES → partitionBy("year", "month", "day")
  │     └─ NO  → partitionBy("year", "month")
  └─ NO
      Is there a natural partition key?
        ├─ YES → partitionBy(natural_key) if cardinality < 1000
        └─ NO  → No partition, use Z-ORDER instead
```

### 5.3 Anti-Patterns to Avoid

| Anti-Pattern                        | Better Approach                              |
|-------------------------------------|----------------------------------------------|
| `collect()` on large DataFrames     | Use DataFrame operations or `toPandas()` on aggregated data |
| Python UDFs                         | Use Spark built-in functions or Pandas UDFs  |
| `df.count()` for null check         | Use `df.isEmpty()` (Spark 3.3+)             |
| Over-partitioning (many small files)| Fewer partitions + OPTIMIZE                  |
| Caching everything                  | Cache only reused DataFrames (≥2 uses)       |
| Nested loops with DataFrames        | Use joins or window functions                |
| `repartition(1)` for "single file"  | Use `coalesce(1)` or Delta OPTIMIZE         |

---

## 6. Code Organization

### 6.1 Notebook Structure

```
# Databricks notebook source

# COMMAND ----------
# MAGIC %md
# MAGIC # Pipeline: {pipeline_id}
# MAGIC Generated by Coda ⚙️ — AI-Agent Migration Factory™
# MAGIC
# MAGIC | Property | Value |
# MAGIC |----------|-------|
# MAGIC | Source    | SAP MARA, SAP MARC |
# MAGIC | Target   | migration.curated.dim_material |
# MAGIC | Pattern  | SCD Type 2 |
# MAGIC | Schedule | Daily 06:00 UTC |

# COMMAND ----------
# Widget parameters
dbutils.widgets.text("environment", "production")
dbutils.widgets.text("load_date", "")
dbutils.widgets.text("source_schema", "raw")
dbutils.widgets.text("target_schema", "curated")

# COMMAND ----------
# Imports and configuration
import logging
from datetime import datetime
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1: Load Source Data

# COMMAND ----------
# Source loading functions

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2: Transformations

# COMMAND ----------
# Transformation functions

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3: Data Quality Checks

# COMMAND ----------
# Quality validation

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4: Write to Target

# COMMAND ----------
# Delta Lake write / merge

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5: Post-Processing

# COMMAND ----------
# Metrics logging, OPTIMIZE, cleanup
```

### 6.2 Module Organization (for complex pipelines)

```
pipeline_package/
├── __init__.py
├── config.py          # Configuration and constants
├── sources.py         # Source data loading functions
├── transforms.py      # Transformation functions
├── quality.py         # Data quality check functions
├── writers.py         # Target write functions
├── utils.py           # Helper/utility functions
└── metrics.py         # Logging and metrics
```

### 6.3 Documentation Standards

Every generated file must include:

1. **File header** — Pipeline ID, generation date, agent version
2. **Function docstrings** — Google style with Args, Returns, Raises
3. **Inline comments** — For complex business logic only (not obvious code)
4. **Metadata cell** — Source/target/pattern/schedule in notebook header

---

> **Coda ⚙️** — *"Boas práticas aplicadas. Código de produção desde a geração."*
