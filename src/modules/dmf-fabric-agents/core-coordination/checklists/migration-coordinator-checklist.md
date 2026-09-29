# Migration Coordinator Checklist

**Agent:** Orion (Migration Coordinator)  
**Version:** 1.0

---

## Pre-Migration Checklist

### Environment Setup
- [ ] Source platform connections validated
- [ ] Target platform provisioned and accessible
- [ ] All 9 agents operational and configured
- [ ] Migration Control DB initialized (PostgreSQL)
- [ ] Message Queue operational (Redis + Celery)
- [ ] Monitoring stack deployed (Grafana + InfluxDB)
- [ ] Artifact storage configured

### Planning
- [ ] Migration plan approved by PM
- [ ] Pipeline scope defined and documented
- [ ] Wave strategy defined (pilot → batch → final)
- [ ] Success criteria agreed with stakeholders
- [ ] Rollback plan documented and tested
- [ ] Cutover strategy selected (trickle/big-bang)
- [ ] Communication plan established

---

## Wave Execution Checklist

### Pre-Wave
- [ ] Previous wave completed (if applicable)
- [ ] Pipeline IDs selected for this wave
- [ ] Dependencies resolved (no unresolved)
- [ ] Parallelism configured
- [ ] Celery workers provisioned

### During Wave
- [ ] Scout scan initiated and completed
- [ ] Logan extraction completed for all pipelines
- [ ] Coda generation completed for all pipelines
- [ ] Vera validation passed for >= 85% pipelines
- [ ] Shield compliance passed for all pipelines
- [ ] Phoenix self-healing logged
- [ ] All failed pipelines escalated

### Post-Wave
- [ ] Balance reconciliation completed
- [ ] Scribe documentation generated
- [ ] Wave status report generated
- [ ] Stakeholders notified
- [ ] Audit trail recorded

---

## Gate Validation Checklist

### Pre-Gate
- [ ] All required artifacts identified
- [ ] Quality criteria loaded from config
- [ ] Checklist template ready

### During Validation
- [ ] Each artifact existence verified
- [ ] Quality criteria applied
- [ ] Cross-references validated
- [ ] Issues documented

### Post-Validation
- [ ] Gate report generated using template
- [ ] Result recorded in audit trail
- [ ] Stakeholders notified
- [ ] Next phase agents prepared
