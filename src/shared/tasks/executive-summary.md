---
task: executive-summary
version: 1.0
elicit: true
description: Generate executive summary and status report for stakeholders
---

# Generate Executive Summary

## Purpose

Create concise, high-impact executive summaries that communicate project status, key achievements, risks, and recommendations to senior stakeholders and executives.

## Process

### Step 1: Gather Report Information

ASK the user for the following information:

1. **Reporting Period**: What timeframe? (weekly, monthly, quarterly)
2. **Project Phase**: Current phase (planning, development, testing, production)
3. **Key Achievements**: What was accomplished this period?
4. **Current Status**: On track, at risk, or off track?
5. **Budget Status**: Spending vs budget
6. **Timeline Status**: Progress vs plan
7. **Issues/Risks**: Any critical concerns to escalate?
8. **Next Period Focus**: What are the priorities for next period?

### Step 2: Assess Overall Project Health

DETERMINE RAG (Red/Amber/Green) status:

**🟢 GREEN - On Track:**

- All milestones on schedule
- Budget within ±5%
- No critical risks
- Quality metrics met
- Stakeholders satisfied

**🟡 AMBER - At Risk:**

- 1-2 milestones delayed
- Budget variance 5-15%
- 1-2 medium/high risks
- Quality concerns manageable
- Some stakeholder concerns

**🔴 RED - Off Track:**

- Multiple milestone delays
- Budget overrun >15%
- Critical risks or blockers
- Quality below standards
- Stakeholder dissatisfaction

### Step 3: Highlight Key Metrics

SELECT most important metrics for executives:

**Essential Metrics:**

- Budget: Spent vs Allocated (% and $)
- Timeline: Progress vs Plan (% complete)
- Scope: Delivered vs Committed (features/requirements)
- Quality: Defects, test coverage, incident rate
- Team: Utilization, morale, turnover

**Visualization:**

- Use simple charts (progress bars, trend lines)
- Show actuals vs targets
- Highlight variances (red/green indicators)

### Step 4: Identify Top 3 Achievements

SHOWCASE most significant accomplishments:

**Good Achievement Statements:**

- ✅ Specific and measurable
- ✅ Business value clear
- ✅ Impressive to executives
- ✅ Demonstrates progress

**Examples:**

- ✅ "Processed 785K records with 99.7% quality"
- ✅ "Completed 2 weeks ahead of schedule"
- ✅ "Reduced processing time by 60%"
- ❌ "Made good progress" (too vague)

### Step 5: Highlight Top Risks

IDENTIFY 3 most critical risks to escalate:

**Risk Presentation for Executives:**

