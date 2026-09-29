# 📚 Documentation Agent — Best Practices

## 1. Executive Report Writing

### Principles
- **Audience first**: Write for C-level sponsors and project managers, not engineers
- **Lead with results**: Start with outcomes, then provide context
- **Quantify everything**: Use metrics, percentages, and concrete numbers
- **Visual over textual**: Prefer charts and tables over paragraphs
- **Action-oriented**: End every section with clear recommendations

### Structure
1. Executive Summary (1-2 pages max)
2. Key Metrics Dashboard
3. Scope and Objectives (brief)
4. Results by Wave
5. Risks and Mitigations
6. Recommendations and Next Steps
7. Appendices (detailed data)

### Do's and Don'ts
| ✅ Do                                | ❌ Don't                                 |
|---------------------------------------|------------------------------------------|
| Use bullet points                     | Write long paragraphs                    |
| Include RAG status indicators         | Use only text to describe status         |
| Quantify impact and progress          | Use vague language ("mostly done")       |
| Highlight blockers and risks early    | Bury issues in appendices                |
| Include a glossary for technical terms| Assume audience knows acronyms           |

---

## 2. Technical Documentation Standards

### Structure
- **Title and metadata** at the top (author, date, version, status)
- **Table of contents** for documents over 5 pages
- **Prerequisites** section before procedures
- **Step-by-step instructions** with numbered steps
- **Code examples** with syntax highlighting
- **Expected outputs** alongside commands
- **Cross-references** to related documents

### Code Documentation
```python
# ✅ Good: Clear docstring with parameters and return type
def transform_material(raw_record: dict) -> dict:
    """
    Transform a raw material record from SAP MARA to Silver layer format.
    
    Args:
        raw_record: Raw material record from Bronze layer
        
    Returns:
        Transformed record conforming to Silver schema
        
    Raises:
        ValidationError: If required fields are missing
    """
```

### Naming Conventions
| Type           | Convention                    | Example                          |
|----------------|-------------------------------|-----------------------------------|
| Documents      | kebab-case                    | `migration-report.md`            |
| Diagrams       | `lineage-{domain}.md`        | `lineage-materials.md`           |
| Runbooks       | `runbook-{topic}.md`         | `runbook-monitoring.md`          |
| Templates      | `{type}-tmpl.md`             | `migration-report-tmpl.md`       |

---

## 3. Mermaid Diagram Conventions

### General Rules
- Maximum node count per diagram: **30 nodes**
- If more nodes needed, split into sub-diagrams
- Always include a **legend** subgraph
- Use **descriptive labels** on edges (not just arrows)
- Use **subgraphs** to group related nodes
- Use consistent **color coding** via styles

### Layer Color Coding
```mermaid
graph LR
    classDef source fill:#ff9999,stroke:#cc0000,color:#000
    classDef bronze fill:#cd7f32,stroke:#8b4513,color:#fff
    classDef silver fill:#c0c0c0,stroke:#808080,color:#000
    classDef gold fill:#ffd700,stroke:#daa520,color:#000
```

### Standard Layouts
| Diagram Type       | Direction | Use Case                          |
|--------------------|-----------|-----------------------------------|
| Data Lineage       | LR        | Source to target flow              |
| Architecture       | TB        | System layers                     |
| Decision Trees     | TD        | Troubleshooting flows             |
| Timeline           | LR        | Gantt/timeline charts             |
| Dependencies       | LR        | Object relationships              |

### Edge Label Standards
| Label Pattern                | Meaning                           |
|------------------------------|-----------------------------------|
| `"Extract AS-IS"`            | No transformation                 |
| `"Cast + Validate"`          | Type conversion + validation      |
| `"Join + Cleanse"`           | Table join + data cleansing       |
| `"Aggregate + Enrich"`       | Aggregation + derived columns     |
| `"Filter: condition"`        | Conditional filtering             |

---

## 4. Runbook Authoring

### Structure (per runbook)
1. **Overview** — Purpose and scope
2. **Prerequisites** — Tools, access, knowledge required
3. **Procedures** — Step-by-step with expected outputs
4. **Troubleshooting** — Common issues and resolutions
5. **Escalation** — When and how to escalate
6. **Contacts** — On-call, SMEs, management
7. **Revision History** — Version, date, author, changes

