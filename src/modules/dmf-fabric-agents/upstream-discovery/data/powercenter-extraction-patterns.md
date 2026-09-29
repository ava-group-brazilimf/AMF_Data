# PowerCenter Extraction Patterns
# Referência: Mapeamento de transformações PowerCenter → Pseudocode → PySpark
# Carregado por: logic-extractor quando language = InformaticaPowerCenterXML

---

## Aggregator
**Extração:** GROUP BY fields nos ports com `GROUP BY = True`, expressões de OUTPUT ports.
**Pseudocode:**
```
AGGREGATE input_table
GROUP BY [group_by_fields]
COMPUTE [output_port = expression, ...]
OUTPUT aggregated_table
```
**PySpark:**
```python
df_agg = df.groupBy([group_by_fields]).agg(
    F.sum("field").alias("output_field"),
    F.count("*").alias("count_field")
)
```

---

## Expression
**Extração:** Expressão de cada OUTPUT port.
**Pseudocode:**
```
FOR EACH row in input_table:
  COMPUTE output_col = expression
OUTPUT transformed_table
```
**PySpark:**
```python
df = df.withColumn("output_col", expr("expression"))
```

---

## Filter
**Extração:** Atributo `FILTEREXPRESSION`.
**PySpark:**
```python
df_filtered = df.filter(expr("filter_expression"))
```

---

## Joiner
**Extração:** `JoinType` (Normal=inner, Master Outer=right, Detail Outer=left,
Full Outer=outer), `JoinCondition`.
**PySpark:**
```python
join_map = {"Normal":"inner","Master Outer":"right",
            "Detail Outer":"left","Full Outer":"outer"}
df = df_detail.join(df_master, on=join_condition, how=join_map[join_type])
```
> ⚠️ Usar broadcast hint na tabela menor se volume < 200 MB.

---

## Lookup
**Extração:** `LOOKUPTABLENAME`, `LOOKUPCONDITION`, ports de retorno, cache mode.
**PySpark:**
```python
# Connected Lookup
df = df.join(df_lookup.hint("broadcast"), on=lookup_condition, how="left")
# Lookup com SQL Override → extrair query e passar pelo SQL parser antes
```

---

## Router
**Extração:** OUTPUT GROUPs com `FILTEREXPRESSION` por grupo.
**PySpark:**
```python
df_g1 = df.filter(expr("condition_1"))
df_g2 = df.filter(expr("condition_2"))
df_default = df.filter(~expr("condition_1") & ~expr("condition_2"))
```

---

## Update Strategy
**Extração:** `UPDATESTRATEGYEXPRESSION` com DD_INSERT, DD_UPDATE, DD_DELETE.
**PySpark (Delta Lake):**
```python
from delta.tables import DeltaTable
DeltaTable.forName(spark, "target_table").merge(
    source=df_source, condition="target.key = source.key"
).whenMatchedUpdate(set={...}).whenNotMatchedInsert(values={...}).execute()
```

---

## Sorter
**PySpark:**
```python
df = df.orderBy([F.col("f1").asc(), F.col("f2").desc()])
```

---

## Union
**PySpark:**
```python
df = df_g1.unionByName(df_g2).unionByName(df_g3)
```

---

## Sequence Generator
**Extração:** `START_VALUE`, `INCREMENT_BY`, `CYCLE`.
**PySpark:**
```python
df = df.withColumn("seq", F.row_number().over(Window.orderBy(F.lit(1))))
```
> `row_number()` para sequências contíguas; `monotonically_increasing_id()` para
> alto volume sem necessidade de contiguidade.

---

## Normalizer (COBOL/DB2)
**PySpark:**
```python
df = df.select("key", F.explode(F.array([F.col(f"f_{i}") for i in range(1,n+1)])).alias("value"))
```

---

## Source Qualifier SQL Override
> Extrair SQL completo e registrar em `sql_overrides[]` no pseudocode.
> Processar separadamente via `*extract-logic` com `language=SQL`.

---

## Java Transformation / External Procedure
> **Não suportado para auto-extração.**
> Registrar `manual_migration_required: true`, documentar ports e descrição.

---

## Mapeamento de tipos de dados

| PowerCenter | PySpark / Delta Lake |
|---|---|
| String(n) | StringType() |
| Number(p,s) | DecimalType(p,s) |
| Integer | IntegerType() |
| Bigint | LongType() |
| Float | FloatType() |
| Double | DoubleType() |
| Date/Time | TimestampType() |
| Date | DateType() |
| Binary | BinaryType() |

---

## Confidence scoring

| Condição | Ajuste |
|---|---|
| Apenas Aggregator/Expression/Filter/Sorter | +0.10 |
| Lookup com cache=YES | +0.05 |
| SQL Override presente | −0.15 |
| JavaTransformation presente | −0.40 (mínimo LOW) |
| ExternalProcedure presente | −0.30 |
| Cross-folder Shortcut sem definição local | −0.10 |
| Normalizer (COBOL source) | −0.20 |
