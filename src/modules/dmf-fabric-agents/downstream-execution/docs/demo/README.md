# 🎮 InsightForge Demo - Interactive Capabilities Showcase

This folder contains demo scenarios and sample data that showcase the InsightForge BI Developer Agent capabilities.

## Quick Start

1. Activate the agent: `@bi-developer`
2. Run: `*demo`
3. Select a scenario (1-5)
4. Watch outputs generated in real-time
5. Choose to generate HTML dashboard at the end

---

## 📁 What's in This Folder

```
demo/
├── README.md              ← This file
└── sample-data/           ← Sample CSV files for demo
    ├── sales-transactions.csv
    ├── customers.csv
    ├── products.csv
    └── budget.csv
```

## 📊 Where Outputs Go

Run the demo only after the wave has been initialized with an explicit
`wave_config_path`. Outputs are saved below the active project:

```
projects/{project_name}/outputs/downstream/bi/
├── documentation/     ← Requirements documents
├── semantic-models/   ← Star schema definitions
├── dax-measures/      ← DAX measure libraries (.dax, .md)
├── dashboards/        ← Dashboard specs + HTML previews
├── reports/           ← Report specifications
├── security/          ← RLS configurations
├── optimization/      ← Performance analysis
└── validation/        ← Checklist results
```

**Note:** The `bi/` folder starts empty. Files are generated during demo interaction.

---

## Demo Scenarios

### 📊 Scenario 1: Sales Analytics Dashboard

**Business Context:**
Create a complete sales analytics solution for Contoso Retail.

**What Gets Generated:**
- Requirements document with personas (Executive, Regional Manager, Sales Rep)
- Star schema with FACT_Sales and dimensions (Date, Customer, Product, Geography)
- DAX measures library (50+ measures including time intelligence)
- Dashboard layout specification
- Interactive HTML dashboard preview

**Sample Data Used:** `sales-transactions.csv`, `customers.csv`, `products.csv`

---

### 📈 Scenario 2: Financial KPI Scorecard

**Business Context:**
Build an executive financial dashboard with budget variance analysis.

**What Gets Generated:**
- Financial requirements document
- Financial semantic model
- Financial DAX measures (Actuals vs Budget, Variance %, Running Totals)
- KPI Scorecard specification
- HTML dashboard with KPI cards

**Sample Data Used:** `budget.csv`

---

### ⚡ Scenario 3: Performance Optimization

**Business Context:**
Demonstrate dataset performance tuning techniques.

**What Gets Generated:**
- Performance analysis report
- Optimization recommendations
- Before/after comparisons
- Performance checklist results

---

### 🔐 Scenario 4: Row-Level Security

**Business Context:**
Implement data security for multi-tenant access.

**What Gets Generated:**
- Security requirements
- RLS role definitions
- DAX filter expressions
- Testing documentation

---

### 🎯 Scenario 5: Custom Demo

**You choose:**
- Describe your own business scenario
- Agent adapts to your requirements
- Same output structure applies

---

## 🌐 HTML Dashboard Generation

At the end of any demo, you'll be asked:

```
Would you like to generate an interactive dashboard preview?

1. 🌐 Yes - Generate HTML Dashboard Preview
2. 📄 No - Keep markdown/specification outputs only
3. 📦 Generate All - Create both specs and HTML preview
```

If you select **Yes** or **Generate All**, an HTML file is created at:
`projects/{project_name}/outputs/downstream/bi/dashboards/dashboard-preview_{timestamp}.html`

The HTML dashboard includes:
- ✓ Interactive Chart.js visualizations
- ✓ KPI cards with trend indicators
- ✓ Filter dropdowns (visual demonstration)
- ✓ Responsive design for mobile
- ✓ Professional Power BI-like styling
- ✓ InsightForge branding

**To view:** Right-click the HTML file → Open with browser

---

## Sample Data Details

### sales-transactions.csv (20 rows)
| Field | Description |
|-------|-------------|
| OrderDate | Transaction date |
| Region | Sales region (West, East, Central, South) |
| ProductCategory | Product category |
| ProductName | Product name |
| Quantity | Units sold |
| UnitPrice | Price per unit |
| CustomerSegment | Customer type (Enterprise, Consumer, SMB) |

### customers.csv (10 rows)
| Field | Description |
|-------|-------------|
| CustomerID | Unique identifier |
| CustomerName | Company/customer name |
| Segment | Customer segment |
| Region | Geographic region |
| JoinDate | Customer since date |

### products.csv (15 rows)
| Field | Description |
|-------|-------------|
| ProductID | Unique identifier |
| ProductName | Product name |
| Category | Product category |
| UnitCost | Cost per unit |
| UnitPrice | Selling price |

### budget.csv (24 rows)
| Field | Description |
|-------|-------------|
| Year | Fiscal year |
| Month | Month number |
| Department | Department name |
| BudgetAmount | Planned budget |
| ActualAmount | Actual spend |

---

## 💡 Tips

- Run `*demo` for guided experience
- Use `*generate-html` anytime to create HTML dashboards
- All outputs are timestamped for version tracking
- Compare different scenarios to see the agent's versatility
- Use the sample data with individual commands like `*create-semantic-model`
