#!/usr/bin/env python
"""Check whether this repository can run on a fresh agent environment (Claude Code / Codex / QoderWork)."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "amazon-supplement-boundary-analysis"
FINALIZER_SKILL = ROOT / "skills" / "supplement-audience-satellite-formula-finalizer"
SCRATCH = ROOT / "outputs" / "scratch" / "portability-check"


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def check_exists(path: Path, label: str) -> None:
    if not path.exists():
        fail(f"Missing {label}: {path}")
    ok(f"{label}: {path.relative_to(ROOT)}")


def check_import(module: str) -> None:
    try:
        importlib.import_module(module)
    except Exception as exc:  # pragma: no cover - diagnostic script
        fail(f"Cannot import {module}: {exc}")
    ok(f"Python dependency importable: {module}")


def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        fail(f"Command failed: {' '.join(command)}")
    return result.stdout.strip()


def main() -> None:
    check_exists(ROOT / "README.md", "README")
    check_exists(ROOT / "requirements.txt", "requirements")
    check_exists(ROOT / ".gitignore", "gitignore")
    check_exists(SKILL / "SKILL.md", "skill")
    check_exists(SKILL / "agents" / "openai.yaml", "Codex skill UI metadata")
    check_exists(SKILL / "assets" / "radar_scores_template.json", "radar score template")
    check_exists(SKILL / "assets" / "case_config_template.json", "case config template")

    for name in [
        "create_case_workspace.py",
        "analyze_sif_excel.py",
        "generate_radar.py",
    ]:
        check_exists(SKILL / "scripts" / name, f"skill script {name}")

    for name in [
        "workflow.md",
        "output-contract.md",
        "scoring-rubric.md",
        "supplement-facts-guidelines.md",
    ]:
        check_exists(SKILL / "references" / name, f"skill reference {name}")

    check_exists(FINALIZER_SKILL / "SKILL.md", "finalizer skill")
    check_exists(FINALIZER_SKILL / "agents" / "openai.yaml", "finalizer skill UI metadata")
    for name in [
        "audience-first-framework.md",
        "output-template.md",
        "output-contract.md",
        "lab-handoff-checklist.md",
    ]:
        check_exists(FINALIZER_SKILL / "references" / name, f"finalizer skill reference {name}")

    check_exists(ROOT / "scripts" / "analyze_autocomplete.py", "autocomplete analysis script")

    check_exists(ROOT / "AGENTS.md", "AGENTS.md (universal project instructions)")
    check_exists(ROOT / "CLAUDE.md", "CLAUDE.md (Claude Code pointer)")

    for name in [
        "codex-setup.md",
        "agent-setup.md",
        "github-upload-checklist.md",
        "output-organization.md",
    ]:
        check_exists(ROOT / "docs" / name, f"doc {name}")

    check_import("openpyxl")
    check_import("PIL")

    SCRATCH.mkdir(parents=True, exist_ok=True)
    radar_stdout = run(
        [
            sys.executable,
            str(SKILL / "scripts" / "generate_radar.py"),
            str(SKILL / "assets" / "radar_scores_template.json"),
            "--output-dir",
            str(SCRATCH),
            "--name",
            "portability-radar",
        ]
    )
    radar_result = json.loads(radar_stdout)
    check_exists(Path(radar_result["html"]), "generated radar HTML")
    check_exists(Path(radar_result["png"]), "generated radar PNG")

    case_stdout = run(
        [
            sys.executable,
            str(SKILL / "scripts" / "create_case_workspace.py"),
            "--asin",
            "TESTASIN",
            "--core-ingredient",
            "Test Ingredient",
            "--timestamp",
            "20990101-000000",
            "--output-root",
            str(SCRATCH),
        ]
    )
    case_result = json.loads(case_stdout)
    check_exists(Path(case_result["paths"]["case_dir"]), "generated test case folder")
    check_exists(Path(case_result["paths"]["case_dir"]) / "case_config.json", "generated test case config")

    print("\nPortability check passed.")
    print("Generated scratch files are intentionally ignored by Git.")


if __name__ == "__main__":
    main()
