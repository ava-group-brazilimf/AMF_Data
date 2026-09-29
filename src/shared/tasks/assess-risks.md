---
task: assess-risks
version: 1.0
elicit: true
description: Identify project risks, assess impact/probability, and define mitigation strategies
---

# Assess Project Risks

## Purpose

Systematically identify, analyze, and document project risks with mitigation strategies. Create and maintain a risk register for ongoing tracking.

## Process

### Step 1: Gather Project Context

ASK the user for the following information:

1. **Project Type**: What kind of project? (Data pipeline, analytics platform, migration, etc.)
2. **Project Phase**: Planning, active development, testing, or production?
3. **Current Challenges**: Any known issues or concerns?
4. **Historical Context**: Similar projects that had problems? Lessons learned?
5. **Stakeholder Concerns**: What worries the team or executives?
6. **Timeline Pressure**: Are there fixed deadlines or time constraints?
7. **Budget Constraints**: Are there budget limitations or cost concerns?

### Step 2: Identify Risks by Category

ANALYZE and identify risks across all categories:

**Technical Risks:**

- Technology complexity or unfamiliarity
- Data quality issues (missing, invalid, inconsistent)
- Performance and scalability challenges
- Integration difficulties with existing systems
- Security and compliance vulnerabilities
- Infrastructure reliability

**Resource Risks:**

- Key person dependency (single point of failure)
- Team skill gaps or insufficient expertise
- Resource availability conflicts
- Contractor/vendor reliability
- Turnover or attrition

**Process Risks:**

- Unclear or changing requirements
- Insufficient testing or quality assurance
- Poor communication or coordination
- Inadequate documentation
- Lack of change control

**External Risks:**

- Vendor delays or failures
- Regulatory/compliance changes
- Budget cuts or funding issues
- Organizational changes or priorities
- Third-party dependencies

**Business Risks:**

- Scope creep or gold plating
- Stakeholder misalignment
- Unrealistic expectations
- Poor user adoption
- ROI not achieved

### Step 3: Assess Risk Impact and Probability

EVALUATE each risk using standard framework:

**Probability Scale:**

- **Low (10-30%)**: Unlikely to occur
- **Medium (40-60%)**: Reasonably possible
- **High (70-90%)**: Likely to occur

**Impact Scale:**

- **Low**: Minor cost/time increase (< 5%), workarounds available
- **Medium**: Moderate cost/time increase (5-15%), requires replanning
- **High**: Major cost/time increase (> 15%), threatens project success
- **Critical**: Project failure or cancellation risk

**Risk Score = Probability × Impact**

**Priority Levels:**

- 🔴 **CRITICAL** (High Prob + High Impact)
- 🟠 **HIGH** (High Prob + Med Impact OR Med Prob + High Impact)
- 🟡 **MEDIUM** (Med Prob + Med Impact OR combinations)
- 🟢 **LOW** (Low Prob + Low Impact)

### Step 4: Perform Root Cause Analysis

For HIGH and CRITICAL risks, conduct root cause analysis:

**5 Whys Technique:**

```
Risk: Pipeline fails frequently
Why? → Data type mismatches in source files
Why? → No validation at ingestion
Why? → No data profiling done upfront
Why? → Assumed source data was consistent
Why? → No requirements gathering process
ROOT CAUSE: Inadequate requirements and data analysis phase
```

**Fishbone Diagram Categories:**

- People: Skills, availability, training
- Process: Methodology, standards, communication
- Technology: Tools, infrastructure, complexity
- Data: Quality, availability, consistency
- External: Vendors, regulations, dependencies

### Step 5: Define Mitigation Strategies

CREATE actionable mitigation plans:

**Mitigation Strategy Types:**

**1. Avoidance** - Change plans to eliminate risk

- Example: Use proven technology instead of experimental

**2. Transfer** - Shift risk to third party

- Example: Use managed service instead of self-hosting

**3. Mitigation** - Reduce probability or impact

- Example: Add data quality checks to catch errors early

**4. Acceptance** - Acknowledge and monitor

- Example: Accept minor performance risk with monitoring in place

**Each Mitigation Should Include:**

- Specific actions to take
- Owner/responsible party
- Timeline for implementation
- Success criteria
- Cost/effort required

### Step 6: Create Risk Register

DOCUMENT all risks in structured format:

```
RISK ID: RISK-001
Title: Data Quality Below Expectations
Category: Technical
Probability: High (70%)
Impact: High (3-4 week delay, $30K cost)
Risk Score: HIGH
Root Cause: Source systems have inconsistent data formats
Current Status: Active
Owner: Data Engineering Lead

Mitigation Strategy:
├─ Action 1: Conduct comprehensive data profiling (Week 1)
├─ Action 2: Implement validation rules in landing layer (Week 2)
├─ Action 3: Create reject handling process (Week 3)
├─ Action 4: Set up data quality monitoring (Week 4)
└─ Contingency: Budget 20% extra time for cleansing

Monitoring Plan:
├─ Track reject rate weekly (target < 2%)
├─ Review data quality metrics daily
└─ Escalate if reject rate > 5%

Last Updated: {DATE}
Next Review: {DATE + 7 days}
```

