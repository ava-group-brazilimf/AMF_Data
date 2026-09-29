---
task: create-semantic-model
version: 1.0
elicit: true
description: Design and implement a Power BI semantic model with proper star schema, relationships, and metadata
---

# Create Semantic Model

## Purpose
Design a comprehensive semantic model (data model) for Power BI that follows star schema principles, establishes proper relationships, and includes business-friendly naming and descriptions.

## Process

### Step 1: Gather Requirements
ASK the user for the following information:

1. **Data Sources**: What tables/views will be included in the model?
2. **Business Domain**: What business area does this model serve? (Sales, Finance, HR, etc.)
3. **Key Metrics**: What are the primary KPIs and measures needed?
4. **Grain**: What is the lowest level of detail for fact tables?
5. **User Personas**: Who will use this model? (Executives, Analysts, Operations)
6. **Historical Depth**: How far back should data go?
7. **Refresh Frequency**: Real-time, daily, hourly?

### Step 2: Design Model Architecture

CREATE a model design covering:

**Fact Tables**
- Identify transaction/event tables
- Define grain (level of detail)
- Identify foreign keys to dimensions
- Plan aggregation strategies

**Dimension Tables**
- Identify descriptive entities
- Plan for slowly changing dimensions
- Design hierarchies
- Create surrogate keys

**Relationships**
- Define cardinality (1:*, *:1)
- Set cross-filter direction
- Identify active vs inactive relationships

### Step 3: Generate Artifacts

PRODUCE the following deliverables:

1. **Model Diagram** (Text-based ERD)
   - Tables and relationships
   - Cardinality notation
   - Key columns highlighted

2. **Table Definitions** (TMDL/JSON format)
   - Column names and types
   - Display folders
   - Descriptions and formatting
   - Sort by columns

3. **Relationship Definitions**
   - From/To tables and columns
   - Cardinality and direction
   - Active/Inactive status

4. **Hierarchy Definitions**
   - Date hierarchies
   - Geographic hierarchies
   - Organizational hierarchies

### Step 4: Document Model

CREATE documentation including:
- Business glossary
- Data lineage
- Refresh schedule
- Security requirements

## Output Structure

```
semantic-model/
├── model/
│   ├── tables/
│   │   ├── fact-sales.tmdl
│   │   ├── dim-date.tmdl
│   │   ├── dim-customer.tmdl
│   │   └── dim-product.tmdl
│   ├── relationships.tmdl
│   └── model.tmdl
├── docs/
│   ├── data-dictionary.md
│   ├── model-diagram.md
│   └── business-glossary.md
└── README.md
```

## Quality Criteria

- [ ] Star schema structure (no snowflaking unless justified)
- [ ] All relationships defined with proper cardinality
- [ ] Descriptive names (no abbreviations)
- [ ] All columns have descriptions
- [ ] Proper data types assigned
- [ ] Hierarchies created for drill-down
- [ ] Date table marked and complete
- [ ] No circular dependencies
