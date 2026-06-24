# Output Contract

## Folder Naming

Every complete run must write into:

```text
outputs/cases/{ASIN}-{core-ingredient}-{yyyyMMdd-HHmmss}/
```

Use filesystem-safe names:

- Uppercase ASIN.
- Convert core ingredient to short hyphen-case ASCII when possible.
- Timestamp format: `yyyyMMdd-HHmmss`.

Example:

```text
outputs/cases/B0GKPTBN59-C15-Pentadecanoic-Acid-20260421-133715/
```

## Standard Files

Recommended names:

```text
{name}-ingredient-traffic-boundary-report.md
{name}-solution-comparison.md
{name}-radar-chart.html
{name}-radar-chart.png
{name}-scheme-{direction}-supplement-facts-3-variants.md
{name}-final-{ingredient-stack}-softgel-formula.md
```

## Language Contract

Formal report deliverables are Chinese-first:

- `{name}-ingredient-traffic-boundary-report.md` must be a Chinese report.
- `{name}-solution-comparison.md` must be a Chinese comparison report.
- Radar-chart titles, notes, legends, and scoring rationale must be Chinese.
- Formal report section titles, table headers, risk labels, posture labels, and synthesized table cells must be Chinese. Do not reuse English table scaffolding from upstream skills such as `Observed Ingredient Table`, `Ingredient Classification`, `Risk Matrix`, `Missing Evidence Points`, `Rebuild Posture Summary`, `ingredient_name`, `TM_risk`, `keep concept`, or `legal review`.
- Source evidence files may preserve raw English data, but any synthesized judgment, conclusion, or recommendation should be Chinese.
- Keep exact English ASINs, product titles, ingredient names, keyword strings, regulatory terms, and URLs unchanged when translation would reduce precision.

Do not output an English formal report unless the user explicitly asks for English.

Before final delivery, run the Chinese deliverable validation gate against formal Markdown reports:

```powershell
python skills/amazon-supplement-boundary-analysis/scripts/validate_chinese_deliverable.py "outputs/cases/{case}/deliverables/*-ingredient-traffic-boundary-report.md" "outputs/cases/{case}/deliverables/*-solution-comparison.md"
```

## Separation Rules

- `skills/`: reusable skill, scripts, templates, references only.
- `outputs/cases/`: final case deliverables.
- `outputs/inputs/`: copied input files.
- `outputs/scratch/`: intermediate or exploratory files.
- `outputs/legacy/`: old project outputs retained for reference.
- `result/` and `formula-reconstruction-result/`: legacy historical sinks. Do not place new final deliverables there.

For the final formula-closing stage, use the current case directory only:

```text
outputs/cases/{case}/deliverables/final/{name}-final-formula-brief.md
```

Do not write generated reports, charts, or case JSON into the skill directory.
