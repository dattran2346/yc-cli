from __future__ import annotations

import json
import sys
from collections import Counter

from yc_cli.models import SUMMARY_FIELDS


def _project(company: dict, fields: list[str]) -> dict:
    return {k: company.get(k) for k in fields if k in company}


def _print_table(rows: list[dict], columns: list[str] | None = None) -> None:
    if not rows:
        print("(no results)")
        return
    if columns is None:
        columns = list(rows[0].keys())
    widths = {col: len(col) for col in columns}
    str_rows = []
    for row in rows:
        sr = {}
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            s = str(val) if val is not None else ""
            if len(s) > 60:
                s = s[:57] + "..."
            sr[col] = s
            widths[col] = max(widths[col], len(s))
        str_rows.append(sr)
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    sep = "  ".join("-" * widths[col] for col in columns)
    print(header)
    print(sep)
    for sr in str_rows:
        print("  ".join(sr.get(col, "").ljust(widths[col]) for col in columns))


def output_companies(
    companies: list[dict],
    *,
    fmt: str = "json",
    fields: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
) -> None:
    total = len(companies)
    sliced = companies[offset : offset + limit]
    use_fields = fields or SUMMARY_FIELDS
    projected = [_project(c, use_fields) for c in sliced]

    if fmt == "json":
        envelope = {
            "count": len(projected),
            "total": total,
            "offset": offset,
            "companies": projected,
        }
        print(json.dumps(envelope, indent=2, ensure_ascii=False))
    else:
        print(f"Showing {len(projected)} of {total} (offset {offset})\n")
        _print_table(projected, use_fields)


def output_single(company: dict, *, fmt: str = "json") -> None:
    if fmt == "json":
        print(json.dumps(company, indent=2, ensure_ascii=False))
    else:
        for k, v in company.items():
            if isinstance(v, list):
                v = ", ".join(str(i) for i in v)
            label = k.ljust(25)
            val = str(v) if v is not None else ""
            print(f"{label} {val}")


def output_meta_list(
    items: list[dict], *, fmt: str = "json", label: str = "items"
) -> None:
    if fmt == "json":
        print(json.dumps({"count": len(items), label: items}, indent=2, ensure_ascii=False))
    else:
        _print_table(items)


def output_stats(
    meta: dict, companies: list[dict], *, fmt: str = "json"
) -> None:
    status_counts = Counter(c.get("status", "Unknown") for c in companies)
    industry_counts = Counter(c.get("industry", "Unknown") for c in companies)
    batch_counts = Counter(c.get("batch", "Unknown") for c in companies)
    hiring_count = sum(1 for c in companies if c.get("isHiring"))
    team_sizes = [c.get("team_size", 0) for c in companies if c.get("team_size")]
    avg_team = round(sum(team_sizes) / len(team_sizes), 1) if team_sizes else 0

    stats = {
        "total_companies": len(companies),
        "by_status": dict(status_counts.most_common()),
        "top_industries": dict(industry_counts.most_common(10)),
        "top_batches": dict(batch_counts.most_common(10)),
        "currently_hiring": hiring_count,
        "average_team_size": avg_team,
    }

    if fmt == "json":
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print(f"Total companies: {stats['total_companies']}")
        print(f"Currently hiring: {stats['currently_hiring']}")
        print(f"Average team size: {stats['average_team_size']}")
        print("\nBy status:")
        for s, n in status_counts.most_common():
            print(f"  {s}: {n}")
        print("\nTop 10 industries:")
        for ind, n in industry_counts.most_common(10):
            print(f"  {ind}: {n}")
        print("\nTop 10 batches:")
        for b, n in batch_counts.most_common(10):
            print(f"  {b}: {n}")
