---
task: project-health-check
version: 1.0
elicit: false
description: Assess current project health across all dimensions
---

# Project Health Check

## Purpose

Perform comprehensive assessment of project health across schedule, budget, scope, quality, risks, and team morale. Identify issues and recommend corrective actions.

## Process

### Step 1: Gather Current Status

COLLECT data across all project dimensions:

**Schedule Status:**

- Milestones: on-time vs delayed
- Sprint velocity: actual vs planned
- Critical path status
- Blockers and dependencies

**Budget Status:**

- Spend to date vs budget
- Burn rate analysis
- Forecast to completion
- Cost overruns or savings

**Scope Status:**

- Requirements completed vs planned
- Scope changes approved
- Technical debt accumulation
- Delivered features vs committed

**Quality Status:**

- Defect rate and severity
- Test coverage
- Code review compliance
- Technical debt metrics

**Risk & Issues:**

- Open risks and severity
- Active issues and age
- Escalations needed
- Trend analysis

**Team Health:**

- Morale and satisfaction
- Utilization and burnout risk
- Turnover and retention
- Skill gaps

### Step 2: Calculate Health Scores

ASSIGN numeric scores (1-10) for each dimension:

**Scoring Guide:**

```
9-10 = Excellent (Green)
7-8  = Good (Green)
5-6  = Fair (Amber)
3-4  = Poor (Red)
1-2  = Critical (Red)
```

**Weighting:**

- Schedule: 25%
- Budget: 25%
- Scope: 15%
- Quality: 20%
- Risks: 10%
- Team: 5%

**Overall Health Score = Σ(Dimension Score × Weight)**

### Step 3: Identify Root Causes

For dimensions scoring < 7, ANALYZE root causes:

- Why is this dimension struggling?
- What events led to current state?
- Are there systemic issues?
- What patterns are emerging?

### Step 4: Assess Trends

DETERMINE if situation is improving or deteriorating:

- Compare to previous health check
- Identify velocity of change
- Project trajectory (better/stable/worse)
- Predict future state in 30 days

### Step 5: Recommend Actions

PROVIDE specific, prioritized recommendations:

**Immediate (This Week):**

- Stop-the-bleeding actions
- Critical issue resolution
- Emergency resources

**Short-term (2-4 Weeks):**

- Tactical improvements
- Process fixes
- Resource adjustments

**Long-term (1-3 Months):**

- Strategic changes
- Organizational improvements
- Capability building

## Output Structure

