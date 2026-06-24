# Workflow

## 1. Gather Evidence

Prefer evidence in this order:

1. listing title, bullets, images, and `Supplement Facts`
2. official brand pages
3. official PDFs or HCP sheets
4. patent, trademark, and literature records
5. reviews or secondary sources as support only

## 2. Split Layered Ingredient Lines

Always separate:

- host nutrient
- branded source
- organism or source identity
- process or standardization clue
- dosage

Example:

`Calcium (as AlgaeCal(R) Mesophyllum superpositum) 750 mg`

Minimum split:

- `Calcium`
- `AlgaeCal(R)`
- `Mesophyllum superpositum`
- `750 mg`

Do not assume the dosage belongs equally to all layers.

## 3. Build the Fixed Outputs

### Observed Ingredient Table

Fields:

- `ingredient_name`
- `alias`
- `source_or_form`
- `dosage_if_visible`
- `claim_link`
- `confidence`

### Ingredient Classification

Use exactly one category:

- `generic`
- `branded`
- `likely proprietary`
- `unclear`

### Risk Matrix

Score:

- `TM_risk`
- `patent_risk`
- `compliance_risk`
- `marketplace_risk`

Allowed values:

- `low`
- `medium`
- `high`
- `unknown`

### Missing Evidence Points

Use this when:

- a label is incomplete
- taxonomy or ingredient identity is inconsistent
- rights ownership is unclear
- claim mapping is incomplete
- supplier or regulatory documentation is missing

### Rebuild Posture Summary

Use:

- `keep concept`
- `replace`
- `avoid`
- `legal review`

## 4. Chinese Output Rule

Answer in Chinese, but keep exact English marks, Latin species names, statutes, and URLs where useful.

## 5. Guardrails

- Do not claim non-infringement.
- Do not teach claim-by-claim patent avoidance.
- Do not merge the competitor's facts with the user's intended formula.
- Do not treat aggressive bone-density claims as ordinary structure/function language.
