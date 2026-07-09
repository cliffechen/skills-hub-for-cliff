---
name: supplement-keyword-monitor
description: Monitor Amazon US dietary-supplement breakout keywords from AMZ123 Amazon Brand Analytics (ABA/SFR) rankings, classify and translate supplement terms, tier rising opportunities, enrich Tier 1/2 terms with Sorftime trend/CPC/extension data, maintain weekly history, and generate a Chinese HTML opportunity report. Use when Codex needs to run or resume the weekly supplement keyword monitor, find emerging supplement ingredients or benefit terms, inspect Tier 1/2/3 signals, query/export monitoring history, update the supplement dictionary or exclusion rules, or adapt the monitor to another Amazon category.
---

# Amazon Supplement Keyword Monitor

## Objective

Run a three-stage monitoring pipeline with two Agent handoffs. Preserve the original ABA ranking logic while keeping installed Skill files read-only and all runtime state inside the user's chosen workspace.

## Read the relevant references

- Read [configuration.md](references/configuration.md) before first use, dependency setup, API configuration, or troubleshooting.
- Read [exchange-schemas.md](references/exchange-schemas.md) before writing either Agent output JSON file.
- Read [methodology.md](references/methodology.md) before interpreting tiers, burst types, or business opportunities.

## Resolve locations

Treat the directory containing this file as `<skill-root>`. Run scripts from the user's target workspace, not from the installed Skill directory.

The scripts create:

- `<workspace>/reports/`: HTML reports, logs, CSV exports, and exchange JSON files.
- `<workspace>/.supplement-keyword-monitor/data/`: mutable dictionary, exclusion rules, and SQLite history.

Set `SUPPLEMENT_MONITOR_WORKSPACE` only when the process cannot use the target workspace as its working directory.

## Run the workflow

### 1. Perform preflight checks

1. Confirm Python 3.9 or newer.
2. Run `python <skill-root>/scripts/smoke_test.py` on first installation.
3. Check imports for `httpx`, `selectolax`, and `jinja2`. If missing, install from `<skill-root>/scripts/requirements.txt`.
4. Configure `SORFTIME_API_KEY` through an environment variable or `<workspace>/.env` when Sorftime enrichment is wanted. Never display, log, or copy the actual key into Skill files.
5. Explain that a full run accesses AMZ123 and Sorftime and writes workspace files.
6. Preserve existing workspace runtime data. Do not delete history or overwrite customized dictionaries.

### 2. Run stage 1: scrape and prepare classification

Run this command with the target workspace as the working directory:

```text
python <skill-root>/scripts/main.py step1
```

Stop if the command exits nonzero. A low scrape count means the upstream page or network likely failed; do not continue with stale or partial data.

Read `reports/.exchange/llm_input.json`. If it contains keywords, classify every exact key and write `reports/.exchange/llm_output.json` according to [exchange-schemas.md](references/exchange-schemas.md).

Use only these labels: `ingredient`, `benefit`, `brand`, `condition`, `form`, `unrelated`. Provide a non-empty Chinese translation for every input, including unrelated terms. Do not add, normalize, drop, or rename keyword keys.

### 3. Run stage 2: tier and enrich

Run:

```text
python <skill-root>/scripts/main.py step2
```

The script validates classification coverage before changing the workspace dictionary. It then filters exclusions, removes falling or flat ABA terms, assigns Tier 1/2/3, optionally queries Sorftime, updates SQLite history, and writes `reports/.exchange/analysis_input.json`.

Stop on validation, API, or file errors. Do not fabricate missing Sorftime fields.

### 4. Write the analysis handoff

Read `reports/.exchange/analysis_input.json` and [methodology.md](references/methodology.md). Write `reports/.exchange/analysis_output.json` according to [exchange-schemas.md](references/exchange-schemas.md).

For every Tier 1 keyword:

1. Explain the ABA rank movement first.
2. Use monthly search volume, CPC, and extension terms only as supporting evidence.
3. State the opportunity, competition, and material risk in concise Chinese.
4. Avoid unsupported medical, regulatory, or profitability claims.

Cluster every Tier 1 keyword exactly once. Keep all findings traceable to fields present in `analysis_input.json`.

### 5. Run stage 3: render and verify

Run:

```text
python <skill-root>/scripts/main.py step3
```

The script refuses incomplete analysis JSON. Verify that:

- `reports/supplement_monitor_YYYY-WXX.html` exists and is non-empty.
- The report shows the current ISO week and Tier counts.
- The weekly log contains stages 1, 2, and 3.
- No API key appears in the report, log, or exchange files.

Present the HTML report path and a short answer-first summary of the strongest signals and limitations.

## Resume or perform narrower tasks

- If `llm_input.json` exists but `llm_output.json` is missing or invalid, complete classification and resume at stage 2.
- If `analysis_input.json` exists but `analysis_output.json` is missing or invalid, complete analysis and resume at stage 3.
- If only the HTML layout changed, rerun stage 3.
- For the latest historical overview, run `python <skill-root>/scripts/view_data.py`.
- Add `--tier 1`, `--keyword <term>`, `--weeks`, or `--export` for narrower history tasks.

## Customize safely

Edit the workspace copies under `<workspace>/.supplement-keyword-monitor/data/`, never the bundled seed files:

- `supplement_dict.json`: supplement ingredients, benefits, brands, and health markers.
- `exclusion_rules.json`: exact exclusions plus non-human and non-ingestible regex patterns.

To adapt another category, use a separate workspace and replace both runtime files together. Keep schema keys unchanged unless the Python logic is also updated.

## Guardrails

- Treat a smaller ABA rank number as better. Calculate movement as previous rank minus current rank.
- Use ABA rank as the trend direction source of truth; use Sorftime volume as supporting context.
- Treat this as market-signal research, not medical, legal, or guaranteed-profit advice.
- Do not commit `.env`, runtime databases, reports, logs, exchange files, or cache files into a distributed Skill.
- Do not bypass the minimum scrape guard merely to finish a run; diagnose the upstream failure first.
- Do not change the user's existing project files unless the user explicitly asks for maintenance beyond running the monitor.
