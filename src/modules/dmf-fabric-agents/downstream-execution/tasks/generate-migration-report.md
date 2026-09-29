# 📚 Task: Generate Migration Report

## Command
`*generate-report`

## Objective
Aggregate all artifacts produced by all agents in the AI-Agent Migration Factory and generate a comprehensive migration report. The report includes an executive summary (for sponsors and stakeholders) and a detailed technical report (for engineers and architects).

---

## Prerequisites

- All upstream agents have completed their execution
- Artifacts available:
  - `migration-coordinator → execution-log.json, wave-status-report.md`
  - `discovery-scout → inventory.json, dependency-graph.json`
  - `logic-extractor → digital-twin.json, pseudocode/*.json`
  - `code-generator → generated-code/*.py`
  - `quality-gate → validation-report/*.json`
  - `security-compliance → compliance-report/*.json, audit-trail.log`
  - `self-healing → healing-log/*.json`
  - `reconciliation → reconciliation-report.json`

---

## Steps

### 1. Artifact Collection
- Scan all agent output directories for artifacts
- Validate artifact integrity (JSON schema validation, file existence)
- Log missing or corrupted artifacts
- Create artifact manifest with checksums

### 2. Executive Summary Generation
- Extract key metrics: total tables migrated, success rate, duration, data volume
- Summarize per-wave results with status indicators (✅ ❌ ⚠️)
- Highlight critical findings and risks
- Generate recommendation section
- Target audience: C-level sponsors, project managers

### 3. Technical Report Generation
- Detailed per-pipeline analysis with transformation logic
- Data quality metrics per table (row counts, null rates, type mismatches)
- Performance metrics (throughput, latency, resource utilization)
- Error analysis with root cause categorization
- Code generation statistics
- Security and compliance summary

### 4. Visualization Embedding
- Generate summary charts (progress bars, pie charts via Mermaid)
- Embed data quality heatmaps
- Include architecture overview diagram
- Add wave timeline Gantt chart
- Populate template sections `3.1`, `3.3`, and references for visuals in the final report
- Render complete Mermaid blocks before insertion:
  - `{{timeline_mermaid_chart}}` must contain a fully valid fenced Mermaid Gantt block
  - `{{wave_outcome_pie_chart}}` must contain a fully valid fenced Mermaid pie block

### 5. Assembly and Formatting
- Merge sections using `migration-report-tmpl.md` template
- Generate table of contents
- Add metadata header (generation date, agent version, artifact sources)
- Format in Markdown with proper heading hierarchy
- Generate PT-BR version first, then EN-US
- Produce the 3 outputs from the same source assembly:
  - Full: all sections
  - Executive extract: sections `1`, `3.2`, `4` (status summary only), `7.1`, `8`, `Final Recommendation`
  - Technical extract: sections `2`, `3`, `4`, `5`, `6`, `7`, `9`

### 5.1 Deterministic Extraction Rules
- Preserve original section order from the full report in all extracts
- When extracting section `4` for executive output, keep only:
  - Wave status overview bullets
  - Wave summary paragraph
  - Wave recommendation
  - Exclude per-table detail table in executive output
- Keep `Final Recommendation` as a standalone mandatory block in executive output
- Keep all subsection headings to preserve anchors and cross-reference integrity

### 5.2 Executive Length Control
- Target executive output: maximum 5 pages equivalent
- If content exceeds target, compress in this order:
  - Shorten wave observations and findings to one bullet per wave
  - Keep only top 3 business risks in section `7.1`
  - Keep only immediate and short-term recommendations in section `8`
- Never remove: section `1`, section `3.2`, section `Final Recommendation`

### 5.3 Data Availability Fallback
- If a metric is unavailable, replace placeholder with `N/A (not provided)`
- Record every missing metric in validation summary under open items
- Do not leave unresolved placeholders in any output

### 6. Final Validation Gate
- Validate no unresolved placeholders remain (pattern: `{{...}}`)
- Validate Mermaid blocks render in all outputs
- Validate internal cross-references and heading anchors
- Validate PT-BR and EN-US parity for required sections
- Validate executive output length target (<= 5 pages equivalent)
- Validate all `N/A (not provided)` fields are listed as open validation items
- Block publication if critical validation errors are found

---

## Output

| File                                         | Description                      |
|----------------------------------------------|----------------------------------|
| `projects/{project_name}/outputs/downstream/documentation/migration-reports/migration-report.md`       | Full migration report (50+ pages) |
| `projects/{project_name}/outputs/downstream/documentation/migration-reports/migration-report-executive.md` | Executive summary extract     |
| `projects/{project_name}/outputs/downstream/documentation/migration-reports/migration-report-technical.md` | Technical details extract     |
| `projects/{project_name}/outputs/downstream/documentation/migration-reports/migration-report.en.md` | EN-US full report |
| `projects/{project_name}/outputs/downstream/documentation/migration-reports/migration-report-executive.en.md` | EN-US executive extract |
| `projects/{project_name}/outputs/downstream/documentation/migration-reports/migration-report-technical.en.md` | EN-US technical extract |

---

## Quality Criteria

- [ ] All upstream artifacts consumed and referenced
- [ ] Executive summary ≤ 5 pages
- [ ] Technical report includes per-table metrics
- [ ] Technical report includes throughput, latency, resource utilization, and code generation statistics
- [ ] All charts and diagrams render correctly
- [ ] Security and compliance summary included with evidence references
- [ ] Table of contents is accurate
- [ ] Both PT-BR and EN-US versions generated
- [ ] Metadata header present with generation timestamp
- [ ] No placeholder text remaining (`{{...}}` pattern fully resolved)
- [ ] Executive extract respects 5-page equivalent target
- [ ] Every `N/A (not provided)` metric is listed in open validation items
