"""
engine.py  [v1.1]
-----------------
Core engine for removing duplicate rows from CSV files.

CHANGELOG v1.1:
  - run() now auto-detects mode:
      • multi_column_groups present → runs each ColumnGroup sequentially,
        the output of group N feeds group N+1 (pipeline).
      • otherwise → falls back to v1.0 single-pass behaviour.
  - _run_single_pass()   : extracted from v1.0 run() for reuse.
  - _run_multi_pass()    : NEW — iterates over ColumnGroup list.
  - save_report()        : NEW — delegates to reporter.save_report_json().
  - get_report()         : now returns multi-report when in multi mode.
  - All internal state preserved: _df_original, _df_cleaned, _report,
    _group_reports (new).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from config.settings import ColumnGroup, DuplicateRemoverConfig
from utils.reporter import (
    generate_multi_report,
    generate_report,
    save_report_json,
)
from utils.validator import validate_columns, validate_input_file

logger = logging.getLogger(__name__)


class DuplicateRemover:
    """
    Production-grade engine for removing duplicate rows from CSV files.

    Supports two modes (auto-selected via config):
      1. Simple mode   — single subset + keep strategy (v1.0 compatible).
      2. Multi-column  — named ColumnGroup pipeline run sequentially (v1.1).

    Typical usage:
        engine = DuplicateRemover(config)
        engine.load("data.csv").run().save().save_report()
        print(engine.get_report())
    """

    def __init__(self, config: Optional[DuplicateRemoverConfig] = None) -> None:
        self.config: DuplicateRemoverConfig = config or DuplicateRemoverConfig()
        self._df_original: Optional[pd.DataFrame] = None
        self._df_cleaned: Optional[pd.DataFrame] = None
        self._report: dict = {}
        self._group_reports: List[dict] = []

        logger.info("DuplicateRemover v1.1 initialized")
        logger.debug("Config: %s", self.config)

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def load(self, filepath: str) -> "DuplicateRemover":
        """
        Load a CSV file into the engine.

        Args:
            filepath: Path to the input CSV.

        Returns:
            self  (method chaining)
        """
        path = Path(filepath)
        validate_input_file(path)

        logger.info("Loading: %s", path)
        self._df_original = pd.read_csv(
            path,
            encoding=self.config.encoding,
            sep=self.config.delimiter,
        )
        logger.info(
            "Loaded %d rows × %d columns from '%s'",
            len(self._df_original),
            len(self._df_original.columns),
            path.name,
        )
        return self

    def run(self) -> "DuplicateRemover":
        """
        Execute deduplication.

        Automatically selects multi-column pipeline mode when
        config.multi_column_groups is populated, otherwise falls
        back to simple single-pass mode.

        Returns:
            self  (method chaining)
        """
        if self._df_original is None:
            raise RuntimeError("No data loaded. Call load() before run().")

        if self.config.has_multi_groups:
            logger.info(
                "Mode: MULTI-COLUMN | %d group(s) defined",
                len(self.config.multi_column_groups),
            )
            self._run_multi_pass()
        else:
            logger.info("Mode: SIMPLE (single-pass)")
            self._run_single_pass()

        return self

    def save(self, output_path: Optional[str] = None) -> "DuplicateRemover":
        """
        Write the cleaned DataFrame to a CSV file.

        Args:
            output_path: Explicit destination. Defaults to config path.

        Returns:
            self  (method chaining)
        """
        if self._df_cleaned is None:
            raise RuntimeError("No cleaned data. Call run() before save().")

        out = Path(output_path) if output_path else self._default_csv_path()
        out.parent.mkdir(parents=True, exist_ok=True)
        self._df_cleaned.to_csv(out, index=False, encoding=self.config.encoding)
        logger.info("Cleaned CSV saved → %s", out)
        return self

    def save_report(self, report_path: Optional[str] = None) -> Path:
        """
        Persist the run report to a timestamped JSON file.

        Args:
            report_path: Optional explicit path. When None, uses config.

        Returns:
            Path to the written JSON report.
        """
        if not self._report:
            raise RuntimeError("No report available. Call run() first.")

        if report_path:
            out = Path(report_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            import json
            with out.open("w", encoding="utf-8") as fh:
                json.dump(self._report, fh, indent=4, ensure_ascii=False, default=str)
            logger.info("Report saved → %s", out)
            return out

        return save_report_json(
            report=self._report,
            report_dir=self.config.report_dir,
            report_filename=self.config.report_filename,
        )

    def get_report(self) -> dict:
        """Return the full deduplication report (single or multi)."""
        if not self._report:
            raise RuntimeError("No report available. Call run() first.")
        return self._report

    def get_cleaned_df(self) -> pd.DataFrame:
        """Return the cleaned DataFrame (after run())."""
        if self._df_cleaned is None:
            raise RuntimeError("No cleaned data. Call run() first.")
        return self._df_cleaned.copy()

    # ──────────────────────────────────────────────────────────────────
    # Internal — single pass (v1.0 logic, unchanged)
    # ──────────────────────────────────────────────────────────────────

    def _run_single_pass(self) -> None:
        """Deduplicate using config.subset_columns and config.keep."""
        assert self._df_original is not None
        subset = self._resolve_simple_subset()

        logger.info(
            "Single-pass | subset=%s | keep='%s'",
            subset or "ALL COLUMNS",
            self.config.keep,
        )

        before = len(self._df_original)
        self._df_cleaned = self._df_original.drop_duplicates(
            subset=subset,
            keep=self.config.keep,
        ).reset_index(drop=True)
        after = len(self._df_cleaned)
        removed = before - after

        logger.info(
            "Result: %d → %d rows (%d removed / %.1f%%)",
            before, after, removed,
            removed / before * 100 if before else 0,
        )

        self._report = generate_report(
            df_original=self._df_original,
            df_cleaned=self._df_cleaned,
            subset=subset,
            keep=self.config.keep,
            group_name="simple",
        )

    # ──────────────────────────────────────────────────────────────────
    # Internal — multi-column pipeline (v1.1 new)
    # ──────────────────────────────────────────────────────────────────

    def _run_multi_pass(self) -> None:
        """
        Run each ColumnGroup sequentially.
        The cleaned output of pass N is the input of pass N+1.
        """
        assert self._df_original is not None
        self._group_reports = []
        current_df = self._df_original.copy()

        for group in self.config.multi_column_groups:
            validate_columns(current_df, group.columns)
            df_before = current_df.copy()

            logger.info(
                "Group '%s' | columns=%s | keep='%s' | rows_in=%d",
                group.name, group.columns, group.keep, len(current_df),
            )

            current_df = current_df.drop_duplicates(
                subset=group.columns,
                keep=group.keep,
            ).reset_index(drop=True)

            group_report = generate_report(
                df_original=df_before,
                df_cleaned=current_df,
                subset=group.columns,
                keep=group.keep,
                group_name=group.name,
            )
            self._group_reports.append(group_report)

            logger.info(
                "Group '%s' done | removed=%d rows",
                group.name,
                group_report["duplicates_removed"],
            )

        self._df_cleaned = current_df

        self._report = generate_multi_report(
            group_reports=self._group_reports,
            df_original=self._df_original,
            df_final=self._df_cleaned,
        )

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    def _resolve_simple_subset(self) -> Optional[list[str]]:
        if not self.config.subset_columns:
            return None
        assert self._df_original is not None
        validate_columns(self._df_original, self.config.subset_columns)
        return list(self.config.subset_columns)

    def _default_csv_path(self) -> Path:
        return Path(self.config.output_dir) / self.config.output_filename