### Writing Procedures
- Number every step sequentially
- Include **expected output** after each command
- Include **verification step** after critical operations
- Always document **rollback procedure**
- Use `⚠️ WARNING` callouts for destructive operations
- Include estimated time for each procedure

### Example Procedure Format
```markdown
### Procedure: Restart Failed Pipeline

**Estimated time:** 5-10 minutes  
**Risk level:** Low  
**Rollback:** N/A (restarting does not modify data)

1. Navigate to Databricks Workspace → Workflows
   - **Expected:** Workflow list page loads
   
2. Locate the failed job by name: `pipeline_{table_name}`
   - **Expected:** Job visible with ❌ Failed status

3. Click on the failed run → View error logs
   - **Expected:** Error details displayed

4. ⚠️ **Verify** that no other jobs depend on this pipeline's output
   - Run: `SELECT * FROM job_dependencies WHERE upstream = '{job_name}'`
   
5. Click "Run Now" to restart the pipeline
   - **Expected:** Job starts with 🔄 Running status

6. **Verify:** Monitor job for 5 minutes until completion
   - **Expected:** Job shows ✅ Succeeded status
```

---

## 5. Changelog Format (Keep a Changelog)

### Rules
1. **Reverse chronological** order (newest first)
2. **Group by version** with release date
3. **ISO 8601 date format** (YYYY-MM-DD)
4. **One entry per change** — atomic descriptions
5. Use **imperative mood** ("Add" not "Added")
6. **Link to issues/commits** where applicable
7. Mark **Unreleased** changes at the top

### Section Definitions
| Section        | Description                                            |
|----------------|--------------------------------------------------------|
| **Added**      | New features or capabilities                           |
| **Changed**    | Changes in existing functionality                      |
| **Deprecated** | Features marked for removal in future versions         |
| **Removed**    | Features removed in this version                       |
| **Fixed**      | Bug fixes                                              |
| **Security**   | Security vulnerability fixes or improvements           |

### Example Entry
```markdown
## [1.2.0] - 2026-02-13

### Added
- Add support for MARC table migration (#142)
- Add data quality validation for MARA fields (#145)

### Changed
- Improve Bronze-to-Silver transformation performance by 40% (#148)

### Fixed
- Fix null handling in vendor code lookup (#150)
- Fix duplicate detection in material master (#151)

### Security
- Rotate API keys for Databricks workspace access (#155)
```

---

## 6. Multilingual Documentation

### Language Priority
1. **PT-BR** (Primary) — Generated first
2. **EN-US** (Secondary) — Generated as translation

### Translation Rules
- Technical terms remain in English (e.g., "pipeline", "cluster", "Bronze layer")
- Code examples are **never** translated
- File names are **always** in English
- Table headers can be bilingual
- Use consistent terminology across both languages
- Maintain a glossary of translated terms

### File Naming for Languages
```
migration-report.md          # PT-BR (primary, no suffix)
migration-report.en.md       # EN-US (secondary, .en suffix)
```

---

## 7. Publishing Workflows

### Confluence Publishing
1. Authenticate via API token
2. Create or find space for migration documentation
3. Create page hierarchy matching document structure
4. Upload content in Confluence Storage Format (XHTML)
5. Attach diagrams and images
6. Set page permissions (project team = edit, stakeholders = view)
7. Verify page rendering

### SharePoint Publishing
1. Authenticate via OAuth2 / Service Principal
2. Navigate to target document library
3. Upload Markdown files converted to DOCX
4. Upload PDF exports
5. Set metadata (project, date, version, status)
6. Configure permissions

### Git Publishing
1. Create documentation branch: `docs/migration-v{version}`
2. Commit all generated files with message: `docs: generate migration documentation v{version}`
3. Create pull request for review (optional)
4. Merge to main branch
5. Tag release: `docs-v{version}`

### PDF Export
1. Convert Markdown to PDF via Pandoc or equivalent
2. Apply corporate template (headers, footers, logos)
3. Generate table of contents
4. Embed diagrams as images (render Mermaid to SVG first)
5. Apply page numbers and cross-references
6. Store in `projects/{project_name}/outputs/downstream/documentation/` directory