- Clear risk statement
- Probability and impact (High/Medium/Low)
- Business consequences
- Mitigation actions (what we're doing)
- Decision needed (if any)

**Risk Prioritization:**

- Critical/High risks only (executives don't need all risks)
- Focus on risks needing their attention or decisions
- Include mitigation status

### Step 6: Provide Clear Recommendations

GIVE actionable recommendations for executives:

**Types of Recommendations:**

- Approve/reject decisions needed
- Resource allocation changes
- Budget adjustments
- Timeline modifications
- Scope trade-offs
- Escalation to higher levels

**Format:**

- State recommendation clearly
- Provide business rationale
- Quantify impact if possible
- Offer alternatives if applicable

## Output Structure

```markdown
# EXECUTIVE SUMMARY - {PROJECT_NAME}

**Report Date:** {DATE}
**Reporting Period:** {Q4 2025 / November 2025 / Week 45}
**Project Phase:** {Planning / Development / Testing / Production}
**Report Author:** {Delivery Lead Name}

---

## PROJECT STATUS: 🟢 GREEN

---

## KEY METRICS

### Budget

- **Allocated:** $150,000
- **Spent:** $112,500 (75%)
- **Remaining:** $37,500
- **Variance:** 🟢 On Target

### Timeline

- **Planned Duration:** 10 weeks
- **Elapsed:** 7.5 weeks (75%)
- **Status:** 🟢 On Schedule
- **Completion Date:** February 28, 2026 (on track)

### Scope

- **Total Requirements:** 8
- **Completed:** 8 (100%)
- **In Progress:** 0
- **Not Started:** 0
- **Status:** 🟢 Complete

### Quality

- **Defects:** 0 critical, 2 minor
- **Test Coverage:** 95%
- **Data Quality:** 99.7% valid records
- **Status:** 🟢 Excellent

---

## ACHIEVEMENTS THIS PERIOD

### 🎉 Major Accomplishments

**1. Completed All 8 Requirements Ahead of Schedule**

- Delivered full ETL pipeline 2 weeks early
- All acceptance criteria met and signed off
- Zero critical defects in production

**2. Processed 785K Trip Records with 99.7% Quality**

- Implemented comprehensive validation framework
- Data reject rate < 0.3% (target was <2%)
- Automated quality monitoring operational

**3. Implemented Medallion Architecture (Landing/Silver/Gold)**

- 3-layer data architecture fully operational
- Clean separation of concerns
- Reusable framework for future data sources

**4. Created 25+ Unit Tests with 95% Coverage**

- Comprehensive test suite covering all transformations
- Automated regression testing
- Quality gates enforced

**5. Generated Complete Documentation**

- Architecture diagrams and design docs
- Operational runbooks
- User guides and training materials

---

## TOP 3 RISKS

### 🟡 RISK 1: Infrastructure Costs Trending Higher

**Risk Level:** Medium
**Probability:** 40%
**Impact:** $5K-$10K additional annual cost (15% over estimate)

**Description:**
Azure Synapse consumption higher than estimated due to complex queries and larger data volumes than initially projected.

**Mitigation Actions:**

- ✅ Implemented query performance optimization (complete)
- 🔄 Configuring auto-pause/resume (in progress)
- 📅 Evaluating reserved instances for 30% savings (planned Q2)

**Status:** Under control, monitoring closely

**Executive Decision Needed:** None at this time

---

### 🟡 RISK 2: Key Resource May Transition

**Risk Level:** Medium
**Probability:** 50%
**Impact:** 2-3 week delay if resource unavailable

**Description:**
Senior Data Engineer (critical resource) may be assigned to another high-priority project in March.

**Mitigation Actions:**

- ✅ Cross-training junior engineer (in progress)
- ✅ Documentation of all critical components (complete)
- ✅ Backup contractor identified and on retainer

**Status:** Mitigated, but monitoring closely

**Executive Decision Needed:** Confirm resource allocation for March-April

---

### 🟢 RISK 3: Data Quality Issues (CLOSED)

**Risk Level:** Low (was High in previous period)
**Status:** ✅ **RISK RETIRED**

**Description:**
Data quality issues that were causing 15 pipeline failures/month have been resolved through comprehensive validation framework.

**Resolution:**

- Implemented TRY_CAST for all type conversions
- Added reject tables for invalid records
- Set up real-time quality monitoring

**Result:**
Zero pipeline failures for 3 consecutive weeks

---

## NEXT 30 DAYS

### Priorities for Next Period

**Week 1-2: Performance Optimization**

- Query tuning and indexing
- Load testing for scale
- Resource utilization optimization

**Week 3: User Acceptance Testing (UAT)**

- Business user testing
- Sign-off on all requirements
- Training sessions

**Week 4: Production Go-Live**

- Final deployment checklist
- Production cutover
- Post-launch monitoring

### Budget for Next Period

- **Remaining Budget:** $37,500
- **Expected Spend:** $25,000
- **Reserve:** $12,500 (for contingencies)

---

## FINANCIAL SUMMARY

### Cost Breakdown (To Date)

| Category       | Budget       | Actual       | Variance       | Status       |
| -------------- | ------------ | ------------ | -------------- | ------------ |
| Development    | $109,000     | $87,200      | +$21,800 (20%) | 🟢 Under     |
| Infrastructure | $21,000      | $15,750      | +$5,250 (25%)  | 🟢 Under     |
| Testing & QA   | $12,000      | $9,550       | +$2,450 (20%)  | 🟢 Under     |
| **Total**      | **$142,000** | **$112,500** | **+$29,500**   | **🟢 Under** |

### Forecast to Completion

| Item              | Forecast     | Budget       | Variance          |
| ----------------- | ------------ | ------------ | ----------------- |
| Remaining Work    | $25,000      | $37,500      | +$12,500          |
| **Total Project** | **$137,500** | **$150,000** | **+$12,500 (8%)** |

**Projection:** Will complete under budget by approximately 8%

---

## TEAM & RESOURCES

### Current Team

| Role                   | Name           | Allocation | Utilization |
| ---------------------- | -------------- | ---------- | ----------- |
| Data Engineer (Senior) | John Smith     | 100%       | 90%         |
| Data Engineer (Junior) | Jane Doe       | 100%       | 85%         |
| QA Engineer            | Mike Johnson   | 50%        | 95%         |
| Project Manager        | Sarah Williams | 25%        | 100%        |

### Team Health

**Morale:** 🟢 High
**Productivity:** 🟢 Excellent
**Turnover Risk:** 🟢 Low
**Skill Level:** 🟢 Strong

**Notes:**

- Team working well together
- No overtime required
- Good work-life balance maintained

---

## STAKEHOLDER FEEDBACK

### Business Users

**Rating:** ⭐⭐⭐⭐⭐ (5/5)

**Comments:**

- "Very impressed with data quality"
- "Pipeline is reliable and fast"
- "Team responsive to our needs"

### Technical Leadership

**Rating:** ⭐⭐⭐⭐ (4/5)

**Comments:**

- "Architecture is solid and scalable"
- "Good documentation and testing"
- "Would like more performance optimization"

### Executive Sponsor

**Rating:** ⭐⭐⭐⭐⭐ (5/5)

**Comments:**

- "Project ahead of schedule and under budget"
- "Confident in successful go-live"
- "Great example for future projects"

---

## EXECUTIVE RECOMMENDATIONS

### 1. ✅ APPROVE: Production Go-Live (Week 4)

**Recommendation:** Approve production deployment as planned for February 28, 2026

**Rationale:**

- All requirements complete and tested
- Quality exceeds standards
- UAT sign-off obtained
- Risk level acceptable

**Impact:** Deliver business value 2 weeks early

**Alternatives:** None recommended

---

### 2. 💰 CONSIDER: Allocate $5K for Enhanced Monitoring

**Recommendation:** Approve $5K investment in Datadog or Application Insights for production monitoring

**Rationale:**

- Current monitoring basic, enterprise-grade needed for production
- Proactive issue detection prevents costly outages
- ROI: One prevented outage pays for tool

**Impact:** Improved production stability and incident response

**Alternatives:** Use built-in Azure Monitor (basic capabilities)

---

### 3. 👥 REQUEST: Confirm Resource Allocation for March-April

**Recommendation:** Confirm Senior Data Engineer availability for March-April (post-launch support)

**Rationale:**

- Critical for production stabilization period
- Knowledge transfer to support team
- Resolve any production issues quickly

**Impact:** Smooth transition to production, reduced risk

**Alternatives:** Use backup contractor (higher cost, slower ramp-up)

---

### 4. 🚀 PROPOSE: Expand to Yellow Taxi Data (Phase 2)

**Recommendation:** Begin planning for Phase 2 expansion to Yellow Taxi data in Q2 2026

**Rationale:**

- Reusable framework proven successful
- Business demand for additional data sources
- Team has capacity and expertise

**Impact:** Additional business value, leverage existing investment

**Budget Estimate:** $80K-$100K (40% less than Phase 1 due to reuse)

---

## APPENDIX

### Milestone Completion

| Milestone            | Target Date | Actual Date | Variance | Status |
| -------------------- | ----------- | ----------- | -------- | ------ |
| Infrastructure Ready | Week 2      | Week 2      | On time  | ✅     |
| Landing Layer        | Week 4      | Week 3.5    | -0.5 wk  | ✅     |
| Silver Layer         | Week 6      | Week 5.5    | -0.5 wk  | ✅     |
| Gold Layer           | Week 8      | Week 7      | -1 wk    | ✅     |
| Testing Complete     | Week 9      | Week 8      | -1 wk    | ✅     |
| Production Go-Live   | Week 10     | Week 8.5    | -1.5 wk  | 🔄     |

### Key Documents

- [Project Charter](docs/project-charter.md)
- [Architecture Document](docs/architecture.md)
- [Risk Register](docs/risk-register.md)
- [Test Results](docs/test-results.md)

---

**Next Report:** {DATE + reporting period}
**Questions or Concerns:** Contact {Delivery Lead Name} at {email}

---

**Prepared By:** {Name}, Delivery Lead
**Reviewed By:** {Technical Lead Name}
**Approved By:** ☐ Pending / ✅ Approved
**Approval Date:** ****\_\_****
```

## Best Practices

1. **Keep It Short**: 2-3 pages maximum for executives
2. **Lead with Status**: Show RAG status prominently at top
3. **Use Visuals**: Charts, dashboards, progress bars
4. **Be Honest**: Don't hide problems, show how you're addressing them
5. **Focus on Business Value**: Connect technical achievements to business outcomes
6. **Quantify Everything**: Use numbers (%, $, days) not vague terms
7. **Highlight Decisions Needed**: Make it clear what you need from executives
8. **Consistent Format**: Use same format every period for easy comparison
9. **Forward-Looking**: Balance past achievements with future plans
10. **Proofread**: No typos or errors for executive audience

## Executive Communication Tips

**DO:**

- ✅ Use business language, minimize jargon
- ✅ Lead with the bottom line
- ✅ Quantify impact in money and time
- ✅ Show trends (better/worse/same)
- ✅ Provide clear recommendations
- ✅ Be confident but realistic

**DON'T:**

- ❌ Use technical jargon without explanation
- ❌ Bury important information in details
- ❌ Present problems without solutions
- ❌ Overpromise or spin bad news
- ❌ Include unnecessary technical details
- ❌ Make it longer than 3 pages

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual executive summary: 4-6 hours
- With DeliveryPro agent: 1-2 hours
- **Effort reduction: 65-75%**
