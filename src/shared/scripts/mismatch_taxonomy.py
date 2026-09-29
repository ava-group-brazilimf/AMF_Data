"""
mismatch_taxonomy.py
B-013 — Mismatch root-cause taxonomy for reconciliation evidence reports.

Categories cover the most common causes of source/target mismatches in data
migrations. Each mismatch is classified into one category and the summary
can be attached to the reconciliation-evidence.md artifact.

Usage:
    from scripts.mismatch_taxonomy import MismatchRecord, classify_mismatch, summarize_mismatches

    record = MismatchRecord(entity="orders", source_value=1000, target_value=990, field="row_count")
    classified = classify_mismatch(record)
    print(classified.category)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MismatchCategory(Enum):
    ROW_COUNT_DELTA = "row_count_delta"
    TRANSFORMATION_ERROR = "transformation_error"
    NULL_INTRODUCED = "null_introduced"
    TRUNCATION = "truncation"
    TYPE_MISMATCH = "type_mismatch"
    ENCODING_ERROR = "encoding_error"
    UNKNOWN = "unknown"


@dataclass
class MismatchRecord:
    entity: str
    source_value: object
    target_value: object
    field: str
    notes: str = ""


@dataclass
class ClassifiedMismatch:
    record: MismatchRecord
    category: MismatchCategory
    description: str


@dataclass
class RootCauseSummary:
    total: int
    by_category: dict[MismatchCategory, int] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [f"Mismatch Root-Cause Summary (total: {self.total})"]
        for cat, count in sorted(self.by_category.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat.value:<30} {count}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Classification rules (ordered — first match wins)
# ---------------------------------------------------------------------------

def classify_mismatch(record: MismatchRecord) -> ClassifiedMismatch:
    """Classify a single mismatch record into a root-cause category."""
    src = record.source_value
    tgt = record.target_value

    # NULL introduced in target
    if src is not None and tgt is None:
        return ClassifiedMismatch(
            record=record,
            category=MismatchCategory.NULL_INTRODUCED,
            description=f"Field '{record.field}' has value in source but NULL in target",
        )

    # Row count delta — field name is "row_count" or values are ints representing counts
    if record.field in ("row_count", "count", "total_rows"):
        return ClassifiedMismatch(
            record=record,
            category=MismatchCategory.ROW_COUNT_DELTA,
            description=f"Row count delta: source={src} target={tgt}",
        )

    # Truncation — both are strings, target is shorter substring of source
    if isinstance(src, str) and isinstance(tgt, str):
        if len(src) > len(tgt) and src.startswith(tgt):
            return ClassifiedMismatch(
                record=record,
                category=MismatchCategory.TRUNCATION,
                description=f"Field '{record.field}' truncated from {len(src)} to {len(tgt)} chars",
            )

        # Transformation error — both non-null strings but different (date formats etc.)
        if src != tgt:
            return ClassifiedMismatch(
                record=record,
                category=MismatchCategory.TRANSFORMATION_ERROR,
                description=f"Field '{record.field}' transformed differently: '{src}' → '{tgt}'",
            )

    # Type mismatch
    if src is not None and tgt is not None and type(src) != type(tgt):
        return ClassifiedMismatch(
            record=record,
            category=MismatchCategory.TYPE_MISMATCH,
            description=f"Field '{record.field}' type changed from {type(src).__name__} to {type(tgt).__name__}",
        )

    return ClassifiedMismatch(
        record=record,
        category=MismatchCategory.UNKNOWN,
        description=f"Field '{record.field}': unclassified mismatch",
    )


def summarize_mismatches(records: list[MismatchRecord]) -> RootCauseSummary:
    """Classify all records and produce a category count summary."""
    by_category: dict[MismatchCategory, int] = {}
    for rec in records:
        cat = classify_mismatch(rec).category
        by_category[cat] = by_category.get(cat, 0) + 1
    return RootCauseSummary(total=len(records), by_category=by_category)
