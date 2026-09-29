# Data Modeling Best Practices

## Dimensional Modeling

### Star Schema Design

1. **Facts vs Dimensions**
   - Facts contain measures (numeric, additive)
   - Dimensions contain descriptive attributes
   - Keep facts narrow, dimensions wide

2. **Granularity First**
   - Always define grain before designing
   - Document grain explicitly
   - Grain drives everything else

3. **Conformed Dimensions**
   - Reuse dimensions across facts
   - Ensure consistent keys
   - Maintain single source of truth

### SCD Types

| Type | Description | Use Case |
|------|-------------|----------|
| Type 1 | Overwrite | No history needed |
| Type 2 | Add new row | Full history required |
| Type 3 | Add column | Limited history |

### Naming Conventions

```
fact_{subject}          - fact_sales, fact_orders
dim_{entity}            - dim_customer, dim_product
bridge_{relationship}   - bridge_customer_segment
ref_{lookup}           - ref_country, ref_currency
```

---

## Data Contracts

### Contract Structure

```yaml
contract:
  name: "{source}_to_{target}"
  version: "1.0.0"
  owner: "{team}"
  
  schema:
    - name: column_name
      type: data_type
      nullable: boolean
      description: "..."
      
  sla:
    freshness: "daily"
    quality_threshold: 99.5
    
  evolution:
    breaking_changes: "versioned"
    deprecation_period: "30 days"
```

### Schema Evolution Rules

- **Non-breaking**: Add nullable column, add default value
- **Breaking**: Remove column, change type, change key

---

## Metrics Documentation

### Metric Template

```yaml
metric:
  name: "revenue_ytd"
  display_name: "Revenue Year to Date"
  description: "Total revenue from start of year"
  
  formula: "SUM(fact_sales.amount) WHERE date >= year_start"
  
  aggregations:
    allowed: [SUM, AVG]
    default: SUM
    
  filters:
    - date_range
    - region
    
  owner: "Finance Team"
  sla: "Daily by 6 AM"
```

---

## Quality Guidelines

1. **No circular dependencies** between tables
2. **No orphan entities** without relationships
3. **Consistent granularity** within a model
4. **Complete documentation** for all entities
5. **Clear ownership** for all metrics
