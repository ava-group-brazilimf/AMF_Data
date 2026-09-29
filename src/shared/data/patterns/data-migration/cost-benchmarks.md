# Cost Benchmarks & Rate Cards

**Version:** 1.0  
**Last Updated:** January 22, 2026  
**Purpose:** Industry benchmarks for cost estimation in Data & Analytics projects

---

## 💵 HOURLY RATES BY ROLE (USD)

### US/Western Europe Rates

| Role               | Junior (0-3 yrs) | Mid (3-7 yrs) | Senior (7-12 yrs) | Lead (12+ yrs) |
| ------------------ | ---------------- | ------------- | ----------------- | -------------- |
| Data Engineer      | $80-100          | $110-140      | $150-180          | $190-220       |
| Data Scientist     | $90-110          | $120-150      | $160-190          | $200-240       |
| Data Analyst       | $70-85           | $95-120       | $130-150          | $160-180       |
| ML Engineer        | $95-115          | $125-155      | $165-195          | $205-245       |
| Analytics Engineer | $85-105          | $115-145      | $155-185          | $195-225       |
| DevOps Engineer    | $90-110          | $120-150      | $160-190          | $200-230       |
| Solution Architect | $110-130         | $140-170      | $180-210          | $220-260       |
| Cloud Architect    | $105-125         | $135-165      | $175-205          | $215-255       |
| Product Owner      | $95-115          | $125-155      | $165-195          | $205-235       |
| Scrum Master       | $85-105          | $115-145      | $155-185          | $195-225       |
| QA Engineer        | $70-90           | $100-130      | $140-170          | $180-210       |
| Technical Writer   | $65-80           | $90-115       | $125-150          | $160-185       |
| Business Analyst   | $75-90           | $100-125      | $135-160          | $170-195       |
| Project Manager    | $90-110          | $120-150      | $160-190          | $200-230       |
| Delivery Lead      | $100-120         | $130-160      | $170-200          | $210-250       |

### Eastern Europe Rates (40-50% of US rates)

| Role           | Junior | Mid    | Senior | Lead     |
| -------------- | ------ | ------ | ------ | -------- |
| Data Engineer  | $35-50 | $55-70 | $75-90 | $95-110  |
| Data Scientist | $40-55 | $60-75 | $80-95 | $100-120 |
| Data Analyst   | $30-40 | $45-60 | $65-75 | $80-90   |
| ML Engineer    | $40-55 | $60-75 | $80-95 | $100-120 |

### India/Asia Rates (25-35% of US rates)

| Role           | Junior | Mid    | Senior | Lead    |
| -------------- | ------ | ------ | ------ | ------- |
| Data Engineer  | $20-30 | $35-50 | $55-70 | $75-90  |
| Data Scientist | $25-35 | $40-55 | $60-75 | $80-100 |
| Data Analyst   | $18-25 | $30-45 | $50-60 | $65-75  |
| ML Engineer    | $25-35 | $40-55 | $60-75 | $80-100 |

**Notes:**

- Rates vary by company size, industry, and location
- Consulting firms typically charge 2-2.5x employee cost
- Freelancers typically charge 1.5-2x employee hourly rate
- Add 25-40% for benefits/overhead (US/Europe)

---

## ☁️ AZURE INFRASTRUCTURE COSTS

### Compute

| Service                          | Size            | vCPU     | RAM (GB) | Monthly Cost (USD)      |
| -------------------------------- | --------------- | -------- | -------- | ----------------------- |
| **Azure VM (B-Series)**          | B2s             | 2        | 4        | $30                     |
| **Azure VM (D-Series)**          | D4s_v5          | 4        | 16       | $140                    |
| **Azure VM (D-Series)**          | D8s_v5          | 8        | 32       | $280                    |
| **Azure VM (D-Series)**          | D16s_v5         | 16       | 64       | $560                    |
| **Azure Databricks**             | Standard        | 4 DBU/hr | -        | ~$600/mo (continuous)   |
| **Azure Databricks**             | Premium         | 8 DBU/hr | -        | ~$1,200/mo (continuous) |
| **Azure Synapse Dedicated Pool** | DW100c          | 1 DWU    | -        | $1,200                  |
| **Azure Synapse Dedicated Pool** | DW500c          | 5 DWU    | -        | $6,000                  |
| **ADF Integration Runtime**      | General Purpose | 4 Core   | 8 GB     | $0.25/hr ($180/mo)      |

