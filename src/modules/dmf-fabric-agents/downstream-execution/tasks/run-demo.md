---
task: run-demo
version: 1.0
elicit: true
description: Interactive demonstration of InsightForge BI Developer Agent capabilities with output generation
---

# Run Demo - InsightForge Agent

## Purpose
Showcase the full capabilities of the InsightForge BI Developer Agent through an interactive demonstration that generates real outputs.

## Pre-requisite: Verify Output Structure

BEFORE starting demo, ALWAYS verify/create the bi-outputs folder structure:

```
projects/{project_name}/outputs/downstream/bi/
├── semantic-models/     # .gitkeep
├── dax-measures/        # .gitkeep
├── dashboards/          # .gitkeep
├── reports/             # .gitkeep
├── documentation/       # .gitkeep
├── security/            # .gitkeep
├── optimization/        # .gitkeep
└── validation/          # .gitkeep
```

IF any folder is missing, CREATE it silently before proceeding.

## Demo Flow

### Step 1: Welcome & Scenario Selection
PRESENT the following options to the user:

```
🎮 INSIGHTFORGE DEMO - SELECT A SCENARIO

1. 📊 Sales Analytics Dashboard
   Complete sales solution with KPIs, trends, and regional analysis
   
2. 📈 Financial KPI Scorecard  
   Executive financial dashboard with budget variance
   
3. ⚡ Performance Optimization
   Demonstrate dataset tuning and optimization
   
4. 🔐 Security Implementation
   Row-Level Security design and testing
   
5. 🎯 Custom Demo
   Describe your own scenario

Enter a number (1-5):
```

### Step 2: Execute Selected Demo

FOR each demo scenario, generate ALL outputs progressively:

**Phase 1: Requirements (save to projects/{project_name}/outputs/downstream/bi/documentation/)**
- Generate requirements document
- Create user personas
- Define success criteria

**Phase 2: Semantic Model (save to projects/{project_name}/outputs/downstream/bi/semantic-models/)**
- Star schema design
- Table definitions
- Relationship specifications
- Hierarchy definitions

**Phase 3: DAX Measures (save to projects/{project_name}/outputs/downstream/bi/dax-measures/)**
- Base aggregations
- Time intelligence
- KPIs and comparisons
- Complete measure library

**Phase 4: Dashboard Specification (save to projects/{project_name}/outputs/downstream/bi/dashboards/)**
- Layout wireframe
- Visual specifications
- Interactivity design
- Mobile layout

**Phase 5: Validation (save to projects/{project_name}/outputs/downstream/bi/validation/)**
- Quality checklist results
- Model validation report

### Step 3: Final Output Generation

AT THE END of the demo, ALWAYS ask:

```
✅ DEMO COMPLETE!

All outputs have been saved to: projects/{project_name}/outputs/downstream/bi/

Would you like to generate an interactive dashboard preview?

1. 🌐 Yes - Generate HTML Dashboard Preview
   Creates a fully interactive dashboard you can open in browser
   
2. 📄 No - Keep markdown/specification outputs only

3. 📦 Generate All - Create both specs and HTML preview

Enter your choice (1-3):
```

### Step 4: HTML Dashboard Generation

IF user selects option 1 or 3, GENERATE the HTML dashboard:

**File**: `projects/{project_name}/outputs/downstream/bi/dashboards/dashboard-preview_{timestamp}.html`

The HTML dashboard MUST include:
- Interactive charts (using Chart.js)
- KPI cards with conditional formatting
- Filter dropdowns (non-functional demo)
- Responsive design
- Professional styling
- Footer crediting InsightForge Agent

USE this template structure for the HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Dashboard Name} - InsightForge Demo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Professional Power BI-like styling */
        :root {
            --primary: #0078D4;
            --positive: #107C10;
            --negative: #D13438;
            --background: #F3F2F1;
        }
        /* ... full styling ... */
    </style>
</head>
<body>
    <!-- Header with title and filters -->
    <!-- KPI Cards row -->
    <!-- Charts section -->
    <!-- Data table -->
    <!-- Footer with InsightForge branding -->
    <script>
        // Chart.js implementations
    </script>
</body>
</html>
```

### Step 5: Summary & Next Steps

DISPLAY summary of all generated files:

```
📁 GENERATED OUTPUTS

projects/{project_name}/outputs/downstream/bi/
├── documentation/
│   └── requirements_{scenario}_{timestamp}.md
├── semantic-models/
│   └── model_{scenario}_{timestamp}.md
├── dax-measures/
│   └── measures_{scenario}_{timestamp}.dax
├── dashboards/
│   ├── spec_{scenario}_{timestamp}.md
│   └── dashboard-preview_{timestamp}.html  ← Open in browser!
└── validation/
    └── checklist_{scenario}_{timestamp}.md

🚀 NEXT STEPS:
1. Open the HTML dashboard in your browser
2. Review the semantic model specification
3. Copy DAX measures to Power BI Desktop
4. Use specs as requirements for development

Need help with anything else? Try:
- *create-semantic-model for a custom model
- *create-dax for specific measures
- *optimize-dataset for performance tuning
```

## Output File Templates

### Requirements Output Template
```markdown
# BI Requirements: {Scenario Name}
Generated: {Timestamp}
Agent: InsightForge v1.0

## Executive Summary
{Generated content}

## User Personas
{Generated personas}

## Functional Requirements
{Generated requirements table}
```

### Semantic Model Output Template
```markdown
# Semantic Model: {Scenario Name}
Generated: {Timestamp}

## Model Diagram
{ASCII diagram}

## Table Definitions
{Generated tables}

## Relationships
{Generated relationships}
```

### DAX Output Template
```dax
// =====================================================
// DAX Measure Library: {Scenario Name}
// Generated: {Timestamp}
// Agent: InsightForge BI Developer v1.0
// =====================================================

// --- BASE MEASURES ---
{Generated measures}

// --- TIME INTELLIGENCE ---
{Generated measures}

// --- KPIS ---
{Generated measures}
```

## Quality Criteria

- [ ] All 5 phases completed
- [ ] Outputs saved to correct folders
- [ ] Files named with timestamps
- [ ] HTML dashboard is valid and renders correctly
- [ ] User offered choice for HTML generation
- [ ] Summary displayed at end
