#!/usr/bin/env python3
"""Offline preflight for the portable Amazon research skill."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


SKILL_NAME = "amazon-sorftime-mcp-with-serpapi-tavily"


def codex_home() -> Path:
    return Path(os.getenv("CODEX_HOME") or (Path.home() / ".codex"))


def check(name: str, ok: bool, required: bool, detail: str, fix: str = "") -> dict:
    return {
        "name": name,
        "ok": bool(ok),
        "required": required,
        "detail": detail,
        "fix": fix if not ok else "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check local dependencies without network calls.")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    home = codex_home()
    config_path = home / "config.toml"
    config = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    sorftime_match = re.search(
        r"https://mcp\.sorftime\.com\?key=([^\"\s]+)", config, flags=re.IGNORECASE
    )
    sorftime_configured = bool(
        sorftime_match
        and sorftime_match.group(1)
        and "REPLACE_WITH" not in sorftime_match.group(1).upper()
    )
    tavily_env = bool(os.getenv("TAVILY_API_KEY", "").strip())
    serpapi_env = bool(os.getenv("SERPAPI_KEY", "").strip())
    tavily_mcp = bool(re.search(r"\[mcp_servers\.tavily", config, flags=re.IGNORECASE))
    required_files = [
        root / "SKILL.md",
        root / "references" / "methodology.md",
        root / "references" / "keyword-drift.md",
        root / "scripts" / "analyze_keyword_drift.py",
        root / "scripts" / "validate_research_data.py",
        root / "scripts" / "render_report.py",
        root / "scripts" / "fetch_serpapi_google_trends.py",
    ]

    checks = [
        check(
            "Python 3.10+ for skill scripts",
            sys.version_info >= (3, 10),
            True,
            f"detected {sys.version.split()[0]}",
            "Install Python 3.10 or newer.",
        ),
        check(
            "Skill package files",
            all(path.is_file() for path in required_files),
            True,
            str(root),
            "Re-extract or reinstall the skill package.",
        ),
        check(
            "Sorftime MCP",
            sorftime_configured,
            True,
            "configured" if sorftime_configured else "missing or placeholder",
            "Add the Sorftime MCP URL with your local API key in Codex Settings/config.toml.",
        ),
        check(
            "Tavily MCP",
            tavily_env and tavily_mcp,
            True,
            f"environment={'yes' if tavily_env else 'no'}, mcp={'yes' if tavily_mcp else 'no'}",
            "Set TAVILY_API_KEY for the Windows user and add the Tavily MCP section.",
        ),
        check(
            "SerpApi Google Trends",
            serpapi_env,
            False,
            "environment=yes" if serpapi_env else "optional environment variable missing",
            "Set SERPAPI_KEY to use the preferred Google Web Trends collector; a user-supplied Web CSV is the fallback.",
        ),
        check(
            "Feishu credentials",
            bool(os.getenv("FEISHU_APP_ID") and os.getenv("FEISHU_APP_SECRET")),
            False,
            "optional; required only for Bitable delivery",
            "Configure the optional bundled feishu-mcp/.env when delivery is needed.",
        ),
    ]

    payload = {
        "skill": SKILL_NAME,
        "codex_home": str(home),
        "config_path": str(config_path),
        "checks": checks,
        "core_ready": all(item["ok"] for item in checks if item["required"]),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in checks:
            marker = "OK" if item["ok"] else ("MISSING" if item["required"] else "OPTIONAL")
            print(f"[{marker}] {item['name']}: {item['detail']}")
            if item["fix"]:
                print(f"  -> {item['fix']}")
        print("READY" if payload["core_ready"] else "NOT_READY")
    raise SystemExit(0 if payload["core_ready"] else 1)


if __name__ == "__main__":
    main()