### Storage

| Service                  | Type                        | Monthly Cost (per TB) |
| ------------------------ | --------------------------- | --------------------- |
| **Azure Blob Storage**   | Hot tier                    | $18                   |
| **Azure Blob Storage**   | Cool tier                   | $10                   |
| **Azure Blob Storage**   | Archive tier                | $2                    |
| **Azure Data Lake Gen2** | Hot tier                    | $18                   |
| **Azure SQL Database**   | General Purpose (4 vCore)   | $460                  |
| **Azure SQL Database**   | Business Critical (4 vCore) | $1,380                |
| **Azure Cosmos DB**      | Provisioned (400 RU/s)      | $24                   |

### Analytics & AI

| Service                          | Tier          | Monthly Cost                                    |
| -------------------------------- | ------------- | ----------------------------------------------- |
| **Azure OpenAI (GPT-4)**         | -             | $0.03/1K input tokens, $0.06/1K output tokens   |
| **Azure OpenAI (GPT-4o)**        | -             | $0.005/1K input tokens, $0.015/1K output tokens |
| **Azure Machine Learning**       | Basic compute | $0.15-0.50/hr (varies by VM)                    |
| **Power BI Premium**             | Per capacity  | $4,995/mo (P1)                                  |
| **Power BI Pro**                 | Per user      | $10/user/mo                                     |
| **Azure Synapse Serverless SQL** | -             | $5/TB processed                                 |
| **Azure Stream Analytics**       | Standard      | $0.11/streaming unit/hr                         |

### Networking & Security

| Service                       | Tier     | Monthly Cost         |
| ----------------------------- | -------- | -------------------- |
| **Azure VPN Gateway**         | Basic    | $28                  |
| **Azure Application Gateway** | Standard | $140                 |
| **Azure Key Vault**           | Standard | $0.03/10K operations |
| **Azure Monitor**             | -        | $2.30/GB ingested    |

**Notes:**

- Prices as of Jan 2026, US East region
- Reserved instances: 30-70% savings (1-3 year commitment)
- Spot instances: Up to 90% savings (interruptible workloads)
- Dev/Test subscriptions: 15-40% discount
- Auto-pause/resume for non-prod: 60-80% savings

---

## ☁️ AWS INFRASTRUCTURE COSTS

### Compute

| Service                   | Size      | vCPU   | RAM (GB) | Monthly Cost (USD)    |
| ------------------------- | --------- | ------ | -------- | --------------------- |
| **EC2 (t3.medium)**       | -         | 2      | 4        | $30                   |
| **EC2 (m5.xlarge)**       | -         | 4      | 16       | $140                  |
| **EC2 (m5.2xlarge)**      | -         | 8      | 32       | $280                  |
| **EC2 (m5.4xlarge)**      | -         | 16     | 64       | $560                  |
| **EMR (3-node cluster)**  | m5.xlarge | -      | -        | ~$500/mo (continuous) |
| **Redshift (dc2.large)**  | -         | 2 vCPU | 15 GB    | $180/node             |
| **Redshift (ra3.xlplus)** | -         | 4 vCPU | 32 GB    | $1,086/node           |
| **Glue DPU**              | -         | 4 vCPU | 16 GB    | $0.44/hour            |

### Storage

| Service                     | Type             | Monthly Cost (per TB)      |
| --------------------------- | ---------------- | -------------------------- |
| **S3 Standard**             | -                | $23                        |
| **S3 Intelligent-Tiering**  | -                | $23 (+ $0.0025/1K objects) |
| **S3 Glacier Instant**      | -                | $4                         |
| **S3 Glacier Deep Archive** | -                | $1                         |
| **EBS (gp3)**               | SSD              | $80                        |
| **EBS (st1)**               | HDD              | $45                        |
| **RDS (db.m5.large)**       | MySQL/PostgreSQL | $140                       |

### Analytics & AI

| Service                            | Tier       | Monthly Cost                             |
| ---------------------------------- | ---------- | ---------------------------------------- |
| **Amazon Bedrock (Claude Sonnet)** | -          | $0.003/1K input, $0.015/1K output tokens |
| **SageMaker (ml.m5.xlarge)**       | -          | $0.23/hr ($165/mo continuous)            |
| **Athena**                         | -          | $5/TB scanned                            |
| **QuickSight**                     | Enterprise | $18/user/mo                              |
| **Kinesis Data Streams**           | -          | $0.015/shard-hour + $0.014/million PUT   |

