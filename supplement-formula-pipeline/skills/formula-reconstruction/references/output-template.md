# Output Template

Use this section order unless the user explicitly asks for another format.

## 1. Executive Summary

Include:

- optimization objective
- anchor keyword(s) selected and why
- biggest formula upgrade point
- biggest market demand addressed
- biggest remaining uncertainty

## 2. Upstream Inheritance

Summarize from Skill 1 and Skill 2:

- safe ingredient pool (keep concept items)
- forbidden items (avoid items)
- items pending legal review
- Skill 2 candidate directions used as starting point

## 3. Autocomplete Signal Analysis

Summarize the four formula-design signal dimensions extracted from the
Amazon search bar dropdown suggestions:

### Ingredient Association Signals

| associated_ingredient | mention_count | source_suggestions |
| --- | --- | --- |

→ Implication: which ingredients to consider adding to the formula.

### Dosage & Potency Signals

| signal | count | source_suggestions |
| --- | --- | --- |

→ Implication: what dosage level or strength consumers expect.

### Form-Factor Preference Signals

| form | mention_count | source_suggestions |
| --- | --- | --- |

→ Implication: which dosage form to develop as Tier 1 vs Tier 2.

### Audience & Occasion Signals

| audience_or_occasion | count | source_suggestions |
| --- | --- | --- |

→ Implication: which demographic or use-case to optimize the formula for.

If no autocomplete data was available, note the gap explicitly.

## 4. Keyword Competition Matrix

| keyword | monthly_search_volume | ABA_weekly_rank | SPR | PPC_bid | click_concentration | natural_position | assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |

Include:

- anchor keyword recommendation with rationale
- red ocean keywords to deprioritize
- blue ocean or momentum keywords to target

## 5. Market Demand Insights

| insight_type | source | detail | implication_for_formula |
| --- | --- | --- | --- |

Sources should include:

- Amazon reviews (sorftime MCP)
- Reddit discussions (Apify MCP)
- Web research (exa MCP / web search)

## 6. Scientific Evidence Table

| ingredient | effective_dose_range | evidence_level | key_findings | source |
| --- | --- | --- | --- | --- |

Evidence levels: Strong, Moderate, Emerging, Weak

## 7. Candidate Formula Directions

### Tier A — Consumer-Signal-Driven Directions (2-3 directions)

Label each direction with `[消费者信号驱动]`.

For each direction, include:

- direction name
- anchor keyword(s)
- core ingredients and dosages
- changes vs reference product
- scientific rationale
- market demand addressed
- keyword competitive advantage
- claim posture
- commercialization notes

### Tier B — Science-Mechanism-Driven Directions (2 directions)

Label each direction with `[科学机制驱动]`.

Same fields as Tier A, plus:

- **mechanism rationale** — which biological pathways are targeted and why
  the combination is synergistic
- **consumer signal gap** — explicitly note that this combination was NOT
  found in consumer search signals, and explain why it may still be valuable
- scientific rationale
- market demand addressed
- keyword competitive advantage
- claim posture
- commercialization notes

## 8. Risk & Feasibility Notes

List:

- residual IP or compliance risks
- supply chain feasibility concerns
- form factor and manufacturing considerations
- recommended pre-launch checks

## 9. HTML Supplement Facts Label (Post-Confirmation)

> This section is generated **only after** the user selects a formula direction
> and confirms the final ingredient list. It is NOT part of the initial output.

When triggered, produce a self-contained HTML file with:

- **File name**: `{name}-supplement-facts-{YYYY-MM-DD}-{HHmm}.html`
  (use `mcp_sorftimeMCP_get_time` for the timestamp)
- **Save location**: `formula-reconstruction-result/{name}/`
- **Language**: English only
- **Style**: white background, black text, Arial/Helvetica, inline CSS, no external deps

### Left Panel — Supplement Facts Box

```
┌─────────────────────────────────────────┐
│  Supplement Facts                       │  ← .sf-title (36px bold)
│  Serving Size 1 {form} ({weight})       │
│  Servings Per Container {count}         │
│  ═══════════════════════════════════════ │  ← .bar-thick (8px)
│  Amount Per Serving        % Daily Value│
│  ═══════════════════════════════════════ │  ← .bar-thick
│  Calories                  {cal}        │  ← .row .bold
│  ─────────────────────────────────────  │  ← .bar-medium (4px)
│  Total Fat          {g}        {%}*     │  ← .row .bold
│  ─ Saturated Fat    {g}        {%}*     │  ← .row .indent1
│  Total Carbohydrate {g}        {%}*     │  ← .row .bold
│  ─ Dietary Fiber    {g}        {%}*     │  ← .row .indent1
│  ─ Total Sugars     {g}          †      │  ← .row .indent1
│  ── Incl. {x}g Added Sugars   {%}*     │  ← .row .indent2
│  Protein            {g}        {%}*     │  ← .row .bold
│  ─────────────────────────────────────  │  ← .bar-medium
│  Vitamin C          {mg}       {%}      │  ← .row
│  ... (minerals)                         │
│  ═══════════════════════════════════════ │  ← .bar-thick
│  Fish Collagen ...  {mg}         †      │  ← .blend-row
│  ... (active ingredients)               │
│  ═══════════════════════════════════════ │  ← .bar-thick
│  * % DV based on 2,000 cal diet         │  ← .footnote
│  † Daily Value not established.         │
└─────────────────────────────────────────┘
```

### Right Panel — Other Ingredients, Suggested Use & Caution

The right panel has exactly **three blocks** in this fixed order. Wording is
locked — only change the parts marked `{variable}`. Do NOT add, remove, or
rephrase any other sentence.

#### Block 1 — Other Ingredients

```
Other Ingredients
{comma-separated list, descending by weight, Latin names in italics}.
```

The ingredient list is product-specific. Always end with a period.

#### Block 2 — Suggested Use

```
Suggested Use
As a dietary supplement, take {dose_description} daily,
preferably as directed by a healthcare professional.
```

`{dose_description}` examples: `one (1) capsule`, `two (2) capsules`,
`three (3) capsules`. Only this phrase changes per product.

#### Block 3 — Caution

```
Caution
Consult a healthcare professional before use if pregnant, nursing,
taking medications, or if you have a medical condition.
Do not use if safety seal is broken or missing.
```

This block is **identical across all products** — never modify it.

#### Optional: Allergen line

If the formula contains a major allergen (milk, soy, wheat, egg, peanuts,
tree nuts, fish, shellfish), add a single line **below** the Caution block:

```
Contains: {allergen list}.
```

If no major allergens are present, omit this line entirely.

### CSS Class Reference

| class | purpose | height/size |
| --- | --- | --- |
| `.sf-panel` | white bordered box | border: 2px solid #000 |
| `.sf-title` | panel title | 36px font-weight: 900 |
| `.bar-thick` | major separator | 8px |
| `.bar-medium` | section separator | 4px |
| `.bar-thin` | minor separator | 1px |
| `.row` | nutrient row | 11px font |
| `.blend-row` | active ingredient row | 11px font |
| `.indent1` | 1st level indent | padding-left: 14px |
| `.indent2` | 2nd level indent | padding-left: 26px |
| `.other-panel` | right-side text | 13px font |
| `.allergen` | allergen block | 12px font, bold Contains |
