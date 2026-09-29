"""
prd_traceability.py
B-019 — Story and epic traceability to PRD IDs.

Provides a traceability matrix that maps backlog items back to PRD sections.
Detects unmapped backlog items (no prd_ids) and uncovered PRD sections
(referenced by no backlog item).

Usage:
    from scripts.prd_traceability import (
        PRDSection, BacklogItem, TraceabilityMatrix, check_coverage,
    )

    sections = [PRDSection(prd_id="PRD-1.1", title="Governance Foundation")]
    items = [BacklogItem(backlog_id="B-001", title="Policy schema", prd_ids=["PRD-1.1"])]

    report = check_coverage(items, sections)
    print(report.unmapped_items)     # items with no PRD mapping
    print(report.uncovered_sections) # PRD sections not covered by any item
"""
from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class PRDSection:
    """A section in the Product Requirements Document."""
    prd_id: str       # e.g. "PRD-1.1", "PRD-2.0"
    title: str
    description: str = ""


@dataclass
class BacklogItem:
    """A backlog item (story or epic) that maps to one or more PRD sections."""
    backlog_id: str       # e.g. "B-001"
    title: str
    prd_ids: list[str] = field(default_factory=list)


@dataclass
class TraceabilityReport:
    """Coverage report from the traceability matrix."""
    total_backlog: int
    total_prd_sections: int
    mapped_count: int                      # items that have ≥1 prd_id
    unmapped_items: list[str]              # backlog_ids with no prd_ids
    uncovered_sections: list[str]          # prd_ids not referenced by any item


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def check_coverage(
    items: list[BacklogItem],
    sections: list[PRDSection],
) -> TraceabilityReport:
    """Evaluate traceability coverage between backlog items and PRD sections.

    Args:
        items:    All backlog items to check.
        sections: All known PRD sections.

    Returns:
        TraceabilityReport with coverage counts and gap lists.
    """
    all_prd_ids = {s.prd_id for s in sections}
    referenced_prd_ids: set[str] = set()

    unmapped_items: list[str] = []
    mapped_count = 0

    for item in items:
        if not item.prd_ids:
            unmapped_items.append(item.backlog_id)
        else:
            mapped_count += 1
            for prd_id in item.prd_ids:
                referenced_prd_ids.add(prd_id)

    uncovered_sections = sorted(all_prd_ids - referenced_prd_ids)

    return TraceabilityReport(
        total_backlog=len(items),
        total_prd_sections=len(sections),
        mapped_count=mapped_count,
        unmapped_items=unmapped_items,
        uncovered_sections=uncovered_sections,
    )


# ---------------------------------------------------------------------------
# Matrix class (object-oriented API)
# ---------------------------------------------------------------------------

class TraceabilityMatrix:
    """Stores backlog items and PRD sections, then produces coverage reports."""

    def __init__(self) -> None:
        self._items: list[BacklogItem] = []
        self._sections: list[PRDSection] = []

    def add_section(self, section: PRDSection) -> None:
        """Register a PRD section."""
        self._sections.append(section)

    def add_item(self, item: BacklogItem) -> None:
        """Register a backlog item."""
        self._items.append(item)

    def check_coverage(self) -> TraceabilityReport:
        """Produce the traceability coverage report from registered data."""
        return check_coverage(self._items, self._sections)