**Notes:**

- Prices as of Jan 2026, US East region
- Reserved instances: 30-75% savings (1-3 year commitment)
- Savings Plans: Flexible commitment-based discounts
- Spot instances: Up to 90% savings

---

## 📊 PROJECT COST BENCHMARKS

### Small Project (3-6 months)

- **Team Size:** 3-5 people
- **Total Effort:** 1,500-3,000 hours
- **Labor Cost:** $150K-$400K
- **Infrastructure:** $5K-$15K
- **Total Cost:** $155K-$415K

**Typical Scope:**

- Single data source integration
- Basic ETL pipeline
- Simple analytics dashboard
- Limited ML model (1-2 models)

### Medium Project (6-12 months)

- **Team Size:** 6-10 people
- **Total Effort:** 4,000-10,000 hours
- **Labor Cost:** $500K-$1.5M
- **Infrastructure:** $20K-$60K
- **Total Cost:** $520K-$1.56M

**Typical Scope:**

- Multiple data source integration
- Complex ETL with data quality
- Enterprise dashboards
- ML platform with 3-5 models
- Basic MLOps

### Large Project (12-24 months)

- **Team Size:** 10-20 people
- **Total Effort:** 12,000-30,000 hours
- **Labor Cost:** $1.8M-$5M
- **Infrastructure:** $75K-$250K
- **Total Cost:** $1.875M-$5.25M

**Typical Scope:**

- Enterprise data platform
- Data lake + data warehouse
- Real-time and batch pipelines
- Advanced analytics & ML
- Full MLOps with CI/CD
- Multiple business domains

### Enterprise Program (24+ months)

- **Team Size:** 20-50 people
- **Total Effort:** 40,000-100,000+ hours
- **Labor Cost:** $6M-$20M+
- **Infrastructure:** $300K-$1M+
- **Total Cost:** $6.3M-$21M+

**Typical Scope:**

- Enterprise-wide data transformation
- Data mesh or data fabric
- Multi-cloud deployment
- Advanced AI/ML at scale
- Data governance & security
- Change management

---

## 🤖 AGENTIC AI COST SAVINGS

### Effort Reduction by Activity

| Activity                  | Traditional Effort | With Agentic AI | Savings |
| ------------------------- | ------------------ | --------------- | ------- |
| **Requirements Analysis** | 100 hrs            | 40 hrs          | 60%     |
| **Data Pipeline Design**  | 80 hrs             | 30 hrs          | 62.5%   |
| **ETL Development**       | 200 hrs            | 80 hrs          | 60%     |
| **Data Quality Rules**    | 60 hrs             | 20 hrs          | 66.7%   |
| **Testing & Validation**  | 120 hrs            | 40 hrs          | 66.7%   |
| **Documentation**         | 80 hrs             | 20 hrs          | 75%     |
| **Code Reviews**          | 40 hrs             | 15 hrs          | 62.5%   |
| **Deployment Scripts**    | 30 hrs             | 10 hrs          | 66.7%   |
| **Monitoring Setup**      | 40 hrs             | 15 hrs          | 62.5%   |

**Overall Project Savings:** 40-70% effort reduction  
**Quality Impact:** 20-30% fewer defects  
**Time to Market:** 40-60% faster delivery

### Example: Medium Data Engineering Project

**Traditional Approach:**

- Total Effort: 8,000 hours
- Duration: 12 months
- Team Size: 8 people
- Labor Cost: $1,200,000
- Infrastructure: $50,000
- **Total Cost: $1,250,000**

**With Agentic AI:**

- Total Effort: 3,500 hours (56% reduction)
- Duration: 6 months (50% reduction)
- Team Size: 6 people (25% reduction)
- Labor Cost: $525,000 (56% reduction)
- Infrastructure: $25,000 (50% reduction, shorter duration)
- AI Tools Cost: $10,000
- **Total Cost: $560,000**

**Savings: $690,000 (55% cost reduction)**

---

## 📈 ONGOING OPERATIONAL COSTS

### Infrastructure (Annual)

