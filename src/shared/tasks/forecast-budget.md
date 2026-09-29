---
task: forecast-budget
version: 1.0
elicit: true
description: Analyze budget burn rate and forecast future costs
---

# Forecast Budget and Cost Burn

## Purpose

Analyze current budget consumption, predict future spending, identify cost risks, and provide recommendations for budget management.

## Process

### Step 1: Gather Budget Information

ASK the user for the following information:

1. **Total Budget**: What is the approved project budget?
2. **Budget Breakdown**: How is budget allocated? (dev, infrastructure, contingency)
3. **Time Elapsed**: How much of the timeline has passed? (weeks/months)
4. **Actual Spend**: How much has been spent to date?
5. **Committed Costs**: Any committed but not yet paid expenses?
6. **Scope Changes**: Any approved scope changes affecting budget?
7. **Resource Changes**: Any rate changes or team composition changes?

### Step 2: Calculate Burn Rate

COMPUTE current burn metrics:

**Weekly/Monthly Burn Rate:**

```
Burn Rate = Total Spent / Time Elapsed
```

**Projected Budget at Completion (BAC):**

```
Projected BAC = (Total Spent / Time Elapsed) × Total Timeline
```

**Budget Variance:**

```
Variance = Approved Budget - Projected BAC
Variance % = (Variance / Approved Budget) × 100%
```

**Cost Performance Index (CPI):**

```
CPI = Budgeted Cost of Work Performed / Actual Cost of Work Performed
CPI > 1.0 = Under budget (good)
CPI = 1.0 = On budget
CPI < 1.0 = Over budget (concern)
```

**Schedule Performance Index (SPI):**

```
SPI = Budgeted Cost of Work Performed / Budgeted Cost of Work Scheduled
SPI > 1.0 = Ahead of schedule
SPI = 1.0 = On schedule
SPI < 1.0 = Behind schedule
```

### Step 3: Identify Cost Drivers

ANALYZE what is driving costs:

**Labor Costs:**

- Actual hours vs estimated hours by role
- Overtime or premium rates
- Resource utilization rates
- Contractor vs FTE mix

**Infrastructure Costs:**

- Cloud consumption (compute, storage, network)
- Licensing fees
- Tool subscriptions
- Third-party services

**Other Costs:**

- Travel and expenses
- Training
- External consulting
- Hardware/software purchases

**Cost Categories:**

- ✅ Planned and expected
- ⚠️ Unplanned but necessary
- 🔴 Wasteful or avoidable

### Step 4: Forecast Future Costs

PROJECT remaining budget needs:

**Forecast Method 1: Linear Projection**

```
Remaining Cost = (Budget / Timeline) × Remaining Time
```

**Forecast Method 2: Earned Value**

```
Estimate to Complete (ETC) = (BAC - Earned Value) / CPI
Estimate at Completion (EAC) = Actual Cost + ETC
```

**Forecast Method 3: Bottom-Up**

- Itemize remaining work
- Estimate cost for each item
- Sum to get total remaining cost

**Risk-Adjusted Forecast:**

```
Best Case (90% confidence) = Forecast × 0.9
Most Likely (50% confidence) = Forecast × 1.0
Worst Case (10% confidence) = Forecast × 1.2
```

### Step 5: Identify Budget Risks

ASSESS risks to budget:

**Budget Risk Types:**

**Scope Risks:**

- Scope creep
- Unapproved changes
- Gold plating
- Impact: +10-30% typically

**Resource Risks:**

- Resource availability
- Rate increases
- Overtime needs
- Impact: +5-20% typically

**Technical Risks:**

- Technology challenges
- Integration complexity
- Performance issues
- Impact: +10-25% typically

**External Risks:**

- Vendor price increases
- Currency fluctuations
- Regulatory requirements
- Impact: Varies widely

### Step 6: Recommend Actions

PROVIDE cost management recommendations:

**Cost Reduction Opportunities:**

- Optimize cloud resources
- Renegotiate vendor contracts
- Use offshore resources
- Implement automation
- Descope nice-to-have features

**Budget Request Options:**

- Request additional funding
- Reallocate from contingency
- Reduce scope to fit budget
- Extend timeline to spread costs

**Monitoring Improvements:**

- Weekly budget reviews
- Real-time cost tracking
- Automated alerts for overruns
- Regular forecast updates

## Output Structure

