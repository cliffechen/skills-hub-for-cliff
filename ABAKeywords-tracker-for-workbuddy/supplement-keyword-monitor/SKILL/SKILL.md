---
name: supplement-keyword-monitor
description: Monitor Amazon US dietary-supplement breakout keywords from AMZ123 Amazon Brand Analytics (ABA/SFR) rankings, classify and translate supplement terms, tier rising opportunities, enrich Tier 1/2 terms with Sorftime trend/CPC/extension data, maintain weekly history, and generate a Chinese HTML opportunity report. Use when WorkBuddy needs to run or resume the weekly supplement keyword monitor, find emerging supplement ingredients or benefit terms, inspect Tier 1/2/3 signals, query/export monitoring history, update the supplement dictionary or exclusion rules, or adapt the monitor to another Amazon category.
---

# Amazon Supplement Keyword Monitor

## Objective

Run the three-stage monitor with two WorkBuddy reasoning handoffs. Keep the installed Skill read-only and write all mutable state to the user's chosen workspace.

## Load references as needed

- Read [configuration.md](references/configuration.md) for first use, setup, paths, and troubleshooting.
- Read [exchange-schemas.md](references/exchange-schemas.md) before writing Agent exchange JSON.
- Read [methodology.md](references/methodology.md) before interpreting tiers or market opportunities.

Treat the directory containing this file as `<skill-root>`. Run commands with the user's target workspace as the working directory.

## Run the complete workflow

### 1. Check the environment

1. Require Python 3.9 or newer.
2. Run `python <skill-root>/scripts/smoke_test.py` on first installation.
3. If packages are missing, install `<skill-root>/requirements.txt`.
4. Read `SORFTIME_API_KEY` only from the environment or `<workspace>/.env`. Never display or log it.
5. Explain that a full run accesses AMZ123 and optionally Sorftime, then writes workspace files.

### 2. Run stage 1

```text
python <skill-root>/scripts/main.py step1
```

Stop on a nonzero exit. Read `reports/.exchange/llm_input.json`, classify every exact keyword, and write `llm_output.json` using [exchange-schemas.md](references/exchange-schemas.md).

Use only `ingredient`, `benefit`, `brand`, `condition`, `form`, and `unrelated`. Provide a non-empty Chinese translation for every item. Do not rename, add, or drop keys.

### 3. Run stage 2

```text
python <skill-root>/scripts/main.py step2
```

Let the script validate classification coverage, filter exclusions, remove falling/flat ABA terms, assign tiers, query optional Sorftime enrichment, update history, and write `analysis_input.json`.

Stop on validation or file errors. Never invent missing Sorftime values.

### 4. Write Tier 1 analysis

Read `analysis_input.json`, [exchange-schemas.md](references/exchange-schemas.md), and [methodology.md](references/methodology.md). Write `analysis_output.json`.

- Lead with ABA rank movement.
- Use search volume, CPC, and extensions as supporting evidence only.
- Explain opportunity, competition, uncertainty, and material risks in concise Chinese.
- Cluster every Tier 1 keyword exactly once.
- Avoid unsupported medical, regulatory, or profitability claims.

### 5. Run stage 3 and deliver

```text
python <skill-root>/scripts/main.py step3
```

Verify the current-week HTML report, Tier counts, complete three-stage log, and absence of API keys. Present the HTML file through WorkBuddy's available file-sharing surface or provide its absolute path, followed by a brief strongest-signals summary.

## Resume and query

- Complete missing `llm_output.json` and resume at stage 2.
- Complete missing `analysis_output.json` and resume at stage 3.
- Rerun stage 3 after template-only changes.
- Run `python <skill-root>/scripts/view_data.py` for the latest overview.
- Add `--tier 1`, `--keyword <term>`, `--weeks`, or `--export` for narrower history queries.

## Customize safely

Edit only the workspace copies under `<workspace>/.supplement-keyword-monitor/data/`. Do not edit bundled `data/` seeds after installation.

Keep `supplement_dict.json` and `exclusion_rules.json` together when adapting another category. Use a separate workspace to avoid mixing histories.

## Guardrails

- Interpret smaller ABA rank numbers as stronger; calculate movement as previous minus current.
- Use ABA rank for direction and Sorftime volume only for supporting context.
- Treat outputs as research signals, not medical, legal, or guaranteed-profit advice.
- Never distribute `.env`, `history.db`, reports, logs, exchange JSON, caches, or compiled Python files.
- Stop on an abnormally low scrape instead of publishing a partial report.
