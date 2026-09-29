# Task: Create Data Value Proposition

**Command:** `*value-prop`  
**Agent:** DataStrategist (Alex)  
**Output:** `value-proposition.md`

---

## Objective

Create a compelling data value proposition that articulates the business value, benefits, and ROI of the data initiative to stakeholders. Includes a mandatory **factory vs. manual migration performance comparison** that quantifies the efficiency gain.

---

## Prerequisites

- [ ] Problem statement defined
- [ ] KPIs identified
- [ ] Stakeholders mapped
- [ ] Understanding of current state

---

## Steps

### Step 1: Understand Current State

Document the "Before" scenario:

| Aspect | Current State |
|--------|---------------|
| **Data Access** | How do users access data today? |
| **Decision Making** | How are decisions made? |
| **Time to Insight** | How long does it take? |
| **Data Quality** | What's the confidence level? |
| **Cost** | What are current data costs? |

### Step 2: Define Future State

Document the "After" scenario:

| Aspect | Future State |
|--------|--------------|
| **Data Access** | How will users access data? |
| **Decision Making** | How will decisions be made? |
| **Time to Insight** | Target time to insight |
| **Data Quality** | Target confidence level |
| **Cost** | Projected cost savings/investments |

### Step 3: Identify Value Drivers

For each stakeholder group, identify value:

| Stakeholder | Primary Value | Secondary Value |
|-------------|---------------|-----------------|
| **Executives** | Strategic insight | Risk reduction |
| **Managers** | Operational efficiency | Cost savings |
| **Analysts** | Time savings | Data accuracy |
| **Users** | Self-service | Real-time access |

### Step 4: Quantify Benefits

Calculate tangible benefits:

```yaml
benefits:
  revenue_impact:
    description: "Revenue increase from better decisions"
    calculation: "{formula}"
    estimated_value: "$X"
    timeframe: "12 months"
    
  cost_savings:
    description: "Cost reduction from automation"
    calculation: "{formula}"
    estimated_value: "$Y"
    timeframe: "12 months"
    
  time_savings:
    description: "Hours saved per analyst"
    calculation: "hours/week * analysts * weeks"
    estimated_value: "Z hours"
    timeframe: "yearly"
    
  quality_improvement:
    description: "Reduction in data errors"
    calculation: "current_errors - target_errors"
    estimated_value: "X% reduction"
    timeframe: "6 months"
```

### Step 5: Identify Intangible Benefits

Document qualitative benefits:
- Improved decision confidence
- Enhanced collaboration
- Better governance
- Reduced risk
- Competitive advantage

### Step 6: Calculate ROI

```yaml
roi_calculation:
  investment:
    implementation: "$X"
    maintenance: "$Y/year"
    total_3_year: "$Z"
    
  returns:
    year_1: "$A"
    year_2: "$B"
    year_3: "$C"
    total_3_year: "$D"
    
  roi:
    simple_roi: "(Returns - Investment) / Investment"
    payback_period: "X months"
    npv: "$E"
```

### Step 7: Calculate Factory vs. Manual Performance Gain

This step is **mandatory**. It quantifies the efficiency gain of executing the migration through the AI-Agent Migration Factory™ compared to a traditional manual consulting engagement.

#### 7.1 — Gather Object Metrics

Load the inventory data (from `inventory-enriched.json` or `all-objects-inventory.csv` if available) to extract:
- Total objects by type: Tables, Views, Procedures, Functions, Indexes
- Complexity distribution: Low, Medium, High
- Number of databases/sources
- Total SQL lines / code volume

If inventory data is not yet available, use estimates from the problem statement or stakeholder inputs.

#### 7.2 — Estimate Traditional (Manual) Effort

Apply industry-standard benchmarks for manual migration consulting:

| Phase | Activity | Formula | Benchmark |
|-------|----------|---------|-----------|
| UPSTREAM | Discovery + Inventory | 40h per database | Manual cataloging, interviews |
| UPSTREAM | STTM Mapping | Table×1.5h + Proc×2.5h + View×0.75h + Func×1.0h | Per-object manual mapping |
| UPSTREAM | Dependency Analysis | 15h per database | Manual trace + documentation |
| MIDSTREAM | Architecture Design | 30h per database | Manual design sessions |
| MIDSTREAM | Data Modeling | 40h per database | Manual ER modeling |
| MIDSTREAM | DDL + ETL Code | 2.5h per object | Manual coding + review |
| MIDSTREAM | Security / PII Review | 20h per database | Manual scan + classification |
| DOWNSTREAM | QA / Validation | 1.0h per object (subset) | Manual test case execution |
| DOWNSTREAM | Reconciliation | 60h per database | Manual row count + checksums |
| DOWNSTREAM | Documentation | 120h per database | Manual runbook writing |
| GENERAL | Project Management | +20% overhead on total | Coordination, meetings, reporting |

