"""
logger.py  [v1.1]
-----------------
Centralized logging setup for the DuplicateRemover engine.

CHANGELOG v1.1:
  - setup_logger() now accepts `log_to_file`, `log_dir`, `log_filename`
    directly from DuplicateRemoverConfig (no more manual string path).
  - Rotating file handler (max 2 MB × 3 backups) replaces plain FileHandler.
  - Log format includes session separator on first init for easier log tailing.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    level: str = "INFO",
    log_to_file: bool = False,
    log_dir: str = "logs",
    log_filename: str = "duplicate_remover.log",
) -> None:
    """
    Configure the root logger with console + optional rotating-file handlers.

    Args:
        level       : Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR').
        log_to_file : When True, also write logs to a rotating file.
        log_dir     : Directory for the log file (created if missing).
        log_filename: Name of the log file.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]

    if log_to_file:
        log_path = Path(log_dir) / log_filename
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=2 * 1024 * 1024,   # 2 MB per file
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
        handlers.append(file_handler)

    logging.basicConfig(
        level=numeric_level,
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
        force=True,
    )

    root = logging.getLogger()
    root.info("=" * 55)
    root.info("  DuplicateRemover session started  |  level=%s", level)
    if log_to_file:
        root.info("  Log file: %s/%s", log_dir, log_filename)
    root.info("=" * 55)
