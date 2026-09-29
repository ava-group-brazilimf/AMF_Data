---
task: estimate-project
version: 1.0
elicit: true
description: Estimate project costs (resources, infrastructure, maintenance) and timeline
---

# Estimate Project Cost and Timeline

## Purpose

Calculate comprehensive project costs including development effort, infrastructure, and ongoing maintenance. Provide realistic timeline estimates with resource allocation.

## Process

### Step 1: Gather Project Information

ASK the user for the following information:

1. **Project Scope**: What is being built? (pipeline, analytics platform, dashboard, etc.)
2. **Key Deliverables**: What are the main outputs? (DDL scripts, ETL, tests, docs, etc.)
3. **Technology Stack**: What technologies will be used? (Azure, AWS, SQL, Spark, etc.)
4. **Team Composition**: What roles are available? (Data Engineer, Architect, BI Dev, etc.)
5. **Complexity Level**: Low/Medium/High based on:
   - Number of data sources
   - Transformation complexity
   - Integration requirements
   - Regulatory/compliance needs
6. **Geographic Model**: Onshore, offshore, nearshore, or mixed?
7. **Existing Context**: Any similar projects completed? Historical data?

### Step 2: Estimate Development Effort

CALCULATE effort by role and activity:

**Activities to Estimate:**

- Requirements analysis and design
- Architecture and technical design
- Development (DDL, ETL, pipelines)
- Data quality framework
- Testing (unit, integration, UAT)
- Documentation
- Deployment and go-live
- Knowledge transfer

**Roles to Consider:**

- Senior Data Engineer ($120-$180/h)
- Data Solution Architect ($150-$250/h)
- BI Developer ($100-$150/h)
- QA Engineer ($90-$140/h)
- Technical Writer ($80-$120/h)
- Project Manager ($120-$200/h - typically 15-20% overhead)

**Apply Complexity Multipliers:**

- Low Complexity: 1.0x
- Medium Complexity: 1.3x
- High Complexity: 1.8x

**Add Buffers:**

- Unknowns buffer: 15-20%
- Testing & QA buffer: 20-25% of dev time
- Ramp-up time: 1-2 weeks for new team

### Step 3: Calculate Infrastructure Costs

ESTIMATE cloud infrastructure costs:

**Azure Resources (common):**

- Azure Synapse Analytics / Databricks
- Azure SQL Database
- Azure Data Factory / Data Pipelines
- Azure Data Lake Storage (Gen2)
- Monitoring (Log Analytics, Application Insights)
- Networking (VNet, Private Endpoints)

**AWS Resources (common):**

- Redshift or EMR
- RDS (PostgreSQL/MySQL)
- Glue / Lambda
- S3 Storage
- CloudWatch

**Calculation Method:**

1. Identify required services
2. Estimate monthly consumption
3. Add 20-30% buffer for spikes
4. Calculate annual cost (monthly × 12)

### Step 4: Calculate Ongoing Costs

DETERMINE maintenance and operational costs:

**Support & Maintenance (typically 20-25% of dev cost per year):**

- Bug fixes and enhancements
- Performance tuning
- Security patches
- User support
- New data source additions

**Infrastructure (recurring):**

- Annual cloud costs
- Licensing fees
- Monitoring tools
- Backup and disaster recovery

### Step 5: Create Timeline

DEVELOP realistic delivery timeline:

**Phases:**

1. Planning & Design (10-15% of timeline)
2. Development (50-60% of timeline)
3. Testing & QA (20-25% of timeline)
4. Deployment & Stabilization (10-15% of timeline)

**Factor in:**

- Sprint/iteration length (2-4 weeks typical)
- Resource availability (80% utilization for planning)
- Holidays and vacations
- Stakeholder review cycles
- Dependencies and blockers

### Step 6: Assess Risks and Contingencies

IDENTIFY cost/timeline risks:

**Common Risks:**

- Scope creep (+20-30% cost impact)
- Data quality issues (+10-20% cost impact)
- Resource availability (+5-15% cost impact)
- Technology challenges (+10-25% cost impact)
- Stakeholder delays (+10-20% timeline impact)

**Contingency Recommendations:**

- Development: 15-20% buffer
- Infrastructure: 20-25% buffer
- Timeline: 15-20% buffer

## Output Structure

