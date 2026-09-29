# Logic Extractor Checklist

**Agent:** Logan (Logic Extractor)  
**Version:** 1.0

---

## Pre-Extraction

### Input Validation
- [ ] `inventory.json` received from Discovery Scout
- [ ] `dependency-graph.json` received from Discovery Scout
- [ ] Source code files accessible in workspace
- [ ] Source language identified for each pipeline
- [ ] LLM API keys configured and validated (GPT-4 / Claude 3.5)
- [ ] AST parsers available for all identified languages
- [ ] Output directory structure created (`projects/{project_name}/outputs/upstream/logic/`)

### Scope Definition
- [ ] Pipeline scope confirmed (full or subset)
- [ ] Complexity classification reviewed
- [ ] UDFs pre-identified from inventory scan
- [ ] Known edge cases or exceptions documented
- [ ] SME contacts identified for escalation

---

## Code Analysis

### AST Parsing
- [ ] All source files successfully parsed by AST
- [ ] Parse errors logged with line numbers
- [ ] Fallback regex extraction used where AST fails
- [ ] Multi-language pipelines handled correctly
- [ ] Config files parsed (Oozie, Airflow, SSIS)

### Input/Output Identification
- [ ] All input sources (tables, files, APIs) identified
- [ ] All output targets (tables, files, APIs) identified
- [ ] Read/write modes documented (overwrite, append, merge)
- [ ] Partition strategies identified
- [ ] Data formats documented (Parquet, ORC, CSV, JSON)

### Control Flow Analysis
- [ ] IF/ELSE branches mapped
- [ ] CASE/WHEN logic extracted
- [ ] Loop patterns identified
- [ ] Error handling documented (try/catch, ON ERROR)
- [ ] Conditional execution paths documented

---

## Business Rule Documentation

### Rule Extraction
- [ ] Filter rules extracted (WHERE, HAVING conditions)
- [ ] Transformation rules extracted (CASE, calculations)
- [ ] Validation rules extracted (NULL checks, ranges)
- [ ] Aggregation rules extracted (GROUP BY, window functions)
- [ ] Lookup/reference rules extracted (JOINs)
- [ ] SCD patterns identified (Type 1, 2, 3)
- [ ] Deduplication logic extracted

### Rule Quality
- [ ] Each rule has a confidence score (0.0-1.0)
- [ ] Each rule has a source reference (file, line number)
- [ ] Business intent documented (not just syntax)
- [ ] Assumptions explicitly documented
- [ ] Low-confidence rules flagged for SME review
- [ ] Ambiguous rules noted with alternatives

---

## Pseudocode Quality

### Completeness
- [ ] All READ steps defined (100% input coverage)
- [ ] All WRITE steps defined (100% output coverage)
- [ ] >= 90% business rules mapped to pseudocode steps
- [ ] Data flow is consistent (no orphan columns)
- [ ] Step ordering respects dependencies

### Platform Independence
- [ ] No platform-specific syntax (HiveQL, PySpark, etc.)
- [ ] No vendor-specific function names
- [ ] Pseudocode uses standardized step types only
- [ ] Transformation logic expressed in natural language
- [ ] Column references use semantic names

### Readability
- [ ] Each step has a human-readable description
- [ ] Business context included for each transformation
- [ ] Complex logic broken into atomic steps
- [ ] Comments explain WHY, not just WHAT

---

## Digital Twin

### Physical Layer
- [ ] 100% of inventory objects mapped
- [ ] Schema information captured (columns, types)
- [ ] Dependencies preserved from dependency graph
- [ ] Complexity scores included
- [ ] Object status documented (active, deprecated, orphan)

### Semantic Layer
- [ ] Business names assigned to all entities
- [ ] Business domain classification completed
- [ ] Data classification applied (PII, financial, etc.)
- [ ] Data quality rules mapped
- [ ] End-to-end lineage traceable

### Target Layer
- [ ] Target platform mapping completed
- [ ] Medallion layer assigned (bronze, silver, gold)
- [ ] Storage format selected (Delta, Parquet, etc.)
- [ ] Partition strategy defined
- [ ] Migration strategy classified (lift-and-shift, refactor, rebuild)

### Cross-Layer Validation
- [ ] Physical→Semantic mapping complete
- [ ] Semantic→Target mapping complete
- [ ] No orphan entities in any layer
- [ ] Dependency graph preserved across layers
- [ ] Gap analysis documented

---

## SME Validation

### Review Preparation
- [ ] Low-confidence items compiled for review
- [ ] Unresolved UDFs listed with context
- [ ] Ambiguous business rules documented
- [ ] Review package prepared (pseudocode + original code)
- [ ] Priority order defined (critical pipelines first)

### SME Review Execution
- [ ] 20% sample of business rules reviewed by SME
- [ ] UDF interpretations validated by SME
- [ ] Edge case handling confirmed
- [ ] Assumptions approved or corrected
- [ ] Post-SME confidence scores updated

### Post-Validation
- [ ] Confidence report generated (`*confidence-report`)
- [ ] All SME feedback incorporated
- [ ] Gate 1 readiness assessed
- [ ] Artifacts ready for Code Generator (Coda)
- [ ] Extraction log finalized

---

*Checklist defined by AI-Agent Migration Factory™ v4.0*
