"""
generate_github_issues.py
Backlog → GitHub Issues  (B-001 through B-019 "Must" items)

Reads BACKLOG-INITIAL-MOSCOW-TSHIRT.md, extracts Must items,
and writes one Markdown issue file per item to .github/ISSUE_TEMPLATE/backlog/

Usage (standalone):
    python -m scripts.generate_github_issues [--backlog <path>] [--out <dir>]
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------

@dataclass
class BacklogItem:
    id: str
    epic: str
    title: str
    priority: str
    size: str
    depends_on: str
    acceptance: str

    def to_issue_markdown(self) -> str:
        labels = f"backlog, {self.priority.lower()}, {self.epic.lower().replace(' ', '-')}, size-{self.size.lower()}"
        deps = self.depends_on if self.depends_on != "None" else "—"
        return (
            f"---\n"
            f"name: \"{self.id}: {self.title}\"\n"
            f"about: \"Backlog item from MoSCoW sprint plan\"\n"
            f"labels: \"{labels}\"\n"
            f"---\n\n"
            f"## {self.id}: {self.title}\n\n"
            f"Epic: {self.epic}\n"
            f"Priority: {self.priority}\n"
            f"Size: {self.size}\n"
            f"Depends On: {deps}\n\n"
            f"## Acceptance Criteria\n\n"
            f"{self.acceptance}\n\n"
            f"## Definition of Done\n\n"
            f"- [ ] Implementation complete\n"
            f"- [ ] Tests passing\n"
            f"- [ ] Reviewed and approved\n"
            f"- [ ] Linked to Epic tracker\n"
        )


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_ROW_RE = re.compile(
    r"^\|\s*(?P<id>B-\d+)\s*\|"
    r"\s*(?P<epic>[^|]+?)\s*\|"
    r"\s*(?P<title>[^|]+?)\s*\|"
    r"\s*(?P<priority>[^|]+?)\s*\|"
    r"\s*(?P<size>[^|]+?)\s*\|"
    r"\s*(?P<depends>[^|]+?)\s*\|"
    r"\s*(?P<acceptance>[^|]+?)\s*\|"
)


def parse_must_items(backlog_text: str) -> list[BacklogItem]:
    """Extract rows where Priority == 'Must' from a Markdown table."""
    items: list[BacklogItem] = []
    for line in backlog_text.splitlines():
        m = _ROW_RE.match(line)
        if not m:
            continue
        if m.group("priority").strip() != "Must":
            continue
        items.append(
            BacklogItem(
                id=m.group("id").strip(),
                epic=m.group("epic").strip(),
                title=m.group("title").strip(),
                priority=m.group("priority").strip(),
                size=m.group("size").strip(),
                depends_on=m.group("depends").strip(),
                acceptance=m.group("acceptance").strip(),
            )
        )
    return items


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_issue_markdown_files(items: list[BacklogItem], out_dir: Path) -> list[Path]:
    """Write one .md issue file per item; return list of created paths."""
    import re as _re
    out_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for item in items:
        slug = item.id.lower().replace("-", "")
        title_slug = _re.sub(r"[^a-z0-9]+", "-", item.title.lower()).strip("-")[:40]
        file_path = out_dir / f"{slug}-{title_slug}.md"
        file_path.write_text(item.to_issue_markdown(), encoding="utf-8")
        created.append(file_path)
    return created


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate GitHub issue files from backlog Must items"
    )
    base = Path(__file__).parent.parent
    parser.add_argument(
        "--backlog",
        default=str(base / "BACKLOG-INITIAL-MOSCOW-TSHIRT.md"),
        help="Path to backlog Markdown file",
    )
    parser.add_argument(
        "--out",
        default=str(base / ".github" / "ISSUE_TEMPLATE" / "backlog"),
        help="Output directory for issue files",
    )
    args = parser.parse_args(argv)

    backlog_path = Path(args.backlog)
    if not backlog_path.exists():
        print(f"ERROR: backlog file not found: {backlog_path}", file=sys.stderr)
        return 1

    text = backlog_path.read_text(encoding="utf-8")
    items = parse_must_items(text)
    if not items:
        print("No Must items found in backlog.")
        return 0

    out_dir = Path(args.out)
    created = write_issue_markdown_files(items, out_dir)
    print(f"Generated {len(created)} issue file(s) in {out_dir}")
    for p in created:
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
