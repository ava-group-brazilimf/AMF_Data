# Strategy Best Practices

**Document:** Best Practices for Data Strategy Definition  
**Agent:** DataStrategist  
**Version:** 1.0

---

## Problem Definition Best Practices

### Start with "Why"

Always begin by understanding the business driver:
- What is the business trying to achieve?
- Why is this important now?
- What triggered this initiative?

**Good:** "We're losing $2M annually due to inventory discrepancies"
**Bad:** "We need a data warehouse"

### Be Specific

Vague problems lead to vague solutions:
- Avoid generic statements
- Include specific numbers where possible
- Name specific processes, systems, or teams

**Good:** "Sales forecasting accuracy is 65%, causing 20% overstock in Q4"
**Bad:** "Our forecasting needs improvement"

### Quantify Impact

If it can't be measured, it's hard to prove success:
- Financial impact (costs, revenue, savings)
- Operational impact (time, resources, capacity)
- Customer impact (satisfaction, retention, experience)

### Define Clear Boundaries

Scope creep is the enemy of delivery:
- Be explicit about what's in scope
- Be equally explicit about what's out of scope
- Document constraints upfront
- State assumptions clearly

---

## KPI Design Best Practices

### SMART KPIs

Every KPI should be:
- **S**pecific: Clear and unambiguous
- **M**easurable: Has a number or percentage
- **A**chievable: Realistic target
- **R**elevant: Aligned to business objectives
- **T**ime-bound: Has a deadline

### Balance Leading and Lagging

| Type | Description | Example |
|------|-------------|---------|
| **Leading** | Predicts future performance | Daily pipeline runs |
| **Lagging** | Measures past results | Monthly revenue impact |

Include both for a complete picture.

### Avoid Vanity Metrics

| Vanity Metric | Better Alternative |
|---------------|-------------------|
| Total records processed | Records processed correctly |
| System uptime | Data freshness |
| Number of reports | Reports used for decisions |

### Set Realistic Targets

- Base targets on baseline + achievable improvement
- Consider industry benchmarks
- Account for learning curve
- Build in buffer for unknowns

### Define Calculations Clearly

Document the exact formula:
```
Error Rate = (Records with Errors / Total Records) × 100

Where:
- Records with Errors = count of records failing DQ rules
- Total Records = count of all records in the batch
```

---

## Success Criteria Best Practices

### Prioritize Ruthlessly

Not all criteria are equal:
- **Must Have**: Project fails without these
- **Should Have**: Important but not critical
- **Nice to Have**: Added value if achieved

### Make Them Measurable

Each criterion needs a clear threshold:

**Measurable:** "Data latency ≤ 15 minutes for 99% of records"
**Not Measurable:** "Data should be timely"

### Define Validation Method

How will you prove the criterion is met?
- What data will you use?
- Who will verify?
- When will you validate?

### Get Agreement Early

Success criteria should be agreed before work begins:
- Review with stakeholders
- Get formal sign-off
- Document any disagreements

---

## Stakeholder Management Best Practices

### Identify All Stakeholders

Don't forget:
- Business sponsors (funding)
- End users (daily use)
- Data providers (source systems)
- IT operations (maintenance)
- Compliance/Legal (regulations)

### Map Interest vs. Influence

```
        High Influence
             │
   Manage    │    Partner
   Closely   │    Closely
             │
─────────────┼─────────────
             │
   Monitor   │    Keep
   (Minimal) │    Informed
             │
        Low Influence
    Low Interest   High Interest
```

### Tailor Communication

| Stakeholder Type | Communication Style |
|------------------|---------------------|
| Executive | High-level, outcomes focused |
| Technical | Detailed, implementation focused |
| End User | Benefits focused, training oriented |
| Data Provider | Impact focused, requirements clear |

---

## Common Pitfalls to Avoid

### Problem Statement Pitfalls

| Pitfall | Example | Solution |
|---------|---------|----------|
| Solution masquerading as problem | "We need a data lake" | Ask "why" five times |
| Too broad | "Improve analytics" | Narrow to specific area |
| No quantification | "It's causing problems" | Estimate the impact |
| Missing stakeholders | Only IT involved | Include business users |

### KPI Pitfalls

| Pitfall | Example | Solution |
|---------|---------|----------|
| Too many KPIs | 20+ KPIs | Focus on 3-5 key metrics |
| No baseline | Target without current state | Measure before setting target |
| Unmeasurable | "Improved data quality" | Define specific DQ dimensions |
| Gaming potential | Easy to cheat | Include balancing metrics |

### Success Criteria Pitfalls

| Pitfall | Example | Solution |
|---------|---------|----------|
| All "Nice to Have" | No required criteria | Define at least 2 "Must Have" |
| Moving goalposts | Changing criteria mid-project | Baseline and version control |
| No approver | Nobody to sign off | Assign accountability |
| Unrealistic thresholds | 100% accuracy | Set achievable targets |

---

## Templates and Examples

### Problem Statement Quick Template

```markdown
**Problem:** {What is happening}
**Impact:** {Quantified business impact}
**Scope:** {What we will address}
**Success:** {How we know it's solved}
```

### KPI Quick Template

```markdown
**KPI:** {Name}
**Formula:** {Calculation}
**Baseline:** {Current value}
**Target:** {Goal value}
**Source:** {Where data comes from}
```

### Success Criterion Quick Template

```markdown
**Criterion:** {Description}
**Threshold:** {Measurable target}
**Validation:** {How we verify}
**Approver:** {Who signs off}
```

---

## Handoff Checklist

Before passing to BusinessAnalyst:

- [ ] Problem statement is specific and quantified
- [ ] At least 3 KPIs with baselines and targets
- [ ] Success criteria defined and prioritized
- [ ] Stakeholders identified and mapped
- [ ] Key decisions documented
- [ ] Open questions listed

---

*Best practices maintained by DataStrategist Agent*