## Output Structure

```markdown
# RISK ASSESSMENT - {PROJECT_NAME}

**Assessment Date:** {DATE}
**Project Phase:** {Phase}
**Assessed By:** {Name/Role}
**Next Review:** {DATE + 30 days}

---

## Executive Summary

**Overall Risk Level:** 🟡 MEDIUM

**Risk Distribution:**

- 🔴 Critical Risks: {N}
- 🟠 High Risks: {M}
- 🟡 Medium Risks: {K}
- 🟢 Low Risks: {L}

**Top 3 Concerns:**

1. {Risk 1}
2. {Risk 2}
3. {Risk 3}

---

## Critical and High Priority Risks

### 🔴 RISK-001: Data Quality Issues

**Category:** Technical
**Probability:** High (70%)
**Impact:** High (3-4 week delay, $30K-$40K cost impact)
**Risk Score:** CRITICAL

**Description:**
Source data from legacy systems contains inconsistent formats, missing values, and data type mismatches. Historical analysis shows 15-20% of records have quality issues.

**Root Cause Analysis (5 Whys):**
```

Why are pipeline failures occurring?
└─ Data type mismatches causing SQL errors
Why are types mismatched?
└─ Source files have inconsistent formats
Why are formats inconsistent?
└─ No data quality standards at source
Why no standards?
└─ Legacy systems with no governance
Why no governance?
└─ Technical debt accumulated over years

```

**Impact Assessment:**
├─ Timeline: 3-4 weeks additional dev time for cleansing
├─ Cost: $30,000-$40,000 additional effort
├─ Quality: Reduced trust in data if not addressed
└─ Reputation: Stakeholder frustration and complaints

**Mitigation Strategy:**

**Primary Actions:**
1. **Data Profiling** (Week 1)
   - Profile all source files comprehensively
   - Document data quality issues by category
   - Owner: Data Engineer Lead
   - Cost: $3,000 (20h × $150/h)

2. **Landing Layer Validation** (Week 2)
   - Implement comprehensive validation rules
   - Create reject tables for invalid records
   - Owner: Data Engineer
   - Cost: $4,500 (30h × $150/h)

3. **Quality Monitoring** (Week 3)
   - Set up automated quality checks
   - Create alerting for quality thresholds
   - Owner: Data Engineer
   - Cost: $3,000 (20h × $150/h)

4. **Source System Engagement** (Ongoing)
   - Work with source teams on improvements
   - Document data contracts and SLAs
   - Owner: Delivery Lead
   - Cost: $2,000 (10h × $200/h)

**Contingency Plan:**
- Budget: Add 20% buffer to development cost ($20,000)
- Timeline: Add 2-week buffer to schedule
- Scope: Reduce Gold layer complexity if needed

**Success Metrics:**
- Data reject rate < 2%
- Zero production incidents due to data quality
- Stakeholder confidence rating > 4/5

**Monitoring Plan:**
- Daily: Check reject rates and error logs
- Weekly: Review quality metrics with team
- Monthly: Report trends to stakeholders
- Escalation: Alert if reject rate > 5%

**Status:** 🟠 Active - Mitigation in progress
**Owner:** Data Engineering Lead
**Last Updated:** {DATE}
**Next Review:** {DATE + 7 days}

---

### 🟠 RISK-002: Key Resource Dependency

**Category:** Resource
**Probability:** Medium (50%)
**Impact:** High (2-3 week delay, $20K-$30K cost impact)
**Risk Score:** HIGH

**Description:**
Senior Data Engineer has critical knowledge of the pipeline architecture and transformation logic. No backup resource with equivalent expertise. If unavailable, project timeline at risk.

**Root Cause Analysis:**
```

Why is there key person dependency?
└─ Only one person knows the full architecture
Why only one person?
└─ No knowledge sharing sessions
Why no knowledge sharing?
└─ Project timeline pressure, no time allocated
Why no time allocated?
└─ Aggressive schedule with no buffer

