---
task: create-roadmap
version: 1.0
elicit: true
description: Define project roadmap with phases, milestones, and delivery timeline
---

# Create Project Roadmap

## Purpose

Generate a comprehensive project roadmap with clear phases, milestones, dependencies, and success criteria aligned with business objectives.

## Process

### Step 1: Gather Roadmap Requirements

ASK the user for the following information:

1. **Project Vision**: What is the end goal? What problem are we solving?
2. **Timeline Horizon**: How many months/quarters to plan? (3-12 months typical)
3. **Major Deliverables**: What are the key outputs at the end?
4. **Business Milestones**: Any fixed dates or deadlines? (regulatory, fiscal year-end, etc.)
5. **Resource Constraints**: Team size, budget limits, availability
6. **Dependencies**: External systems, teams, or approvals needed
7. **Phases**: Prefer sequential, parallel, or hybrid approach?

### Step 2: Define Roadmap Phases

CREATE clear phases with objectives:

**Typical Phase Structure:**

**Phase 1: Foundation (15-20% of timeline)**

- Infrastructure setup and provisioning
- Security and governance framework
- Development environment setup
- Team onboarding and training

**Phase 2: Core Development (40-50% of timeline)**

- Landing layer implementation
- Silver layer transformation logic
- Data quality framework
- Core pipeline development

**Phase 3: Enhancement (20-25% of timeline)**

- Gold layer and business metrics
- Advanced analytics and aggregations
- Dashboard and reporting layer
- Integration with downstream systems

**Phase 4: Validation & Go-Live (15-20% of timeline)**

- User acceptance testing (UAT)
- Performance tuning and optimization
- Documentation and training
- Production deployment
- Post-launch stabilization

### Step 3: Define Milestones

ESTABLISH measurable milestones for each phase:

**Milestone Characteristics:**

- Specific and measurable
- Time-bound (target date)
- Achievable and realistic
- Business value aligned
- Clear success criteria
- Reviewable and demonstrable

**Example Milestones:**

- ✅ Infrastructure provisioned and secured
- ✅ Landing layer operational with 3 data sources
- ✅ Silver layer certified (data quality > 95%)
- ✅ Gold layer live with 10 business metrics
- ✅ UAT completed with sign-off
- ✅ Production go-live successful

### Step 4: Map Dependencies

IDENTIFY dependencies and sequence:

**Types of Dependencies:**

- Technical: Infrastructure before development
- Resource: Key person availability
- External: Third-party integrations, approvals
- Data: Source system readiness
- Business: Stakeholder decisions, sign-offs

**Dependency Mapping:**

- Critical path identification
- Parallel workstreams
- Risk areas (single points of failure)
- Buffer zones for high-risk dependencies

### Step 5: Allocate Resources

PLAN resource allocation across phases:

**Resource Planning:**

- Peak team size vs average
- Ramp-up and ramp-down curves
- Skill mix per phase
- Part-time vs full-time allocations
- Contractor vs FTE mix

### Step 6: Define Success Metrics

ESTABLISH KPIs for roadmap tracking:

**Metrics to Track:**

- On-time delivery (milestone hit rate %)
- Budget adherence (spend vs budget %)
- Scope completion (delivered vs planned %)
- Quality metrics (defect rate, test coverage)
- Stakeholder satisfaction scores

## Output Structure

