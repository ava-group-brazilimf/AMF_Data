---
task: analyze-issues
version: 1.0
elicit: true
description: Perform root cause analysis of current issues and their impact
---

# Analyze Issues and Root Causes

## Purpose

Conduct systematic root cause analysis of project issues, incidents, and problems to identify underlying causes and recommend corrective actions.

## Process

### Step 1: Gather Issue Information

ASK the user for the following information:

1. **Issue Description**: What is the problem? What symptoms are visible?
2. **Frequency**: How often does this occur? (one-time, recurring, constant)
3. **Impact**: What is affected? (timeline, budget, quality, team morale, stakeholders)
4. **When Started**: When was this first observed?
5. **Recent Changes**: Any changes to code, data, infrastructure, or team?
6. **Previous Attempts**: What has been tried to fix it? What were the results?
7. **Related Issues**: Are there other similar or related problems?

### Step 2: Categorize the Issue

CLASSIFY the issue by type:

**Technical Issues:**

- Performance degradation
- System failures or crashes
- Data quality problems
- Integration failures
- Security vulnerabilities

**Process Issues:**

- Communication breakdowns
- Unclear requirements
- Inadequate testing
- Poor documentation
- Insufficient reviews

**Resource Issues:**

- Skill gaps
- Insufficient capacity
- Team conflicts
- Turnover/attrition
- Contractor performance

**External Issues:**

- Vendor delays
- Third-party failures
- Regulatory changes
- Budget cuts
- Organizational changes

### Step 3: Perform Root Cause Analysis

USE multiple techniques to identify root causes:

**5 Whys Analysis:**

```
Issue: Pipeline failing 15 times/month
├─ Why? → Data type mismatch errors
│  ├─ Why? → Source data has inconsistent formats
│  │  ├─ Why? → No validation at source
│  │  │  ├─ Why? → No data quality standards
│  │  │  │  ├─ Why? → Legacy system with no governance
│  │  │  │  │  ROOT CAUSE: Technical debt and lack of data governance
```

