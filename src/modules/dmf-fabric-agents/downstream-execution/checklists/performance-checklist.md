---
checklist: performance-checklist
version: 1.0
description: Power BI performance optimization checklist
---

# Performance Optimization Checklist

## Data Model Optimization

### Column Management
- [ ] Auto date/time is DISABLED (File > Options > Data Load)
- [ ] Unused columns removed from model
- [ ] High cardinality text columns reviewed
- [ ] No calculated columns that could be measures
- [ ] Text columns only where necessary (prefer numeric)

### Data Types
- [ ] Using smallest appropriate data type
- [ ] Fixed decimal for currency (not floating point)
- [ ] Whole numbers where decimals not needed
- [ ] No unnecessary precision in decimals

### Relationships
- [ ] Single-direction relationships where possible
- [ ] No unnecessary bi-directional relationships
- [ ] Many-to-many relationships avoided or optimized
- [ ] Relationship columns same data type

### Table Structure
- [ ] Star schema implemented (not snowflake)
- [ ] Fact tables at appropriate grain
- [ ] Aggregation tables created for large facts
- [ ] Reference tables properly sized

---

## DAX Optimization

### Measure Efficiency
- [ ] Variables used to avoid repeated calculations
- [ ] DIVIDE used instead of / operator
- [ ] CALCULATE used only when necessary
- [ ] No deeply nested CALCULATE functions

### Iterator Functions
- [ ] SUMX/AVERAGEX only when needed
- [ ] No nested iterators where avoidable
- [ ] Row context used efficiently

### Filter Context
- [ ] FILTER function uses minimal columns
- [ ] ALL/ALLEXCEPT used appropriately
- [ ] No unnecessary filter modifications

### Best Practices
```dax
// BAD - Nested iterators
SUMX(
    Sales,
    SUMX(RELATEDTABLE(Products), Products[Price])
)

// GOOD - Pre-joined data
SUM(Sales[Amount])
```

---

## Query Optimization

### Visual Count
- [ ] No more than 8 visuals per page
- [ ] Complex visuals limited per page
- [ ] Cards/KPIs grouped efficiently

### Visual Configuration
- [ ] Top N filters applied where appropriate
- [ ] Unnecessary sorting removed
- [ ] Visual-level filters minimized
- [ ] Default slicer values set to reduce scope

### Cross-Filtering
- [ ] Cross-filtering direction minimized
- [ ] Unnecessary highlighting disabled
- [ ] Edit interactions configured

---

## DirectQuery Optimization (if applicable)

### Source Database
- [ ] Appropriate indexes exist
- [ ] Statistics up to date
- [ ] Query folding verified in Power Query
- [ ] Materialized views considered

### Model Configuration
- [ ] Aggregations implemented
- [ ] Composite model considered
- [ ] User-defined aggregations configured
- [ ] Referential integrity assumed where valid

---

## Refresh Optimization

### Incremental Refresh
- [ ] Enabled for large tables
- [ ] RangeStart/RangeEnd parameters configured
- [ ] Appropriate partition size selected
- [ ] Historical vs current data partitioned

### Gateway Performance
- [ ] Gateway properly sized
- [ ] Concurrent queries limited
- [ ] Mashup containers configured

---

## Monitoring

### Performance Analyzer
- [ ] Long-running visuals identified
- [ ] DAX query times reviewed
- [ ] Direct query times acceptable
- [ ] Render times appropriate

### Metrics to Track
- [ ] Dataset refresh duration
- [ ] Report load time
- [ ] Query response time
- [ ] Memory consumption

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Dashboard Load Time | < 5 sec | |
| Report Page Load | < 3 sec | |
| Dataset Refresh | < 30 min | |
| Single Visual Render | < 2 sec | |
| DAX Query Time | < 1 sec | |
