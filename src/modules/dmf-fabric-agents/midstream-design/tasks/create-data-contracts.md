# Task: Create Data Contracts

**Command:** `*data-contracts` / `*DC`  
**Output:** `data-contracts.md`

---

## Objective

Define data contracts for all inputs (sources) and outputs (consumers) to ensure data quality and schema consistency.

---

## Prerequisites

- [ ] Data model complete
- [ ] Source systems identified
- [ ] Consumers identified
- [ ] SLAs known

---

## Steps

### Step 1: Identify Sources

List all data sources:
- Files (CSV, Parquet, JSON)
- APIs
- Databases
- Streaming sources

### Step 2: Define Input Contracts

For each source, create a contract:

```yaml
contract:
  name: "{source}_input"
  version: "1.0.0"
  owner: "{source_team}"
  
  source:
    type: "csv|api|database|stream"
    location: "path or endpoint"
    format: "csv|json|parquet"
    
  schema:
    - name: column_name
      type: string|int|decimal|date|timestamp
      nullable: true|false
      description: "..."
      validation:
        - rule: "not_null"
        - rule: "unique"
        
  freshness:
    expected: "daily|hourly|real-time"
    max_delay: "2 hours"
    
  quality:
    completeness: 99%
    validity: 99%
```

### Step 3: Identify Consumers

List all data consumers:
- BI tools
- ML models
- Reports
- Downstream systems

### Step 4: Define Output Contracts

For each output, create a contract:

```yaml
contract:
  name: "{target}_output"
  version: "1.0.0"
  owner: "{data_team}"
  
  schema:
    - name: column_name
      type: data_type
      nullable: boolean
      description: "..."
      
  sla:
    freshness: "daily by 6 AM"
    availability: 99.9%
    
  breaking_changes:
    notification: "30 days advance"
    versioning: "semantic"
```

### Step 5: Define Evolution Rules

Document how schemas can evolve:

| Change Type | Impact | Policy |
|-------------|--------|--------|
| Add nullable column | Non-breaking | Immediate |
| Add with default | Non-breaking | Immediate |
| Remove column | Breaking | 30-day notice |
| Change type | Breaking | 30-day notice |
| Rename column | Breaking | 30-day notice |

### Step 6: Document Contracts

Create `data-contracts.md` with all contracts organized by:
- Input contracts
- Output contracts
- Evolution policies
- SLAs

---

## Output Template

```markdown
# Data Contracts

## Input Contracts

### {Source 1}
[Contract YAML]

### {Source 2}
[Contract YAML]

## Output Contracts

### {Target 1}
[Contract YAML]

## Evolution Policy
[Rules table]

## SLA Summary
[SLA table]
```

---

## Validation

- [ ] All sources have contracts
- [ ] All consumers have contracts
- [ ] Schemas match data model
- [ ] SLAs are realistic
- [ ] Evolution rules defined