```markdown
# PROJECT HEALTH CHECK - {PROJECT_NAME}

**Assessment Date:** {DATE}
**Project Phase:** {Phase}
**Assessor:** {Delivery Lead Name}
**Overall Status:** 🟢 Healthy / 🟡 At Risk / 🔴 Critical

---

## EXECUTIVE SUMMARY

**Overall Health Score:** 7.2 / 10 (🟢 Good)

**Key Findings:**

- ✅ Schedule and budget on track
- ⚠️ Quality concerns need attention
- ⚠️ Team morale declining
- ✅ Risks well-managed

**Immediate Actions Required:** 2
**Recommended Escalations:** 0

---

## HEALTH SCORECARD

| Dimension   | Score      | Status | Trend | Weight   | Notes              |
| ----------- | ---------- | ------ | ----- | -------- | ------------------ |
| Schedule    | 8/10       | 🟢     | ↗️    | 25%      | 1 week ahead       |
| Budget      | 9/10       | 🟢     | →     | 25%      | 8% under budget    |
| Scope       | 7/10       | 🟢     | ↗️    | 15%      | All committed done |
| Quality     | 5/10       | 🟡     | ↘️    | 20%      | Defect rate rising |
| Risks       | 7/10       | 🟢     | →     | 10%      | Under control      |
| Team        | 6/10       | 🟡     | ↘️    | 5%       | Morale concerns    |
| **OVERALL** | **7.2/10** | **🟢** | **→** | **100%** | Good overall       |

**Legend:**

- ↗️ Improving
- → Stable
- ↘️ Declining

---

## DETAILED ANALYSIS

### 1️⃣ Schedule Health: 8/10 (🟢 Good, ↗️ Improving)

**Current Status:**

- Project ahead of schedule by 1 week
- 6 of 6 milestones delivered on time
- Sprint velocity: 18 SP (target: 16 SP)
- Zero critical path delays

**Positive Indicators:**

- ✅ Ahead of schedule (1 week early)
- ✅ All milestones hit
- ✅ Velocity above target
- ✅ No blockers on critical path

**Concerns:**

- ⚠️ Fast pace may impact quality (see Quality section)
- ⚠️ Team working extra hours to maintain pace

**Trend:** Improving (was on-schedule last month, now ahead)

**Recommendation:** Maintain current pace but monitor quality and team burnout

---

### 2️⃣ Budget Health: 9/10 (🟢 Excellent, → Stable)

**Current Status:**

- Spent: $112,500 of $150,000 (75%)
- Time elapsed: 75%
- Forecast: $137,500 (8% under budget)
- CPI: 1.13 (excellent)

**Positive Indicators:**

- ✅ Under budget by 8%
- ✅ Burn rate declining as expected
- ✅ No cost overruns
- ✅ Infrastructure costs optimized

**Concerns:**

- None at this time

**Trend:** Stable (consistently under budget)

**Recommendation:** Stay the course, reallocate surplus to Phase 2

---

### 3️⃣ Scope Health: 7/10 (🟢 Good, ↗️ Improving)

**Current Status:**

- 8 of 8 requirements complete (100%)
- 0 scope changes approved
- Technical debt: Low
- Feature completeness: 100%

**Positive Indicators:**

- ✅ All committed scope delivered
- ✅ No scope creep
- ✅ Strict change control working well

**Concerns:**

- ⚠️ Some "nice-to-have" features deferred to Phase 2
- ⚠️ Stakeholders requesting enhancements

**Trend:** Improving (was 85% complete last month)

**Recommendation:** Hold the line on scope, plan Phase 2 for enhancements

---

### 4️⃣ Quality Health: 5/10 (🟡 Fair, ↘️ Declining)

**Current Status:**

- Defect rate: 12 defects/month (baseline: 3/month)
- Test coverage: 82% (target: 90%)
- Code review: 95% compliance (target: 100%)
- Data quality: 99.7% (excellent)

**Positive Indicators:**

- ✅ Data quality excellent
- ✅ Most code reviewed

**Concerns:**

- 🔴 **Defect rate 4x baseline (CRITICAL)**
- 🟡 Test coverage below target
- 🟡 Code review not 100%

**Root Cause Analysis:**
```

Why are defects increasing?
└─ Fast development pace sacrificing quality
Why fast pace?
└─ Pressure to deliver early
Why pressure?
└─ Stakeholder expectations set too high
Impact: Team cutting corners to hit dates

```

**Trend:** Declining (was 3 defects/month in previous period)

**Recommendation:** IMMEDIATE ACTION REQUIRED
1. Slow down sprint pace (16 SP → 14 SP)
2. Mandatory code review 100%
3. Increase test coverage to 90% before next release

---

### 5️⃣ Risk Health: 7/10 (🟢 Good, → Stable)

**Current Status:**
- Critical risks: 0
- High risks: 2 (both mitigated)
- Medium risks: 3
- Low risks: 5

**Positive Indicators:**
- ✅ No critical risks
- ✅ High risks have mitigation plans
- ✅ Regular risk reviews

**Concerns:**
- ⚠️ Data quality risk re-opened (see Quality section)
- ⚠️ Team burnout risk emerging

**Trend:** Stable (risk count unchanged)

**Recommendation:** Continue weekly risk reviews, watch burnout risk

---

### 6️⃣ Team Health: 6/10 (🟡 Fair, ↘️ Declining)

**Current Status:**
- Team morale: 6/10 (was 8/10 last month)
- Utilization: 92% (target: 80-85%)
- Overtime: 8h/week average
- Turnover risk: Medium (1 person considering leaving)

**Positive Indicators:**
- ✅ Team collaboration good
- ✅ Skills adequate for work
- ✅ No conflicts or disputes

**Concerns:**
- 🟡 **Morale declining (8→6) (CONCERN)**
- 🟡 **Overutilization (92% vs 85% target)**
- 🟡 **Overtime unsustainable (8h/week)**
- 🟡 **Turnover risk (Senior DE may leave)**

**Root Cause Analysis:**
```