| Environment     | Small | Medium | Large | Enterprise |
| --------------- | ----- | ------ | ----- | ---------- |
| **Production**  | $60K  | $200K  | $600K | $2M+       |
| **Staging**     | $20K  | $60K   | $180K | $600K      |
| **Dev/Test**    | $10K  | $30K   | $90K  | $300K      |
| **Total Infra** | $90K  | $290K  | $870K | $2.9M      |

### Managed Services (Annual)

| Service                  | Small | Medium | Large |
| ------------------------ | ----- | ------ | ----- |
| **Databricks**           | $50K  | $200K  | $800K |
| **Snowflake**            | $60K  | $250K  | $1M   |
| **Power BI**             | $20K  | $80K   | $300K |
| **Monitoring (Datadog)** | $10K  | $40K   | $150K |

### Support & Maintenance (Annual)

| Activity                | % of Dev Cost | Small | Medium | Large   |
| ----------------------- | ------------- | ----- | ------ | ------- |
| **Application Support** | 15-20%        | $30K  | $100K  | $375K   |
| **Infrastructure Ops**  | 10-15%        | $15K  | $50K   | $150K   |
| **Enhancements**        | 20-30%        | $50K  | $150K  | $500K   |
| **Total Annual**        | 45-65%        | $95K  | $300K  | $1,025K |

---

## 🎯 COST OPTIMIZATION STRATEGIES

### 1. Right-Size Infrastructure

- Start small, scale as needed
- Monitor utilization, downsize underused resources
- **Typical Savings:** 20-40%

### 2. Reserved Capacity

- 1-year or 3-year commitments
- **Typical Savings:** 30-70%

### 3. Auto-Scaling & Scheduling

- Scale down non-prod environments
- Auto-pause idle resources
- Schedule start/stop times
- **Typical Savings:** 40-70% on non-prod

### 4. Leverage Agentic AI

- Automate repetitive tasks
- Generate code, tests, docs
- **Typical Savings:** 40-70% effort

### 5. Offshore/Nearshore Mix

- Onshore leads, offshore execution
- Follow-the-sun model
- **Typical Savings:** 30-50% on blended rates

### 6. Open Source Tools

- Replace proprietary with OSS where feasible
- Apache Spark vs Databricks
- PostgreSQL vs commercial databases
- **Typical Savings:** 50-80% on software licenses

### 7. Serverless Architecture

- Pay only for actual usage
- No idle capacity costs
- **Typical Savings:** 30-60% for variable workloads

---

## 📋 ESTIMATION RULES OF THUMB

### Development Effort Allocation

- **Requirements & Design:** 15-20%
- **Development:** 40-50%
- **Testing:** 20-25%
- **Deployment & Documentation:** 10-15%

### Non-Development Overhead

- **Meetings & Ceremonies:** 15-20%
- **Code Reviews:** 5-10%
- **Support & Maintenance:** 5-10%

### Buffers & Contingencies

- **Development Buffer:** 15-20%
- **Testing Buffer:** 20-25%
- **Integration Buffer:** 10-15%
- **Management Reserve:** 10-15%

### Team Utilization

- **Target Utilization:** 80-85% (not 100%)
- **Ramp-Up Time:** 2-4 weeks for new team members
- **Ramp-Down Time:** 1-2 weeks for knowledge transfer

### Velocity

- **Junior Developer:** 25-30 story points/sprint
- **Mid Developer:** 35-45 story points/sprint
- **Senior Developer:** 45-55 story points/sprint

---

## 💡 KEY TAKEAWAYS

1. **Labor is 80-90% of project cost** - Focus optimization here
2. **Agentic AI saves 40-70% effort** - Adopt AI tools aggressively
3. **Infrastructure can be optimized 30-70%** - Right-size, reserve, schedule
4. **Offshore/nearshore saves 30-50%** - But factor in communication overhead
5. **Ongoing costs = 45-65% of initial dev cost annually** - Plan for long-term
6. **Be conservative in estimates** - Add 15-20% buffer minimum
7. **Track actuals vs estimates** - Build your own benchmark database

---

**Last Updated:** January 22, 2026  
**Source:** Industry surveys, Avanade project database, cloud provider pricing  
**Note:** All costs are approximate and vary by region, company size, and market conditions. Use as guidelines, not absolute values.