```
Total_Manual_Hours = Sum(all phases) × 1.20
```

#### 7.3 — Estimate Factory (Automated) Effort

Apply factory reduction factors per phase:

| Phase | Reduction Factor | Rationale |
|-------|------------------|-----------|
| Discovery + Inventory | 95–97% | Automated scan, classification, dead-code detection |
| STTM Mapping | 65–75% | Agent-generated draft, human review only |
| Dependency Analysis | 95–97% | Automated DAG generation |
| Architecture Design | 35–45% | Agent-assisted, human decision |
| Data Modeling | 35–45% | Agent-assisted, human validation |
| DDL + ETL Code | 70–80% | Auto-generated from model, human review |
| Security / PII Review | 65–75% | Automated PII scan, human approval |
| QA / Validation | 65–75% | Automated gate scoring, evidence packages |
| Reconciliation | 75–85% | Automated checksums, row counts, schema diffs |
| Documentation | 75–85% | Auto-generated runbooks, changelogs |
| Project Management | 75–85% | Orchestrator agent, automated tracking |

```
Total_Factory_Hours = Sum(phase_hours × (1 - reduction_factor))
```

#### 7.4 — Calculate Performance Gain

Compute the consolidated metrics:

```yaml
performance_gain:
  formula: "((Manual_Hours - Factory_Hours) / Manual_Hours) × 100"
  total_manual_hours: "{calculated}"
  total_factory_hours: "{calculated}"
  hours_saved: "{Manual - Factory}"
  percentage_gain: "{result}%"
  
  # Scenario analysis
  scenarios:
    conservative:
      description: "50% automation, partial adoption"
      gain_percentage: "{calc}%"
    realistic:
      description: "70-75% automation, experienced team"
      gain_percentage: "{calc}%"
    optimistic:
      description: "80%+ automation, template reuse"
      gain_percentage: "{calc}%"
      
  # Timeline comparison
  timeline:
    team_size: "{N people}"
    manual_duration_months: "{Manual_Hours / (team_size × 160)}"
    factory_duration_months: "{Factory_Hours / (team_size × 160)}"
    months_saved: "{manual - factory}"
    
  # Cost comparison (use client’s rate or market average)
  cost:
    hourly_rate: "{rate}"
    manual_cost: "{Manual_Hours × rate}"
    factory_cost: "{Factory_Hours × rate}"
    savings: "{manual_cost - factory_cost}"
```

#### 7.5 — Qualitative Gains

Document non-quantitative advantages:

| Dimension | Manual Approach | Factory Approach |
|-----------|----------------|------------------|
| Auditability | Ad-hoc reports | GateScore with evidence packages |
| Repeatability | Depends on consultant | Reproducible per wave |
| Dead-code elimination | Migrated by omission | Automatically detected and excluded |
| Rollback capability | Rarely tested | Automated runbook + self-healing |
| Knowledge retention | Leaves with consultant | Encoded in agents and artifacts |
| Data mismatch risk | 8–15% industry average | ≤2% target (Gate 3 reconciliation) |

> **CRITICAL:** The performance gain section is **mandatory**. The value proposition is incomplete without this comparison. Always show the formula, the per-phase breakdown, and at least the realistic scenario percentage.

---

## Output Template

