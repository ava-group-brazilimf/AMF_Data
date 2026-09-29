---
task: setup-output-structure
version: 1.0
elicit: false
description: Initialize the bi-outputs folder structure for organized artifact storage
---

# Setup Output Structure

## Purpose
Ensure the bi-outputs folder structure exists and is properly organized before any artifact generation.

## When to Run
- On agent activation (automatically)
- Before running `*demo`
- Before any command that generates outputs
- When user requests `*setup-outputs`

## Required Folder Structure

CREATE the following structure in `projects/{project_name}/outputs/downstream/bi/`:

```
projects/{project_name}/outputs/downstream/bi/
├── README.md                  # Explains the structure
├── semantic-models/           # Data model definitions
│   └── .gitkeep
├── dax-measures/              # DAX measure libraries
│   └── .gitkeep
├── dashboards/                # Dashboard specs and HTML previews
│   └── .gitkeep
├── reports/                   # Report specifications
│   └── .gitkeep
├── documentation/             # Requirements and technical docs
│   └── .gitkeep
├── security/                  # RLS configurations
│   └── .gitkeep
├── optimization/              # Performance analysis reports
│   └── .gitkeep
└── validation/                # Checklist results
    └── .gitkeep
```

## Folder Descriptions

| Folder | Purpose | File Types |
|--------|---------|------------|
| `semantic-models/` | Star schema designs, table definitions, relationships | `.md`, `.tmdl`, `.yaml` |
| `dax-measures/` | DAX measure libraries, calculations, KPIs | `.dax`, `.md` |
| `dashboards/` | Dashboard wireframes, specs, HTML previews | `.md`, `.html`, `.yaml` |
| `reports/` | Paginated and interactive report specs | `.md`, `.yaml` |
| `documentation/` | Requirements, technical docs, guides | `.md` |
| `security/` | Row-Level Security configs, role definitions | `.md`, `.yaml` |
| `optimization/` | Performance analysis, tuning recommendations | `.md` |
| `validation/` | Checklist results, quality reports | `.md` |

## File Naming Convention

All generated files MUST follow this pattern:

```
{type}_{name}_{YYYY-MM-DD_HHmm}.{ext}
```

**Examples:**
- `semantic-model_sales-analytics_2026-01-22_1430.md`
- `dax-measures_financial-kpis_2026-01-22_1445.dax`
- `dashboard-preview_sales_2026-01-22_1500.html`
- `checklist_performance_2026-01-22_1515.md`

## Verification Process

BEFORE generating any output:

1. CHECK if `projects/{project_name}/outputs/downstream/bi/` folder exists
2. CHECK if all 8 subfolders exist
3. CREATE any missing folders
4. CONFIRM structure is ready

## Implementation Commands

### PowerShell (Windows)
```powershell
$basePath = "bi-developer-agent/bi-outputs"
$folders = @(
    "semantic-models",
    "dax-measures", 
    "dashboards",
    "reports",
    "documentation",
    "security",
    "optimization",
    "validation"
)

# Create base folder if not exists
if (-not (Test-Path $basePath)) {
    New-Item -Path $basePath -ItemType Directory -Force
}

# Create subfolders with .gitkeep
foreach ($folder in $folders) {
    $folderPath = Join-Path $basePath $folder
    if (-not (Test-Path $folderPath)) {
        New-Item -Path $folderPath -ItemType Directory -Force
        New-Item -Path (Join-Path $folderPath ".gitkeep") -ItemType File -Force
    }
}
```

### Bash (Linux/Mac)
```bash
BASE_PATH="bi-developer-agent/bi-outputs"
FOLDERS=(
    "semantic-models"
    "dax-measures"
    "dashboards"
    "reports"
    "documentation"
    "security"
    "optimization"
    "validation"
)

mkdir -p "$BASE_PATH"

for folder in "${FOLDERS[@]}"; do
    mkdir -p "$BASE_PATH/$folder"
    touch "$BASE_PATH/$folder/.gitkeep"
done
```

## Success Confirmation

AFTER setup, display:

```
✅ Output structure verified!

📁 projects/{project_name}/outputs/downstream/bi/
   ├── semantic-models/    Ready
   ├── dax-measures/       Ready
   ├── dashboards/         Ready
   ├── reports/            Ready
   ├── documentation/      Ready
   ├── security/           Ready
   ├── optimization/       Ready
   └── validation/         Ready

All outputs will be saved with timestamp: {YYYY-MM-DD_HHmm}
```

## Quality Criteria

- [ ] All 8 subfolders exist
- [ ] Each subfolder has .gitkeep
- [ ] README.md exists in projects/{project_name}/outputs/downstream/bi/
- [ ] No orphan files in root of projects/{project_name}/outputs/downstream/bi/
