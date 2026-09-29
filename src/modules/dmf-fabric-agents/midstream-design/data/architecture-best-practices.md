# Architecture Best Practices

**Reference:** DataArchitect Agent  
**Version:** 1.0

---

## Data Architecture Principles

### 1. Layered Architecture

Organize data into distinct layers with clear purposes:

| Layer | Purpose | Characteristics |
|-------|---------|-----------------|
| **Landing** | Raw ingestion | Source fidelity, append-only |
| **Bronze** | Cleansed | Typed, deduplicated, validated |
| **Silver** | Curated | Business logic, enriched |
| **Gold** | Aggregated | Consumption-ready, optimized |

### 2. Single Source of Truth

- One authoritative source for each business entity
- Clear lineage from source to consumption
- Avoid data duplication across systems
- Use reference tables for shared lookups

### 3. Schema Evolution

- Design for change (new columns, new sources)
- Use flexible formats (Delta, Parquet with schema)
- Version schemas with clear migration paths
- Document breaking vs non-breaking changes

### 4. Separation of Concerns

- Keep storage separate from compute
- Separate orchestration from transformation logic
- Decouple ingestion from processing
- Independent scaling of components

---

## Technology Selection Criteria

### Storage Selection

| Factor | Considerations |
|--------|----------------|
| **Volume** | GB vs TB vs PB scale |
| **Access Pattern** | Sequential vs random |
| **Update Frequency** | Append vs update vs delete |
| **Query Engine** | Spark, SQL, Presto |
| **Cost** | Storage vs egress vs compute |

### Processing Selection

| Factor | Considerations |
|--------|----------------|
| **Latency** | Batch vs streaming |
| **Complexity** | Simple ETL vs ML |
| **Scale** | Single node vs distributed |
| **Team Skills** | SQL vs Python vs Scala |
| **Integration** | Source/target connectivity |

### Orchestration Selection

| Factor | Considerations |
|--------|----------------|
| **Dependencies** | Simple vs complex DAGs |
| **Monitoring** | Built-in vs custom |
| **Alerting** | Native vs integration |
| **Retry Logic** | Automatic vs manual |
| **Cost Model** | Per execution vs flat |

---

## Data Modeling Best Practices

### Dimensional Modeling

**When to Use:**
- BI/reporting workloads
- Known query patterns
- Historical analysis
- Team familiar with star schema

**Key Principles:**
1. Define clear grain for fact tables
2. Use conformed dimensions across facts
3. Apply SCD appropriately
4. Balance normalization vs performance

### Data Vault

**When to Use:**
- Unknown/evolving requirements
- Multiple source systems
- Strong audit requirements
- Agile delivery model

**Key Principles:**
1. Hub = business key
2. Link = relationship
3. Satellite = context/history
4. Hash keys for integration

### One Big Table (OBT)

**When to Use:**
- Simple analytics
- Single subject area
- Performance critical
- BI tool limitations

**Key Principles:**
1. Pre-join all dimensions
2. Accept redundancy
3. Optimize for read
4. Consider refresh complexity

---

## Performance Optimization

### Partitioning Strategy

| Strategy | When to Use |
|----------|-------------|
| **Date-based** | Time-series queries common |
| **Key-based** | Filter by specific values |
| **Hybrid** | Multiple access patterns |

**Best Practices:**
- Partition by common filter columns
- Avoid too many small partitions
- Consider data distribution
- Prune partitions in queries

### Indexing/Clustering

| Strategy | Purpose |
|----------|---------|
| **Z-ordering** | Multi-column filter optimization |
| **Clustering** | Physical co-location |
| **Bloom Filters** | Point lookups |

### Caching

| Level | When to Use |
|-------|-------------|
| **Query Cache** | Repeated queries |
| **Materialized Views** | Expensive aggregations |
| **Pre-aggregation** | Known metrics |

---

## Security Best Practices

### Defense in Depth

1. **Network**: VNets, private endpoints
2. **Identity**: AAD, service principals
3. **Access**: RBAC, ACLs
4. **Data**: Encryption, masking
5. **Audit**: Logging, monitoring

### Row-Level Security

- Implement at serving layer
- Use dynamic filters
- Test with different user contexts
- Consider performance impact

### Column Masking

| Data Type | Masking Approach |
|-----------|------------------|
| PII (names) | Partial redaction |
| SSN/ID | Hash or tokenize |
| Financial | Round or range |
| Dates | Generalize (month/year) |

---

## Data Quality Integration

### Quality Checkpoints

| Layer | Quality Checks |
|-------|----------------|
| Landing → Bronze | Schema validation, null checks |
| Bronze → Silver | Business rules, referential integrity |
| Silver → Gold | Aggregation validation, completeness |

### Quarantine Pattern

1. Validate records on ingestion
2. Pass good records to next layer
3. Route bad records to quarantine
4. Alert on threshold breach
5. Enable investigation and reprocessing

---

## Scalability Patterns

### Horizontal Scaling

- Partition data for parallel processing
- Use distributed compute (Spark, Synapse)
- Design for stateless operations
- Avoid single points of contention

### Vertical Scaling

- Optimize code before scaling up
- Use appropriate VM/cluster sizes
- Monitor resource utilization
- Right-size based on workload

### Cost Optimization

1. Use spot/preemptible instances
2. Auto-scale based on demand
3. Archive historical data
4. Monitor and eliminate waste

---

## Disaster Recovery

### Recovery Patterns

| Pattern | RPO | RTO | Cost |
|---------|-----|-----|------|
| **Hot-Hot** | Near 0 | Near 0 | High |
| **Hot-Warm** | Minutes | Minutes | Medium |
| **Hot-Cold** | Hours | Hours | Low |

### Backup Strategy

1. **Continuous backup** for critical data
2. **Point-in-time recovery** for databases
3. **Geo-redundant storage** for durability
4. **Regular restore testing**

---

## Documentation Standards

### Architecture Document

Must include:
- High-level diagram
- Layer descriptions
- Technology justifications
- Data flow diagrams
- Security approach
- Scalability strategy

### Data Model Document

Must include:
- ERD diagrams
- Table definitions
- Column descriptions
- Relationship mappings
- Naming conventions

### Decision Records

Must include:
- Context and problem
- Decision made
- Alternatives considered
- Consequences

---

## Anti-Patterns to Avoid

### Architecture Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Big Ball of Mud** | No clear structure | Layer architecture |
| **Golden Hammer** | One tech for everything | Right tool for job |
| **Resume Driven** | New tech without need | Business-driven selection |

### Modeling Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Mega Dimension** | Too many attributes | Split into role-playing dims |
| **Junk Drawer** | Unrelated columns together | Purpose-driven tables |
| **Missing History** | No SCD when needed | Plan for historical tracking |

---

## References

- Kimball Group: https://www.kimballgroup.com/
- Data Vault 2.0: https://datavaultalliance.com/
- Microsoft Well-Architected Framework
- Databricks Lakehouse Best Practices

---

*Reference maintained by DataArchitect Agent*
