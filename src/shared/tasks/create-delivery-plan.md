---
task: create-delivery-plan
version: 1.0
elicit: true
description: Create detailed delivery plan with resource allocation and work breakdown
---

# Create Detailed Delivery Plan

## Purpose

Generate a comprehensive delivery plan with work breakdown structure (WBS), sprint/iteration planning, resource allocation, and critical path identification.

## Process

### Step 1: Gather Planning Requirements

ASK the user for the following information:

1. **Project Scope**: What needs to be delivered? List of features/requirements
2. **Timeline**: Target completion date or duration
3. **Team Composition**: Available roles and their capacity
4. **Working Model**: Agile/Scrum, Waterfall, Hybrid?
5. **Sprint Length**: If Agile, sprint duration (1-4 weeks typical)
6. **Constraints**: Fixed deadlines, resource limitations, dependencies
7. **Prioritization**: Must-have vs nice-to-have features

### Step 2: Create Work Breakdown Structure (WBS)

DECOMPOSE project into manageable work packages:

**WBS Levels:**

1. **Level 1**: Major phases (Foundation, Development, Testing, Deployment)
2. **Level 2**: Deliverables per phase (Landing Layer, Silver Layer, etc.)
3. **Level 3**: Activities per deliverable (DDL, ETL, Tests, Docs)
4. **Level 4**: Tasks per activity (specific work items)

**WBS Principles:**

- 100% Rule: WBS includes 100% of work
- Mutually Exclusive: No overlap between work packages
- Outcome-Oriented: Focus on deliverables, not activities
- Right Size: 8-80 hour rule (tasks should be 1-10 days)

### Step 3: Estimate Effort by Work Package

CALCULATE effort for each work package:

**Estimation Techniques:**

**Three-Point Estimation:**

```
Optimistic (O): Best case scenario
Most Likely (M): Realistic estimate
Pessimistic (P): Worst case scenario

Expected = (O + 4M + P) / 6
```

**Story Points (for Agile):**

- Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21
- Based on complexity, not hours
- Team velocity determines sprint capacity

**Task-Based Estimation:**

- List all tasks
- Estimate hours per task
- Sum to get work package total
- Add buffer (15-20%)

### Step 4: Sequence Activities

DETERMINE logical order and dependencies:

**Dependency Types:**

- **Finish-to-Start (FS)**: B starts when A finishes (most common)
- **Start-to-Start (SS)**: B starts when A starts
- **Finish-to-Finish (FF)**: B finishes when A finishes
- **Start-to-Finish (SF)**: B finishes when A starts (rare)

**Critical Path Method (CPM):**

1. Identify all activity sequences
2. Calculate earliest start/finish times (forward pass)
3. Calculate latest start/finish times (backward pass)
4. Identify critical path (zero slack activities)
5. Focus management on critical path activities

**Parallel vs Sequential:**

- Identify work that can be done in parallel
- Balance resource loading
- Minimize project duration

### Step 5: Allocate Resources

ASSIGN team members to work packages:

**Resource Allocation Principles:**

- Match skills to tasks
- Balance workload across team
- Avoid overallocation (>100% utilization)
- Plan for ramp-up and ramp-down
- Account for vacations, holidays, sick leave
- Include training and knowledge transfer time

**Utilization Planning:**

- 80-85% utilization for planning (not 100%)
- Reserve 15-20% for meetings, emails, context switching
- Peak utilization should be temporary, not sustained

### Step 6: Create Sprint/Iteration Plan

For Agile projects, ORGANIZE work into sprints:

**Sprint Planning:**

- Sprint goal (what business value)
- Sprint backlog (which stories/tasks)
- Team capacity (available hours)
- Sprint velocity (historical story points)

**Sprint Structure:**

```
Sprint N (2 weeks)
├─ Sprint Planning (4h)
├─ Daily Standups (10 × 15min)
├─ Development Work
├─ Sprint Review/Demo (2h)
└─ Sprint Retrospective (1.5h)
```

### Step 7: Identify Milestones and Gates

DEFINE key checkpoints and decision points:

**Milestone Types:**

- Phase completion
- Deliverable sign-off
- Decision gates (go/no-go)
- Stakeholder reviews
- External dependencies

**Quality Gates:**

- Code review complete
- Tests passing (e.g., 80% coverage)
- Security scan passed
- Performance benchmarks met
- Documentation complete

## Output Structure

