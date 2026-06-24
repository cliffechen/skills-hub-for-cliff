# Workflow

## 1. Read Upstream Deliverables

Load and validate:

- `{name}-upstream-risk-report.md` (Skill 1)
- `{name}-safe-rebuild-brief.md` (Skill 2)

Extract:

- safe ingredient pool (items with posture `keep concept`)
- forbidden items (posture `avoid`)
- items needing legal review
- candidate rebuild directions from Skill 2

If either deliverable is missing, stop and request it.

## 2. Autocomplete Signal Analysis

If an autocomplete suggestions file (`.txt`, one suggestion per line) is
available, run the analysis script:

```bash
python scripts/analyze_autocomplete.py "<suggestions.txt>" \
    --output-dir "<output-dir>" --name "<prefix>" --seed-brand "<brand>"
```

Read the generated `*-autocomplete-signals.md` report and extract the four
formula-design signal dimensions:

### Signal priority for formula decisions

| Priority | Signal dimension | What it tells you | Example |
| --- | --- | --- | --- |
| 1 | **Ingredient association** | Which other ingredients consumers mentally link to the seed product → add to formula | "fatty 15 omega 3" → consider adding Omega-3 |
| 2 | **Dosage / potency** | What strength consumers expect or desire → set dosage | "advanced formula strength" → go higher than reference |
| 3 | **Form-factor preference** | Which dosage forms consumers actively seek → choose form | gummies 8× vs capsules 3× → Gummies is a strong signal |
| 4 | **Audience / occasion** | Who is searching and why → tailor formula to demographic | "for women" → consider female-adapted ingredients |

### Integration rules

- **Ingredient association signals override pure scientific-mechanism reasoning.**
  If consumers search for "product X + ingredient Y" but you were considering
  ingredient Z based on mechanism alone, prioritize Y unless it fails the
  safety check from Skill 1/2.
- **Dosage signals set the floor, not the ceiling.** If consumers search for
  "200mg" and the reference product is 100mg, the new formula should be ≥200mg
  (within GRAS/safety limits).
- **Form-factor signals inform Tier 1 vs Tier 2 product decisions.** The most
  searched form is Tier 1; the second most searched is Tier 2.
- **Audience signals guide ingredient selection for secondary positions.** If
  "for women" is strong, consider adding female-relevant ingredients (e.g.
  folate, iron, evening primrose oil) as secondary formula components.

If no autocomplete file is provided, proceed to Step 3 but note the gap in
the final report.

## 3. Keyword Competition Analysis

Use **sorftime MCP** to gather:

- `product_traffic_terms` for the target ASIN
- `keyword_detail` for each top traffic keyword
- `keyword_trend` for momentum signals
- `keyword_extends` for long-tail opportunities
- `keyword_search_results` for competitive landscape

Build a **Keyword Competition Matrix** with these columns:

| keyword | monthly_search_volume | ABA_weekly_rank | SPR | PPC_bid | click_concentration | natural_position | assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |

Assessment categories:

- `蓝海推荐` — low SPR + low PPC + decent volume
- `潜力观察` — growing trend but moderate competition
- `红海回避` — high SPR + high PPC + dominated by big brands
- `品牌词借力` — competitor brand keyword with low PPC, usable for ads

Select 1-2 **anchor keywords** that the formula should optimize around.

## 4. Market Demand Mining

### Source A: Amazon Reviews (sorftime MCP)

- Pull `product_reviews` for the target ASIN (both Positive and Negative)
- Pull reviews for top 2-3 competing ASINs if useful
- Extract: pain points, unmet needs, form factor complaints, desired additions

### Source B: Reddit Discussions (Apify MCP)

- Use `parseforge/reddit-posts-scraper` to search relevant subreddits:
  - r/Supplements, r/Nootropics, r/Fitness, r/aging, r/Arthritis
- Search queries: target ingredient names, product category, competitor names
- Extract: real user experiences, stack combinations, complaints, wishes

### Source C: Web Research (exa MCP / web search)

- Search for consumer forums, health blogs, trend articles
- Extract: emerging ingredient trends, consumer sentiment shifts

Synthesize into a **Market Demand Insights** table:

| insight_type | source | detail | implication_for_formula |
| --- | --- | --- | --- |

Insight types:

- `痛点` — something users complain about
- `未满足需求` — something users wish existed
- `形态偏好` — preferences about pill size, form, taste
- `成分期望` — specific ingredients users ask for
- `趋势信号` — emerging trends in the category

## 5. Scientific Evidence Validation

For each candidate ingredient (from Skill 2 directions + demand insights):

- Search **exa MCP** or **web search** for:
  - PubMed systematic reviews or meta-analyses
  - Examine.com ingredient pages
  - NIH Office of Dietary Supplements fact sheets
  - Cochrane reviews if available

Build a **Scientific Evidence Table**:

| ingredient | effective_dose_range | evidence_level | key_findings | source |
| --- | --- | --- | --- | --- |

Evidence levels:

- `Strong` — multiple RCTs or meta-analysis
- `Moderate` — 1-2 RCTs or strong observational data
- `Emerging` — preclinical or limited human data
- `Weak` — mostly anecdotal or in-vitro only

Only recommend ingredients at `Strong` or `Moderate` evidence level
for primary formula positions. `Emerging` ingredients may be suggested
as optional differentiators with explicit caveats.

## 6. Formula Direction Synthesis

Produce **two tiers** of Candidate Formula Directions:

### Tier A — Consumer-Signal-Driven Directions (2-3 directions)

These are the **primary** directions. Ingredient choices originate from
observed consumer behavior:

