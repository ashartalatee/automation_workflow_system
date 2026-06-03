"""
settings.py  [v1.1]
-------------------
Centralized configuration for the DuplicateRemover engine.

CHANGELOG v1.1:
  - Added `multi_column_groups`: define named detection groups, each with
    its own column list and keep strategy.
  - Added `save_report`: toggle JSON report output.
  - Added `report_dir` / `report_filename`: control where JSON report lands.
  - Added `log_to_file`: toggle file-based logging.
  - Added `log_dir` / `log_filename`: control log file path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


@dataclass
class ColumnGroup:
    """
    A single named duplicate-detection group.

    Attributes:
        name    : Human-readable label (used in report keys).
        columns : Column names to compare within this group.
        keep    : Which occurrence to keep: 'first', 'last', or False (none).
    """

    name: str
    columns: List[str]
    keep: Literal["first", "last", False] = "first"

    def __post_init__(self) -> None:
        valid = ("first", "last", False)
        if self.keep not in valid:
            raise ValueError(
                f"[ColumnGroup '{self.name}'] Invalid keep='{self.keep}'. "
                f"Must be one of {valid}."
            )
        if not self.columns:
            raise ValueError(
                f"[ColumnGroup '{self.name}'] 'columns' must not be empty."
            )


@dataclass
class DuplicateRemoverConfig:
    """
    Configuration dataclass for the DuplicateRemover engine (v1.1).

    Simple mode  → set `subset_columns` (unchanged from v1.0).
    Multi-column → set `multi_column_groups` with named ColumnGroup entries.
    Both modes can run in the same execution (sequential pipeline).

    Attributes:
        subset_columns      : Single-group column list (v1.0 compatibility).
        keep                : Keep strategy for simple mode.
        multi_column_groups : Named groups for multi-column detection (v1.1).
        encoding            : CSV encoding. Default: 'utf-8'.
        delimiter           : CSV separator. Default: ','.
        output_dir          : Directory for cleaned CSV output.
        output_filename     : Filename for cleaned CSV.
        save_report         : Write JSON report to disk. Default: True.
        report_dir          : Directory for JSON report. Default: 'outputs'.
        report_filename     : Filename for JSON report.
        log_level           : Logging verbosity. Default: 'INFO'.
        log_to_file         : Enable file-based logging. Default: False.
        log_dir             : Directory for log file. Default: 'logs'.
        log_filename        : Log file name. Default: 'duplicate_remover.log'.
    """

    # ── Simple mode (v1.0 compatible) ──────────────────────────────────
    subset_columns: List[str] = field(default_factory=list)
    keep: Literal["first", "last", False] = "first"

    # ── Multi-column mode (v1.1 new) ────────────────────────────────────
    multi_column_groups: List[ColumnGroup] = field(default_factory=list)

    # ── I/O ─────────────────────────────────────────────────────────────
    encoding: str = "utf-8"
    delimiter: str = ","
    output_dir: str = "outputs"
    output_filename: str = "cleaned_output.csv"

    # ── Report (v1.1 new) ───────────────────────────────────────────────
    save_report: bool = True
    report_dir: str = "outputs"
    report_filename: str = "dedup_report.json"

    # ── Logging (v1.1 new) ──────────────────────────────────────────────
    log_level: str = "INFO"
    log_to_file: bool = False
    log_dir: str = "logs"
    log_filename: str = "duplicate_remover.log"

    def __post_init__(self) -> None:
        valid_keep = ("first", "last", False)
        if self.keep not in valid_keep:
            raise ValueError(
                f"Invalid 'keep' value: '{self.keep}'. "
                f"Must be one of {valid_keep}."
            )

    @property
    def has_multi_groups(self) -> bool:
        """True when at least one named ColumnGroup is configured."""
        return len(self.multi_column_groups) > 0

    def get_group_by_name(self, name: str) -> Optional[ColumnGroup]:
        """Return the first ColumnGroup with matching name, or None."""
        return next((g for g in self.multi_column_groups if g.name == name), None)