```markdown
# DELIVERY PLAN - {PROJECT_NAME}

**Plan Date:** {DATE}
**Project Duration:** {N} weeks ({Start} - {End})
**Methodology:** Agile/Scrum (2-week sprints)
**Team Size:** {X} FTE peak, {Y} FTE average
**Plan Owner:** {Delivery Lead Name}

---

## PROJECT OVERVIEW

**Objective:** {Clear statement of what we're building}

**Key Deliverables:**

1. {Deliverable 1}
2. {Deliverable 2}
3. {Deliverable 3}

**Success Criteria:**

- {Measurable outcome 1}
- {Measurable outcome 2}
- {Measurable outcome 3}

---

## WORK BREAKDOWN STRUCTURE

### Phase 1: Foundation (Weeks 1-2)

**1.1 Infrastructure Setup**
├─ 1.1.1 Azure subscription and resource groups (4h)
├─ 1.1.2 Synapse/SQL Database provisioning (8h)
├─ 1.1.3 Data Lake storage setup (4h)
├─ 1.1.4 Networking and security (8h)
└─ **Subtotal: 24 hours**

**1.2 Security & Governance**
├─ 1.2.1 RBAC configuration (6h)
├─ 1.2.2 Encryption setup (4h)
├─ 1.2.3 Audit logging configuration (4h)
├─ 1.2.4 Data classification (6h)
└─ **Subtotal: 20 hours**

**1.3 Development Environment**
├─ 1.3.1 Git repository setup (2h)
├─ 1.3.2 CI/CD pipeline configuration (8h)
├─ 1.3.3 Development tools installation (4h)
├─ 1.3.4 Team onboarding (6h)
└─ **Subtotal: 20 hours**

**Phase 1 Total: 64 hours (8 days × 1 FTE)**

---

### Phase 2: Landing Layer (Weeks 3-4)

**2.1 DDL Development**
├─ 2.1.1 Landing table design (4h)
├─ 2.1.2 DDL script creation (6h)
├─ 2.1.3 Audit columns setup (2h)
├─ 2.1.4 Deployment and testing (4h)
└─ **Subtotal: 16 hours**

**2.2 CSV Ingestion**
├─ 2.2.1 Bulk insert logic (8h)
├─ 2.2.2 Error handling (6h)
├─ 2.2.3 Data lineage tracking (4h)
├─ 2.2.4 Testing with sample data (6h)
└─ **Subtotal: 24 hours**

**2.3 Parquet Ingestion**
├─ 2.3.1 PySpark ingestion script (10h)
├─ 2.3.2 Schema inference (4h)
├─ 2.3.3 Error handling (6h)
├─ 2.3.4 Testing and validation (6h)
└─ **Subtotal: 26 hours**

**2.4 Reference Data**
├─ 2.4.1 JSON parsing logic (8h)
├─ 2.4.2 TSV loading script (4h)
├─ 2.4.3 Reference table population (4h)
└─ **Subtotal: 16 hours**

**Phase 2 Total: 82 hours (10 days × 1 FTE)**

---

### Phase 3: Silver Layer (Weeks 5-7)

**3.1 DDL Development**
├─ 3.1.1 Silver table design (proper types) (6h)
├─ 3.1.2 DDL script creation (8h)
├─ 3.1.3 Indexes and constraints (6h)
├─ 3.1.4 Reject table design (4h)
└─ **Subtotal: 24 hours**

**3.2 Transformation Logic**
├─ 3.2.1 Type conversion logic (12h)
├─ 3.2.2 Data cleansing rules (10h)
├─ 3.2.3 Business rule implementation (12h)
├─ 3.2.4 Computed columns (8h)
└─ **Subtotal: 42 hours**

**3.3 Data Quality Framework**
├─ 3.3.1 Validation rules (15h)
├─ 3.3.2 Quality scoring logic (8h)
├─ 3.3.3 Reject handling process (8h)
├─ 3.3.4 Monitoring and alerting (10h)
└─ **Subtotal: 41 hours**

**3.4 Testing**
├─ 3.4.1 Unit test development (12h)
├─ 3.4.2 Integration testing (10h)
├─ 3.4.3 Data validation (8h)
└─ **Subtotal: 30 hours**

**Phase 3 Total: 137 hours (17 days × 1 FTE or 9 days × 2 FTE)**

---

### Phase 4: Gold Layer (Weeks 8-9)

**4.1 DDL Development**
├─ 4.1.1 Gold table design (6h)
├─ 4.1.2 Enriched table DDL (4h)
├─ 4.1.3 Aggregated table DDL (4h)
└─ **Subtotal: 14 hours**

**4.2 Enrichment Logic**
├─ 4.2.1 JOIN logic with reference tables (10h)
├─ 4.2.2 Business metrics calculation (12h)
├─ 4.2.3 Temporal dimensions (8h)
└─ **Subtotal: 30 hours**

**4.3 Aggregation Logic**
├─ 4.3.1 Summary table logic (8h)
├─ 4.3.2 KPI calculations (10h)
├─ 4.3.3 Performance optimization (8h)
└─ **Subtotal: 26 hours**

**4.4 Semantic Models**
├─ 4.4.1 Power BI semantic model (12h)
├─ 4.4.2 DAX measures (10h)
├─ 4.4.3 Dashboard prototypes (14h)
└─ **Subtotal: 36 hours**

**Phase 4 Total: 106 hours (13 days × 1 FTE or 7 days × 2 FTE)**

---

### Phase 5: Testing & Deployment (Week 10)

**5.1 Testing**
├─ 5.1.1 UAT preparation (4h)
├─ 5.1.2 UAT execution support (12h)
├─ 5.1.3 Bug fixes (10h)
└─ **Subtotal: 26 hours**

**5.2 Documentation**
├─ 5.2.1 Architecture documentation (8h)
├─ 5.2.2 Operational runbooks (8h)
├─ 5.2.3 User guides (6h)
└─ **Subtotal: 22 hours**

**5.3 Deployment**
├─ 5.3.1 Deployment checklist (4h)
├─ 5.3.2 Production deployment (6h)
├─ 5.3.3 Smoke testing (4h)
├─ 5.3.4 Go-live support (8h)
└─ **Subtotal: 22 hours**

**Phase 5 Total: 70 hours (9 days × 1 FTE)**

---

## EFFORT SUMMARY

| Phase                     | Hours   | Days (@8h) | FTE | Duration     |
| ------------------------- | ------- | ---------- | --- | ------------ |
| Phase 1: Foundation       | 64      | 8          | 1.0 | 2 weeks      |
| Phase 2: Landing Layer    | 82      | 10         | 1.0 | 2 weeks      |
| Phase 3: Silver Layer     | 137     | 17         | 1.5 | 3 weeks      |
| Phase 4: Gold Layer       | 106     | 13         | 1.5 | 2 weeks      |
| Phase 5: Testing & Deploy | 70      | 9          | 1.0 | 1 week       |
| **TOTAL**                 | **459** | **57**     |     | **10 weeks** |

**Notes:**

- Assumes 80% utilization (6.4 productive hours/day)
- Includes buffer for meetings, reviews, emails
- Does not include PM overhead (tracked separately)

---

## SPRINT PLAN (Agile/Scrum - 2-week sprints)

### Sprint 1 (Weeks 1-2): Foundation

**Sprint Goal:** Operational infrastructure and development environment

**Sprint Backlog:**
| ID | Story | Est | Owner | Status |
|----|-------|-----|-------|--------|
| US-001 | Azure infrastructure setup | 8 SP | Architect | ⚪ |
| US-002 | Security and RBAC configuration | 5 SP | Architect | ⚪ |
| US-003 | Development environment setup | 3 SP | DevOps | ⚪ |
| US-004 | Team onboarding | 2 SP | PM | ⚪ |

**Sprint Capacity:** 18 story points
**Sprint Velocity (target):** 16-18 SP

---

### Sprint 2 (Weeks 3-4): Landing Layer

**Sprint Goal:** Ingest CSV, Parquet, and reference data to Landing

**Sprint Backlog:**
| ID | Story | Est | Owner | Status |
|----|-------|-----|-------|--------|
| US-005 | Landing DDL and tables | 3 SP | Data Eng | ⚪ |
| US-006 | CSV bulk ingestion | 5 SP | Data Eng | ⚪ |
| US-007 | Parquet PySpark ingestion | 8 SP | Data Eng | ⚪ |
| US-008 | Reference data loading | 3 SP | Data Eng | ⚪ |

**Sprint Capacity:** 19 story points

---

### Sprint 3 (Weeks 5-6): Silver Layer - Part 1

**Sprint Goal:** Transformation logic and type conversions

**Sprint Backlog:**
| ID | Story | Est | Owner | Status |
|----|-------|-----|-------|--------|
| US-009 | Silver DDL with proper types | 5 SP | Data Eng | ⚪ |
| US-010 | Type conversion logic | 8 SP | Data Eng | ⚪ |
| US-011 | Data cleansing rules | 5 SP | Data Eng | ⚪ |

**Sprint Capacity:** 18 story points

---

### Sprint 4 (Week 7): Silver Layer - Part 2

**Sprint Goal:** Data quality framework operational

**Sprint Backlog:**
| ID | Story | Est | Owner | Status |
|----|-------|-----|-------|--------|
| US-012 | Validation rules and scoring | 8 SP | Data Eng | ⚪ |
| US-013 | Reject handling process | 5 SP | Data Eng | ⚪ |
| US-014 | Unit tests for Silver | 5 SP | QA | ⚪ |

**Sprint Capacity:** 18 story points

---

### Sprint 5 (Weeks 8-9): Gold Layer

**Sprint Goal:** Business-ready analytics and BI models

**Sprint Backlog:**
| ID | Story | Est | Owner | Status |
|----|-------|-----|-------|--------|
| US-015 | Gold enriched tables | 8 SP | Data Eng | ⚪ |
| US-016 | Gold aggregated tables | 5 SP | Data Eng | ⚪ |
| US-017 | Power BI semantic model | 8 SP | BI Dev | ⚪ |
| US-018 | Dashboard prototypes | 5 SP | BI Dev | ⚪ |

**Sprint Capacity:** 26 story points (2 devs)

---

### Sprint 6 (Week 10): Testing & Deployment

**Sprint Goal:** Production go-live successful

**Sprint Backlog:**
| ID | Story | Est | Owner | Status |
|----|-------|-----|-------|--------|
| US-019 | UAT execution | 8 SP | QA | ⚪ |
| US-020 | Documentation complete | 5 SP | Writer | ⚪ |
| US-021 | Production deployment | 5 SP | DevOps | ⚪ |

**Sprint Capacity:** 18 story points

---

## RESOURCE ALLOCATION

### Team Composition by Sprint

| Sprint   | Data Eng | Architect | BI Dev | QA  | Writer | DevOps | PM   | Total FTE |
| -------- | -------- | --------- | ------ | --- | ------ | ------ | ---- | --------- |
| Sprint 1 | 0.5      | 1.0       | 0      | 0   | 0      | 0.5    | 0.25 | 2.25      |
| Sprint 2 | 1.0      | 0.25      | 0      | 0   | 0      | 0      | 0.25 | 1.5       |
| Sprint 3 | 1.5      | 0         | 0      | 0.5 | 0      | 0      | 0.25 | 2.25      |
| Sprint 4 | 1.0      | 0         | 0      | 1.0 | 0      | 0      | 0.25 | 2.25      |
| Sprint 5 | 1.0      | 0         | 1.0    | 0   | 0      | 0      | 0.25 | 2.25      |
| Sprint 6 | 0.5      | 0         | 0      | 0.5 | 0.5    | 0.5    | 0.25 | 2.25      |

**Peak Team Size:** 2.25 FTE (Sprint 1, 3-6)
**Average Team Size:** 2.1 FTE

### Individual Allocation

**John Smith - Senior Data Engineer**

- Sprint 1: 50% (4h/day)
- Sprint 2-5: 100% (8h/day)
- Sprint 6: 50% (4h/day)

**Sarah Johnson - Data Architect**

- Sprint 1: 100% (8h/day)
- Sprint 2: 25% (2h/day - reviews)
- Sprint 3-6: 0%

**Mike Williams - BI Developer**

- Sprint 1-4: 0%
- Sprint 5: 100% (8h/day)
- Sprint 6: 0%

**Jane Doe - QA Engineer**

- Sprint 1-2: 0%
- Sprint 3: 50% (4h/day)
- Sprint 4: 100% (8h/day)
- Sprint 5: 0%
- Sprint 6: 50% (4h/day)

---

## DEPENDENCIES

### Internal Dependencies

| From                    | To                         | Type | Notes    |
| ----------------------- | -------------------------- | ---- | -------- |
| Infrastructure (US-001) | All development            | FS   | Blocking |
| Landing DDL (US-005)    | CSV ingestion (US-006)     | FS   | Blocking |
| Landing DDL (US-005)    | Parquet ingestion (US-007) | FS   | Blocking |
| Silver DDL (US-009)     | Transformations (US-010)   | FS   | Blocking |
| Silver complete         | Gold development           | FS   | Blocking |

### External Dependencies

| Dependency                  | Owner        | Required By     | Status         | Risk      |
| --------------------------- | ------------ | --------------- | -------------- | --------- |
| Azure subscription approval | IT Dept      | Sprint 1, Day 1 | ✅ Done        | 🟢 Low    |
| Source data access          | Data Owner   | Sprint 2, Day 1 | 🔄 In Progress | 🟡 Medium |
| BI tool licenses            | Procurement  | Sprint 5, Day 1 | ⚪ Pending     | 🟢 Low    |
| Production change window    | Change Board | Sprint 6, Day 1 | ⚪ Pending     | 🟡 Medium |

---

## CRITICAL PATH
```

