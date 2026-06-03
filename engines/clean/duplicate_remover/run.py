"""
run.py  [v1.1]
--------------
Entry point for the DuplicateRemover engine.

Pipeline:  load → run → save → save_report (optional) → print summary

CHANGELOG v1.1:
  - --config flag: load YAML config file (overrides all other flags).
  - --save-report flag: write JSON report to outputs/.
  - --log-file flag: enable rotating log file.
  - Multi-column mode: auto-activated when config.yaml defines groups.

Usage examples:
    # Simple mode (CLI flags)
    python run.py --input datasets/customers_raw.csv

    # Simple mode with subset
    python run.py --input datasets/customers_raw.csv --subset email --keep last

    # Multi-column mode via YAML
    python run.py --config config/config.yaml --save-report

    # Full options
    python run.py --input data.csv --subset email name --keep first \\
                  --save-report --log-file --log-level DEBUG
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.loader import load_yaml_config
from config.settings import DuplicateRemoverConfig
from core.engine import DuplicateRemover
from utils.logger import setup_logger


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="duplicate_remover",
        description="DuplicateRemover v1.1 — Remove duplicate rows from CSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Config file (takes precedence over individual flags)
    p.add_argument(
        "--config",
        type=str,
        default=None,
        metavar="PATH",
        help="Path to YAML config file. When set, all other flags are ignored.",
    )

    # I/O
    p.add_argument(
        "--input",
        type=str,
        default="datasets/customers_raw.csv",
        metavar="PATH",
        help="Input CSV path (default: datasets/customers_raw.csv)",
    )
    p.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="PATH",
        help="Output CSV path (default: outputs/cleaned_output.csv)",
    )

    # Dedup options
    p.add_argument(
        "--subset",
        nargs="*",
        default=[],
        metavar="COL",
        help="Column(s) for simple dedup. Omit to compare ALL columns.",
    )
    p.add_argument(
        "--keep",
        choices=["first", "last", "none"],
        default="first",
        help="Keep strategy: first | last | none  (default: first)",
    )

    # Report
    p.add_argument(
        "--save-report",
        action="store_true",
        default=False,
        help="Save JSON report to outputs/ after run.",
    )

    # Logging
    p.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Console log verbosity (default: INFO)",
    )
    p.add_argument(
        "--log-file",
        action="store_true",
        default=False,
        help="Also write logs to logs/duplicate_remover.log",
    )

    return p.parse_args()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _print_summary(report: dict, output_path: str | None = None) -> None:
    """Print a formatted summary to stdout."""
    is_multi = "per_group" in report

    print("\n" + "═" * 58)
    print("  DUPLICATE REMOVER v1.1 — SUMMARY REPORT")
    print("═" * 58)

    if is_multi:
        print(f"  Mode          : MULTI-COLUMN ({report['groups_run']} group(s))")
        print(f"  Generated at  : {report['generated_at']}")
        print(f"  Rows before   : {report['total_rows_before']}")
        print(f"  Rows after    : {report['total_rows_after']}")
        print(f"  Total removed : {report['total_duplicates_removed']} "
              f"({report['overall_removal_rate_pct']}%)")
        print()
        print("  ── Per-group breakdown ─────────────────────────────")
        for g in report["per_group"]:
            print(
                f"  [{g['group_name']:20s}] "
                f"cols={g['columns_checked']}  "
                f"removed={g['duplicates_removed']}  "
                f"keep={g['keep_strategy']}"
            )
    else:
        print(f"  Mode          : SIMPLE")
        print(f"  Rows before   : {report['rows_before']}")
        print(f"  Rows after    : {report['rows_after']}")
        print(f"  Removed       : {report['duplicates_removed']} "
              f"({report['removal_rate_pct']}%)")
        print(f"  Keep strategy : {report['keep_strategy']}")
        print(f"  Columns used  : {report['columns_checked']}")

        if report.get("duplicate_groups_detail"):
            print("\n  ── Top duplicate keys ──────────────────────────────")
            for row in report["duplicate_groups_detail"][:5]:
                count = row.pop("_count", "?")
                print(f"  {row}  → {count}× duplicated")

        if report.get("duplicate_sample"):
            print("\n  ── Sample removed rows (up to 5) ───────────────────")
            print(json.dumps(report["duplicate_sample"], indent=4, ensure_ascii=False))

    if output_path:
        print(f"\n  Output CSV    : {output_path}")
    print("═" * 58 + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    # ── Config resolution ────────────────────────────────────────────────
    if args.config:
        config = load_yaml_config(args.config)
        # Bootstrap logger from YAML config
        setup_logger(
            level=config.log_level,
            log_to_file=config.log_to_file,
            log_dir=config.log_dir,
            log_filename=config.log_filename,
        )
        save_report_flag = config.save_report
    else:
        setup_logger(
            level=args.log_level,
            log_to_file=args.log_file,
        )
        keep_value = False if args.keep == "none" else args.keep
        config = DuplicateRemoverConfig(
            subset_columns=args.subset,
            keep=keep_value,
            log_level=args.log_level,
            log_to_file=args.log_file,
        )
        save_report_flag = args.save_report

    # ── Pipeline ─────────────────────────────────────────────────────────
    engine = DuplicateRemover(config=config)
    engine.load(args.input).run().save(args.output)

    if save_report_flag:
        report_path = engine.save_report()
        print(f"\n  Report saved  : {report_path}")

    _print_summary(engine.get_report(), output_path=args.output)


if __name__ == "__main__":
    main()
