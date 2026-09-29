---
task: create-report
version: 1.0
elicit: true
description: Design paginated or interactive reports for detailed data presentation
---

# Create Report

## Purpose
Design detailed reports (paginated or interactive) for scenarios requiring precise formatting, printing, or detailed data exploration.

## Process

### Step 1: Gather Requirements
ASK the user for the following information:

1. **Report Type**: Paginated (for print/export) or Interactive?
2. **Purpose**: What business process does this report support?
3. **Distribution**: How will it be shared? (Email, portal, print)
4. **Frequency**: Daily, weekly, monthly, on-demand?
5. **Parameters**: What filters should users be able to select?
6. **Data Volume**: Approximate rows expected?
7. **Format Requirements**: Specific layout needs? (Legal paper, landscape, etc.)

### Step 2: Design Report Structure

**For Paginated Reports:**
- Header with logo, title, parameters
- Body with grouped data sections
- Footer with page numbers, timestamps
- Sub-reports for drill-down

**For Interactive Reports:**
- Navigation tabs/pages
- Filter panel design
- Drill-through structure
- Export options

### Step 3: Generate Specification

PRODUCE the following:

1. **Report Layout**
   - Page/canvas size
   - Section breakdown
   - Header/footer content
   - Grouping levels

2. **Parameter Design**
   - Parameter name and type
   - Default values
   - Cascading dependencies
   - Multi-select options

3. **Data Display**
   - Table/matrix structure
   - Conditional formatting
   - Totals and subtotals
   - Sorting requirements

4. **Export Configuration**
   - Supported formats (PDF, Excel, Word)
   - Rendering options

## Output Structure

```
report/
├── specs/
│   ├── report-layout.md
│   ├── parameter-design.md
│   └── data-mapping.md
├── rdl/ (for paginated)
│   └── report-definition.rdl
├── docs/
│   ├── user-guide.md
│   └── distribution-schedule.md
└── README.md
```

## Quality Criteria

- [ ] Clear purpose defined
- [ ] Appropriate report type selected
- [ ] Parameters provide meaningful filtering
- [ ] Layout optimized for consumption method
- [ ] Export formats tested
- [ ] Performance acceptable for data volume
