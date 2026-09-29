# 📚 Task: Generate Changelog

## Command
`*generate-changelog`

## Objective
Analyze Git log history and agent execution records to generate a comprehensive, chronological changelog. Follow the [Keep a Changelog](https://keepachangelog.com/) format with semantic versioning.

---

## Prerequisites

- Git repository accessible with full history
- Artifacts available:
  - `migration-coordinator → execution-log.json`
  - All agent output directories with timestamped artifacts

---

## Steps

### 1. Git History Analysis
- Parse Git log for all commits in the migration repository
- Categorize commits by type:
  - `feat:` → Added
  - `fix:` → Fixed
  - `breaking:` → Changed (Breaking)
  - `deprecate:` → Deprecated
  - `remove:` → Removed
  - `security:` → Security
- Extract commit metadata (author, date, files changed)

### 2. Agent Execution History Analysis
- Parse `execution-log.json` for all agent execution events
- Identify major milestones (wave completions, gate approvals)
- Catalog self-healing events and their resolutions
- Track configuration changes over time

### 3. Version Determination
- Apply semantic versioning rules:
  - **MAJOR**: Breaking changes, schema modifications, pipeline restructuring
  - **MINOR**: New features, new tables, new transformations
  - **PATCH**: Bug fixes, performance improvements, documentation updates
- Group changes by version

### 4. Changelog Generation
- Use `changelog-tmpl.md` template
- Generate entries in reverse chronological order (newest first)
- Each version section includes:
  - Release date
  - **Added** — New features and capabilities
  - **Changed** — Changes in existing functionality
  - **Deprecated** — Features marked for future removal
  - **Removed** — Features removed in this release
  - **Fixed** — Bug fixes
  - **Security** — Security-related changes
- Include links to relevant commits and artifacts

### 5. Summary Statistics
- Total number of changes by category
- Timeline visualization (Mermaid Gantt chart)
- Contributor statistics
- Most changed components

---

## Output

| File                                               | Description                       |
|----------------------------------------------------|-----------------------------------|
| `projects/{project_name}/outputs/downstream/documentation/changelogs/changelog.md`          | Full changelog                    |
| `projects/{project_name}/outputs/downstream/documentation/changelogs/changelog-summary.md`  | Summary with statistics           |

---

## Quality Criteria

- [ ] All Git commits categorized
- [ ] Semantic versioning correctly applied
- [ ] Reverse chronological order
- [ ] Each version has a release date
- [ ] Breaking changes clearly highlighted
- [ ] Links to commits and artifacts functional
- [ ] Keep a Changelog format strictly followed
- [ ] Both PT-BR and EN-US versions generated