```markdown
# Data Value Proposition

**Project:** {project_name}  
**Date:** {date}  
**Author:** DataStrategist  
**Version:** 1.0

---

## Executive Summary

{2-3 sentence value proposition statement}

**Key Message:** {one-liner that captures the value}

---

## The Problem

### Current State
{Description of current challenges}

### Impact of the Problem
- Financial: {cost of current state}
- Operational: {inefficiencies}
- Strategic: {missed opportunities}

---

## The Solution

### Future State Vision
{Description of future state with this initiative}

### Key Capabilities
1. {Capability 1}: {benefit}
2. {Capability 2}: {benefit}
3. {Capability 3}: {benefit}

---

## Value for Stakeholders

### For Executives
- {Value 1}
- {Value 2}

### For Managers
- {Value 1}
- {Value 2}

### For Analysts/Users
- {Value 1}
- {Value 2}

---

## Quantified Benefits

| Benefit Category | Metric | Value | Timeframe |
|------------------|--------|-------|-----------|
| Revenue Impact | {metric} | ${value} | {time} |
| Cost Savings | {metric} | ${value} | {time} |
| Time Savings | {metric} | {hours} | {time} |
| Quality | {metric} | {%} | {time} |

### Total Expected Value
- **Year 1:** ${X}
- **Year 2:** ${Y}
- **Year 3:** ${Z}
- **3-Year Total:** ${Total}

---

## ROI Analysis

| Metric | Value |
|--------|-------|
| Total Investment | ${X} |
| Total Returns (3 years) | ${Y} |
| Simple ROI | {X}% |
| Payback Period | {X} months |

---

## Risk Mitigation Value

| Risk | Current Exposure | After Implementation |
|------|-----------------|---------------------|
| {Risk 1} | {exposure} | {mitigated} |
| {Risk 2} | {exposure} | {mitigated} |

---

## Factory vs. Manual Migration — Performance Gain

### Effort Comparison by Phase

| Phase | Activity | Manual (hours) | Factory (hours) | Reduction |
|-------|----------|---------------|-----------------|-----------|
| UPSTREAM | Discovery + Inventory | {h} | {h} | {%} |
| UPSTREAM | STTM Mapping | {h} | {h} | {%} |
| UPSTREAM | Dependency Analysis | {h} | {h} | {%} |
| MIDSTREAM | Architecture Design | {h} | {h} | {%} |
| MIDSTREAM | Data Modeling | {h} | {h} | {%} |
| MIDSTREAM | DDL + ETL Code | {h} | {h} | {%} |
| MIDSTREAM | Security / PII Review | {h} | {h} | {%} |
| DOWNSTREAM | QA / Validation | {h} | {h} | {%} |
| DOWNSTREAM | Reconciliation | {h} | {h} | {%} |
| DOWNSTREAM | Documentation | {h} | {h} | {%} |
| GENERAL | Project Management | {h} | {h} | {%} |
| | **TOTAL** | **{total_manual} h** | **{total_factory} h** | **{gain}%** |

### Performance Gain Formula

```
Performance Gain (%) = ((Manual_Hours - Factory_Hours) / Manual_Hours) × 100
Performance Gain (%) = (({total_manual} - {total_factory}) / {total_manual}) × 100
Performance Gain (%) = {result}%
```

### Scenario Analysis

| Scenario | Assumption | Gain |
|----------|------------|------|
| Conservative | 50% automation, partial adoption | {%} |
| **Realistic** | 70–75% automation, experienced team | **{%}** |
| Optimistic | 80%+ automation, template reuse | {%} |

### Timeline Impact

| Metric | Manual | Factory |
|--------|--------|---------|
| Team size | {N} people | {N} people |
| Duration | {X} months | {Y} months |
| Months saved | — | {Z} months |

### Cost Impact

| Metric | Manual | Factory | Savings |
|--------|--------|---------|---------|
| Total hours | {h} | {h} | {h} |
| Total cost | {$X} | {$Y} | **{$Z}** |

### Qualitative Gains

| Dimension | Manual | Factory |
|-----------|--------|---------|
| Auditability | Ad-hoc reports | GateScore with evidence |
| Repeatability | Consultant-dependent | Reproducible per wave |
| Dead-code risk | Migrated by omission | Auto-detected and excluded |
| Rollback | Rarely tested | Automated self-healing |
| Knowledge retention | Leaves with consultant | Encoded in agents |
| Data mismatch | 8–15% typical | ≤2% target |

---

## Success Metrics

| KPI | Baseline | Target | Timeline |
|-----|----------|--------|----------|
| {KPI 1} | {current} | {target} | {date} |
| {KPI 2} | {current} | {target} | {date} |

---

## Call to Action

{Clear next steps and decision required}
```

---

## Handoff

After completing value proposition:
- **Continue UPSTREAM:** Create strategy summary → `*strategy-summary`
- **Review KPIs:** Verify alignment → `*create-kpis`
- **Next phase:** Proceed to BusinessAnalyst → `@business-analyst *help`