```markdown
# PROJECT COST ESTIMATION - {PROJECT_NAME}

## Executive Summary

- Total Development Cost: ${X}
- Infrastructure Cost (Year 1): ${Y}
- Total Year 1 Cost: ${Z}
- Ongoing Annual Cost: ${W}
- Timeline: {N} weeks
- Team Size: {M} FTE peak

## Development Costs

### Resource Breakdown

| Role                  | Hours    | Rate   | Cost         |
| --------------------- | -------- | ------ | ------------ |
| Senior Data Engineer  | 320h     | $150/h | $48,000      |
| Data Architect        | 80h      | $200/h | $16,000      |
| BI Developer          | 120h     | $130/h | $15,600      |
| QA Engineer           | 80h      | $120/h | $9,600       |
| Technical Writer      | 36h      | $100/h | $3,600       |
| Project Manager (15%) | 90h      | $180/h | $16,200      |
| **TOTAL**             | **726h** |        | **$109,000** |

## Infrastructure Costs (Annual)

| Component         | Specification | Monthly    | Annual      |
| ----------------- | ------------- | ---------- | ----------- |
| Azure Synapse     | DW100c        | $1,000     | $12,000     |
| Azure SQL DB      | S2 (50 DTU)   | $300       | $3,600      |
| Data Factory      | 300 runs/mo   | $200       | $2,400      |
| Data Lake Storage | 500GB         | $100       | $1,200      |
| Monitoring        | 5GB/day       | $150       | $1,800      |
| **TOTAL**         |               | **$1,750** | **$21,000** |

## Ongoing Costs (Years 2+)

| Component                   | Annual Cost      |
| --------------------------- | ---------------- |
| Infrastructure              | $21,000          |
| Support & Maintenance (20%) | $21,800          |
| **TOTAL**                   | **$42,800/year** |

## Cost Summary

### Year 1 (Development + Operations)

- Development: $109,000
- Infrastructure: $21,000
- **Total Year 1: $130,000**

### Years 2-5 (Operations Only)

- **Annual Cost: $42,800**

### 5-Year TCO

- Year 1: $130,000
- Years 2-5: $171,200
- **5-Year Total: $301,200**

## Timeline

### Phase Breakdown

| Phase             | Duration     | Key Deliverables              |
| ----------------- | ------------ | ----------------------------- |
| Planning & Design | 2 weeks      | Architecture, design docs     |
| Development       | 5 weeks      | DDL, ETL, quality checks      |
| Testing & QA      | 2 weeks      | Unit tests, integration tests |
| Deployment        | 1 week       | Go-live, stabilization        |
| **TOTAL**         | **10 weeks** |                               |

### Resource Allocation

| Week | Data Eng | Architect | BI Dev | QA  | PM   |
| ---- | -------- | --------- | ------ | --- | ---- |
| 1-2  | 1.0      | 0.5       | 0      | 0   | 0.25 |
| 3-7  | 1.0      | 0         | 1.0    | 0.5 | 0.25 |
| 8-9  | 1.0      | 0         | 0.5    | 1.0 | 0.25 |
| 10   | 1.0      | 0.5       | 0      | 0.5 | 0.25 |

## Cost Optimization Opportunities

### With Agentic AI (60% dev time reduction):

- Development: $109,000 → $43,600 (savings: $65,400)
- **New Year 1 Total: $64,600 (50% savings)**

### Infrastructure Optimization:

- Reserved instances: Save 30-40% ($6,300-$8,400/year)
- Auto-pause/resume: Save 40-50% compute ($4,800-$6,000/year)
- Serverless: Save 30-40% overall ($6,300-$8,400/year)

## Risks and Assumptions

### Key Assumptions

✅ Team has required technology experience
✅ No major scope changes during development
✅ Source data quality is acceptable
✅ Standard 40-hour work week (no overtime)

### Cost Risks

🔴 HIGH: Scope creep (+20-30% cost impact)
🟡 MEDIUM: Data quality issues (+10-15% cost impact)
🟡 MEDIUM: Infrastructure costs higher (+15-20% infra cost)
🟢 LOW: Resource availability (+5-10% cost impact)

### Recommended Contingency: 20%

- Development buffer: $21,800
- Infrastructure buffer: $4,200
- **Total Contingency: $26,000**

### Total Budget (with contingency):

- Base Cost: $130,000
- Contingency: $26,000
- **Total Budget: $156,000**

## Approval

| Stakeholder | Role             | Approved | Date |
| ----------- | ---------------- | -------- | ---- |
|             | Delivery Lead    | ☐        |      |
|             | Finance Director | ☐        |      |
|             | Technical Lead   | ☐        |      |

---

**Last Updated:** {DATE}
**Next Review:** {DATE + 30 days}
```

## Best Practices

1. **Use Historical Data**: Reference similar completed projects
2. **Conservative Estimates**: Add 15-20% buffer for unknowns
3. **Include Hidden Costs**: Licenses, training, support, monitoring
4. **Document Assumptions**: Make all assumptions explicit and clear
5. **Validate with Team**: Get input from technical leads on complexity
6. **Track Actuals**: Compare estimates to actuals for future learning
7. **Update Regularly**: Revisit estimates monthly as project progresses

## Impact Metrics

**Typical Effort Reduction with Agentic AI:**

- Manual estimation: 8-12 hours
- With DeliveryPro agent: 2-3 hours
- **Effort reduction: 60-75%**
