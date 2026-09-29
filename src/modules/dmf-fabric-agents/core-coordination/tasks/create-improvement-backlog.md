# Task: Create Improvement Backlog

**Command:** `*backlog` / `*IB`  
**Output:** `improvement-backlog.md`

---

## Objective

Create and maintain a prioritized backlog of improvement opportunities based on feedback, metrics, and observations from the pipeline execution.

---

## Prerequisites

- [ ] Pipeline has been executed at least once
- [ ] Metrics collected
- [ ] Feedback gathered
- [ ] Error logs available

---

## Steps

### Step 1: Collect Issues

Gather issues from all sources:

| Source | How to Collect |
|--------|----------------|
| Agent logs | Review error and warning logs |
| Gate failures | Analyze why gates failed |
| Human feedback | Survey team members |
| Metrics | Identify metrics below target |
| Handoffs | Note transition friction |

### Step 2: Categorize Issues

Group issues by type:

```yaml
categories:
  - name: "Technical"
    examples: ["Bug", "Performance", "Integration"]
    
  - name: "Process"
    examples: ["Workflow", "Handoff", "Documentation"]
    
  - name: "People"
    examples: ["Training", "Communication", "Skills"]
    
  - name: "Tools"
    examples: ["Infrastructure", "Automation", "Monitoring"]
```

### Step 3: Analyze Root Causes

For each issue, apply 5 Whys:

```markdown
**Issue:** [Description]

**5 Whys Analysis:**
1. Why? → [First level answer]
2. Why? → [Second level answer]
3. Why? → [Third level answer]
4. Why? → [Fourth level answer]
5. Why? → [Root cause]

**Root Cause:** [Summary]
```

### Step 4: Prioritize

Use RICE scoring:

| Issue | Reach | Impact | Confidence | Effort | RICE Score |
|-------|-------|--------|------------|--------|------------|
| Issue 1 | 8 | 3 | 80% | 2 | 9.6 |
| Issue 2 | 5 | 2 | 90% | 1 | 9.0 |

### Step 5: Create Action Items

For each prioritized issue:

```yaml
action_item:
  id: "IMP-001"
  issue: "{issue description}"
  action: "{specific action}"
  owner: "{agent or person}"
  deadline: "{date}"
  success_criteria: "{how we know it's done}"
  effort: "{estimate}"
  dependencies: ["{dependencies}"]
```

### Step 6: Document Backlog

Create improvement-backlog.md with:
- Summary of issues
- Categorized list
- Priority matrix
- Action items
- Timeline

---

## Output Template

```markdown
# Improvement Backlog

## Summary
| Total Issues | Critical | High | Medium | Low |
|--------------|----------|------|--------|-----|
| {count} | {count} | {count} | {count} | {count} |

## Issues by Category

### Technical
| ID | Issue | Root Cause | Priority | Owner |
|----|-------|------------|----------|-------|
| IMP-001 | {issue} | {cause} | High | {owner} |

### Process
[Similar table]

### People
[Similar table]

### Tools
[Similar table]

## Priority Matrix
[Impact vs Effort visualization]

## Action Items

### High Priority
[Action items with deadlines]

### Quick Wins
[Low effort, high impact items]

## Timeline
[Gantt or timeline view]
```

---

## Validation

- [ ] All issues documented
- [ ] Root causes identified
- [ ] Priorities assigned
- [ ] Owners assigned
- [ ] Deadlines set
- [ ] Dependencies mapped
