---
task: create-dashboard
version: 1.0
elicit: true
description: Design and specify a Power BI dashboard layout with visual hierarchy, interactivity, and user experience focus
---

# Create Dashboard

## Purpose
Design a comprehensive dashboard specification that transforms data into actionable insights through effective visual storytelling aligned with user personas and business goals.

## Process

### Step 1: Gather Requirements
ASK the user for the following information:

1. **Dashboard Purpose**: What decisions will this dashboard support?
2. **Target Audience**: Who will use this? (Executive, Manager, Analyst, Operations)
3. **Key Questions**: What top 5 questions must this dashboard answer?
4. **KPIs**: What are the critical metrics to display?
5. **Comparison Context**: What comparisons matter? (vs last year, vs target, vs budget)
6. **Drill-down Needs**: What details do users need to explore?
7. **Refresh Frequency**: How often will data update?
8. **Access Method**: Desktop, mobile, embedded, both?

### Step 2: Design Visual Hierarchy

CREATE a layout covering:

**Executive Summary Section (Top)**
- KPI cards with trend indicators
- High-level status indicators
- Critical alerts/exceptions

**Analysis Section (Middle)**
- Trend visualizations
- Comparison charts
- Geographic/categorical breakdowns

**Detail Section (Bottom)**
- Detailed tables
- Drill-through targets
- Supporting information

### Step 3: Select Visualizations

MATCH data types to appropriate visuals:

| Data Type | Recommended Visual |
|-----------|-------------------|
| KPI value + trend | Card with sparkline |
| Time series | Line chart / Area chart |
| Part-to-whole | Donut chart / Treemap |
| Comparison | Bar chart (horizontal) |
| Ranking | Bar chart (sorted) |
| Geographic | Map / Filled map |
| Correlation | Scatter plot |
| Distribution | Histogram |
| Detailed data | Matrix / Table |

### Step 4: Generate Specification

PRODUCE the following deliverables:

1. **Dashboard Layout** (Wireframe specification)
   ```
   +------------------+------------------+------------------+
   |    KPI Card 1    |    KPI Card 2    |    KPI Card 3    |
   |    Revenue       |    Units Sold    |    Margin %      |
   +------------------+------------------+------------------+
   |                                     |                  |
   |    Sales Trend Line Chart           |   Top Products   |
   |    (12 months with YoY comparison)  |   Bar Chart      |
   |                                     |                  |
   +-------------------------------------+------------------+
   |                  Sales by Region Map                   |
   +--------------------------------------------------------+
   |              Detailed Sales Table (Drill-through)      |
   +--------------------------------------------------------+
   ```

2. **Visual Specifications**
   - Chart type and configuration
   - Fields to use
   - Formatting requirements
   - Conditional formatting rules
   - Tooltip customization

3. **Interactivity Design**
   - Slicer configurations
   - Cross-filter behavior
   - Drill-through pages
   - Bookmarks for scenarios

4. **Theme & Branding**
   - Color palette
   - Font specifications
   - Logo placement
   - Consistent spacing

### Step 5: Document Dashboard

CREATE documentation including:
- User guide
- Navigation instructions
- Data refresh schedule
- Known limitations

## Output Structure

```
dashboard/
├── specs/
│   ├── layout-wireframe.md
│   ├── visual-specs.md
│   ├── interactivity-design.md
│   └── theme-config.json
├── assets/
│   ├── color-palette.md
│   └── icons/
├── docs/
│   ├── user-guide.md
│   └── design-rationale.md
└── README.md
```

## Visual Design Principles

1. **Z-Pattern Reading**: Place most important content top-left to bottom-right
2. **F-Pattern Scanning**: Key info on left, details on right
3. **Progressive Disclosure**: Summary → Analysis → Detail
4. **Color Intentionally**: Use color for meaning, not decoration
5. **White Space**: Don't overcrowd; give visuals room to breathe
6. **Consistent Alignment**: Grid-based layout
7. **Mobile Consideration**: Design responsive layouts

## Quality Criteria

- [ ] Clear visual hierarchy established
- [ ] All KPIs have context (trend, comparison)
- [ ] Consistent color usage
- [ ] Appropriate chart types selected
- [ ] Interactivity enhances (not complicates) experience
- [ ] Mobile layout considered
- [ ] Accessibility requirements met
- [ ] Performance optimized (limited visuals per page)
