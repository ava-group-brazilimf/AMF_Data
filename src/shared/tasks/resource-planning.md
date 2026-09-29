---
task: resource-planning
version: 1.0
elicit: true
description: Create resource allocation and capacity planning
---

# Resource Planning and Capacity Management

## Purpose

Plan resource allocation, manage team capacity, identify resource gaps, and optimize resource utilization across project lifecycle.

## Process

### Step 1: Gather Resource Requirements

ASK the user for the following information:

1. **Project Work**: What needs to be done? (WBS or task list)
2. **Skills Required**: What skills are needed for each task?
3. **Timeline**: Project duration and key milestones
4. **Available Resources**: Who is available? Current capacity?
5. **Resource Constraints**: Any limitations (budget, availability, location)
6. **Priorities**: Critical vs non-critical work
7. **Flex Options**: Can we use contractors, offshore, part-time?

### Step 2: Identify Resource Roles and Skills

DEFINE roles and required skills:

**Common Data & Analytics Roles:**

- Senior Data Engineer (SQL, PySpark, ETL)
- Data Solution Architect (Architecture, design)
- BI Developer (Power BI, DAX, semantic models)
- Data Analyst (Requirements, profiling)
- QA Engineer (Testing, quality assurance)
- Technical Writer (Documentation)
- Project Manager / Scrum Master
- DevOps Engineer (CI/CD, infrastructure)

**Skill Levels:**

- Junior (0-2 years)
- Mid-level (3-5 years)
- Senior (6-10 years)
- Principal/Lead (10+ years)

### Step 3: Calculate Resource Demand

ESTIMATE hours needed by role:

**Demand Calculation:**

```
Total Hours by Role = Σ(Task Hours for that Role)

Example:
Data Engineer:
├─ Landing Layer: 80h
├─ Silver Layer: 120h
├─ Gold Layer: 60h
└─ Total: 260h (32.5 days @ 8h/day)
```

**Capacity Planning:**

```
FTE Required = Total Hours / (Available Days × Hours/Day × Utilization)

Example:
260h / (60 days × 8h × 0.80) = 0.68 FTE
Round up = 1.0 FTE Data Engineer
```

### Step 4: Assess Resource Supply

IDENTIFY available capacity:

**Current Team:**

- Who is currently on the team?
- What is their capacity? (100% = 8h/day)
- Any planned leave or absences?
- Other project commitments?

**Net Available Capacity:**

```
Net Capacity = Gross Capacity - Commitments - Leave - Buffer

Example:
John (DE): 160h/month
- Other projects: -40h
- Vacation: -16h (2 days)
- Buffer (15%): -15h
= Net: 89h/month available
```

### Step 5: Perform Gap Analysis

COMPARE demand vs supply:

**Gap Types:**

- **Surplus**: More capacity than needed (underutilization)
- **Deficit**: Less capacity than needed (overallocation)
- **Skill Gap**: Wrong skills available

**Gap Resolution Options:**

- Hire/contract additional resources
- Train existing resources
- Descope or delay work
- Increase utilization (overtime - not sustainable)
- Offshore or nearshore resources

### Step 6: Optimize Resource Allocation

BALANCE workload and efficiency:

**Optimization Principles:**

- **Skill Match**: Assign work to appropriate skill level
- **Leveling**: Smooth peaks and valleys
- **Utilization**: Target 80-85%, not 100%
- **Cross-Training**: Reduce single points of failure
- **Succession**: Plan for transitions and backup

**Optimization Techniques:**

- Resource smoothing (adjust schedule within float)
- Resource leveling (delay non-critical work)
- Fast-tracking (parallel work where possible)
- Crashing (add resources to critical path)

### Step 7: Create Staffing Plan

DOCUMENT resource allocation over time:

**Staffing Plan Components:**

- Ramp-up schedule
- Resource allocation by phase
- Peak vs average staffing
- Contractor vs FTE mix
- Onboarding and offboarding dates

## Output Structure