START → Infrastructure (2w) → Landing Layer (2w) → Silver Layer (3w) →
Gold Layer (2w) → Testing (1w) → END

Total Duration: 10 weeks
Float/Slack: 0 days (critical path has no slack)

```

**Critical Path Activities:**
1. ✅ Infrastructure setup (2 weeks) - NO DELAY ALLOWED
2. ✅ Landing layer development (2 weeks) - NO DELAY ALLOWED
3. ✅ Silver layer development (3 weeks) - NO DELAY ALLOWED
4. ✅ Gold layer development (2 weeks) - NO DELAY ALLOWED
5. ✅ Testing and deployment (1 week) - NO DELAY ALLOWED

**Non-Critical Activities (have slack):**
- Documentation (can be done in parallel)
- Training materials (can extend beyond go-live)
- Dashboard enhancements (nice-to-have features)

---

## MILESTONES & GATES

| # | Milestone | Date | Success Criteria | Gate Type |
|---|-----------|------|------------------|-----------|
| M1 | Infrastructure Ready | End Sprint 1 | All Azure resources provisioned | Quality Gate |
| M2 | Landing Layer Operational | End Sprint 2 | 3 data sources ingesting | Demo |
| M3 | Silver Layer Certified | End Sprint 4 | Data quality >95% | Quality Gate |
| M4 | Gold Layer Complete | End Sprint 5 | BI models functional | Demo |
| M5 | Production Go-Live | End Sprint 6 | Zero critical defects | Go/No-Go |

---

## RISK MANAGEMENT IN PLAN

**Schedule Risks Identified:**

**🟡 RISK: Landing layer takes longer**
- Mitigation: Start Sprint 2 early if Sprint 1 finishes ahead
- Contingency: Reduce Gold layer scope if needed

**🟡 RISK: Data quality issues delay Silver**
- Mitigation: Early data profiling in Sprint 1
- Contingency: Add 1-week buffer to Sprint 4

**🟢 RISK: Resource unavailability**
- Mitigation: Cross-training, backup resources identified
- Contingency: Extend timeline by 1 sprint if needed

---

## COMMUNICATION PLAN

**Daily Standup:** 15 minutes, 9:00 AM
- What did you do yesterday?
- What will you do today?
- Any blockers?

**Sprint Planning:** 4 hours, first day of sprint
- Review backlog
- Select stories for sprint
- Commit to sprint goal

**Sprint Review:** 2 hours, last day of sprint
- Demo completed work
- Gather feedback
- Update backlog

**Sprint Retrospective:** 1.5 hours, last day of sprint
- What went well?
- What could improve?
- Action items for next sprint

**Weekly Status Report:** Friday, 4:00 PM
- Progress update to stakeholders
- Risks and issues
- Next week's plan

---

**Plan Owner:** {Delivery Lead Name}
**Last Updated:** {DATE}
**Next Review:** Weekly during sprint planning
**Approval Status:** Draft / Approved / Active
```

## Best Practices

1. **Bottom-Up Estimates**: Get input from those doing the work
2. **Include Buffers**: Add 15-20% for unknowns
3. **Balance Resources**: Avoid overallocation (keep at 80-85%)
4. **Identify Critical Path**: Focus on activities that affect timeline
5. **Plan for Risks**: Build contingency into critical path
6. **Update Weekly**: Keep plan current with actuals
7. **Track Variances**: Learn from differences between plan and actual
8. **Communicate Changes**: Keep stakeholders informed of plan updates

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual delivery planning: 16-20 hours
- With DeliveryPro agent: 4-6 hours
- **Effort reduction: 70-75%**
