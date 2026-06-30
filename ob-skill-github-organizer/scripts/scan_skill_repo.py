#!/usr/bin/env python3
"""Scan a local Agent Skills repository and emit a compact JSON inventory."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*", re.DOTALL)


def run_git(repo: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return completed.stdout.strip()
    except Exception:
        return ""


def read_text(path: Path, limit: int = 12000) -> str:
    try:
        data = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""
    return data[:limit]


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_-]+:\s*", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            result[current_key] = value.strip().strip('"').strip("'")
        elif current_key:
            result[current_key] += " " + line.strip().strip('"').strip("'")
    return result


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def direct_children(path: Path) -> list[str]:
    try:
        return sorted(child.name for child in path.iterdir() if child.name != ".git")
    except Exception:
        return []


def detect_platform(skill_dir: Path, root: Path, skill_text: str) -> list[str]:
    labels: list[str] = []
    rel_path = rel(skill_dir, root).lower()
    has_root_skill = (skill_dir / "SKILL.md").exists()
    has_nested_skill = (skill_dir / "SKILL" / "SKILL.md").exists()
    has_wb_readme = (skill_dir / "README_WORKBUDDY.md").exists()
    has_openai_yaml = (skill_dir / "agents" / "openai.yaml").exists()
    lower_text = skill_text.lower()
    is_wb_dir = rel_path.endswith("-wb") or "workbuddy" in rel_path

    if has_wb_readme and has_nested_skill:
        labels.append("WorkBuddy standard package")
    elif is_wb_dir:
        labels.append("WorkBuddy directory")

    if "agent-agnostic" in lower_text or "workspace skill" in lower_text:
        labels.append("Agent generic")

    if has_openai_yaml and not is_wb_dir:
        labels.append("Codex/OpenAI original")

    if has_root_skill and not labels:
        labels.append("Codex/Claude/QoderWork compatible")

    if has_root_skill and not has_wb_readme and not has_nested_skill:
        labels.append("WorkBuddy convertible")

    return labels


def find_skill_dirs(root: Path) -> list[Path]:
    skill_dirs: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        if ".git" in current.parts:
            continue
        dirnames[:] = [d for d in dirnames if d != ".git"]
        if "SKILL.md" in filenames:
            skill_dirs.add(current)
        if (current / "SKILL" / "SKILL.md").exists():
            skill_dirs.add(current)
    return sorted(skill_dirs, key=lambda p: rel(p, root))


def scan_repo(root: Path) -> dict[str, Any]:
    root = root.resolve()
    skills: list[dict[str, Any]] = []
    for skill_dir in find_skill_dirs(root):
        skill_file = skill_dir / "SKILL.md"
        nested_skill_file = skill_dir / "SKILL" / "SKILL.md"
        entry_file = skill_file if skill_file.exists() else nested_skill_file
        skill_text = read_text(entry_file)
        fm = parse_frontmatter(skill_text)
        rel_path = rel(skill_dir, root)
        git_date = run_git(root, ["log", "-1", "--format=%cI", "--", rel_path])
        git_subject = run_git(root, ["log", "-1", "--format=%s", "--", rel_path])
        children = direct_children(skill_dir)
        skills.append(
            {
                "path": rel_path,
                "name": fm.get("name") or skill_dir.name,
                "description": fm.get("description", ""),
                "entry": rel(entry_file, root),
                "latest_commit_date": git_date,
                "latest_commit_subject": git_subject,
                "direct_children": children,
                "has_root_skill": skill_file.exists(),
                "has_nested_workbuddy_skill": nested_skill_file.exists(),
                "has_readme": (skill_dir / "README.md").exists(),
                "has_readme_workbuddy": (skill_dir / "README_WORKBUDDY.md").exists(),
                "has_agents_openai": (skill_dir / "agents" / "openai.yaml").exists(),
                "has_references": (skill_dir / "references").is_dir(),
                "has_scripts": (skill_dir / "scripts").is_dir(),
                "has_assets": (skill_dir / "assets").is_dir(),
                "platform_labels": detect_platform(skill_dir, root, skill_text),
            }
        )
    return {"repo_path": str(root), "skill_count": len(skills), "skills": skills}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a local skills repository.")
    parser.add_argument("--repo-path", required=True, help="Local repository path.")
    parser.add_argument("--output-json", help="Write JSON to this path. Defaults to stdout.")
    args = parser.parse_args()

    inventory = scan_repo(Path(args.repo_path))
    payload = json.dumps(inventory, ensure_ascii=False, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
