# Configuration and operation

## Requirements

- Python 3.9 or newer.
- Internet access to AMZ123 for ABA pages.
- Optional Sorftime API Key for trend, CPC, and extended-keyword enrichment.
- Python packages listed in `requirements.txt`.

Install dependencies from the target workspace:

```text
python -m pip install -r <skill-root>/requirements.txt
```

Success means the command exits without an error. If the Python command is unavailable, locate or install Python before running the monitor.

## Workspace selection

Use the user's target project or output directory as the process working directory. The Skill resolves that directory as `<workspace>`.

If the execution environment cannot set its working directory, set:

```text
SUPPLEMENT_MONITOR_WORKSPACE=<absolute-workspace-path>
```

Never point this at the installed Skill directory.

## Sorftime configuration

Prefer an environment variable named `SORFTIME_API_KEY`. Alternatively, create `<workspace>/.env` from the bundled safe example and fill only the local copy:

```text
SORFTIME_API_KEY=
VERIFY_SSL=true
```

The Agent performs classification and report writing directly, so no separate LLM API Key is needed.

If Sorftime is not configured, the pipeline still creates a report, but trend history, CPC, extensions, and burst-type evidence may be absent.

## Optional settings

| Variable | Default | Purpose |
|---|---:|---|
| `VERIFY_SSL` | `true` | Verify HTTPS certificates. Keep enabled. |
| `SUPPLEMENT_MONITOR_MAX_PAGES` | `5` | Maximum pages per AMZ123 query combination. |
| `SUPPLEMENT_MONITOR_MIN_SCRAPED` | `500` | Abort threshold for suspiciously small scrapes. |
| `SORFTIME_CONCURRENCY` | `10` | Maximum concurrent Sorftime keyword jobs. |
| `SORFTIME_TIMEOUT` | `30` | Sorftime request timeout in seconds. |

Only set `VERIFY_SSL=false` as a temporary diagnostic for a known local proxy problem. Re-enable certificate verification afterward.

## Runtime files

```text
<workspace>/
├── .env                                      # optional; never commit
├── .supplement-keyword-monitor/
│   └── data/
│       ├── supplement_dict.json              # mutable workspace copy
│       ├── exclusion_rules.json              # mutable workspace copy
│       └── history.db                        # generated SQLite history
└── reports/
    ├── .exchange/                            # generated Agent handoffs
    ├── run_YYYY-WXX.log
    └── supplement_monitor_YYYY-WXX.html
```

The first script run seeds the two JSON configuration files without overwriting later user changes.

## Failure handling

- Exit code 2 with missing packages: install `requirements.txt`.
- Stage 1 scrape below the safe minimum: stop; inspect network access or AMZ123 page structure.
- Missing or invalid `llm_output.json`: repair it against `llm_input.json`; do not bypass validation.
- Missing or invalid `analysis_output.json`: repair it against `analysis_input.json`; do not publish a partial report.
- Sorftime failures: retain ABA-only results and clearly disclose missing enrichment.
- Proxy or TLS errors: inspect the system proxy first. Do not permanently disable SSL verification.
