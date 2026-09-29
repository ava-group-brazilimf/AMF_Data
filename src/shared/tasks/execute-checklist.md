---
task: execute-checklist
version: 2.0
elicit: true
description: Execute delivery checklists for quality assurance and compliance
---

# Execute Checklist

## Purpose
Run through delivery checklists to ensure quality, compliance, and completeness at key project milestones.

## Available Checklists

| Checklist | Items | Use Case |
|-----------|-------|----------|
| Delivery Lead Checklist | 85 | Comprehensive project delivery |
| Project Kickoff Checklist | 50 | Project initiation |
| Change Checklist | 50 | Change request processing |

## Process

### Step 1: Select Checklist
ASK the user which checklist to execute:

```
📋 SELECT CHECKLIST TO EXECUTE

1. 📊 Delivery Lead Checklist (85 items)
   Comprehensive project delivery assurance
   
2. 🚀 Project Kickoff Checklist (50 items)
   Project initiation and setup
   
3. 🔄 Change Checklist (50 items)
   Change request processing

Enter a number (1-3):
```

### Step 2: Execute Checklist
FOR each section:

1. Present checklist items
2. Ask user for status (Complete/Partial/Not Started/N/A)
3. Capture notes for partial/incomplete items
4. Calculate section completion percentage

### Step 3: Generate Report
CREATE completion report:

```
📊 CHECKLIST COMPLETION REPORT

Checklist: [Name]
Date: [Date]
Project: [Project]

Overall Completion: XX%

Section Breakdown:
├── Section 1: XX% (Y of Z items)
├── Section 2: XX% (Y of Z items)
└── Section 3: XX% (Y of Z items)

Items Requiring Attention:
- [ ] Item 1 - Notes
- [ ] Item 2 - Notes

Recommendations:
1. Action 1
2. Action 2
```

## Output Format

SAVE to: `projects/{project_name}/outputs/summary/delivery/checklist_{type}_{project}_{timestamp}.md`

## Indicative Impact

| Traditional | AI-Assisted | Improvement |
|-------------|-------------|-------------|
| 2-3 hours manual review | 15 minutes | 90% faster |
| Inconsistent execution | Standardized | Better quality |
| Paper-based tracking | Digital records | Better traceability |
