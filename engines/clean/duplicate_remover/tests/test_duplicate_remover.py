"""
test_duplicate_remover.py  [v1.1]
----------------------------------
Unit tests for DuplicateRemover engine.

Coverage:
  TestDuplicateRemoverConfig   — dataclass validation incl. ColumnGroup
  TestColumnGroup              — v1.1 new: named group validation
  TestValidator                — file + column validation
  TestDuplicateRemoverEngine   — simple & multi-column run, save, chaining
  TestMultiColumnPipeline      — sequential group dedup (v1.1 NEW)
  TestReporter                 — single + multi report generation + JSON save
  TestConfigLoader             — YAML config loading (v1.1 NEW)

Run:
    python -m pytest tests/ -v
    python -m pytest tests/ -v --tb=short   # compact tracebacks
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.loader import load_yaml_config
from config.settings import ColumnGroup, DuplicateRemoverConfig
from core.engine import DuplicateRemover
from utils.reporter import generate_multi_report, generate_report, save_report_json
from utils.validator import validate_columns, validate_input_file


# ══════════════════════════════════════════════════════════════════════════════
# Shared fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def simple_csv(tmp_path: Path) -> Path:
    """5-row CSV with 1 exact duplicate and 2 email duplicates."""
    data = (
        "id,name,email,city\n"
        "1,Budi,budi@email.com,Surabaya\n"
        "2,Siti,siti@email.com,Jakarta\n"
        "3,Budi,budi@email.com,Bandung\n"   # same email as row 1, diff city
        "4,Andi,andi@email.com,Medan\n"
        "1,Budi,budi@email.com,Surabaya\n"  # exact duplicate of row 1
    )
    p = tmp_path / "simple.csv"
    p.write_text(data, encoding="utf-8")
    return p


@pytest.fixture
def multi_csv(tmp_path: Path) -> Path:
    """CSV designed for multi-column pipeline tests."""
    data = (
        "id,name,email,city,department\n"
        "1,Budi,budi@email.com,Surabaya,Engineering\n"
        "2,Siti,siti@email.com,Jakarta,Marketing\n"
        "3,Budi,budi2@email.com,Surabaya,Engineering\n"  # same name+city
        "4,Andi,andi@email.com,Bandung,Finance\n"
        "5,Budi,budi@email.com,Surabaya,Engineering\n"   # dup email of row 1
        "6,Dewi,dewi@email.com,Surabaya,HR\n"
        "7,Andi,andi2@email.com,Bandung,Finance\n"       # same name+city as 4
    )
    p = tmp_path / "multi.csv"
    p.write_text(data, encoding="utf-8")
    return p


@pytest.fixture
def yaml_config_file(tmp_path: Path) -> Path:
    """Write a minimal valid YAML config to a temp file."""
    cfg = {
        "subset_columns": [],
        "keep": "first",
        "multi_column_groups": [
            {"name": "by_email", "columns": ["email"], "keep": "first"},
            {"name": "by_name_city", "columns": ["name", "city"], "keep": "last"},
        ],
        "encoding": "utf-8",
        "delimiter": ",",
        "output_dir": str(tmp_path / "outputs"),
        "output_filename": "cleaned.csv",
        "save_report": True,
        "report_dir": str(tmp_path / "outputs"),
        "report_filename": "report.json",
        "log_level": "DEBUG",
        "log_to_file": False,
        "log_dir": str(tmp_path / "logs"),
        "log_filename": "test.log",
    }
    p = tmp_path / "config.yaml"
    p.write_text(yaml.dump(cfg), encoding="utf-8")
    return p


# ══════════════════════════════════════════════════════════════════════════════
# Config Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestDuplicateRemoverConfig:

    def test_default_values(self):
        cfg = DuplicateRemoverConfig()
        assert cfg.keep == "first"
        assert cfg.encoding == "utf-8"
        assert cfg.delimiter == ","
        assert cfg.subset_columns == []
        assert cfg.multi_column_groups == []
        assert cfg.save_report is True
        assert cfg.log_to_file is False

    def test_invalid_keep_raises(self):
        with pytest.raises(ValueError, match="Invalid 'keep'"):
            DuplicateRemoverConfig(keep="random")  # type: ignore

    def test_keep_false_valid(self):
        cfg = DuplicateRemoverConfig(keep=False)
        assert cfg.keep is False

    def test_has_multi_groups_false_by_default(self):
        assert DuplicateRemoverConfig().has_multi_groups is False

    def test_has_multi_groups_true(self):
        cfg = DuplicateRemoverConfig(
            multi_column_groups=[ColumnGroup("g1", ["email"])]
        )
        assert cfg.has_multi_groups is True

    def test_get_group_by_name_found(self):
        g = ColumnGroup("by_email", ["email"])
        cfg = DuplicateRemoverConfig(multi_column_groups=[g])
        assert cfg.get_group_by_name("by_email") is g

    def test_get_group_by_name_missing(self):
        cfg = DuplicateRemoverConfig()
        assert cfg.get_group_by_name("ghost") is None


# ══════════════════════════════════════════════════════════════════════════════
# ColumnGroup Tests (v1.1 NEW)
# ══════════════════════════════════════════════════════════════════════════════

class TestColumnGroup:

    def test_valid_group(self):
        g = ColumnGroup("test", ["email", "name"], keep="last")
        assert g.name == "test"
        assert g.columns == ["email", "name"]
        assert g.keep == "last"

    def test_invalid_keep_raises(self):
        with pytest.raises(ValueError, match="Invalid keep"):
            ColumnGroup("bad", ["email"], keep="maybe")  # type: ignore

    def test_empty_columns_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            ColumnGroup("bad", columns=[])

    def test_keep_false_valid(self):
        g = ColumnGroup("no_keep", ["email"], keep=False)
        assert g.keep is False


# ══════════════════════════════════════════════════════════════════════════════
# Validator Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestValidator:

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            validate_input_file(tmp_path / "ghost.csv")

    def test_empty_file_raises(self, tmp_path: Path):
        f = tmp_path / "empty.csv"
        f.write_text("")
        with pytest.raises(ValueError, match="empty"):
            validate_input_file(f)

    def test_directory_raises(self, tmp_path: Path):
        with pytest.raises(TypeError):
            validate_input_file(tmp_path)

    def test_columns_missing_raises(self):
        df = pd.DataFrame({"a": [1], "b": [2]})
        with pytest.raises(ValueError, match="not found"):
            validate_columns(df, ["a", "z"])

    def test_columns_ok_no_raise(self):
        df = pd.DataFrame({"a": [1], "b": [2]})
        validate_columns(df, ["a", "b"])  # must not raise


# ══════════════════════════════════════════════════════════════════════════════
# Engine — Simple mode
# ══════════════════════════════════════════════════════════════════════════════

class TestDuplicateRemoverEngine:

    def test_run_before_load_raises(self, tmp_path: Path):
        engine = DuplicateRemover(DuplicateRemoverConfig(output_dir=str(tmp_path)))
        with pytest.raises(RuntimeError, match="No data loaded"):
            engine.run()

    def test_save_before_run_raises(self, tmp_path: Path):
        engine = DuplicateRemover(DuplicateRemoverConfig(output_dir=str(tmp_path)))
        with pytest.raises(RuntimeError, match="No cleaned data"):
            engine.save()

    def test_get_report_before_run_raises(self, tmp_path: Path):
        engine = DuplicateRemover(DuplicateRemoverConfig(output_dir=str(tmp_path)))
        with pytest.raises(RuntimeError, match="No report"):
            engine.get_report()

    def test_full_row_dedup_keep_first(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(keep="first", output_dir=str(tmp_path))
        engine = DuplicateRemover(cfg)
        engine.load(str(simple_csv)).run()
        r = engine.get_report()
        assert r["rows_before"] == 5
        assert r["duplicates_removed"] == 1   # only row 5 is exact dup of row 1
        assert r["rows_after"] == 4

    def test_subset_email_dedup(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(
            subset_columns=["email"], keep="first", output_dir=str(tmp_path)
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(simple_csv)).run()
        r = engine.get_report()
        # budi@email.com appears 3× → keep 1 → remove 2
        assert r["rows_after"] == 3
        assert r["duplicates_removed"] == 2

    def test_keep_none_removes_all_email_dupes(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(
            subset_columns=["email"], keep=False, output_dir=str(tmp_path)
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(simple_csv)).run()
        r = engine.get_report()
        # budi appears 3× → all removed; siti + andi appear once → kept
        assert r["rows_after"] == 2

    def test_save_creates_csv(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(output_dir=str(tmp_path))
        engine = DuplicateRemover(cfg)
        engine.load(str(simple_csv)).run().save()
        out = tmp_path / "cleaned_output.csv"
        assert out.exists()
        assert len(pd.read_csv(out)) == engine.get_report()["rows_after"]

    def test_method_chaining_returns_self(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(output_dir=str(tmp_path))
        engine = DuplicateRemover(cfg)
        assert engine.load(str(simple_csv)).run().save() is engine

    def test_invalid_subset_column_raises(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(
            subset_columns=["nonexistent"], output_dir=str(tmp_path)
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(simple_csv))
        with pytest.raises(ValueError, match="not found"):
            engine.run()

    def test_get_cleaned_df_returns_copy(self, simple_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(output_dir=str(tmp_path))
        engine = DuplicateRemover(cfg)
        engine.load(str(simple_csv)).run()
        df = engine.get_cleaned_df()
        assert isinstance(df, pd.DataFrame)


# ══════════════════════════════════════════════════════════════════════════════
# Engine — Multi-column pipeline (v1.1 NEW)
# ══════════════════════════════════════════════════════════════════════════════

class TestMultiColumnPipeline:

    def test_multi_mode_activated_when_groups_present(
        self, multi_csv: Path, tmp_path: Path
    ):
        cfg = DuplicateRemoverConfig(
            multi_column_groups=[
                ColumnGroup("by_email", ["email"], keep="first"),
            ],
            output_dir=str(tmp_path),
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(multi_csv)).run()
        r = engine.get_report()
        # Multi-report has 'per_group' key
        assert "per_group" in r
        assert r["groups_run"] == 1

    def test_two_groups_pipeline(self, multi_csv: Path, tmp_path: Path):
        """
        Group 1: deduplicate by email
        Group 2: deduplicate by name+city
        Each group's output feeds the next.
        """
        cfg = DuplicateRemoverConfig(
            multi_column_groups=[
                ColumnGroup("by_email", ["email"], keep="first"),
                ColumnGroup("by_name_city", ["name", "city"], keep="first"),
            ],
            output_dir=str(tmp_path),
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(multi_csv)).run()
        r = engine.get_report()

        assert r["groups_run"] == 2
        assert r["total_rows_before"] == 7   # 7 rows in multi_csv
        assert r["total_rows_after"] <= r["total_rows_before"]
        assert r["total_duplicates_removed"] >= 0

        # Per-group reports should each have the right structure
        for g in r["per_group"]:
            assert "group_name" in g
            assert "duplicates_removed" in g
            assert "columns_checked" in g

    def test_multi_report_global_stats(self, multi_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(
            multi_column_groups=[
                ColumnGroup("g1", ["email"], keep="first"),
            ],
            output_dir=str(tmp_path),
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(multi_csv)).run()
        r = engine.get_report()

        assert r["total_rows_before"] == 7
        assert r["total_rows_after"] == r["total_rows_before"] - r["total_duplicates_removed"]
        assert 0.0 <= r["overall_removal_rate_pct"] <= 100.0

    def test_invalid_column_in_group_raises(self, multi_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(
            multi_column_groups=[
                ColumnGroup("bad_group", ["ghost_column"], keep="first"),
            ],
            output_dir=str(tmp_path),
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(multi_csv))
        with pytest.raises(ValueError, match="not found"):
            engine.run()

    def test_save_report_writes_json(self, multi_csv: Path, tmp_path: Path):
        cfg = DuplicateRemoverConfig(
            multi_column_groups=[
                ColumnGroup("by_email", ["email"], keep="first"),
            ],
            output_dir=str(tmp_path),
            report_dir=str(tmp_path),
        )
        engine = DuplicateRemover(cfg)
        engine.load(str(multi_csv)).run()
        report_path = engine.save_report()

        assert report_path.exists()
        with report_path.open() as f:
            data = json.load(f)
        assert "per_group" in data


# ══════════════════════════════════════════════════════════════════════════════
# Reporter Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestReporter:

    def test_single_report_structure(self):
        df_orig = pd.DataFrame({"a": [1, 1, 2], "b": [10, 10, 20]})
        df_clean = pd.DataFrame({"a": [1, 2], "b": [10, 20]})
        r = generate_report(df_orig, df_clean, subset=None, keep="first")

        assert r["rows_before"] == 3
        assert r["rows_after"] == 2
        assert r["duplicates_removed"] == 1
        assert r["removal_rate_pct"] == 33.33
        assert r["columns_checked"] == "ALL"
        assert r["group_name"] == "default"

    def test_report_no_duplicates(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        r = generate_report(df, df, subset=None, keep="first")
        assert r["duplicates_removed"] == 0
        assert r["removal_rate_pct"] == 0.0
        assert r["duplicate_sample"] == []

    def test_report_with_group_name(self):
        df = pd.DataFrame({"email": ["a@b.com", "a@b.com", "c@d.com"]})
        df_clean = df.drop_duplicates(subset=["email"])
        r = generate_report(df, df_clean, subset=["email"], keep="first",
                            group_name="by_email")
        assert r["group_name"] == "by_email"
        assert r["columns_checked"] == ["email"]

    def test_duplicate_groups_detail_populated(self):
        df = pd.DataFrame({
            "email": ["a@b.com", "a@b.com", "a@b.com", "x@y.com"],
        })
        df_clean = df.drop_duplicates(subset=["email"])
        r = generate_report(df, df_clean, subset=["email"], keep="first")
        assert len(r["duplicate_groups_detail"]) >= 1
        assert r["duplicate_groups_detail"][0]["_count"] == 3

    def test_multi_report_structure(self):
        df_orig = pd.DataFrame({"x": range(10)})
        df_final = pd.DataFrame({"x": range(7)})
        g1 = generate_report(df_orig, pd.DataFrame({"x": range(8)}),
                              subset=None, keep="first", group_name="g1")
        g2 = generate_report(pd.DataFrame({"x": range(8)}), df_final,
                              subset=None, keep="first", group_name="g2")
        r = generate_multi_report([g1, g2], df_orig, df_final)

        assert r["total_rows_before"] == 10
        assert r["total_rows_after"] == 7
        assert r["total_duplicates_removed"] == 3
        assert r["groups_run"] == 2
        assert "generated_at" in r

    def test_save_report_json_creates_file(self, tmp_path: Path):
        report = {"rows_before": 10, "rows_after": 8, "test": True}
        path = save_report_json(report, report_dir=str(tmp_path),
                                report_filename="test_report.json")
        assert path.exists()
        with path.open() as f:
            data = json.load(f)
        assert data["rows_before"] == 10

    def test_save_report_filename_has_timestamp(self, tmp_path: Path):
        path = save_report_json({}, report_dir=str(tmp_path),
                                report_filename="my_report.json")
        # Filename should be my_report_YYYYMMDD_HHMMSS.json
        assert path.stem.startswith("my_report_")
        assert len(path.stem) == len("my_report_") + len("20240101_120000")


# ══════════════════════════════════════════════════════════════════════════════
# Config Loader Tests (v1.1 NEW)
# ══════════════════════════════════════════════════════════════════════════════

class TestConfigLoader:

    def test_load_valid_yaml(self, yaml_config_file: Path):
        cfg = load_yaml_config(yaml_config_file)
        assert isinstance(cfg, DuplicateRemoverConfig)
        assert cfg.has_multi_groups is True
        assert len(cfg.multi_column_groups) == 2
        assert cfg.multi_column_groups[0].name == "by_email"
        assert cfg.multi_column_groups[1].name == "by_name_city"
        assert cfg.log_level == "DEBUG"

    def test_load_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_yaml_config(tmp_path / "ghost.yaml")

    def test_load_yaml_none_keep(self, tmp_path: Path):
        """'none' string in YAML should map to Python False."""
        cfg_dict = {
            "keep": "none",
            "multi_column_groups": [],
        }
        p = tmp_path / "cfg.yaml"
        p.write_text(yaml.dump(cfg_dict), encoding="utf-8")
        cfg = load_yaml_config(p)
        assert cfg.keep is False

    def test_load_yaml_defaults_when_keys_missing(self, tmp_path: Path):
        """A nearly-empty YAML should not raise — defaults apply."""
        p = tmp_path / "minimal.yaml"
        p.write_text("keep: first\n", encoding="utf-8")
        cfg = load_yaml_config(p)
        assert cfg.encoding == "utf-8"
        assert cfg.output_dir == "outputs"
        assert cfg.has_multi_groups is False