```

**Impact Assessment:**
├─ Timeline: 2-3 weeks delay if person unavailable
├─ Cost: $20,000-$30,000 for backfill and ramp-up
├─ Quality: Potential for errors with less experienced backup
└─ Morale: Team stress and burnout risk

**Mitigation Strategy:**

1. **Cross-Training Program** (Weeks 1-4)
   - Weekly knowledge sharing sessions (2h/week)
   - Pair programming on critical components
   - Owner: Senior Data Engineer + Junior DE
   - Cost: $4,800 (32h × $150/h)

2. **Documentation** (Ongoing)
   - Architecture diagrams and design docs
   - Code comments and runbooks
   - Owner: Technical Writer
   - Cost: $3,600 (36h × $100/h)

3. **Backup Resource Identified** (Week 1)
   - Identify and onboard backup contractor
   - Provide access and orientation
   - Owner: Delivery Lead
   - Cost: $1,500 (10h × $150/h)

4. **Code Reviews** (Ongoing)
   - Mandatory peer reviews for all code
   - Ensure multiple people understand each component
   - Owner: All Engineers
   - Cost: $0 (included in dev process)

**Contingency Plan:**
- Have pre-qualified contractor on retainer
- Budget for 2-week knowledge transfer if needed
- Reduce scope to de-risk timeline

**Status:** 🟢 Mitigated - Cross-training started
**Owner:** Delivery Lead
**Last Updated:** {DATE}
**Next Review:** {DATE + 14 days}

---

## Medium Priority Risks

### 🟡 RISK-003: Infrastructure Costs Higher Than Expected

**Category:** Financial
**Probability:** Medium (40%)
**Impact:** Medium ($5K-$10K additional annual cost)
**Risk Score:** MEDIUM

**Mitigation:**
- Implement cost monitoring and alerts (Week 1)
- Optimize queries for performance (Ongoing)
- Use auto-pause/resume features (Week 2)
- Consider reserved instances (Month 3)

**Owner:** Solution Architect
**Status:** 🟢 Monitoring

---

### 🟡 RISK-004: Scope Creep

**Category:** Business
**Probability:** Medium (50%)
**Impact:** Medium (1-2 week delay, $10K-$15K cost)
**Risk Score:** MEDIUM

**Mitigation:**
- Implement formal change control process (Week 1)
- Weekly scope review with stakeholders
- Document all "out of scope" requests for Phase 2
- Require executive approval for any scope changes

**Owner:** Project Manager
**Status:** 🟢 Controls in place

---

## Low Priority Risks

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|-----------|-------|
| RISK-005 | Network latency | Low | Low | Monitor performance | DevOps |
| RISK-006 | Vendor delay | Low | Medium | Early orders, backup vendor | PM |
| RISK-007 | Testing gaps | Low | Low | Test coverage metrics | QA Lead |

---

## Risk Trend Analysis

**Risks Closed This Period:** 2
- RISK-012: Source data access (Granted)
- RISK-015: Azure subscription (Approved)

**Risks Elevated This Period:** 1
- RISK-001: Data quality (Medium → Critical due to recent findings)

**New Risks This Period:** 3
- RISK-016: Regulatory compliance requirement
- RISK-017: Dashboard performance concerns
- RISK-018: User training needs

---

## Risk Response Budget

**Total Mitigation Cost:** $42,400
- Data quality measures: $12,500
- Cross-training and documentation: $10,000
- Infrastructure optimization: $8,000
- Contingency reserve (20%): $20,000

**Budget Status:** ✅ Approved and allocated

---

## Next Actions

**Immediate (This Week):**
- [ ] Start data profiling (RISK-001)
- [ ] Begin cross-training sessions (RISK-002)
- [ ] Set up cost monitoring (RISK-003)
- [ ] Implement change control process (RISK-004)

**Short-term (Next 2-4 Weeks):**
- [ ] Complete landing layer validation (RISK-001)
- [ ] Onboard backup resource (RISK-002)
- [ ] Optimize query performance (RISK-003)

**Ongoing:**
- [ ] Weekly risk review meeting
- [ ] Monthly risk register update
- [ ] Quarterly lessons learned session

---

## Risk Review Schedule

| Meeting | Frequency | Attendees | Focus |
|---------|-----------|-----------|-------|
| Daily Standup | Daily | Dev Team | Active risks, blockers |
| Risk Review | Weekly | Leads, PM | All medium+ risks |
| Steering Committee | Monthly | Executives | Critical/high risks only |
| Retrospective | End of Phase | All | Lessons learned |

---

**Risk Register Owner:** {Delivery Lead Name}
**Last Updated:** {DATE}
**Next Review:** {DATE + 7 days}
**Approval Status:** Reviewed and Approved
```

## Best Practices

1. **Be Proactive**: Identify risks early, don't wait for them to become issues
2. **Be Honest**: Don't hide or downplay risks, transparency builds trust
3. **Be Specific**: Vague risks ("something might go wrong") are not actionable
4. **Assign Owners**: Every risk needs a clear owner for tracking
5. **Update Regularly**: Weekly review for active projects
6. **Learn**: Conduct retrospectives and update risk templates
7. **Quantify**: Use numbers (cost, time, probability) not just words
8. **Escalate**: Communicate critical risks to executives immediately

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual risk assessment: 6-8 hours
- With DeliveryPro agent: 2-3 hours
- **Effort reduction: 60-70%**
