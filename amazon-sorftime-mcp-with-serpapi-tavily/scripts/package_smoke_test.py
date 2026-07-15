#!/usr/bin/env python3
"""Offline structural, rendering, connector, and secret-safety smoke test."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EXAMPLE = ROOT / "assets" / "examples" / "algae-calcium" / "data.json"
KEYWORD_SELECTION_EXAMPLE = ROOT / "assets" / "examples" / "keyword-selection-input.json"


def run(*args: str, cwd: Path | None = None, env: dict | None = None) -> str:
    process = subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
    )
    if process.returncode:
        raise AssertionError(
            f"command failed ({process.returncode}): {' '.join(args)}\n"
            f"stdout:\n{process.stdout}\nstderr:\n{process.stderr}"
        )
    return process.stdout


def assert_layout() -> None:
    required = [
        ROOT / "SKILL.md",
        ROOT / "README.md",
        ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "methodology.md",
        ROOT / "references" / "keyword-drift.md",
        ROOT / "references" / "source-routing.md",
        ROOT / "references" / "sorftime-tool-map.md",
        ROOT / "scripts" / "analyze_keyword_drift.py",
        KEYWORD_SELECTION_EXAMPLE,
        ROOT / "scripts" / "render_report.py",
        ROOT / "scripts" / "preflight.py",
        ROOT / "scripts" / "validate_deliverables.py",
        ROOT / "assets" / "config" / "codex-config.example.toml",
        EXAMPLE,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise AssertionError(f"missing package files: {missing}")


def assert_no_secrets() -> None:
    patterns = {
        "live Tavily-style key": re.compile(r"tvly-(?!REPLACE|YOUR)[A-Za-z0-9_-]{16,}"),
        "live Sorftime URL key": re.compile(
            r"mcp\.sorftime\.com\?key=(?!REPLACE|YOUR|<)[A-Za-z0-9_-]{12,}",
            re.IGNORECASE,
        ),
        "filled Feishu secret": re.compile(
            r"FEISHU_APP_SECRET\s*=\s*(?!REPLACE|YOUR|$)[^\r\n#]+", re.IGNORECASE
        ),
        "filled SerpApi secret": re.compile(
            r"SERPAPI_KEY\s*=\s*(?!REPLACE|YOUR|$)[A-Fa-f0-9]{32,}", re.IGNORECASE
        ),
    }
    text_suffixes = {".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".py", ".ps1", ".html"}
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in patterns.items():
            if pattern.search(content):
                hits.append(f"{path.relative_to(ROOT)}: {label}")
    if hits:
        raise AssertionError("secret scan failed:\n" + "\n".join(hits))


def assert_example_pipeline() -> None:
    run(sys.executable, str(SCRIPTS / "validate_research_data.py"), str(EXAMPLE))
    with tempfile.TemporaryDirectory(prefix="amazon-skill-smoke-") as temp_dir:
        output = Path(temp_dir) / "report.html"
        run(
            sys.executable,
            str(SCRIPTS / "render_report.py"),
            str(EXAMPLE),
            "--output",
            str(output),
        )
        content = output.read_text(encoding="utf-8")
        required_fragments = ["algae calcium", "VERIFY", "核心指标", "三道门判断", "数据源统计"]
        for fragment in required_fragments:
            if fragment not in content:
                raise AssertionError(f"rendered report missing: {fragment}")
        if "https://cdn" in content or "<script src=" in content:
            raise AssertionError("rendered report must be self-contained")


def assert_keyword_selection() -> None:
    with tempfile.TemporaryDirectory(prefix="amazon-keyword-selection-") as temp_dir:
        output = Path(temp_dir) / "selection.json"
        run(
            sys.executable,
            str(SCRIPTS / "analyze_keyword_drift.py"),
            str(KEYWORD_SELECTION_EXAMPLE),
            "--output",
            str(output),
        )
        result = json.loads(output.read_text(encoding="utf-8"))
        if result.get("primary_research_keyword") != "algaecal":
            raise AssertionError("keyword selection example must hand off to algaecal")
        if result.get("keyword_handoff") is not True:
            raise AssertionError("keyword selection example must record a keyword handoff")
        algae_supplement = next(
            item for item in result["terms"] if item["keyword"] == "algae supplement"
        )
        if algae_supplement["scoring"]["eligible"] is not False:
            raise AssertionError("broad, low-relevance keyword must fail the hard gates")

        report_data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        report_data["run"]["primary_research_keyword"] = "algaecal"
        report_data["run"]["keyword_handoff"] = True
        report_data["market_capacity"]["primary_keyword_selection"] = {
            "value": result,
            "unit": None,
            "definition": "Deterministic keyword selection smoke test",
            "source": "sorftime",
            "retrieved_at": result["generated_at"],
            "status": "derived",
            "raw_file": None,
            "notes": "Synthetic scoring fixture for renderer validation.",
        }
        selected_data = Path(temp_dir) / "selected-data.json"
        selected_html = Path(temp_dir) / "selected-report.html"
        selected_data.write_text(json.dumps(report_data), encoding="utf-8")
        run(
            sys.executable,
            str(SCRIPTS / "validate_research_data.py"),
            str(selected_data),
        )
        run(
            sys.executable,
            str(SCRIPTS / "render_report.py"),
            str(selected_data),
            "--output",
            str(selected_html),
        )
        selected_content = selected_html.read_text(encoding="utf-8")
        for fragment in (
            "algae calcium → algaecal",
            "主调研词自动选择",
            "25,301.35",
            "algae supplement",
            "listing_relevance_below_70pct",
        ):
            if fragment not in selected_content:
                raise AssertionError(f"selected-keyword report missing: {fragment}")


def assert_fixed_deliverables() -> None:
    with tempfile.TemporaryDirectory(prefix="amazon-fixed-deliverables-") as temp_dir:
        run_dir = Path(temp_dir) / "research-run"
        json_artifacts = [
            run_dir / "raw" / "sorftime" / "keyword-selection-input.json",
            run_dir / "raw" / "sorftime" / "keyword-drift-analysis.json",
            run_dir / "raw" / "google-trends" / "analysis.json",
            run_dir / "raw" / "tavily" / "retained-sources.json",
            run_dir / "raw" / "source-usage.json",
            run_dir / "data.json",
        ]
        for artifact in json_artifacts:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("{}", encoding="utf-8")
        (run_dir / "report.md").write_text("# Report\n", encoding="utf-8")
        html = run_dir / "html" / "report.html"
        html.parent.mkdir(parents=True, exist_ok=True)
        html.write_text("<!doctype html><title>Report</title>", encoding="utf-8")
        run(sys.executable, str(SCRIPTS / "validate_deliverables.py"), str(run_dir))


def assert_feishu_connector() -> None:
    connector = ROOT / "assets" / "feishu-mcp"
    env = os.environ.copy()
    env["FEISHU_SKIP_DOTENV"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    run(
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v",
        cwd=connector,
        env=env,
    )


def main() -> None:
    assert_layout()
    assert_no_secrets()
    assert_example_pipeline()
    assert_keyword_selection()
    assert_fixed_deliverables()
    assert_feishu_connector()
    print("SMOKE_TEST_OK")


if __name__ == "__main__":
    main()
