# Agent Contract Template

## Contract Overview

**Contract ID:** {contract_id}  
**Version:** {version}  
**Last Updated:** {date}

---

## Agent: {agent_name}

### Input Contracts

```yaml
# Input Contract for {agent_name}

inputs:
  required:
    - artifact: "{artifact_name}.md"
      from_agent: "{source_agent_id}"
      description: |
        {Description of what this artifact contains and why it's needed}
      
      validation:
        rules:
          - type: "exists"
            message: "Artifact must exist before processing"
            
          - type: "schema_valid"
            schema: "{schema_reference}"
            message: "Must conform to standard schema"
            
          - type: "sections_present"
            sections:
              - "Overview"
              - "Requirements"
              - "Details"
            message: "Required sections must be present"
            
          - type: "not_empty"
            fields: ["overview", "details"]
            message: "Key fields cannot be empty"
            
      freshness:
        max_age: "24 hours"
        check_timestamp: true
        on_stale: "warn"  # warn|reject|accept
        
      fallback:
        on_missing: "request_from_upstream"
        on_invalid: "notify_orchestrator"
        
  optional:
    - artifact: "{optional_artifact}.md"
      from_agent: "{source_agent_id}"
      description: |
        {Description of optional artifact}
      default_behavior: "proceed_without"
      enhancement: |
        {How this artifact enhances processing if present}
```

---

### Output Contracts

```yaml
# Output Contract for {agent_name}

outputs:
  - artifact: "{output_artifact}.md"
    description: |
      {Description of what this output contains}
    
    to_agents:
      - agent_id: "{target_agent_1}"
        purpose: "{why this agent needs it}"
      - agent_id: "{target_agent_2}"
        purpose: "{why this agent needs it}"
        
    format:
      type: "markdown"  # markdown|yaml|json|sql
      encoding: "utf-8"
      
    location:
      folder: "docs/{subfolder}/"
      naming: "{project}-{artifact}-{timestamp}.md"
      
    sections:
      required:
        - name: "Overview"
          description: "High-level summary"
          min_length: 100
          
        - name: "Details"
          description: "Detailed content"
          
        - name: "Validation"
          description: "Quality checks passed"
          
      optional:
        - name: "Appendix"
          description: "Supporting information"
          
    quality:
      completeness:
        target: 100%
        minimum: 90%
        
      validation:
        - type: "checklist_pass"
          checklist: "{agent}-checklist.md"
          
        - type: "peer_review"
          reviewer: "{reviewing_agent}"
          
    metadata:
      include:
        - created_at
        - created_by
        - version
        - dependencies
```

---

### Handoff Protocol

```yaml
# Handoff Protocol for {agent_name}

handoff:
  trigger:
    type: "artifact_complete"
    artifact: "{output_artifact}.md"
    validation: "checklist_pass"
    
  method: "orchestrator_mediated"  # direct|orchestrator_mediated
  
  pre_handoff:
    - action: "validate_output"
      validator: "{agent}_validator"
      
    - action: "notify_target"
      agents: ["{target_agent}"]
      message: "Artifact ready for processing"
      
  data_transfer:
    format: "markdown"
    compression: false
    checksum: true
    
    location:
      source: "docs/{source_folder}/"
      target: "docs/{target_folder}/"
      
  confirmation:
    required: true
    method: "acknowledgment"
    timeout: "5 minutes"
    
    on_timeout:
      action: "retry"
      max_retries: 3
      escalate_after: true
      
  rollback:
    enabled: true
    method: "version_restore"
    keep_versions: 3
    
  post_handoff:
    - action: "update_status"
      status: "completed"
      
    - action: "log_metrics"
      metrics: ["duration", "artifact_size", "validation_score"]
```

---

### Error Handling

```yaml
# Error Handling for {agent_name}

error_handling:
  on_missing_input:
    severity: "critical"
    
    actions:
      - type: "request_artifact"
        from_agent: "{source_agent}"
        message: "Required artifact missing: {artifact_name}"
        
      - type: "notify"
        recipients: ["{source_agent}", "orchestrator"]
        channel: "status_update"
        
      - type: "wait"
        timeout: "15 minutes"
        
      - type: "escalate"
        after_timeout: true
        to: "orchestrator"
        
  on_validation_failure:
    severity: "warning"
    
    actions:
      - type: "retry"
        count: 3
        delay: "exponential"
        initial_delay: "1 minute"
        max_delay: "5 minutes"
        
      - type: "notify"
        recipients: ["{agent}", "orchestrator"]
        include: ["error_details", "validation_report"]
        
      - type: "escalate"
        after_retries: true
        to: "orchestrator"
        include_context: true
        
  on_processing_error:
    severity: "error"
    
    actions:
      - type: "log"
        level: "error"
        include: ["stack_trace", "input_state", "partial_output"]
        
      - type: "notify"
        recipients: ["orchestrator"]
        priority: "high"
        
      - type: "rollback"
        to: "last_valid_state"
        
  on_timeout:
    threshold: "30 minutes"
    severity: "warning"
    
    actions:
      - type: "checkpoint"
        save_partial: true
        
      - type: "notify"
        recipients: ["orchestrator"]
        message: "Processing timeout - partial results saved"
        
      - type: "option"
        choices:
          - "continue"
          - "escalate"
          - "cancel"
        default: "escalate"
        
  fallback:
    enabled: true
    
    strategies:
      - condition: "all_retries_exhausted"
        action: "human_takeover"
        notify: ["human_operator", "orchestrator"]
        
      - condition: "critical_error"
        action: "abort_pipeline"
        notify: ["all_stakeholders"]
        cleanup: true
```

---

## Contract Validation Checklist

- [ ] All required inputs have sources
- [ ] All outputs have targets
- [ ] Validation rules are testable
- [ ] Error handling covers all scenarios
- [ ] Timeouts are reasonable
- [ ] Rollback procedures are defined
- [ ] Notifications are configured
