#!/usr/bin/env python
"""Analyze Amazon autocomplete (search bar dropdown) suggestions for supplement
formula design signals.

The script reads a plain-text file (one suggestion per line), classifies each
line along four dimensions that matter for supplement product development, and
outputs a structured Markdown report plus a JSON summary.

Four output dimensions
----------------------
1. **Ingredient association** – other ingredients consumers mentally link to the
   seed product (→ guides which ingredients to add to the formula).
2. **Dosage / potency signals** – numeric dosages or "strength" modifiers that
   consumers search for (→ guides how much of each ingredient to use).
3. **Form-factor preference** – dosage forms consumers want (→ guides capsule
   vs gummy vs powder decisions).
4. **Audience / occasion** – demographic or use-case modifiers (→ guides
   whether to skew the formula toward women, seniors, sleep, etc.).

Usage
-----
    python scripts/analyze_autocomplete.py <suggestions.txt> \
        --output-dir <dir> --name <prefix> [--seed-brand "fatty 15"]
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Dictionaries – extend these as new ingredients / forms appear
# ---------------------------------------------------------------------------

INGREDIENT_TERMS: dict[str, list[str]] = {
    "omega_3": ["omega 3", "omega-3", "omega3", "fish oil", "krill oil", "cod liver oil", "dha", "epa"],
    "coq10": ["coq10", "co q10", "coenzyme q10", "ubiquinol", "ubiquinone"],
    "astaxanthin": ["astaxanthin"],
    "urolithin_a": ["urolithin", "mitopure"],
    "nmn_nad": ["nmn", "nad+", "nad supplement", "nicotinamide mononucleotide", "nicotinamide riboside"],
    "resveratrol": ["resveratrol", "pterostilbene"],
    "vitamin_d": ["vitamin d", "vitamin d3", "cholecalciferol"],
    "vitamin_c": ["vitamin c", "ascorbic"],
    "vitamin_k": ["vitamin k", "vitamin k2", "mk-7", "mk7"],
    "magnesium": ["magnesium"],
    "zinc": ["zinc"],
    "iron": ["iron"],
    "collagen": ["collagen"],
    "probiotics": ["probiotic", "probiotics", "synbiotic"],
    "berberine": ["berberine"],
    "quercetin": ["quercetin"],
    "fisetin": ["fisetin"],
    "curcumin": ["curcumin", "turmeric"],
    "biotin": ["biotin"],
    "folate": ["folate", "folic acid"],
    "selenium": ["selenium"],
    "pqq": ["pqq", "pyrroloquinoline"],
    "nac": ["nac", "n-acetyl cysteine", "n acetyl cysteine"],
    "glutathione": ["glutathione"],
    "spermidine": ["spermidine"],
    "taurine": ["taurine"],
    "creatine": ["creatine"],
    "ashwagandha": ["ashwagandha"],
    "melatonin": ["melatonin"],
    "l_theanine": ["l-theanine", "l theanine", "theanine"],
}

FORM_TERMS: dict[str, list[str]] = {
    "gummies": ["gummies", "gummy"],
    "capsules": ["capsules", "capsule", "caps"],
    "softgels": ["softgels", "softgel"],
    "tablets": ["tablets", "tablet"],
    "pills": ["pills", "pill"],
    "powder": ["powder"],
    "liquid": ["liquid", "drops"],
    "chewable": ["chewable", "chewables"],
    "packets": ["packets", "packet", "sachets"],
}

AUDIENCE_TERMS: dict[str, list[str]] = {
    "women": ["for women", "women's", "womens"],
    "men": ["for men", "men's", "mens"],
    "kids": ["for kids", "kids", "children", "child"],
    "adults": ["for adults", "adults"],
    "seniors": ["seniors", "elderly", "over 50", "50+", "60+", "65+"],
}

OCCASION_TERMS: dict[str, list[str]] = {
    "aging": ["aging", "anti aging", "anti-aging", "longevity", "healthy aging"],
    "sleep": ["sleep"],
    "energy": ["energy"],
    "hair": ["hair", "cabello"],
    "skin": ["skin"],
    "nails": ["nails"],
    "weight": ["weight loss", "weight", "metabolism"],
    "immune": ["immune", "immunity"],
    "gut": ["gut", "digestive", "digestion"],
    "liver": ["liver"],
    "heart": ["heart", "cardiovascular"],
    "brain": ["brain", "cognitive", "focus", "memory"],
    "joint": ["joint", "joints", "arthritis"],
    "inflammation": ["inflammation", "anti-inflammatory", "anti inflammatory"],
}

# Suggestions matching any of these patterns are excluded entirely.
EXCLUDE_PATTERNS: list[str] = [
    r"\bfor dogs?\b",
    r"\bfor pets?\b",
    r"\bfor cats?\b",
    r"\bbook\b",
    r"\bcookbook\b",
    r"\bbeef sticks?\b",
    r"\bmeat sticks?\b",
    r"\bjalapeno\b",
]

# These are "noise" – real suggestions but not useful for formula design.
NOISE_PATTERNS: list[str] = [
    r"\brefill\b",
    r"\brefills\b",
    r"\bsubscription\b",
    r"\bbuy again\b",
    r"\breviews?\b",
    r"\bbenefits?\b",
    r"\bstarter kit\b",
    r"\btravel size\b",
    r"\bone bottle\b",
    r"\bshow me\b",
    r"\blooking for\b",
]

# Dosage / potency: match numbers with units, or strength modifiers.
DOSAGE_RE = re.compile(
    r"(\d[\d,]*)\s*(mg|mcg|iu|µg|g)\b",
    re.IGNORECASE,
)
POTENCY_TERMS: list[str] = [
    "advanced formula",
    "advanced",
    "extra strength",
    "double strength",
    "triple strength",
    "high potency",
    "maximum strength",
    "ultra",
    "super",
    "strength",
]
# NOTE: "mega" removed – it false-matches inside "omega".  If a product line
# genuinely uses "mega dose" etc., add a regex-based check instead.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("suggestions", help="Path to .txt file with one suggestion per line.")
    p.add_argument("--output-dir", required=True, help="Directory for output files.")
    p.add_argument("--name", default="autocomplete", help="Output file prefix.")
    p.add_argument("--seed-brand", default="", help="Brand name to strip for cleaner analysis (e.g. 'fatty 15').")
    return p.parse_args()


def load_suggestions(path: Path) -> list[str]:
    """Read, deduplicate, normalise."""
    seen: set[str] = set()
    result: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip().lower()
        if not line or line in seen:
            continue
        seen.add(line)
        result.append(line)
    return result


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def find_terms(text: str, term_dict: dict[str, list[str]]) -> list[str]:
    """Return all dictionary keys whose terms appear in *text*."""
    hits: list[str] = []
    low = text.lower()
    for key, terms in term_dict.items():
        if any(t in low for t in terms):
            hits.append(key)
    return hits


def find_dosages(text: str) -> list[str]:
    """Return dosage strings like '200 mg', '1000 iu'."""
    return [f"{m.group(1)} {m.group(2).lower()}" for m in DOSAGE_RE.finditer(text)]


def find_potency(text: str) -> list[str]:
    low = text.lower()
    hits: list[str] = []
    for t in POTENCY_TERMS:
        # Use word-boundary check to avoid substring false positives
        # (e.g. "mega" inside "omega").
        pattern = r"(?<!\w)" + re.escape(t) + r"(?!\w)"
        if re.search(pattern, low):
            hits.append(t)
    return hits


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def analyze(suggestions: list[str], seed_brand: str) -> dict[str, Any]:
    """Classify every suggestion and aggregate signals."""

    excluded: list[dict[str, str]] = []
    noise: list[dict[str, str]] = []
    classified: list[dict[str, Any]] = []

    ingredient_counter: Counter[str] = Counter()
    form_counter: Counter[str] = Counter()
    audience_counter: Counter[str] = Counter()
    occasion_counter: Counter[str] = Counter()
    dosage_counter: Counter[str] = Counter()
    potency_counter: Counter[str] = Counter()

    # Collect raw suggestions per signal for traceability
    ingredient_sources: dict[str, list[str]] = defaultdict(list)
    form_sources: dict[str, list[str]] = defaultdict(list)
    audience_sources: dict[str, list[str]] = defaultdict(list)
    occasion_sources: dict[str, list[str]] = defaultdict(list)
    dosage_sources: dict[str, list[str]] = defaultdict(list)
    potency_sources: dict[str, list[str]] = defaultdict(list)

    for s in suggestions:
        # --- exclusion ---
        if matches_any(s, EXCLUDE_PATTERNS):
            excluded.append({"suggestion": s, "reason": "non-human-supplement"})
            continue

        # --- noise ---
        if matches_any(s, NOISE_PATTERNS):
            noise.append({"suggestion": s, "reason": "purchase-behavior-or-info-seeking"})
            continue

        # --- strip seed brand for cleaner modifier extraction ---
        stripped = s
        if seed_brand:
            for variant in [seed_brand, seed_brand.replace(" ", "")]:
                stripped = stripped.replace(variant, "").strip()

        entry: dict[str, Any] = {"suggestion": s, "stripped": stripped}

        # Dimension 1: ingredient association
        ingredients = find_terms(s, INGREDIENT_TERMS)
        entry["ingredients"] = ingredients
        for ing in ingredients:
            ingredient_counter[ing] += 1
            ingredient_sources[ing].append(s)

        # Dimension 2: dosage / potency
        dosages = find_dosages(s)
        potencies = find_potency(s)
        entry["dosages"] = dosages
        entry["potency"] = potencies
        for d in dosages:
            dosage_counter[d] += 1
            dosage_sources[d].append(s)
        for p in potencies:
            potency_counter[p] += 1
            potency_sources[p].append(s)

        # Dimension 3: form factor
        forms = find_terms(s, FORM_TERMS)
        entry["forms"] = forms
        for f in forms:
            form_counter[f] += 1
            form_sources[f].append(s)

        # Dimension 4: audience / occasion
        audiences = find_terms(s, AUDIENCE_TERMS)
        occasions = find_terms(s, OCCASION_TERMS)
        entry["audiences"] = audiences
        entry["occasions"] = occasions
        for a in audiences:
            audience_counter[a] += 1
            audience_sources[a].append(s)
        for o in occasions:
            occasion_counter[o] += 1
            occasion_sources[o].append(s)

        classified.append(entry)

    return {
        "total_input": len(suggestions),
        "excluded_count": len(excluded),
        "noise_count": len(noise),
        "analyzed_count": len(classified),
        "excluded": excluded,
        "noise": noise,
        "classified": classified,
        "signals": {
            "ingredients": {
                "counts": dict(ingredient_counter.most_common()),
                "sources": {k: v for k, v in ingredient_sources.items()},
            },
            "dosages": {
                "counts": dict(dosage_counter.most_common()),
                "sources": {k: v for k, v in dosage_sources.items()},
            },
            "potency": {
                "counts": dict(potency_counter.most_common()),
                "sources": {k: v for k, v in potency_sources.items()},
            },
            "forms": {
                "counts": dict(form_counter.most_common()),
                "sources": {k: v for k, v in form_sources.items()},
            },
            "audiences": {
                "counts": dict(audience_counter.most_common()),
                "sources": {k: v for k, v in audience_sources.items()},
            },
            "occasions": {
                "counts": dict(occasion_counter.most_common()),
                "sources": {k: v for k, v in occasion_sources.items()},
            },
        },
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _signal_table(label: str, counts: dict[str, int], sources: dict[str, list[str]]) -> list[str]:
    """Render one signal dimension as a Markdown table with source traceability."""
    if not counts:
        return [f"### {label}", "", "_No signals detected._", ""]
    lines = [
        f"### {label}",
        "",
        "| Signal | Count | Source suggestions |",
        "| --- | ---: | --- |",
    ]
    for key, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        src_list = sources.get(key, [])
        # Show up to 3 source suggestions to keep the table readable
        src_display = "; ".join(f'`{s}`' for s in src_list[:3])
        if len(src_list) > 3:
            src_display += f" … (+{len(src_list) - 3})"
        lines.append(f"| **{key}** | {count} | {src_display} |")
    lines.append("")
    return lines


def generate_markdown(result: dict[str, Any], seed_brand: str) -> str:
    signals = result["signals"]
    lines: list[str] = []

    lines += [
        "# Autocomplete Suggestions Analysis — Formula Design Signals",
        "",
        f"- Seed brand: `{seed_brand or '(none)'}`",
        f"- Total suggestions: **{result['total_input']}**",
        f"- Excluded (non-human-supplement): **{result['excluded_count']}**",
        f"- Noise (purchase-behavior / info-seeking): **{result['noise_count']}**",
        f"- Analyzed: **{result['analyzed_count']}**",
        "",
        "---",
        "",
        "## 1. Ingredient Association Signals → 配方中添加什么成分",
        "",
        "Consumers actively search for the seed product combined with these",
        "ingredients. High-count items indicate strong mental association and",
        "potential demand for a combined formula.",
        "",
    ]
    lines += _signal_table(
        "Ingredient mentions",
        signals["ingredients"]["counts"],
        signals["ingredients"]["sources"],
    )

    lines += [
        "## 2. Dosage & Potency Signals → 配方中用多少剂量",
        "",
        "Numeric dosages and strength modifiers reveal what consumers expect",
        "or desire in terms of potency. Higher-than-reference dosages suggest",
        "an opportunity to differentiate with a stronger formula.",
        "",
    ]
    lines += _signal_table(
        "Explicit dosages",
        signals["dosages"]["counts"],
        signals["dosages"]["sources"],
    )
    lines += _signal_table(
        "Potency / strength modifiers",
        signals["potency"]["counts"],
        signals["potency"]["sources"],
    )

    lines += [
        "## 3. Form-Factor Preference Signals → 开发什么剂型",
        "",
        "The relative frequency of dosage-form mentions reveals which formats",
        "consumers are actively seeking. A form that appears many times but",
        "has few satisfying products on the market is a gap worth filling.",
        "",
    ]
    lines += _signal_table(
        "Form-factor mentions",
        signals["forms"]["counts"],
        signals["forms"]["sources"],
    )

    lines += [
        "## 4. Audience & Occasion Signals → 面向什么人群 / 场景",
        "",
        "Demographic and use-case modifiers tell you who is searching and why.",
        "If a specific audience appears frequently, the formula should consider",
        "ingredients that resonate with that group.",
        "",
    ]
    lines += _signal_table(
        "Audience (demographic)",
        signals["audiences"]["counts"],
        signals["audiences"]["sources"],
    )
    lines += _signal_table(
        "Occasion (use-case / benefit)",
        signals["occasions"]["counts"],
        signals["occasions"]["sources"],
    )

    # --- Excluded & Noise appendix ---
    lines += [
        "---",
        "",
        "## Appendix: Excluded & Noise Suggestions",
        "",
    ]
    if result["excluded"]:
        lines += ["### Excluded (non-human-supplement)", ""]
        for item in result["excluded"]:
            lines.append(f"- `{item['suggestion']}` — {item['reason']}")
        lines.append("")
    if result["noise"]:
        lines += ["### Noise (purchase-behavior / info-seeking)", ""]
        for item in result["noise"]:
            lines.append(f"- `{item['suggestion']}` — {item['reason']}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    txt_path = Path(args.suggestions).expanduser().resolve()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    suggestions = load_suggestions(txt_path)
    result = analyze(suggestions, seed_brand=args.seed_brand)

    json_path = output_dir / f"{args.name}-autocomplete-signals.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = output_dir / f"{args.name}-autocomplete-signals.md"
    md_path.write_text(generate_markdown(result, args.seed_brand), encoding="utf-8")

    print(json.dumps({
        "json": str(json_path),
        "markdown": str(md_path),
        "total": result["total_input"],
        "excluded": result["excluded_count"],
        "noise": result["noise_count"],
        "analyzed": result["analyzed_count"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
