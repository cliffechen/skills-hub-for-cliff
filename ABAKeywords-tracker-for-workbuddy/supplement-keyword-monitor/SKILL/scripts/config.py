"""Portable configuration for the Amazon supplement keyword monitor.

The installed skill is treated as read-only. Mutable dictionaries, the SQLite
database, exchange JSON files, logs, and reports live in the user's workspace.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def _find_first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


# Codex packages keep reusable files in assets/. WorkBuddy packages keep them
# directly under the installed skill root. Supporting both layouts lets the two
# platform packages share one Python implementation.
BUNDLED_DATA_DIR = _find_first_existing(
    SKILL_DIR / "assets" / "data",
    SKILL_DIR / "data",
)
TEMPLATE_DIR = _find_first_existing(
    SKILL_DIR / "assets" / "templates",
    SKILL_DIR / "templates",
)
REQUIREMENTS_PATH = _find_first_existing(
    SCRIPT_DIR / "requirements.txt",
    SKILL_DIR / "requirements.txt",
)


def ensure_dependencies() -> None:
    """Stop with a copyable install command instead of silently installing code."""
    packages = {
        "httpx": "httpx",
        "selectolax": "selectolax",
        "jinja2": "jinja2",
    }
    missing = [label for label, module in packages.items() if importlib.util.find_spec(module) is None]
    if not missing:
        return
    print("Missing Python packages: " + ", ".join(missing))
    print(f'Install them with: "{sys.executable}" -m pip install -r "{REQUIREMENTS_PATH}"')
    raise SystemExit(2)


ensure_dependencies()


def _workspace_root() -> Path:
    configured = os.environ.get("SUPPLEMENT_MONITOR_WORKSPACE", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path.cwd().resolve()


WORKSPACE_ROOT = _workspace_root()
REPORT_DIR = WORKSPACE_ROOT / "reports"
EXCHANGE_DIR = REPORT_DIR / ".exchange"
RUNTIME_DIR = WORKSPACE_ROOT / ".supplement-keyword-monitor"
DATA_DIR = RUNTIME_DIR / "data"
DICT_PATH = DATA_DIR / "supplement_dict.json"
DB_PATH = DATA_DIR / "history.db"


def ensure_runtime_data() -> None:
    """Seed mutable workspace data without overwriting user customizations."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename in ("supplement_dict.json", "exclusion_rules.json"):
        source = BUNDLED_DATA_DIR / filename
        destination = DATA_DIR / filename
        if not destination.exists():
            if not source.exists():
                raise FileNotFoundError(f"Bundled data file not found: {source}")
            shutil.copy2(source, destination)


ensure_runtime_data()


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


_WORKSPACE_ENV = _read_env_file(WORKSPACE_ROOT / ".env")


def _setting(name: str, default: str) -> str:
    return os.environ.get(name) or _WORKSPACE_ENV.get(name) or default


# AMZ123 scraping configuration.
AMZ123_BASE_URL = "https://www.amz123.com/usatopkeywords"
MAX_PAGES = int(_setting("SUPPLEMENT_MONITOR_MAX_PAGES", "5"))
MIN_SCRAPED_KEYWORDS = int(_setting("SUPPLEMENT_MONITOR_MIN_SCRAPED", "500"))
SCRAPE_COMBOS = [
    {"rank": "1_1000", "uprank": "1001", "label": "高排名+高涨幅"},
    {"rank": "1001_10000", "uprank": "1001", "label": "中排名+高涨幅"},
    {"rank": "10001_50000", "uprank": "1001", "label": "低排名+高涨幅"},
    {"rank": "50001", "uprank": "1001", "label": "超低排名+高涨幅"},
    {"rank": "1_1000", "uprank": "101_1000", "label": "高排名+中涨幅"},
    {"rank": "1001_10000", "uprank": "101_1000", "label": "中排名+中涨幅"},
]

# Tier thresholds. The analyzer retains every rising supplement-related term
# and uses these thresholds for its primary breakout rules and rank buckets.
TIER1_RANK_THRESHOLD = 1000
TIER2_RANK_THRESHOLD = 50000
TIER1_SURGE_RATIO = 0.5
TIER1_SURGE_ABS = 1000
TIER2_CROSS_FROM = 100000
TIER2_CROSS_TO = 50000
TIER3_CROSS_FROM = 200000
TIER3_CROSS_TO = 100000
REBOUND_PEAK_THRESHOLD = 100


def _detect_proxy() -> str:
    """Return the current system proxy with a protocol accepted by httpx."""
    try:
        import urllib.request

        proxies = urllib.request.getproxies()
        raw = proxies.get("http", proxies.get("https", ""))
        return raw.replace("https://", "http://") if raw else ""
    except Exception:
        return ""


HTTPX_PROXY = _detect_proxy() or None
SORFTIME_BASE_URL = "https://mcp.sorftime.com"
SORFTIME_CONCURRENCY = int(_setting("SORFTIME_CONCURRENCY", "10"))
SORFTIME_TIMEOUT = int(_setting("SORFTIME_TIMEOUT", "30"))
VERIFY_SSL = _setting("VERIFY_SSL", "true").lower() == "true"
SORFTIME_API_KEY = (
    os.environ.get("SORFTIME_API_KEY", "").strip()
    or _WORKSPACE_ENV.get("SORFTIME_API_KEY", "").strip()
)


def check_ready() -> bool:
    """Report whether optional Sorftime enrichment is configured."""
    if SORFTIME_API_KEY:
        return True
    print("\nSorftime API Key is not configured.")
    print("Set SORFTIME_API_KEY in the environment or in <workspace>/.env.")
    print("The workflow can continue, but Sorftime trend, CPC, and extension data will be skipped.\n")
    return False