```markdown
# PROJECT ROADMAP - {PROJECT_NAME}

## Vision & Objectives

**Project Vision:**
{Clear statement of what we're building and why}

**Business Objectives:**

1. {Objective 1}
2. {Objective 2}
3. {Objective 3}

**Success Criteria:**

- {Measurable outcome 1}
- {Measurable outcome 2}
- {Measurable outcome 3}

---

## Timeline Overview

**Duration:** {N} months ({Start Date} - {End Date})
**Phases:** {M} phases
**Major Milestones:** {K} milestones
**Team Size:** {X-Y} FTE (average-peak)

---

## Phase Breakdown

### Q1 2026: Phase 1 - Foundation (Weeks 1-8)

**Objective:** Establish secure, scalable infrastructure and development environment

**Key Activities:**
├─ Week 1-2: Infrastructure provisioning (Azure/AWS)
├─ Week 3-4: Security & governance setup (RBAC, encryption, auditing)
├─ Week 5-6: Landing layer architecture design
├─ Week 7-8: Development environment setup & team onboarding

**Deliverables:**

- ✅ Cloud infrastructure operational
- ✅ Security framework implemented
- ✅ Landing layer design approved
- ✅ Development environment ready

**Resources:**

- 1x Data Solution Architect (full-time)
- 1x Data Engineer (full-time)
- 0.5x Security Engineer (part-time)
- 0.25x Project Manager

**Dependencies:**

- ⚠️ Azure subscription approval (Week 1)
- ⚠️ Security policy sign-off (Week 3)

**Milestone:** Infrastructure Foundation Complete
**Success Criteria:**

- All Azure resources provisioned
- Security audit passed
- Development environment tested
  **Target Date:** End of Week 8

---

### Q2 2026: Phase 2 - Core Development (Weeks 9-20)

**Objective:** Build Landing and Silver layers with data quality framework

**Key Activities:**
├─ Week 9-12: Landing layer implementation (CSV, Parquet ingestion)
├─ Week 13-16: Silver layer transformation logic
├─ Week 17-20: Data quality framework and validation rules

**Deliverables:**

- ✅ 3+ data sources ingesting to Landing
- ✅ Silver layer with typed data and quality checks
- ✅ Reject handling and data lineage tracking
- ✅ Unit test suite (80%+ coverage)

**Resources:**

- 2x Data Engineer (full-time)
- 0.5x Data Architect (reviews)
- 0.5x QA Engineer (testing)
- 0.25x Project Manager

**Dependencies:**

- ⚠️ Source data access granted (Week 9)
- ⚠️ Schema definitions finalized (Week 10)

**Milestone:** Silver Layer Certified
**Success Criteria:**

- Data quality > 95% valid records
- All unit tests passing
- Performance benchmarks met
  **Target Date:** End of Week 20

---

### Q3 2026: Phase 3 - Analytics Layer (Weeks 21-32)

**Objective:** Deliver Gold layer with business metrics and analytics

**Key Activities:**
├─ Week 21-24: Gold layer enrichment (JOINs, lookups)
├─ Week 25-28: Business metrics and KPIs
├─ Week 29-32: Dashboard prototypes and semantic models

**Deliverables:**

- ✅ Gold enriched tables with business dimensions
- ✅ Gold aggregated tables with KPIs
- ✅ Semantic models for BI tools
- ✅ Dashboard prototypes

**Resources:**

- 1x Data Engineer (full-time)
- 1x BI Developer (full-time)
- 0.5x Data Analyst (requirements)
- 0.25x Project Manager

**Dependencies:**

- ⚠️ Business requirements confirmed (Week 21)
- ⚠️ BI tool licenses procured (Week 25)

**Milestone:** Analytics Layer Live
**Success Criteria:**

- 10+ business metrics operational
- Dashboard response time < 3 seconds
- Stakeholder demo successful
  **Target Date:** End of Week 32

---

### Q4 2026: Phase 4 - Go-Live & Optimization (Weeks 33-40)

**Objective:** Production deployment, tuning, and stabilization

**Key Activities:**
├─ Week 33-36: User acceptance testing (UAT)
├─ Week 37-38: Performance tuning and optimization
├─ Week 39: Production deployment
├─ Week 40: Post-launch support and stabilization

**Deliverables:**

- ✅ UAT sign-off from business users
- ✅ Performance benchmarks achieved
- ✅ Production deployment successful
- ✅ Documentation and training complete

**Resources:**

- 1x Data Engineer (full-time)
- 0.5x QA Engineer (UAT support)
- 0.5x Technical Writer (documentation)
- 0.25x Project Manager

**Dependencies:**

- ⚠️ UAT environment ready (Week 33)
- ⚠️ Production change approval (Week 38)

**Milestone:** Production Go-Live
**Success Criteria:**

- Zero critical defects in production
- All UAT test cases passed
- Training sessions completed
  **Target Date:** End of Week 39

---

## Milestone Summary

| #   | Milestone                 | Target Date | Phase      | Status |
| --- | ------------------------- | ----------- | ---------- | ------ |
| 1   | Infrastructure Foundation | Week 8      | Foundation | 🟢     |
| 2   | Landing Layer Operational | Week 12     | Core Dev   | 🟢     |
| 3   | Silver Layer Certified    | Week 20     | Core Dev   | 🟡     |
| 4   | Analytics Layer Live      | Week 32     | Analytics  | ⚪     |
| 5   | Production Go-Live        | Week 39     | Go-Live    | ⚪     |

**Legend:** 🟢 Complete | 🟡 In Progress | ⚪ Not Started | 🔴 Blocked

---

## Resource Plan

### Team Composition Over Time

| Phase      | Data Eng | Architect | BI Dev | QA  | Writer | PM   | Total FTE |
| ---------- | -------- | --------- | ------ | --- | ------ | ---- | --------- |
| Foundation | 1.0      | 1.0       | 0      | 0   | 0      | 0.25 | 2.25      |
| Core Dev   | 2.0      | 0.5       | 0      | 0.5 | 0      | 0.25 | 3.25      |
| Analytics  | 1.0      | 0         | 1.0    | 0   | 0      | 0.25 | 2.25      |
| Go-Live    | 1.0      | 0         | 0      | 0.5 | 0.5    | 0.25 | 2.25      |

**Peak Team Size:** 3.25 FTE (Phase 2 - Core Development)
**Average Team Size:** 2.5 FTE

---

## Dependencies & Risks

### Critical Dependencies

| Dependency                  | Owner        | Required By | Risk Level |
| --------------------------- | ------------ | ----------- | ---------- |
| Azure subscription approved | IT Dept      | Week 1      | 🟢 Low     |
| Source data access granted  | Data Owner   | Week 9      | 🟡 Medium  |
| BI tool licenses            | Procurement  | Week 25     | 🟢 Low     |
| Production change window    | Change Board | Week 38     | 🟡 Medium  |

### Top Risks to Timeline

| Risk                             | Impact          | Probability | Mitigation                        |
| -------------------------------- | --------------- | ----------- | --------------------------------- |
| Data quality lower than expected | 2-3 weeks delay | Medium      | Early profiling, buffer time      |
| Key resource unavailable         | 1-2 weeks delay | Low         | Cross-training, backup identified |
| Scope creep                      | 4-6 weeks delay | High        | Strict change control process     |

---

## Success Metrics

### Delivery Metrics

| Metric                   | Target                   | Tracking       |
| ------------------------ | ------------------------ | -------------- |
| On-Time Delivery         | > 90% milestones on time | Weekly         |
| Budget Adherence         | ±10% of budget           | Weekly         |
| Scope Completion         | 100% committed scope     | Sprint review  |
| Quality (Defects)        | < 5 critical defects     | Daily          |
| Stakeholder Satisfaction | > 4/5 rating             | Monthly survey |

---

## Communication Plan

**Weekly Status Updates:**

- To: Project team, technical leads
- Format: Email summary + Jira dashboard
- Day: Every Friday

**Monthly Steering Committee:**

- To: Executives, sponsors
- Format: Executive summary presentation
- Day: Last Thursday of month

**Milestone Reviews:**

- To: All stakeholders
- Format: Demo + sign-off meeting
- Timing: At each milestone completion

---

## Next Steps

1. ☐ Review and approve roadmap with stakeholders
2. ☐ Confirm resource availability for Phase 1
3. ☐ Initiate Azure subscription request
4. ☐ Schedule kick-off meeting (Week 1)
5. ☐ Set up project tracking tools (Jira, Confluence)

---

**Roadmap Owner:** {Delivery Lead Name}
**Last Updated:** {DATE}
**Next Review:** {DATE + 30 days}
**Approval Status:** Draft / Approved / In Progress
```

## Best Practices

1. **Start with the End in Mind**: Define success criteria first
2. **Build in Flexibility**: Include buffer time for unknowns (15-20%)
3. **Align with Business**: Link milestones to business value
4. **Communicate Early**: Share draft roadmap for feedback
5. **Track Ruthlessly**: Update status weekly, adjust as needed
6. **Celebrate Milestones**: Recognize team achievements
7. **Learn and Adapt**: Conduct retrospectives after each phase

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual roadmap creation: 12-16 hours
- With DeliveryPro agent: 3-5 hours
- **Effort reduction: 70-75%**