Why is morale declining?
└─ Team working long hours
Why long hours?
└─ Aggressive schedule pressure
Why aggressive schedule?
└─ Stakeholder expectations
Impact: Burnout risk, turnover risk

```

**Trend:** Declining (morale was 8/10 last month, now 6/10)

**Recommendation:** IMMEDIATE ACTION REQUIRED
1. Reduce sprint velocity to sustainable pace
2. Recognize team achievements
3. Plan team social/morale event
4. Address Senior DE retention (compensation, career growth)

---

## RED FLAGS 🚩

**CRITICAL ISSUES (Require immediate action):**

1. 🚩 **Defect Rate 4x Baseline**
   - Impact: Quality at risk, rework increasing
   - Action: Slow pace, increase testing
   - Owner: Tech Lead
   - Due: This week

2. 🚩 **Team Burnout Risk**
   - Impact: Turnover, productivity decline
   - Action: Reduce workload, recognize achievements
   - Owner: Delivery Lead
   - Due: This week

**HIGH PRIORITY ISSUES:**

3. ⚠️ **Test Coverage Below Target**
   - Impact: Risk of defects escaping to production
   - Action: Increase testing before next release
   - Owner: QA Lead
   - Due: 2 weeks

4. ⚠️ **Senior DE Retention Risk**
   - Impact: Project knowledge loss
   - Action: Career conversation, compensation review
   - Owner: HR + Delivery Lead
   - Due: 2 weeks

---

## TREND ANALYSIS

### Health Score Over Time

| Month | Overall | Schedule | Budget | Scope | Quality | Risks | Team |
|-------|---------|----------|--------|-------|---------|-------|------|
| Oct | 7.5 | 7 | 8 | 6 | 8 | 7 | 8 |
| Nov | 7.8 | 8 | 9 | 7 | 7 | 7 | 8 |
| Dec | 7.9 | 8 | 9 | 7 | 6 | 7 | 7 |
| Jan | 7.2 | 8 | 9 | 7 | 5 | 7 | 6 |

**Observations:**
- 📈 Schedule and budget consistently strong
- 📉 Quality declining over 3 months
- 📉 Team morale declining over 2 months
- → Risks stable throughout

**Trajectory:** Overall trending down due to quality and team issues

**Prediction (30 days):**
- If no action: Overall health drops to 6.5 (Amber)
- With corrective actions: Overall health improves to 7.5 (Green)

---

## CORRECTIVE ACTIONS

### Immediate Actions (This Week)

**ACTION 1: Reduce Sprint Velocity**
- Current: 18 SP/sprint
- Target: 14 SP/sprint (22% reduction)
- Rationale: Reduce pressure, improve quality
- Owner: Scrum Master
- Impact: May delay timeline by 1 week, but improve quality

**ACTION 2: Mandatory 100% Code Review**
- Current: 95% compliance
- Target: 100% compliance
- Rationale: Catch defects before testing
- Owner: Tech Lead
- Impact: +2h/week per developer

**ACTION 3: Team Recognition Event**
- Activity: Team lunch or social activity
- Rationale: Boost morale, recognize achievements
- Owner: Delivery Lead
- Budget: $500
- Impact: Improve team morale

**ACTION 4: Senior DE Retention Discussion**
- Meeting: 1-on-1 with Senior DE
- Topics: Career goals, compensation, concerns
- Owner: Delivery Lead + HR
- Impact: Reduce turnover risk

### Short-term Actions (Next 2-4 Weeks)

**ACTION 5: Increase Test Coverage to 90%**
- Current: 82%
- Target: 90%
- Activities: Add unit tests, integration tests
- Owner: QA Lead + Developers
- Timeline: 3 weeks

**ACTION 6: Technical Debt Sprint**
- Dedicate 1 sprint to code cleanup
- Refactor problematic areas
- Improve code quality
- Owner: Tech Lead
- Timeline: Sprint 7 (after MVP)

**ACTION 7: Process Improvement Workshop**
- Conduct team retrospective
- Identify process improvements
- Implement changes
- Owner: Scrum Master
- Timeline: 2 weeks

### Long-term Actions (Next 1-3 Months)

**ACTION 8: Quality Culture Initiative**
- Training on quality practices
- Quality metrics dashboard
- Quality champions program
- Owner: Tech Lead
- Timeline: 3 months

**ACTION 9: Work-Life Balance Policy**
- No overtime expectations
- Flexible working hours
- Mental health support
- Owner: Delivery Lead + HR
- Timeline: Ongoing

---

## STAKEHOLDER COMMUNICATION

**Who Needs to Know:**
- ✅ Executive Sponsor: Yes (quality and team issues)
- ✅ Technical Lead: Yes (immediate actions required)
- ✅ HR: Yes (retention concern)
- ⚪ Business Users: No (no impact to them yet)

**Communication Plan:**
- **This Week:** Email to exec sponsor with this report
- **This Week:** Meeting with tech lead on corrective actions
- **Next Week:** All-hands team meeting on changes
- **Monthly:** Continue health check reports

---

## SUCCESS METRICS

**Targets for Next Health Check (30 days):**

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Overall Health Score | 7.2 | 7.5 | 🎯 |
| Defect Rate | 12/month | <5/month | 🎯 |
| Test Coverage | 82% | 90% | 🎯 |
| Team Morale | 6/10 | 8/10 | 🎯 |
| Utilization | 92% | 85% | 🎯 |
| Sprint Velocity | 18 SP | 14-16 SP | 🎯 |

---

## APPROVAL & NEXT STEPS

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Review health check report | Exec Sponsor | {DATE+3d} | ⚪ |
| Approve corrective actions | Exec Sponsor | {DATE+5d} | ⚪ |
| Implement velocity reduction | Scrum Master | {DATE+7d} | ⚪ |
| Schedule retention discussion | Delivery Lead | {DATE+7d} | ⚪ |
| Next health check | Delivery Lead | {DATE+30d} | ⚪ |

---

**Assessor:** {Delivery Lead Name}
**Last Updated:** {DATE}
**Next Assessment:** {DATE + 30 days}
**Distribution:** Executive Sponsor, Technical Lead, HR, Project Team
```

## Best Practices

1. **Be Objective**: Use data, not opinions
2. **Be Honest**: Don't hide problems from executives
3. **Be Specific**: Provide concrete examples and metrics
4. **Be Actionable**: Every issue needs a corrective action
5. **Be Timely**: Conduct health checks monthly minimum
6. **Be Consistent**: Use same format and metrics each time
7. **Be Transparent**: Share findings with team and stakeholders
8. **Follow Up**: Track action completion and impact

## Health Check Frequency

- **Weekly**: For critical/red projects
- **Bi-weekly**: For at-risk/amber projects
- **Monthly**: For healthy/green projects
- **Ad-hoc**: After major events or escalations

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual health assessment: 4-6 hours
- With DeliveryPro agent: 1-2 hours
- **Effort reduction: 65-75%**