**Fishbone Diagram (6 M's):**

```
ISSUE: High Defect Rate in Production
│
├─ METHODS (Process)
│  ├─ No code review process
│  ├─ Insufficient testing
│  └─ No quality gates
│
├─ MACHINES (Technology)
│  ├─ Outdated development tools
│  ├─ No automated testing
│  └─ Poor monitoring
│
├─ MATERIALS (Data/Inputs)
│  ├─ Poor source data quality
│  ├─ Incomplete requirements
│  └─ Missing test data
│
├─ MANPOWER (People)
│  ├─ Junior team lacking experience
│  ├─ No training program
│  └─ High turnover
│
├─ MEASUREMENT (Metrics)
│  ├─ No quality metrics
│  ├─ No performance baselines
│  └─ Insufficient monitoring
│
└─ MOTHER NATURE (External)
   ├─ Vendor delays
   ├─ Budget constraints
   └─ Timeline pressure
```

**Timeline Analysis:**

- When did issue start?
- What changed at that time?
- Pattern identification (time of day, day of week, specific conditions)

**Contributing Factors:**

- Primary cause (main reason)
- Secondary causes (amplifiers)
- Tertiary causes (enablers)

### Step 4: Assess Impact

QUANTIFY the impact across dimensions:

**Timeline Impact:**

- Delay in days/weeks
- Missed milestones
- Impact on dependent activities

**Cost Impact:**

- Direct costs (rework, overtime, support)
- Indirect costs (opportunity cost, reputation)
- Recovery costs (fixes, enhancements)

**Quality Impact:**

- Defect rate increase
- Customer/stakeholder satisfaction
- Technical debt accumulation

**Team Impact:**

- Morale and motivation
- Productivity loss
- Burnout risk
- Turnover likelihood

**Business Impact:**

- Revenue/profit impact
- Competitive position
- Regulatory/compliance risk
- Strategic objectives affected

### Step 5: Recommend Corrective Actions

DEFINE specific, actionable corrective actions:

**Immediate Actions (Stop the bleeding):**

- Emergency fixes or workarounds
- Incident response and communication
- Damage control measures

**Short-term Actions (1-4 weeks):**

- Tactical fixes to address symptoms
- Process improvements
- Tool or resource additions

**Long-term Actions (1-6 months):**

- Strategic changes to prevent recurrence
- Organizational or cultural changes
- System redesign or refactoring

**Each Action Should Include:**

- Clear description of what to do
- Owner/responsible party
- Timeline and milestones
- Success criteria
- Cost/effort estimate
- Dependencies

### Step 6: Define Prevention Strategies

ESTABLISH measures to prevent recurrence:

**Process Improvements:**

- New checkpoints or quality gates
- Enhanced review processes
- Better documentation standards

**Technical Enhancements:**

- Automated testing or validation
- Monitoring and alerting
- Architectural improvements

**Training & Knowledge:**

- Skill development programs
- Knowledge sharing sessions
- Documentation and runbooks

**Organizational Changes:**

- Role clarifications
- Communication protocols
- Decision-making processes

## Output Structure

```markdown
# ISSUE ANALYSIS & ROOT CAUSE - {ISSUE_NAME}

**Issue ID:** ISS-{NNN}
**Date Reported:** {DATE}
**Analysis Date:** {DATE}
**Analyst:** {NAME/ROLE}
**Priority:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

---

## Issue Summary

**Problem Statement:**
{Clear, concise description of the issue}

**Symptoms Observed:**

- {Symptom 1}
- {Symptom 2}
- {Symptom 3}

**Frequency:** {How often it occurs}
**Duration:** {How long it's been happening}
**Affected Areas:** {Systems, teams, processes affected}

---

## Impact Assessment

### Quantitative Impact

| Dimension       | Impact           | Details                                  |
| --------------- | ---------------- | ---------------------------------------- |
| **Timeline**    | 2-3 weeks delay  | Missed Sprint 5 deadline, pushed go-live |
| **Cost**        | $35,000          | 200h rework × $150/h + $5K infra costs   |
| **Quality**     | 15 defects/month | Up from baseline of 3 defects/month      |
| **Team Morale** | High impact      | 2 team members considering leaving       |

### Qualitative Impact

**Stakeholder Impact:**

- Executive frustration with delays
- Customer complaints about data quality
- Loss of trust in delivery team

**Reputation Impact:**

- Internal: Reduced credibility with business units
- External: Risk of negative client feedback

**Strategic Impact:**

- Delays adjacent projects dependent on this one
- Reduces capacity for new initiatives
- Threatens annual objectives

---

## Root Cause Analysis

### 5 Whys Analysis
```

ISSUE: Pipeline failing with data quality errors (15 incidents/month)

❓ Why are pipeline failures occurring?
└─ Data type mismatches causing SQL conversion errors (60% of failures)

❓ Why are there data type mismatches?
└─ Source CSV files have inconsistent formats (nulls as "NULL" string, dates as text)

      ❓ Why are formats inconsistent?
      └─ No validation or cleansing at the source system

         ❓ Why is there no validation at source?
         └─ Legacy system with no data quality framework

            ❓ Why was no quality framework implemented?
            └─ Technical debt accumulated over 10 years, no budget for improvements

               🎯 ROOT CAUSE: Technical debt and lack of data governance strategy

```

### Fishbone Diagram Analysis

```

                           ┌─────────────────────────────┐
                           │ HIGH PIPELINE FAILURE RATE  │
                           │  (15 incidents/month)       │
                           └─────────────────────────────┘
                                      ▲
                    ┌─────────────────┴─────────────────┐
                    │                                   │
        ┌───────────┴──────────┐           ┌───────────┴──────────┐
        │  METHODS (Process)   │           │ MACHINES (Tech)      │
        ├──────────────────────┤           ├──────────────────────┤
        │ • No data profiling  │           │ • No validation      │
        │ • Skip quality checks│           │   framework          │
        │ • No code reviews    │           │ • Poor monitoring    │
        └──────────────────────┘           │ • Legacy systems     │
                    │                       └──────────────────────┘
                    │                                   │
        ┌───────────┴──────────┐           ┌───────────┴──────────┐
        │ MATERIALS (Data)     │           │ MANPOWER (People)    │
        ├──────────────────────┤           ├──────────────────────┤
        │ • Inconsistent       │           │ • Junior team        │
        │   formats            │           │ • No training        │
        │ • Missing nulls      │           │ • Knowledge gaps     │
        │ • Bad source data    │           │ • High turnover      │
        └──────────────────────┘           └──────────────────────┘

```

### Contributing Factors

**Primary Root Cause (60% of issue):**
- No data validation framework at ingestion
- Source data quality issues propagating downstream

**Secondary Causes (30% of issue):**
- Insufficient testing before production deployment
- Lack of monitoring and early warning systems

**Tertiary Causes (10% of issue):**
- Team skill gaps in data quality practices
- Timeline pressure leading to shortcuts

---

## Timeline of Events

| Date | Event | Impact |
|------|-------|--------|
| Oct 1, 2025 | Pipeline deployed to production | Initial go-live |
| Oct 15, 2025 | First failure observed | 1 incident |
| Nov 2025 | Failures increasing | 8 incidents |
| Dec 2025 | Peak failures | 15 incidents |
| Jan 5, 2026 | Root cause analysis initiated | Analysis started |

**Pattern Identified:**
- Failures spike on Mondays (source data loads over weekend)
- 80% of failures occur between 6-8 AM (batch processing window)
- Failures correlate with specific data sources (Source A = 60% of issues)

---

## Corrective Actions

### Immediate Actions (This Week)

**ACTION 1: Emergency Data Validation**
- **Description:** Add TRY_CAST and COALESCE to all type conversions
- **Owner:** Senior Data Engineer
- **Timeline:** 3 days
- **Cost:** $3,600 (24h × $150/h)
- **Success Criteria:** Zero SQL conversion errors for 1 week
- **Status:** 🟢 In Progress (Started Jan 6)

**ACTION 2: Enhanced Monitoring**
- **Description:** Set up alerts for pipeline failures and data quality issues
- **Owner:** DevOps Engineer
- **Timeline:** 2 days
- **Cost:** $2,400 (16h × $150/h)
- **Success Criteria:** Alerts trigger within 5 minutes of failure
- **Status:** ⚪ Not Started

### Short-term Actions (Next 2-4 Weeks)

**ACTION 3: Comprehensive Data Profiling**
- **Description:** Profile all source data to document quality baseline
- **Owner:** Data Analyst
- **Timeline:** 2 weeks
- **Cost:** $8,000 (80h × $100/h)
- **Success Criteria:** Quality report for all sources, rules documented
- **Status:** ⚪ Not Started

**ACTION 4: Reject Handling Process**
- **Description:** Create reject tables and error handling workflow
- **Owner:** Data Engineer
- **Timeline:** 1 week
- **Cost:** $6,000 (40h × $150/h)
- **Success Criteria:** Invalid records logged, alerts sent, process documented
- **Status:** ⚪ Not Started

**ACTION 5: Code Review Process**
- **Description:** Implement mandatory peer reviews for all pipeline code
- **Owner:** Tech Lead
- **Timeline:** 1 week (setup)
- **Cost:** $1,500 (10h × $150/h setup) + ongoing
- **Success Criteria:** 100% of code reviewed before production
- **Status:** ⚪ Not Started

### Long-term Actions (Next 1-6 Months)

**ACTION 6: Data Quality Framework**
- **Description:** Design and implement enterprise data quality framework
- **Owner:** Data Architect
- **Timeline:** 3 months
- **Cost:** $40,000
- **Success Criteria:** Reusable framework, <1% reject rate across all pipelines
- **Status:** ⚪ Planned for Q2 2026

**ACTION 7: Source System Improvements**
- **Description:** Work with source teams to improve data quality at origin
- **Owner:** Delivery Lead
- **Timeline:** 6 months (ongoing)
- **Cost:** $20,000 (collaborative effort)
- **Success Criteria:** Source data quality improves to >95% valid
- **Status:** ⚪ Planned for Q2-Q3 2026

---

## Prevention Strategies

### Process Improvements

**1. Data Profiling Standard**
- Mandatory profiling for all new data sources before development
- Document baseline quality metrics
- Define acceptable quality thresholds

**2. Quality Gates**
- Gate 1: Requirements include data quality acceptance criteria
- Gate 2: Development includes validation rules
- Gate 3: Testing validates quality rules
- Gate 4: Production deployment requires quality sign-off

**3. Code Review Checklist**
- All type conversions use TRY_CAST
- All nullable columns have COALESCE
- All transformations have error handling
- All pipelines have monitoring

### Technical Enhancements

**1. Automated Validation**
- Schema validation on ingestion
- Data type validation in landing layer
- Business rule validation in silver layer
- Referential integrity checks

**2. Monitoring & Alerting**
- Real-time pipeline health dashboard
- Automated alerts for failures (< 5 min SLA)
- Daily data quality reports
- Weekly trend analysis

**3. Error Handling**
- Graceful degradation (continue processing valid records)
- Structured error logging
- Automatic retry logic for transient failures
- Dead letter queue for persistent failures

### Training & Knowledge

**1. Team Training Program**
- Data quality best practices workshop (2 days)
- SQL error handling techniques (1 day)
- Monitoring and observability (1 day)
- Root cause analysis techniques (1 day)

**2. Knowledge Sharing**
- Weekly "lessons learned" sessions
- Incident postmortem reviews
- Documentation of common issues and fixes
- Cross-training on all pipeline components

**3. Documentation Standards**
- Architecture decision records (ADRs)
- Runbooks for common issues
- Troubleshooting guides
- Code comments and inline documentation

---

## Success Metrics & Monitoring

### Key Metrics to Track

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Pipeline failure rate | 15/month | <2/month | 2 months |
| Data reject rate | ~5% | <1% | 3 months |
| Mean time to detect (MTTD) | 2 hours | <5 minutes | 1 month |
| Mean time to recover (MTTR) | 4 hours | <1 hour | 2 months |
| Repeat incidents | 40% | <10% | 3 months |

### Monitoring Plan

**Daily:**
- Check failure logs and error rates
- Review overnight batch processing results
- Monitor data quality metrics

**Weekly:**
- Review trend charts with team
- Assess corrective action progress
- Update stakeholders on improvements

**Monthly:**
- Executive summary of improvements
- Compare actuals vs targets
- Adjust action plans as needed

---

## Lessons Learned

### What Went Wrong
1. ❌ No data profiling done upfront - assumed data quality was good
2. ❌ Skipped validation rules to meet aggressive timeline
3. ❌ Insufficient monitoring - problems detected too late
4. ❌ No code review process - quality issues not caught early

### What Could Have Prevented This
1. ✅ Allocate 1-2 weeks for data profiling before development
2. ✅ Include data quality requirements in project scope
3. ✅ Implement monitoring and alerting from day 1
4. ✅ Mandatory code reviews with quality checklist

### Recommendations for Future Projects
1. 📝 Create "Data Quality Readiness Assessment" template
2. 📝 Add "Data Profiling" as mandatory project phase
3. 📝 Update project estimation templates to include quality time
4. 📝 Create reusable data quality framework for all projects

---

## Stakeholder Communication

### Communication Plan

**Weekly Status Updates:**
- To: Project team, technical leads
- Content: Corrective action progress, metrics improvement
- Channel: Email + dashboard

**Bi-Weekly Executive Updates:**
- To: Leadership, sponsors
- Content: High-level summary, risk mitigation progress
- Channel: Presentation

**Monthly Retrospective:**
- To: All stakeholders
- Content: Lessons learned, process improvements
- Channel: Meeting + documentation

---

## Approval & Sign-Off

| Stakeholder | Role | Reviewed | Approved | Date |
|-------------|------|----------|----------|------|
| | Technical Lead | ☐ | ☐ | |
| | Delivery Lead | ☐ | ☐ | |
| | Business Owner | ☐ | ☐ | |

---

**Analysis Owner:** {Name}
**Last Updated:** {DATE}
**Next Review:** {DATE + 14 days}
**Status:** Draft / In Review / Approved / Actions in Progress
```

## Best Practices

1. **Be Objective**: Focus on facts, not blame
2. **Dig Deep**: Don't stop at surface-level causes - use 5 Whys
3. **Quantify Impact**: Use numbers (cost, time, defects) not just words
4. **Be Specific**: Vague actions like "improve quality" are not actionable
5. **Assign Owners**: Every action needs a clear owner and timeline
6. **Follow Up**: Track action completion and verify effectiveness
7. **Share Learnings**: Document and share lessons with broader organization
8. **No Blame Culture**: Focus on process and system improvements, not individuals

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual root cause analysis: 6-8 hours
- With DeliveryPro agent: 2-3 hours
- **Effort reduction: 60-70%**