**Ingredient selection priority** (most important first):

1. **Consumer search signals** — autocomplete ingredient associations +
   review-mentioned ingredients
2. **Competitor ad-targeting signals** — what the reference product bids on
   reveals consumer overlap
3. **Review VOC signals** — ingredients consumers mention in reviews
4. **Scientific mechanism complementarity** — used to **validate** the
   consumer-signal choice, not to originate it

### Tier B — Science-Mechanism-Driven Directions (2 directions)

These are **supplementary** directions. Ingredient choices originate from
scientific mechanism analysis (pathway complementarity, synergy studies,
literature-supported stacking logic) rather than direct consumer search
signals.

Tier B directions serve three purposes:
- Provide options when consumer signals are weak or absent for a dimension
- Capture scientifically promising combinations that consumers haven't
  discovered yet (potential first-mover advantage)
- Give the product development team a broader decision space

**Ingredient selection priority** for Tier B (reversed):

1. **Scientific mechanism complementarity** — pathway-level synergy,
   published combination studies, mechanistic rationale
2. **Competitor ad-targeting signals** — validates consumer overlap
3. **Review VOC signals** — confirms relevance
4. **Consumer search signals** — used to check whether the science-driven
   choice has any existing demand (nice-to-have, not required)

### Labeling rule

Every direction must be clearly labeled:
- `[消费者信号驱动]` for Tier A directions
- `[科学机制驱动]` for Tier B directions

This ensures the reader knows the origin logic of each recommendation.

For each direction, specify:

- **Direction name** — short descriptive label
- **Anchor keyword(s)** — which keyword(s) this formula targets
- **Core ingredients + dosages** — what goes in and at what level
- **Ingredient changes vs reference** — what was added, removed, or upgraded
- **Scientific rationale** — why this combination works
- **Market demand addressed** — which pain points or needs this solves
- **Keyword competitive advantage** — how this formula wins on the anchor keyword
- **Claim posture** — suggested structure/function language
- **Commercialization notes** — form factor, pricing implications, supply chain considerations

## 7. HTML Supplement Facts Label

After the user selects a formula direction and confirms the final ingredient list,
generate a standalone HTML file that visually replicates a standard US
Supplement Facts panel.

### Trigger

This step is executed **only after** the user explicitly:
1. Chooses one of the Candidate Formula Directions (e.g. "I choose Plan B"), AND
2. Confirms or adjusts the ingredient list / dosages.

Do NOT generate the HTML during the initial formula reconstruction output.

### File Naming

```
{name}-supplement-facts-{YYYY-MM-DD}-{HHmm}.html
```

- `{name}` — product short name (lowercase, hyphenated), same as the main deliverable.
- `{YYYY-MM-DD}` — generation date.
- `{HHmm}` — generation time (24-hour, hours + minutes).
- Example: `foodology-cutting-jelly-supplement-facts-2026-04-10-1830.html`

Use `mcp_sorftimeMCP_get_time` to obtain the current timestamp for the filename.

Save to the same folder as the main deliverable:
`formula-reconstruction-result/{name}/`

### Design Specifications

- **Language**: English only.
- **Background**: white (`#ffffff`) for the panel, light accent for page background is optional.
- **Typography**: Arial / Helvetica, black text.
- **Layout**: two-column — left = Supplement Facts box, right = Other Ingredients + Allergen Statement.
- **Supplement Facts box** must include:
  - Title "Supplement Facts" in large bold.
  - Serving Size and Servings Per Container.
  - Thick / medium / thin separator bars matching FDA label conventions.
  - "Amount Per Serving" and "% Daily Value" header row.
  - Macro rows: Calories, Total Fat, Saturated Fat, Total Carbohydrate,
    Dietary Fiber, Total Sugars, Added Sugars, Protein — with proper indentation.
  - Vitamin / mineral rows with amounts and %DV.
  - Active / functional ingredient rows with amounts and † for no DV.
  - Footnote: `* Percent Daily Values are based on a 2,000 calorie diet.`
    and `† Daily Value not established.`
- **Other Ingredients** section: comma-separated, descending by weight,
  with Latin names in italics where applicable.
- **Allergen Statement**: bold "Contains:" line + facility cross-contact line.
- The HTML must be **self-contained** (inline CSS, no external dependencies)
  and render correctly when opened directly in any modern browser.

### Reference Template

Use the HTML structure from the first successfully generated label as the
canonical template. The key CSS classes are:

| class | purpose |
| --- | --- |
| `.sf-panel` | white bordered Supplement Facts box |
| `.sf-title` | large bold title |
| `.bar-thick` / `.bar-medium` / `.bar-thin` | FDA-style separator bars (8px / 4px / 1px) |
| `.row` | standard nutrient row with `.name`, `.amount`, `.dv` |
| `.blend-row` | active ingredient row below the thick bar |
| `.indent1` / `.indent2` | sub-nutrient indentation |
| `.other-panel` | right-side Other Ingredients text |
| `.allergen` | allergen statement block |

## 8. Output Rules

- Answer in Chinese.
- Keep exact English ingredient names, keyword terms, and URLs.
- Focus on competitive advantage, not legal certainty.
- Every ingredient recommendation must have a scientific citation.
- Every keyword recommendation must have data backing.

## 9. Guardrails

- Do not recommend ingredients marked `avoid` in upstream reports.
- Do not produce exact manufacturing specifications.
- Do not use disease claims to justify ingredient additions.
- Do not present keyword data as guaranteed ranking outcomes.
- Do not ignore form factor and supply chain feasibility.
