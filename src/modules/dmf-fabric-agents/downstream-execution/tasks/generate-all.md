# 📚 Task: Generate All Documentation

## Command
`*generate-all`

## Objective
Master task that orchestrates all documentation generation in sequence. Produces a comprehensive documentation package covering every aspect of the migration project. This is the recommended way to generate all documentation at once.

---

## Prerequisites

- All upstream agents have completed their execution
- All artifacts are available and valid
- Output directories exist and are writable

---

## Execution Sequence

```
┌─────────────────────────────────────────────────────┐
│            📚 Generate All — Execution Flow          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Step 1: Artifact Validation                        │
│    └── Scan all upstream agent outputs              │
│    └── Validate artifact integrity                  │
│    └── Generate artifact manifest                   │
│                                                     │
│  Step 2: *generate-report                           │
│    └── Executive Summary                            │
│    └── Technical Report                             │
│    └── Per-Wave Status                              │
│                                                     │
│  Step 3: *generate-lineage                          │
│    └── Per-Domain Diagrams                          │
│    └── Master Overview                              │
│    └── Cross-Domain Relationships                   │
│                                                     │
│  Step 4: *generate-runbook                          │
│    └── Monitoring Runbook                           │
│    └── Incident Response                            │
│    └── Troubleshooting Guide                        │
│    └── Maintenance Procedures                       │
│                                                     │
│  Step 5: *generate-changelog                        │
│    └── Git History Analysis                         │
│    └── Changelog Generation                         │
│    └── Summary Statistics                           │
│                                                     │
│  Step 6: Package Assembly                           │
│    └── Generate master index                        │
│    └── Cross-reference all documents                │
│    └── Generate documentation statistics            │
│    └── Create documentation package                 │
│                                                     │
│  Step 7: Publishing                                 │
│    └── Publish to Confluence                        │
│    └── Upload to SharePoint                         │
│    └── Commit to Git                                │
│    └── Export to PDF                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Steps

### 1. Pre-Flight Validation
- Verify all upstream agent output directories exist
- Validate all required artifacts are present
- Check artifact freshness (warn if older than 24 hours)
- Generate artifact manifest with checksums
- Abort if critical artifacts are missing (with detailed error report)

### 2. Execute Generation Tasks
Execute in strict sequence (each step depends on the previous):

1. **`*generate-report`** — Migration report (executive + technical)
2. **`*generate-lineage`** — Data lineage diagrams
3. **`*generate-runbook`** — Operational runbooks
4. **`*generate-changelog`** — Changelog

### 3. Package Assembly
- Generate `documentation-index.md` — master index linking all documents
- Cross-reference documents (e.g., report links to lineage diagrams)
- Generate documentation statistics:
  - Total pages generated
  - Total diagrams generated
  - Total runbooks generated
  - Total time to generate
- Create ZIP package of all documentation

### 4. Quality Review
- Verify all expected output files exist
- Check for broken internal links
- Validate all Mermaid diagrams render
- Ensure no placeholder text remains
- Verify both language versions are present

### 5. Publishing
- Publish to all configured targets:
  - **Confluence**: Create/update space with all documentation
  - **SharePoint**: Upload package to document library
  - **Git**: Commit all documentation with descriptive message
  - **PDF**: Export final documents as PDF
- Log publishing results

---

## Output

All outputs from individual tasks, plus:

| File                                                      | Description                         |
|-----------------------------------------------------------|-------------------------------------|
| `projects/{project_name}/outputs/downstream/documentation/documentation-index.md`                  | Master index of all documentation   |
| `projects/{project_name}/outputs/downstream/documentation/documentation-statistics.json`           | Generation statistics               |
| `projects/{project_name}/outputs/downstream/documentation/documentation-package.zip`               | Complete documentation package      |
| `projects/{project_name}/outputs/downstream/documentation/generation-log.json`                     | Detailed generation execution log   |

---

## Quality Criteria

- [ ] All four generation tasks completed successfully
- [ ] Master index links to all generated documents
- [ ] All cross-references valid
- [ ] Documentation statistics generated
- [ ] Both PT-BR and EN-US versions complete
- [ ] Published to all configured targets
- [ ] Generation log records all steps and timings
- [ ] ZIP package contains all documentation
