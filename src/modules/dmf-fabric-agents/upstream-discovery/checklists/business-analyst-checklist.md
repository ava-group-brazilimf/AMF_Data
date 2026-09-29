# BusinessAnalyst Checklist

**Agent:** BusinessAnalyst  
**Version:** 1.0

---

## Pre-Work Checklist

### Review Upstream Artifacts
- [ ] Problem statement reviewed
- [ ] KPIs reviewed
- [ ] Success criteria reviewed (if available)
- [ ] Stakeholder map reviewed (if available)
- [ ] Key business objectives understood

### Data Source Preparation
- [ ] Data sources identified
- [ ] Access to source documentation
- [ ] Sample data available (if possible)
- [ ] Source owners identified

---

## STTM Checklist

### Source Systems
- [ ] All source systems documented
- [ ] System type specified (DB, API, File)
- [ ] Connection method documented
- [ ] Refresh frequency noted
- [ ] Owner/contact identified

### Source Tables
- [ ] All relevant tables listed
- [ ] Primary keys identified
- [ ] Description provided
- [ ] Row count estimated
- [ ] Key columns documented

### Target Architecture
- [ ] Landing layer defined
- [ ] Bronze layer defined
- [ ] Silver layer defined
- [ ] Gold layer defined
- [ ] Naming conventions documented

### Field Mapping
- [ ] All source columns mapped
- [ ] All target columns defined
- [ ] Data types specified (source and target)
- [ ] Transformation rules documented
- [ ] PK/FK relationships marked

### Transformations
- [ ] Each transformation has description
- [ ] Logic documented (SQL or pseudo-code)
- [ ] Business justification provided
- [ ] Examples included

### Quality Check
- [ ] No unmapped source fields (unless intentional)
- [ ] No undefined target fields
- [ ] Transformation rules are clear
- [ ] No ambiguous mappings

---

## Analytical Questions Checklist

### Question Coverage
- [ ] At least 5 questions defined
- [ ] Questions cover multiple stakeholders
- [ ] Questions address KPIs
- [ ] Questions are specific and measurable

### Question Completeness (per question)
- [ ] Question ID assigned
- [ ] Full question text written
- [ ] Business context explained
- [ ] Priority assigned (High/Medium/Low)
- [ ] Linked KPI identified (if applicable)

### Data Requirements (per question)
- [ ] Dimensions identified
- [ ] Measures identified
- [ ] Grain/granularity specified
- [ ] Required filters noted
- [ ] Time range defined
- [ ] Data sources identified

### Quality Check
- [ ] Questions are answerable with available data
- [ ] Questions align with problem statement
- [ ] No duplicate questions
- [ ] Priorities are balanced

---

## DQ Initial Checklist

### Dimension Coverage
- [ ] Completeness defined
- [ ] Accuracy defined
- [ ] Timeliness defined (if applicable)
- [ ] Consistency defined (if applicable)
- [ ] Uniqueness defined
- [ ] Validity defined

### Critical Fields
- [ ] KPI calculation fields identified
- [ ] Primary key fields identified
- [ ] Business-critical fields identified
- [ ] Thresholds set per field
- [ ] Justification documented

### Validation Rules
- [ ] At least 5 initial rules defined
- [ ] Each rule has description
- [ ] Dimension specified per rule
- [ ] Threshold set per rule
- [ ] Action on failure defined
- [ ] Priority assigned

### Quality Check
- [ ] Rules are testable
- [ ] Thresholds are realistic
- [ ] Critical fields have rules
- [ ] Actions are clear

---

## Gate 1 Readiness Checklist

### Required Artifacts
- [ ] STTM complete
- [ ] Analytical Questions complete
- [ ] DQ Initial complete

### Cross-Reference Validation
- [ ] STTM covers data for all questions
- [ ] DQ rules cover KPI fields
- [ ] Questions link to KPIs
- [ ] Transformation rules support questions

### Handoff Preparation
- [ ] Artifacts in output folder
- [ ] Version documented
- [ ] Open questions listed
- [ ] Ready for Gate 1 validation

---

## Common Issues to Avoid

### STTM
- ❌ Missing source columns
- ❌ Undefined transformation rules
- ❌ No data types specified
- ❌ Missing PK/FK identification

### Analytical Questions
- ❌ Fewer than 5 questions
- ❌ Vague, unmeasurable questions
- ❌ Missing data source identification
- ❌ No priority assignment

### DQ Initial
- ❌ No critical fields identified
- ❌ Unrealistic thresholds
- ❌ Missing action on failure
- ❌ Too few validation rules