```markdown
# RESOURCE PLAN - {PROJECT_NAME}

**Plan Date:** {DATE}
**Project Duration:** {N} weeks ({Start} - {End})
**Planner:** {Delivery Lead Name}
**Status:** Draft / Approved / Active

---

## EXECUTIVE SUMMARY

**Resource Requirements:**

- Peak team size: 3.5 FTE
- Average team size: 2.5 FTE
- Total effort: 520 person-hours
- Duration: 10 weeks
- FTE vs Contractor mix: 80% FTE / 20% Contractor

**Resource Gaps Identified:** 1

- BI Developer needed for Sprint 5 (2 weeks)

**Mitigation:** Contract BI developer identified and available

---

## RESOURCE DEMAND BY ROLE

### Demand Summary

| Role                    | Total Hours | Days (@8h) | Weeks | FTE Equiv |
| ----------------------- | ----------- | ---------- | ----- | --------- |
| Senior Data Engineer    | 280h        | 35         | 7     | 1.0       |
| Data Solution Architect | 80h         | 10         | 2     | 0.2       |
| BI Developer            | 120h        | 15         | 3     | 0.3       |
| QA Engineer             | 80h         | 10         | 2     | 0.2       |
| Technical Writer        | 32h         | 4          | 1     | 0.1       |
| DevOps Engineer         | 40h         | 5          | 1     | 0.1       |
| Project Manager         | 80h         | 10         | 2     | 0.2       |
| **TOTAL**               | **712h**    | **89d**    |       | **2.1**   |

**Note:** FTE Equivalent based on project duration of 10 weeks

### Demand by Phase

| Phase         | DE   | Arch | BI   | QA  | Writer | DevOps | PM  | Total FTE |
| ------------- | ---- | ---- | ---- | --- | ------ | ------ | --- | --------- |
| 1: Foundation | 40h  | 60h  | 0h   | 0h  | 0h     | 24h    | 16h | 1.75      |
| 2: Landing    | 80h  | 10h  | 0h   | 0h  | 0h     | 8h     | 16h | 1.43      |
| 3: Silver     | 120h | 10h  | 0h   | 40h | 0h     | 0h     | 20h | 2.38      |
| 4: Gold       | 80h  | 0h   | 100h | 20h | 0h     | 0h     | 16h | 2.70      |
| 5: Deploy     | 40h  | 0h   | 20h  | 20h | 32h    | 8h     | 12h | 1.65      |

**Peak Demand:** Phase 4 (Gold Layer) - 2.70 FTE

---

## RESOURCE SUPPLY ANALYSIS

### Current Team Capacity

**John Smith - Senior Data Engineer**

- Availability: 100% (full-time)
- Capacity: 160h/month (20 days × 8h)
- Other commitments: 10% (meetings, admin)
- Net capacity: 144h/month
- Project duration: 2.5 months
- **Total Available:** 360h

**Sarah Johnson - Data Architect**

- Availability: 25% (part-time, shared resource)
- Capacity: 40h/month (5 days × 8h)
- Other commitments: None for this project
- Net capacity: 40h/month
- Project duration: 2.5 months
- **Total Available:** 100h

**Mike Williams - QA Engineer**

- Availability: 50% (part-time)
- Capacity: 80h/month (10 days × 8h)
- Other commitments: None
- Vacation: 1 week in month 2
- Net capacity: 70h/month (with vacation)
- Project duration: 2.5 months
- **Total Available:** 175h

**Jane Doe - Project Manager**

- Availability: 25% (shared across 4 projects)
- Capacity: 40h/month
- Net capacity: 40h/month
- Project duration: 2.5 months
- **Total Available:** 100h

### Supply Summary

| Role            | Person        | Available Hours | Demand | Gap                |
| --------------- | ------------- | --------------- | ------ | ------------------ |
| Senior Data Eng | John Smith    | 360h            | 280h   | **+80h (surplus)** |
| Data Architect  | Sarah Johnson | 100h            | 80h    | **+20h (surplus)** |
| BI Developer    | TBD           | 0h              | 120h   | **-120h (GAP)** 🔴 |
| QA Engineer     | Mike Williams | 175h            | 80h    | **+95h (surplus)** |
| Tech Writer     | TBD           | 0h              | 32h    | **-32h (GAP)** 🟡  |
| DevOps          | Shared Pool   | 40h             | 40h    | **0h (matched)**   |
| Project Manager | Jane Doe      | 100h            | 80h    | **+20h (surplus)** |

**Critical Gaps:**

- 🔴 **BI Developer:** Need 120h (15 days)
- 🟡 **Technical Writer:** Need 32h (4 days)

---

## GAP RESOLUTION PLAN

### GAP 1: BI Developer (120h needed)

**Options Evaluated:**

**Option A: Contract BI Developer (RECOMMENDED)**

- Source: Contractor pool, pre-vetted
- Rate: $130/h
- Availability: Confirmed for Sprint 5 (2 weeks)
- Cost: 120h × $130 = $15,600
- Pros: Immediate availability, right skills
- Cons: Higher cost than FTE
- **Decision:** APPROVE

**Option B: Train Data Engineer**

- Train John to do BI work
- Training: 1 week
- Cost: Training + reduced velocity
- Pros: Build internal capability
- Cons: Project delay, learning curve
- **Decision:** REJECT (timeline risk)

**Option C: Descope BI Work**

- Delay dashboards to Phase 2
- Cost: $0
- Pros: No additional cost
- Cons: Business value delayed
- **Decision:** REJECT (business priority)

**Selected:** Option A - Contract BI Developer

---

### GAP 2: Technical Writer (32h needed)

**Options Evaluated:**

**Option A: Part-time Technical Writer**

- Source: Internal shared resource
- Rate: $100/h
- Availability: Last 2 weeks of project
- Cost: 32h × $100 = $3,200
- **Decision:** APPROVE

**Option B: Engineers Write Docs**

- Engineers do their own documentation
- Cost: Engineer rates ($150/h vs $100/h)
- Quality: Lower (not core skill)
- **Decision:** REJECT (cost and quality)

**Selected:** Option A - Part-time Technical Writer

---

## RESOURCE ALLOCATION PLAN

### Detailed Assignment by Sprint

#### Sprint 1 (Weeks 1-2): Foundation

| Resource     | Allocation | Hours/Sprint | Tasks                |
| ------------ | ---------- | ------------ | -------------------- |
| John (DE)    | 50%        | 40h          | Infrastructure setup |
| Sarah (Arch) | 100%       | 60h          | Architecture design  |
| DevOps       | 50%        | 24h          | CI/CD setup          |
| Jane (PM)    | 25%        | 16h          | Planning, tracking   |
| **Total**    |            | **140h**     |                      |

**Capacity Check:** ✅ No overallocation

---

#### Sprint 2 (Weeks 3-4): Landing Layer

| Resource     | Allocation | Hours/Sprint | Tasks                       |
| ------------ | ---------- | ------------ | --------------------------- |
| John (DE)    | 100%       | 80h          | DDL, CSV, Parquet ingestion |
| Sarah (Arch) | 25%        | 10h          | Reviews                     |
| DevOps       | 25%        | 8h           | Pipeline setup              |
| Jane (PM)    | 25%        | 16h          | Planning, tracking          |
| **Total**    |            | **114h**     |                             |

**Capacity Check:** ✅ No overallocation

---

#### Sprint 3 (Weeks 5-6): Silver Layer - Part 1

| Resource     | Allocation | Hours/Sprint | Tasks              |
| ------------ | ---------- | ------------ | ------------------ |
| John (DE)    | 100%       | 80h          | Transformations    |
| Sarah (Arch) | 25%        | 10h          | Reviews            |
| Mike (QA)    | 50%        | 20h          | Test planning      |
| Jane (PM)    | 25%        | 20h          | Planning, tracking |
| **Total**    |            | **130h**     |                    |

**Capacity Check:** ✅ No overallocation

---

#### Sprint 4 (Week 7): Silver Layer - Part 2

| Resource  | Allocation | Hours/Sprint | Tasks              |
| --------- | ---------- | ------------ | ------------------ |
| John (DE) | 100%       | 40h          | Quality framework  |
| Mike (QA) | 100%       | 40h          | Unit tests         |
| Jane (PM) | 25%        | 10h          | Planning, tracking |
| **Total** |            | **90h**      |                    |

**Capacity Check:** ✅ No overallocation

---

#### Sprint 5 (Weeks 8-9): Gold Layer

| Resource      | Allocation | Hours/Sprint | Tasks                       |
| ------------- | ---------- | ------------ | --------------------------- |
| John (DE)     | 100%       | 80h          | Gold enrichment             |
| **Alex (BI)** | 100%       | 100h         | Semantic models, dashboards |
| Mike (QA)     | 25%        | 20h          | Testing                     |
| Jane (PM)     | 25%        | 16h          | Planning, tracking          |
| **Total**     |            | **216h**     |                             |

**Note:** Alex is contractor, billed at $130/h

**Capacity Check:** ✅ No overallocation

---

#### Sprint 6 (Week 10): Deployment

| Resource           | Allocation | Hours/Sprint | Tasks                       |
| ------------------ | ---------- | ------------ | --------------------------- |
| John (DE)          | 100%       | 40h          | Deployment, go-live support |
| **Maria (Writer)** | 100%       | 32h          | Documentation               |
| Mike (QA)          | 50%        | 20h          | UAT support                 |
| DevOps             | 25%        | 8h           | Production setup            |
| Jane (PM)          | 25%        | 12h          | Go-live coordination        |
| **Total**          |            | **112h**     |                             |

**Note:** Maria is part-time writer, billed at $100/h

**Capacity Check:** ✅ No overallocation

---

## RESOURCE LOADING CHART
```

