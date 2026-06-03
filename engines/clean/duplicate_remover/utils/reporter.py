"""
reporter.py  [v1.1]
-------------------
Generates structured deduplication reports after each run.

CHANGELOG v1.1:
  - generate_report()      : unchanged signature, richer output fields.
  - generate_multi_report(): NEW — merges per-group reports + global summary.
  - save_report_json()     : NEW — writes the full report dict to a JSON file
                             with timestamp in filename.
  - Per-group stats now include `duplicate_groups_detail`: value-frequency
    breakdown of duplicate keys (up to top-10) for audit visibility.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Core report builder (single-pass)
# ──────────────────────────────────────────────────────────────────────────────

def generate_report(
    df_original: pd.DataFrame,
    df_cleaned: pd.DataFrame,
    subset: Optional[List[str]],
    keep: Literal["first", "last", False],
    group_name: str = "default",
) -> Dict[str, Any]:
    """
    Build a structured deduplication report for a single pass.

    Args:
        df_original : DataFrame before deduplication.
        df_cleaned  : DataFrame after deduplication.
        subset      : Columns used for detection (None = all columns).
        keep        : Strategy used: 'first', 'last', or False.
        group_name  : Label for this detection pass (used in multi-reports).

    Returns:
        dict with keys:
          group_name, rows_before, rows_after, duplicates_removed,
          removal_rate_pct, columns_checked, keep_strategy,
          columns_in_dataset, duplicate_sample (up to 5 rows),
          duplicate_groups_detail (top-10 duplicate key frequencies).
    """
    rows_before = len(df_original)
    rows_after = len(df_cleaned)
    removed = rows_before - rows_after
    rate = round(removed / rows_before * 100, 2) if rows_before > 0 else 0.0

    # ── Removed-row sample ───────────────────────────────────────────────
    duplicate_sample: list = []
    if removed > 0:
        removed_mask = pd.concat([df_original, df_cleaned]).drop_duplicates(keep=False)
        duplicate_sample = removed_mask.head(5).to_dict(orient="records")

    # ── Duplicate key frequency breakdown (v1.1) ─────────────────────────
    duplicate_groups_detail: list = []
    check_cols = subset if subset else list(df_original.columns)
    try:
        freq = (
            df_original.groupby(check_cols)
            .size()
            .reset_index(name="_count")
            .query("_count > 1")
            .sort_values("_count", ascending=False)
            .head(10)
        )
        duplicate_groups_detail = freq.to_dict(orient="records")
    except Exception:
        pass  # groupby can fail on unhashable types; degrade gracefully

    report: Dict[str, Any] = {
        "group_name": group_name,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": removed,
        "removal_rate_pct": rate,
        "columns_checked": subset if subset else "ALL",
        "keep_strategy": str(keep),
        "columns_in_dataset": list(df_original.columns),
        "duplicate_sample": duplicate_sample,
        "duplicate_groups_detail": duplicate_groups_detail,
    }

    logger.debug("Report generated for group '%s': %d removed", group_name, removed)
    return report


# ──────────────────────────────────────────────────────────────────────────────
# Multi-group report assembler (v1.1 NEW)
# ──────────────────────────────────────────────────────────────────────────────

def generate_multi_report(
    group_reports: List[Dict[str, Any]],
    df_original: pd.DataFrame,
    df_final: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Merge per-group reports into a single top-level summary.

    Args:
        group_reports : List of dicts from generate_report(), one per group.
        df_original   : The very first DataFrame (before any group ran).
        df_final      : The final DataFrame (after all groups ran).

    Returns:
        dict with keys:
          generated_at, total_rows_before, total_rows_after,
          total_duplicates_removed, overall_removal_rate_pct,
          groups_run, per_group (list of individual group reports).
    """
    total_before = len(df_original)
    total_after = len(df_final)
    total_removed = total_before - total_after
    overall_rate = (
        round(total_removed / total_before * 100, 2) if total_before > 0 else 0.0
    )

    multi_report: Dict[str, Any] = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_rows_before": total_before,
        "total_rows_after": total_after,
        "total_duplicates_removed": total_removed,
        "overall_removal_rate_pct": overall_rate,
        "groups_run": len(group_reports),
        "per_group": group_reports,
    }

    logger.info(
        "Multi-report assembled | groups=%d | total removed=%d (%.1f%%)",
        len(group_reports),
        total_removed,
        overall_rate,
    )
    return multi_report


# ──────────────────────────────────────────────────────────────────────────────
# JSON report writer (v1.1 NEW)
# ──────────────────────────────────────────────────────────────────────────────

def save_report_json(
    report: Dict[str, Any],
    report_dir: str = "outputs",
    report_filename: str = "dedup_report.json",
) -> Path:
    """
    Persist the report dictionary to a timestamped JSON file.

    The saved filename is: <stem>_<YYYYMMDD_HHMMSS>.<ext>
    e.g.  dedup_report_20240610_143022.json

    Args:
        report          : The report dict to serialize.
        report_dir      : Output directory (created if missing).
        report_filename : Base filename (timestamp is injected into stem).

    Returns:
        Path of the written JSON file.
    """
    out_dir = Path(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(report_filename).stem
    suffix = Path(report_filename).suffix or ".json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{stem}_{timestamp}{suffix}"
    out_path = out_dir / filename

    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=4, ensure_ascii=False, default=str)

    logger.info("Report saved to: %s", out_path)
    return out_path