```markdown
# BUDGET FORECAST - {PROJECT_NAME}

**Forecast Date:** {DATE}
**Project Phase:** {Phase}
**Time Elapsed:** {X} weeks of {Y} weeks ({Z}%)
**Analyst:** {Delivery Lead Name}

---

## EXECUTIVE SUMMARY

**Budget Status:** 🟢 On Track / 🟡 At Risk / 🔴 Over Budget

**Key Findings:**

- Current spend: ${X} ({Y}% of budget)
- Projected final cost: ${Z} (variance: {±W}%)
- Forecast confidence: {High/Medium/Low}
- Action required: {Yes/No - what action}

---

## BUDGET OVERVIEW

### Approved Budget

| Category            | Approved     | % of Total |
| ------------------- | ------------ | ---------- |
| Development (Labor) | $109,000     | 73%        |
| Infrastructure      | $21,000      | 14%        |
| Testing & QA        | $12,000      | 8%         |
| Contingency (15%)   | $19,500      | 13%        |
| **TOTAL**           | **$150,000** | **100%**   |

### Current Status (as of {DATE})

| Category       | Budget       | Spent        | Committed   | Available   | Status |
| -------------- | ------------ | ------------ | ----------- | ----------- | ------ |
| Development    | $109,000     | $82,500      | $8,000      | $18,500     | 🟢     |
| Infrastructure | $21,000      | $15,750      | $2,100      | $3,150      | 🟢     |
| Testing & QA   | $12,000      | $9,250       | $1,200      | $1,550      | 🟢     |
| Contingency    | $19,500      | $5,000       | $0          | $14,500     | 🟢     |
| **TOTAL**      | **$150,000** | **$112,500** | **$11,300** | **$26,200** | **🟢** |

**Committed:** Contracted but not yet paid
**Available:** Budget remaining after spent + committed

---

## BURN RATE ANALYSIS

### Historical Burn

**Weekly Burn Rate:**
```

Average: $15,000/week
Weeks elapsed: 7.5
Total spent: $112,500

```

**Burn Rate Trend:**
| Week | Spent | Cumulative | Budget | Variance |
|------|-------|------------|--------|----------|
| 1-2 | $28,000 | $28,000 | $30,000 | +$2,000 |
| 3-4 | $30,000 | $58,000 | $60,000 | +$2,000 |
| 5-6 | $32,000 | $90,000 | $90,000 | $0 |
| 7-8 | $22,500 | $112,500 | $120,000 | +$7,500 |

**Observation:** Burn rate decreasing as project nears completion (expected pattern)

### Burn Rate Chart

```

Budget vs Actual Spend

150K ┤ ╭─ Budget
│ ╭───╯
│ ╭───╯
120K┤ ╭───╯
│ ╭───╯
│ Actual ───╮ ╭───╯
90K┤ ╭───────╯
│ ╭───╯
│ ╭───╯
60K┤──╯
│
30K┤
│
0 └─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────
Wk1 Wk2 Wk3 Wk4 Wk5 Wk6 Wk7 Wk8 Wk9 Wk10

Status: 🟢 Actual tracking below budget (favorable)

```

---

## COST PERFORMANCE METRICS

### Earned Value Analysis

**Key Metrics:**
- **Planned Value (PV):** $120,000 (at Week 8)
- **Earned Value (EV):** $127,500 (work completed)
- **Actual Cost (AC):** $112,500 (spent)

**Performance Indices:**
- **CPI (Cost Performance Index):** 1.13
  - Formula: EV / AC = $127,500 / $112,500
  - Status: 🟢 Excellent (13% under budget for work done)

- **SPI (Schedule Performance Index):** 1.06
  - Formula: EV / PV = $127,500 / $120,000
  - Status: 🟢 Good (6% ahead of schedule)

**Interpretation:**
- CPI > 1.0: Getting more value per dollar spent (efficient)
- SPI > 1.0: Completing work faster than planned

---

## FORECAST TO COMPLETION

### Forecast Methods

**Method 1: Linear Projection**
```

Current Burn: $15,000/week
Remaining: 2.5 weeks
Forecast: $112,500 + ($15,000 × 2.5) = $150,000
Variance: $0 (on budget)

```

**Method 2: Earned Value (CPI-based)**
```

Budget at Completion (BAC): $150,000
Earned Value: $127,500
CPI: 1.13

Estimate to Complete (ETC):
= (BAC - EV) / CPI
= ($150,000 - $127,500) / 1.13
= $19,912

Estimate at Completion (EAC):
= AC + ETC
= $112,500 + $19,912
= $132,412

Variance at Completion (VAC):
= BAC - EAC
= $150,000 - $132,412
= +$17,588 (under budget)

```

**Method 3: Bottom-Up (Remaining Work)**
```

Remaining Activities:
├─ Performance optimization: $8,000
├─ UAT support: $6,000
├─ Documentation: $4,000
├─ Deployment: $3,000
└─ Contingency buffer: $5,000
Total: $26,000

