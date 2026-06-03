"""
loader.py  [v1.1 — NEW]
------------------------
Loads engine configuration from a YAML file and hydrates a
DuplicateRemoverConfig dataclass.

Responsibilities:
  - Read config.yaml from disk.
  - Map YAML keys → DuplicateRemoverConfig fields.
  - Convert 'none' string → Python False (pandas keep convention).
  - Build ColumnGroup objects from YAML list entries.
  - Return a fully validated DuplicateRemoverConfig instance.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

from config.settings import ColumnGroup, DuplicateRemoverConfig

logger = logging.getLogger(__name__)

# Default path (same directory as this file)
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _normalize_keep(value: Any) -> Any:
    """Convert YAML string 'none' → Python False for pandas compatibility."""
    if isinstance(value, str) and value.lower() == "none":
        return False
    return value


def load_yaml_config(path: str | Path = DEFAULT_CONFIG_PATH) -> DuplicateRemoverConfig:
    """
    Load and parse a YAML config file into a DuplicateRemoverConfig.

    Args:
        path: Path to the YAML config file.
              Defaults to config/config.yaml (sibling of this file).

    Returns:
        Fully hydrated and validated DuplicateRemoverConfig instance.

    Raises:
        FileNotFoundError : YAML file does not exist.
        ValueError        : YAML is malformed or missing required structure.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: '{config_path}'")

    logger.debug("Loading config from: %s", config_path)

    with config_path.open("r", encoding="utf-8") as fh:
        raw: Dict[str, Any] = yaml.safe_load(fh) or {}

    # ── Multi-column groups ──────────────────────────────────────────────
    groups: list[ColumnGroup] = []
    for entry in raw.get("multi_column_groups", []):
        groups.append(
            ColumnGroup(
                name=entry["name"],
                columns=entry["columns"],
                keep=_normalize_keep(entry.get("keep", "first")),
            )
        )

    config = DuplicateRemoverConfig(
        # Simple mode
        subset_columns=raw.get("subset_columns", []),
        keep=_normalize_keep(raw.get("keep", "first")),
        # Multi-column
        multi_column_groups=groups,
        # I/O
        encoding=raw.get("encoding", "utf-8"),
        delimiter=raw.get("delimiter", ","),
        output_dir=raw.get("output_dir", "outputs"),
        output_filename=raw.get("output_filename", "cleaned_output.csv"),
        # Report
        save_report=raw.get("save_report", True),
        report_dir=raw.get("report_dir", "outputs"),
        report_filename=raw.get("report_filename", "dedup_report.json"),
        # Logging
        log_level=raw.get("log_level", "INFO"),
        log_to_file=raw.get("log_to_file", False),
        log_dir=raw.get("log_dir", "logs"),
        log_filename=raw.get("log_filename", "duplicate_remover.log"),
    )

    logger.info(
        "Config loaded | groups=%d | simple_subset=%s | keep=%s",
        len(groups),
        config.subset_columns or "ALL",
        config.keep,
    )
    return config
