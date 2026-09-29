---
task: execute-checklist
version: 1.0
elicit: true
description: Execute a specified checklist with interactive validation
---

# Execute Checklist

## Purpose
Run through a specified checklist interactively, validating each item and tracking completion status.

## Process

### Step 1: Identify Checklist
ASK the user which checklist to execute:
1. `bi-developer-checklist` - General BI development checklist
2. `dashboard-review-checklist` - Dashboard design review
3. `performance-checklist` - Performance optimization checklist

### Step 2: Execute Checklist
FOR each item in the checklist:
1. Present the item to the user
2. ASK if it passes, fails, or is not applicable
3. CAPTURE any notes or evidence
4. TRACK overall progress

### Step 3: Generate Report
PRODUCE a completion report showing:
- Items passed
- Items failed (with notes)
- Items not applicable
- Overall compliance percentage

## Execution Format

```markdown
## Checklist: {Name}
Started: {DateTime}

### Item 1: {Description}
Status: [ ] Pass [ ] Fail [ ] N/A
Notes: 

### Item 2: {Description}
Status: [ ] Pass [ ] Fail [ ] N/A
Notes:

---

## Summary
- Total Items: X
- Passed: X (X%)
- Failed: X (X%)
- N/A: X

## Failed Items Requiring Action
1. Item X - {Reason}
```