Resource Utilization by Sprint

John (DE)
100% ┤ ████ ████ ████ ████ ████ ████
80% ┤  
 60% ┤  
 40% ┤ ████
20% ┤
0% └───┬────┬────┬────┬────┬────┬────
S1 S2 S3 S4 S5 S6

Sarah (Arch)
100% ┤ ████
80% ┤
60% ┤
40% ┤
20% ┤ ██ ██
0% └───┬────┬────┬────┬────┬────┬────
S1 S2 S3 S4 S5 S6

Alex (BI Contractor)
100% ┤ ████ ████
80% ┤
60% ┤
40% ┤
20% ┤
0% └───┬────┬────┬────┬────┬────┬────
S1 S2 S3 S4 S5 S6

Mike (QA)
100% ┤ ████
80% ┤
60% ┤
40% ┤ ████
20% ┤ ████ ██
0% └───┬────┬────┬────┬────┬────┬────
S1 S2 S3 S4 S5 S6

```

**Observations:**
- John (DE) heavily utilized Sprints 2-6
- Alex (BI) only needed for Sprint 5
- No severe overallocation periods
- Good balance overall

---

## COST IMPLICATIONS

### Labor Cost by Resource

| Resource | Hours | Rate | Cost | Type |
|----------|-------|------|------|------|
| John (DE) | 280h | $150/h | $42,000 | FTE |
| Sarah (Arch) | 80h | $200/h | $16,000 | FTE |
| Alex (BI) | 120h | $130/h | $15,600 | Contractor |
| Mike (QA) | 80h | $120/h | $9,600 | FTE |
| Maria (Writer) | 32h | $100/h | $3,200 | Contractor |
| DevOps | 40h | $150/h | $6,000 | Shared |
| Jane (PM) | 80h | $180/h | $14,400 | FTE |
| **TOTAL** | **712h** | | **$106,800** | |

**Cost Breakdown:**
- FTE Cost: $88,000 (82%)
- Contractor Cost: $18,800 (18%)

**Budget Impact:**
- Labor Budget: $109,000
- Forecast Cost: $106,800
- **Variance:** +$2,200 (2% under budget) ✅

---

## ONBOARDING & OFFBOARDING PLAN

### Onboarding Schedule

**Week 1:**
- ✅ John (DE) - Already on team
- ✅ Sarah (Arch) - Already on team
- ✅ Mike (QA) - Already on team
- ✅ Jane (PM) - Already on team

**Week 8:**
- 📅 Alex (BI Contractor)
  - Onboarding: 1 day
  - Access provisioning: 2 days before start
  - Knowledge transfer: John + Sarah

**Week 9:**
- 📅 Maria (Technical Writer)
  - Onboarding: 0.5 day
  - Access: Read-only to code, docs
  - Knowledge transfer: John

### Offboarding Schedule

**End of Week 9:**
- 📅 Alex (BI Contractor)
  - Knowledge transfer: 4h to John
  - Documentation: Complete
  - Access revocation: End of contract

**End of Week 10:**
- 📅 Maria (Technical Writer)
  - Final documents delivered
  - Access revocation: End of contract

**End of Week 10:**
- 📅 Project team transition to support model
  - John: 20% ongoing support
  - Others: Roll off to next projects

---

## RISK MITIGATION

### Resource Risks

**🟡 RISK: John (DE) Single Point of Failure**
- **Mitigation:**
  - Cross-train Mike (QA) on pipeline basics
  - Comprehensive documentation
  - Backup contractor identified (Tom, available on 1 week notice)
- **Contingency:** Budget for Tom if needed ($150/h)

**🟡 RISK: Contractor No-Show**
- **Mitigation:**
  - Contracts signed 2 weeks before needed
  - Backup contractors in pool
  - Can extend John or delay if critical
- **Contingency:** 1-week schedule buffer

**🟢 RISK: Vacation/Sick Leave**
- **Mitigation:**
  - 15% capacity buffer built in
  - Float in schedule for non-critical path
  - Cross-training for coverage
- **Contingency:** Already accounted for

---

## SKILLS MATRIX

| Resource | SQL | PySpark | BI/DAX | Testing | Docs | Arch |
|----------|-----|---------|--------|---------|------|------|
| John (DE) | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| Sarah (Arch) | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| Alex (BI) | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ |
| Mike (QA) | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| Maria (Writer) | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ |

**Legend:**
- ⭐⭐⭐ Expert (5+ years)
- ⭐⭐ Proficient (2-5 years)
- ⭐ Basic (0-2 years)

**Observations:**
- Good coverage for SQL, PySpark (John)
- Alex brings specialized BI skills
- No significant skill gaps

---

## RESOURCE OPTIMIZATION OPPORTUNITIES

**1. Extend John's Availability**
- Currently: 100% allocated
- Opportunity: Has 80h surplus capacity
- Recommendation: Use for Phase 2 planning or other projects

**2. Reduce Contractor Costs**
- Alex (BI): $15,600
- Alternative: Train John in Power BI ($2,000 training + 1 week time)
- Trade-off: Save $5,000 but add 1 week to timeline
- Recommendation: Not worth the delay

**3. Leverage Shared Resources**
- DevOps pool working well
- Consider for Technical Writer (negotiate shared access)
- Potential savings: $1,000-$2,000

---

## APPROVAL & SIGN-OFF

| Stakeholder | Role | Reviewed | Approved | Date |
|-------------|------|----------|----------|------|
| | Delivery Lead | ☐ | ☐ | |
| | Technical Lead | ☐ | ☐ | |
| | Resource Manager | ☐ | ☐ | |
| | Finance | ☐ | ☐ | |

---

**Plan Owner:** {Delivery Lead Name}
**Last Updated:** {DATE}
**Next Review:** Weekly during sprint planning
**Status:** Draft / Approved / Active
```

## Best Practices

1. **Plan for 80-85% Utilization**: Not 100%, people need buffer time
2. **Include Ramp-Up/Down**: Don't assume instant productivity
3. **Cross-Train**: Reduce single points of failure
4. **Track Actuals**: Compare planned vs actual for learning
5. **Update Weekly**: Resource plans change, keep current
6. **Buffer for Unknowns**: 15-20% contingency
7. **Mix FTE and Contractors**: Balance cost and flexibility
8. **Skill Match**: Don't waste senior people on junior work

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual resource planning: 8-12 hours
- With DeliveryPro agent: 2-4 hours
- **Effort reduction: 65-75%**
