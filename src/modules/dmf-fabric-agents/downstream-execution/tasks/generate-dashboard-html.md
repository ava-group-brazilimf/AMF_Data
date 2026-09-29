---
task: generate-dashboard-html
version: 1.0
elicit: false
description: Generate an interactive HTML dashboard preview from specifications
---

# Generate Dashboard HTML

## Purpose
Create a fully interactive HTML dashboard that can be opened in a browser, demonstrating the dashboard design with real visualizations.

## Process

### Step 1: Gather Dashboard Data

COLLECT the following from context or ask user:
- Dashboard title
- KPI values (4-6 KPIs)
- Trend data (12 months)
- Category breakdown data
- Regional/segment data
- Table data (top performers)

### Step 2: Generate HTML File

CREATE file at: `projects/{project_name}/outputs/downstream/bi/dashboards/dashboard-preview_{timestamp}.html`

### HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{DASHBOARD_TITLE} - InsightForge Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #0078D4;
            --positive-color: #107C10;
            --negative-color: #D13438;
            --warning-color: #FFB900;
            --neutral-color: #605E5C;
            --background-color: #F3F2F1;
            --card-background: #FFFFFF;
            --text-primary: #323130;
            --text-secondary: #605E5C;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--background-color);
            color: var(--text-primary);
            padding: 20px;
            min-height: 100vh;
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 25px;
            background: linear-gradient(135deg, var(--primary-color), #106EBE);
            color: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .dashboard-header h1 {
            font-size: 24px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .filters-bar {
            display: flex;
            gap: 15px;
            padding: 15px 20px;
            background: var(--card-background);
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            flex-wrap: wrap;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .filter-group label {
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
        }

        .filter-group select {
            padding: 8px 12px;
            border: 1px solid #E1DFDD;
            border-radius: 4px;
            font-size: 14px;
            min-width: 150px;
            cursor: pointer;
            background: white;
        }

        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .kpi-card {
            background: var(--card-background);
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid var(--primary-color);
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }

        .kpi-card .kpi-icon { font-size: 28px; margin-bottom: 12px; }
        .kpi-card .kpi-label {
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .kpi-card .kpi-value {
            font-size: 36px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        .kpi-card .kpi-change {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 14px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
        }
        .kpi-card .kpi-change.positive {
            color: var(--positive-color);
            background: rgba(16, 124, 16, 0.1);
        }
        .kpi-card .kpi-change.negative {
            color: var(--negative-color);
            background: rgba(209, 52, 56, 0.1);
        }

        .charts-row {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        @media (max-width: 1024px) {
            .charts-row { grid-template-columns: 1fr; }
        }

        .chart-card {
            background: var(--card-background);
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .chart-card h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .chart-container {
            position: relative;
            height: 300px;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
        }

        .data-table th {
            text-align: left;
            padding: 14px 12px;
            background: var(--background-color);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            font-weight: 600;
        }

        .data-table td {
            padding: 14px 12px;
            border-bottom: 1px solid #E1DFDD;
        }

        .data-table tr:hover { background: var(--background-color); }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-badge.success { background: #DFF6DD; color: var(--positive-color); }
        .status-badge.warning { background: #FFF4CE; color: #8A6914; }
        .status-badge.danger { background: #FDE7E9; color: var(--negative-color); }

        .footer {
            text-align: center;
            padding: 30px 20px;
            color: var(--text-secondary);
            font-size: 12px;
            margin-top: 20px;
        }

        .agent-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, var(--primary-color), #106EBE);
            color: white;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .kpi-card, .chart-card { animation: fadeIn 0.5s ease forwards; }
        .kpi-card:nth-child(1) { animation-delay: 0.1s; }
        .kpi-card:nth-child(2) { animation-delay: 0.2s; }
        .kpi-card:nth-child(3) { animation-delay: 0.3s; }
        .kpi-card:nth-child(4) { animation-delay: 0.4s; }
    </style>
</head>
<body>
    <header class="dashboard-header">
        <div>
            <h1>📊 {DASHBOARD_TITLE}</h1>
            <p style="opacity: 0.9; font-size: 14px;">{SUBTITLE}</p>
        </div>
        <div style="text-align: right; font-size: 12px; opacity: 0.8;">
            <div>Generated: {TIMESTAMP}</div>
            <div>Data Refresh: {REFRESH_SCHEDULE}</div>
        </div>
    </header>

    <div class="filters-bar">
        <div class="filter-group">
            <label>Date Range</label>
            <select><option>Year to Date</option><option>Last 12 Months</option><option>This Quarter</option></select>
        </div>
        <div class="filter-group">
            <label>Region</label>
            <select><option>All Regions</option><option>West</option><option>East</option><option>Central</option><option>South</option></select>
        </div>
        <div class="filter-group">
            <label>Category</label>
            <select><option>All Categories</option>{CATEGORY_OPTIONS}</select>
        </div>
    </div>

    <div class="kpi-container">
        <!-- KPI Cards dynamically inserted -->
    </div>

    <div class="charts-row">
        <div class="chart-card">
            <h3>📈 {TREND_CHART_TITLE}</h3>
            <div class="chart-container"><canvas id="trendChart"></canvas></div>
        </div>
        <div class="chart-card">
            <h3>🏆 {BAR_CHART_TITLE}</h3>
            <div class="chart-container"><canvas id="barChart"></canvas></div>
        </div>
    </div>

    <div class="charts-row">
        <div class="chart-card">
            <h3>📊 {PIE_CHART_TITLE}</h3>
            <div class="chart-container"><canvas id="pieChart"></canvas></div>
        </div>
        <div class="chart-card">
            <h3>📋 {TABLE_TITLE}</h3>
            <table class="data-table">
                <thead><tr>{TABLE_HEADERS}</tr></thead>
                <tbody>{TABLE_ROWS}</tbody>
            </table>
        </div>
    </div>

    <footer class="footer">
        <p>This dashboard was automatically generated by InsightForge BI Developer Agent</p>
        <div class="agent-badge">📊 InsightForge Agent v1.0</div>
        <p style="margin-top: 15px;">© {YEAR} | Generated on {FULL_TIMESTAMP}</p>
    </footer>

    <script>
        // Chart configurations injected based on data
        {CHART_SCRIPTS}
    </script>
</body>
</html>
```

### Step 3: Notify User

AFTER generating the HTML file:

```
✅ Dashboard HTML Generated!

📁 File: projects/{project_name}/outputs/downstream/bi/dashboards/dashboard-preview_{timestamp}.html

🌐 To view:
   - Right-click the file → "Open with Live Server"
   - Or open directly in your web browser
   - Or use VS Code's "Open in Default Browser" option

The dashboard includes:
   ✓ Interactive Chart.js visualizations
   ✓ KPI cards with trend indicators
   ✓ Filter dropdowns (visual only)
   ✓ Responsive design
   ✓ Professional Power BI-like styling
```

## Quality Criteria

- [ ] HTML is valid and well-formatted
- [ ] Chart.js CDN loads correctly
- [ ] All charts render properly
- [ ] Responsive on mobile
- [ ] InsightForge branding included
- [ ] Timestamp in filename
