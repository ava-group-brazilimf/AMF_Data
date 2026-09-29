# 📚 Task: Generate Runbooks

## Command
`*generate-runbook`

## Objective
Create comprehensive operational runbooks for the migrated environment. These runbooks enable Day-2 operations teams to monitor, maintain, troubleshoot, and recover the migrated data pipelines without requiring the original migration team.

---

## Prerequisites

- Artifacts available:
  - `migration-coordinator → execution-log.json, wave-status-report.md`
  - `code-generator → generated-code/*.py`
  - `quality-gate → validation-report/*.json`
  - `self-healing → healing-log/*.json`
  - `security-compliance → compliance-report/*.json`

---

## Steps

### 1. Environment Analysis
- Parse execution logs to identify all deployed components
- Catalog all data pipelines, jobs, and schedules
- Identify monitoring endpoints and health checks
- Map infrastructure dependencies (clusters, storage, network)

### 2. Monitoring Runbook Generation
- Document all monitoring dashboards and their URLs
- Define alert thresholds and notification channels
- Create health check procedures
- Document SLA targets and measurement methods
- Include Databricks job monitoring procedures

### 3. Incident Response Runbook Generation
- Create decision trees for common failure scenarios
- Document escalation procedures with contact information
- Define severity levels and response times
- Include self-healing agent capabilities reference
- Document manual intervention procedures when self-healing fails

### 4. Troubleshooting Runbook Generation
- Catalog common errors from `healing-log/*.json`
- Create step-by-step resolution guides
- Include SQL queries for data investigation
- Document log locations and analysis procedures
- Add performance troubleshooting guides

### 5. Maintenance Runbook Generation
- Document scheduled maintenance windows
- Create procedures for:
  - Cluster scaling up/down
  - Storage cleanup and archival
  - Certificate rotation
  - Secret rotation
  - Backup and restore
- Include rollback procedures for each maintenance task

### 6. Assembly
- Use `runbook-tmpl.md` template for each runbook
- Generate table of contents per runbook
- Add metadata (author, version, last updated, next review date)
- Cross-reference between runbooks

---

## Output

| File                                                    | Description                          |
|---------------------------------------------------------|--------------------------------------|
| `projects/{project_name}/outputs/downstream/documentation/runbooks/runbook-monitoring.md`        | Monitoring and alerting procedures   |
| `projects/{project_name}/outputs/downstream/documentation/runbooks/runbook-incident-response.md` | Incident response playbook           |
| `projects/{project_name}/outputs/downstream/documentation/runbooks/runbook-troubleshooting.md`   | Common troubleshooting guides        |
| `projects/{project_name}/outputs/downstream/documentation/runbooks/runbook-maintenance.md`       | Scheduled maintenance procedures     |
| `projects/{project_name}/outputs/downstream/documentation/runbooks/runbook-index.md`             | Index of all runbooks                |

---

## Quality Criteria

- [ ] All deployed components documented
- [ ] Monitoring procedures cover all pipelines
- [ ] Incident response includes escalation matrix
- [ ] Troubleshooting covers top 20 most common errors
- [ ] Maintenance includes rollback for every procedure
- [ ] Contact information included and verified
- [ ] All procedures tested against environment
- [ ] Both PT-BR and EN-US versions generated