Forecast at Completion:
= $112,500 (spent) + $26,000 (remaining)
= $138,500
Variance: +$11,500 (under budget)

```

### Consolidated Forecast

| Method | Forecast | Variance | Confidence |
|--------|----------|----------|------------|
| Linear Projection | $150,000 | $0 | Medium |
| Earned Value (CPI) | $132,412 | +$17,588 | High |
| Bottom-Up | $138,500 | +$11,500 | High |
| **Weighted Average** | **$137,500** | **+$12,500** | **High** |

**Final Forecast:** $137,500 (8% under budget)

### Confidence Ranges

**Best Case (90% confidence):** $132,000 (12% under)
**Most Likely (50% confidence):** $137,500 (8% under)
**Worst Case (10% confidence):** $145,000 (3% under)

**Interpretation:** Very likely to finish under budget

---

## COST DRIVERS ANALYSIS

### Labor Costs (73% of budget)

| Role | Budget | Actual | Variance | % |
|------|--------|--------|----------|---|
| Senior Data Engineer | $48,000 | $39,000 | +$9,000 | 🟢 19% |
| Data Architect | $16,000 | $14,000 | +$2,000 | 🟢 13% |
| BI Developer | $15,600 | $13,200 | +$2,400 | 🟢 15% |
| QA Engineer | $9,600 | $7,800 | +$1,800 | 🟢 19% |
| Technical Writer | $3,600 | $2,700 | +$900 | 🟢 25% |
| Project Manager | $16,200 | $13,800 | +$2,400 | 🟢 15% |
| **Total Labor** | **$109,000** | **$90,500** | **+$18,500** | **🟢 17%** |

**Key Findings:**
- All roles tracking under budget
- Higher productivity than estimated
- Agentic AI adoption reducing hours (estimated 30% efficiency gain)

### Infrastructure Costs (14% of budget)

| Service | Budget | Actual | Forecast | Variance |
|---------|--------|--------|----------|----------|
| Azure Synapse | $12,000 | $9,450 | $12,600 | -$600 🟡 |
| Azure SQL DB | $3,600 | $2,700 | $3,600 | $0 🟢 |
| Data Factory | $2,400 | $1,800 | $2,400 | $0 🟢 |
| Data Lake Storage | $1,200 | $900 | $1,080 | +$120 🟢 |
| Monitoring | $1,800 | $900 | $1,440 | +$360 🟢 |
| **Total Infra** | **$21,000** | **$15,750** | **$21,120** | **-$120** 🟢 |

**Key Findings:**
- Synapse costs slightly higher than estimated (complex queries)
- Overall infrastructure tracking to budget
- Optimization efforts underway (auto-pause, query tuning)

### Testing & QA Costs (8% of budget)

| Activity | Budget | Actual | Variance |
|----------|--------|--------|----------|
| Test planning | $2,400 | $1,800 | +$600 🟢 |
| Unit test development | $4,800 | $3,900 | +$900 🟢 |
| Integration testing | $2,400 | $2,100 | +$300 🟢 |
| UAT support | $2,400 | $1,450 | +$950 🟢 |
| **Total Testing** | **$12,000** | **$9,250** | **+$2,750** 🟢 |

**Key Findings:**
- Testing ahead of schedule and under budget
- High quality from development reducing test defects
- UAT still in progress (more spend expected)

---

## BUDGET RISKS

### HIGH PRIORITY RISKS

**🟡 RISK 1: Infrastructure Cost Overrun**
- **Probability:** 40%
- **Impact:** +$5K-$10K annually
- **Mitigation:** Query optimization, auto-pause, reserved instances
- **Contingency:** $5,000 allocated

**🟢 RISK 2: Scope Creep**
- **Probability:** 20% (was 50%)
- **Impact:** +$10K-$20K
- **Mitigation:** Strict change control implemented, working well
- **Status:** Risk reduced through controls

**🟢 RISK 3: Resource Rate Increases**
- **Probability:** 10%
- **Impact:** +$5K-$8K
- **Mitigation:** Rates locked in contracts through project end
- **Status:** Low risk

### Budget Risk Reserve

**Total Risk Exposure:** $20,000 (worst case)
**Contingency Available:** $14,500
**Additional Buffer Needed:** $5,500 (if all risks materialize)

**Recommendation:** Current contingency adequate given low risk levels

---

## COST OPTIMIZATION OPPORTUNITIES

### Identified Savings

**1. Agentic AI Adoption (Realized)**
- **Original Estimate:** 320h Senior DE @ $150/h = $48,000
- **Actual with AI:** 260h @ $150/h = $39,000
- **Savings:** $9,000 (19% reduction)
- **Status:** ✅ Achieved

**2. Infrastructure Optimization (In Progress)**
- **Opportunity:** Auto-pause Synapse during non-business hours
- **Potential Savings:** $200-$300/month = $2,400-$3,600/year
- **Status:** 🔄 Configuring

**3. Reserved Instances (Future)**
- **Opportunity:** 1-year reserved instances for SQL/Synapse
- **Potential Savings:** 30% = $6,300/year
- **Status:** 📅 Planned for Month 3

**Total Potential Savings:** $17,700-$18,900 annually

---

## BUDGET FORECAST SCENARIOS

### Scenario 1: Current Trajectory (Most Likely)

**Assumptions:**
- Continue current burn rate
- No major issues
- All optimizations implemented

**Forecast:**
- Final Cost: $137,500
- Variance: +$12,500 (8% under)
- Confidence: 70%

**Recommendation:** Stay the course

---

### Scenario 2: Scope Addition (Low Probability)

**Assumptions:**
- Stakeholder requests 2 additional features
- Estimated effort: +$15,000

**Forecast:**
- Final Cost: $152,500
- Variance: -$2,500 (2% over)
- Contingency needed: Yes

**Recommendation:** Reject scope additions or request budget increase

---

### Scenario 3: Infrastructure Overrun (Medium Probability)

**Assumptions:**
- Synapse costs 20% higher than forecast
- Additional $4,000 infrastructure spend

**Forecast:**
- Final Cost: $141,500
- Variance: +$8,500 (6% under)
- Contingency needed: Partial

**Recommendation:** Continue optimization efforts, monitor closely

---

## RECOMMENDATIONS

### Immediate Actions (This Week)

**1. ✅ APPROVE: Continue Current Plan**
- Current trajectory is favorable (8% under budget)
- No budget adjustments needed
- Maintain current burn rate

**2. 🔧 IMPLEMENT: Infrastructure Optimization**
- Configure auto-pause for Synapse (save $2.4K-$3.6K/year)
- Tune queries for performance (reduce compute costs)
- Owner: Solution Architect
- Timeline: 2 weeks

**3. 📊 MONITOR: Weekly Budget Review**
- Continue weekly budget tracking
- Update forecast monthly
- Alert if variance exceeds 10%

### Short-term Actions (Next Month)

**4. 💰 CONSIDER: Reserved Instances**
- Evaluate 1-year reserved instances for predictable workloads
- Potential savings: $6.3K/year (30% reduction)
- Decision point: Month 3 (after production stabilizes)

**5. 🎯 ALLOCATE: Contingency for Phase 2**
- Project will finish with $12,500 surplus
- Recommend allocating to Phase 2 planning
- Business case for expansion already strong

### Long-term Actions (Next Quarter)

**6. 📝 DOCUMENT: Lessons Learned**
- Capture actual vs estimated for future projects
- Document impact of agentic AI on costs
- Update estimation templates with new benchmarks

---

## BUDGET TRACKING CADENCE

### Weekly
- Review actual spend vs forecast
- Update burn rate calculations
- Identify any cost anomalies
- Report to project team

### Monthly
- Update forecast to completion
- Earned value analysis
- Executive budget summary
- Risk assessment update

### Milestone-Based
- Budget reconciliation at each phase end
- Lessons learned on cost drivers
- Adjust future phase estimates

---

## APPROVAL & SIGN-OFF

| Stakeholder | Role | Reviewed | Approved | Date |
|-------------|------|----------|----------|------|
| | Delivery Lead | ☐ | ☐ | |
| | Finance Manager | ☐ | ☐ | |
| | Executive Sponsor | ☐ | ☐ | |

---

**Forecast Owner:** {Delivery Lead Name}
**Last Updated:** {DATE}
**Next Forecast:** {DATE + 30 days}
**Confidence Level:** High / Medium / Low
```

## Best Practices

1. **Update Regularly**: Weekly actuals, monthly forecasts
2. **Be Conservative**: Use worst-case for planning, best-case for stretch goals
3. **Track Committed Costs**: Don't just look at spent, include committed
4. **Explain Variances**: Always provide context for significant changes
5. **Use Multiple Methods**: Don't rely on one forecast method
6. **Communicate Early**: Alert stakeholders as soon as variance detected
7. **Document Assumptions**: Make all forecast assumptions explicit
8. **Learn and Improve**: Compare actuals to estimates for future projects

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual budget forecasting: 6-8 hours
- With DeliveryPro agent: 2-3 hours
- **Effort reduction: 60-70%**
