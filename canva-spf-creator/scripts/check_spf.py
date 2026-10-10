#!/usr/bin/env python3
"""Check a transcribed Supplement Facts for defects and compute the FDA-ordered panel.

Usage:  python check_spf.py spf.json [--write]

--write adds "panel" and "machine_issues" to the JSON file. Output is candidates only:
every item still needs a human look (see references/fda-spf-rules.md section 9).

spf.json structure (use null for anything the source does not state; never infer):
{
  "product": "ZAB Urolithin A Gummies",
  "dosage_form": "gummy",              # softgel | capsule | tablet | gummy | powder | liquid ...
  "unit_weight_g": 3,                  # weight of one unit, if stated
  "serving_size": {"qty": 3, "unit": "Gummies"},
  "servings_per_container": null,
  "net_count": null,                   # total units in the container
  "footnote_symbol_stated": "**",
  "ingredients": [
    {"name": "Vitamin E", "source": null, "amount": 10, "unit": "mg",
     "amount_stated": "10mg", "dv_stated": 0.07,
     "blend_children": null}           # list of names for a proprietary blend
  ],
  "other_ingredients_stated": "Maltitol, Purified Water, ...",
  "allergen_statement": null
}
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references" / "daily-values.json"
TO_MG = {"g": 1000.0, "mg": 1.0, "mcg": 0.001, "ug": 0.001, "μg": 0.001, "µg": 0.001}


def load_ref():
    ref = json.loads(REF.read_text(encoding="utf-8"))
    index = {}
    for pos, n in enumerate(ref["nutrients"]):
        for key in [n["name"]] + n.get("aliases", []):
            index[key.lower()] = (pos, n)
    return ref, index


def match_nutrient(name, index):
    """Longest alias found as a whole word in the ingredient name."""
    low = name.lower()
    best = None
    for key, val in index.items():
        if re.search(r"(?<![a-z])" + re.escape(key) + r"(?![a-z])", low):
            if best is None or len(key) > len(best[0]):
                best = (key, val)
    return best[1] if best else None


def parse_dv(stated):
    """Return percent as a number, or None for symbols/blank. Fractions under 1 with no % sign
    are read as fractions (0.07 -> 7)."""
    if stated is None:
        return None
    if isinstance(stated, (int, float)):
        return stated * 100 if stated <= 1.5 else float(stated)
    s = str(stated).strip()
    m = re.search(r"<?\s*(\d+(?:\.\d+)?)\s*%", s)
    if m:
        return float(m.group(1))
    m = re.fullmatch(r"\d+(?:\.\d+)?", s)
    if m:
        v = float(s)
        return v * 100 if v <= 1.5 else v
    return None


def fmt_amount(amount, unit):
    if amount is None:
        return "XX " + (unit or "")
    a = float(amount)
    txt = f"{a:,.0f}" if a == int(a) else f"{a:,g}"
    return f"{txt} {unit}"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    spf = json.loads(path.read_text(encoding="utf-8"))
    ref, index = load_ref()
    issues = []

    def add(sev, where, problem, suggestion="", basis=""):
        issues.append({"severity": sev, "where": where, "problem": problem,
                       "suggestion": suggestion, "basis": basis})

    # --- serving arithmetic -------------------------------------------------
    ss = spf.get("serving_size") or {}
    qty, spc, net = ss.get("qty"), spf.get("servings_per_container"), spf.get("net_count")
    if not qty or not ss.get("unit"):
        add("RED", "Serving Size", "Serving size quantity or unit missing", basis="rules 1, 8")
    if spc is None and net is not None and qty:
        spc_calc = net / qty
        add("GREEN" if spc_calc == int(spc_calc) else "RED", "Servings Per Container",
            f"Not stated; {net} / {qty} = {spc_calc:g}",
            f"Servings Per Container: {spc_calc:g}", "rules 8")
        if spc_calc == int(spc_calc):
            spc = int(spc_calc)
    elif spc is None:
        add("RED", "Servings Per Container", "Not stated and no net count to derive it from",
            "Placeholder XX until the user supplies it", "rules 8")
    elif net is not None and qty and spc * qty != net:
        add("RED", "Servings Per Container",
            f"{spc} servings x {qty} per serving = {spc * qty}, but net count is {net}", basis="rules 8")

    # --- ingredients --------------------------------------------------------
    with_dv, without_dv, active_mg = [], [], 0.0
    for i, ing in enumerate(spf.get("ingredients") or []):
        name, amount, unit = ing.get("name") or "", ing.get("amount"), (ing.get("unit") or "").strip()
        where = name or f"ingredient #{i + 1}"
        hit = match_nutrient(name, index)
        stated = parse_dv(ing.get("dv_stated"))
        unit_l = unit.lower()

        if amount is None or not unit:
            add("RED", where, "Amount or unit missing", basis="rules 9A")
        if unit_l in ("iu", "i.u."):
            add("RED", where, "Amount given in IU; FDA panel needs metric units",
                "Convert using the specific form and confirm with the user", "rules 4")
        if unit_l in ("ug", "μg", "µg"):
            add("GREEN", where, f"Unit '{unit}' written as mcg on the panel", basis="rules 4")
            unit = "mcg"
        raw = str(ing.get("amount_stated") or "")
        if re.search(r"\d[a-zA-Zμµ]", raw):
            add("GREEN", where, f"'{raw}' has no space between number and unit", basis="rules 4")
        if unit_l in TO_MG and amount is not None:
            active_mg += float(amount) * TO_MG[unit_l]

        row = {"name": name, "source": ing.get("source"), "amount": fmt_amount(amount, unit),
               "blend_children": ing.get("blend_children")}

        if hit and hit[1]["dv"] is not None:
            pos, n = hit
            row["order"] = pos
            if amount is not None and unit_l in TO_MG and n["unit"] in TO_MG:
                pct = float(amount) * TO_MG[unit_l] / (n["dv"] * TO_MG[n["unit"]]) * 100
                calc = "<1%" if 0 < pct < 1 else f"{round(pct)}%"
                row["dv"] = calc
                if stated is None:
                    row["dv"] = "XX%"
                    add("RED", where, f"Has a Daily Value ({n['dv']} {n['unit']}) but source gives no %DV",
                        f"Panel shows XX%. From the stated amount it would be {calc}. Confirm with the user.",
                        "rules 3")
                elif round(stated) != round(pct):
                    row["dv"] = "XX%"
                    alt = stated / 100 * n["dv"]
                    add("RED", where,
                        f"Source says {ing.get('dv_stated')!r} (= {stated:g}%), but {fmt_amount(amount, unit)} "
                        f"/ DV {n['dv']} {n['unit']} = {pct:.1f}%",
                        f"Panel shows XX%. From the stated amount it would be {calc}; if {stated:g}% is the "
                        f"correct figure, the amount would be {alt:g} {n['unit']}. Ask the user which number "
                        f"is wrong.", "rules 3")
            else:
                row["dv"] = "XX%"
                add("RED", where, "Cannot compute %DV from the given amount/unit", basis="rules 3, 4")
            if n.get("label_unit") and n["label_unit"].lower() not in (unit.lower() + " " + raw.lower()):
                add("YELLOW", where, f"FDA unit for {n['name']} is {n['label_unit']}", basis="rules 4")
            if not ing.get("source") and pos >= 12:
                add("YELLOW", where, "No source form given, e.g. '(as ...)'",
                    "Ask the user for the ingredient form; show the name alone until then", "rules 5")
            with_dv.append(row)
        elif hit:
            row["order"] = hit[0]
            row["dv"] = ""
            with_dv.append(row)
        else:
            row["dv"] = "†"
            if stated is not None:
                add("RED", where, f"No FDA Daily Value exists, but source states {ing.get('dv_stated')!r}",
                    "Use the footnote symbol", "rules 3")
            without_dv.append(row)

    with_dv.sort(key=lambda r: r["order"])
    stated_order = [i.get("name") for i in spf.get("ingredients") or []]
    panel_order = [r["name"] for r in with_dv + without_dv]
    if stated_order != panel_order:
        add("GREEN", "Row order", "Reordered: ingredients with a Daily Value first, in FDA sequence",
            " > ".join(panel_order), "rules 2")
    if with_dv and without_dv:
        add("GREEN", "Row separator", "Heavy bar between ingredients with and without a Daily Value",
            basis="rules 1")

    sym = spf.get("footnote_symbol_stated")
    if without_dv and sym and sym != "†":
        add("GREEN", "Footnote", f"Source uses {sym!r}; panel uses one symbol throughout",
            "† Daily Value not established.", "rules 1")

    # --- dosage form: macronutrients ---------------------------------------
    form = (spf.get("dosage_form") or "").lower()
    names = " ".join(stated_order).lower()
    serving_g = (spf.get("unit_weight_g") or 0) * (qty or 0)
    if form in ref["forms_needing_macros"] and "calorie" not in names:
        if form == "softgel":
            add("YELLOW", "Nutrition lines", "Softgel with an oil carrier may need Calories / Total Fat",
                "Ask for the fill weight; declare when fat is 0.5 g or more per serving", "rules 6")
        else:
            size = f" ({serving_g:g} g per serving)" if serving_g else ""
            add("RED", "Nutrition lines",
                f"Dosage form '{form}'{size} but no Calories / Total Carbohydrate / Sugars lines",
                "Request lab or formula values; do not estimate onto the panel", "rules 6")
    if serving_g and active_mg > serving_g * 1000:
        add("RED", "Amounts", f"Actives total {active_mg:g} mg, more than the {serving_g:g} g serving",
            basis="rules 8")

    # --- other ingredients --------------------------------------------------
    oi = spf.get("other_ingredients_stated")
    oi_clean = None
    if not oi:
        add("RED", "Other Ingredients", "Missing", basis="rules 9A")
    else:
        oi_clean = re.sub(r"^\s*other ingredients\s*:\s*", "", oi, flags=re.I)
        for uk, us in ref["uk_to_us"].items():
            if uk == us:
                continue
            pat = re.compile(r"\b" + uk + r"\b", re.I)
            if pat.search(oi_clean):
                add("GREEN", "Other Ingredients", f"British spelling '{uk}' changed to '{us}'", basis="rules 7")
                oi_clean = pat.sub(lambda m: us.capitalize() if m.group(0)[0].isupper() else us, oi_clean)
        if re.search(r"\)\s+[A-Z]", oi_clean):
            add("YELLOW", "Other Ingredients", "Closing bracket followed directly by a new word: "
                "missing comma, so two ingredients may be run together", "Add the comma and state how you read it",
                "rules 7")
        if oi_clean.count("(") != oi_clean.count(")"):
            add("YELLOW", "Other Ingredients", "Unbalanced brackets", basis="rules 7")
        fixed = re.sub(r"\s+,", ",", oi_clean)
        fixed = re.sub(r",(?=\S)", ", ", fixed)
        fixed = re.sub(r"\s{2,}", " ", fixed).strip()
        if fixed != oi_clean.strip():
            add("GREEN", "Other Ingredients", "Comma spacing normalised", basis="rules 7")
        oi_clean = fixed if fixed.endswith(".") else fixed + "."
        for m in re.finditer(r"(?<!natural )(?<!artificial )\bflavou?r(?:ing)?s?\b", oi_clean, re.I):
            add("YELLOW", "Other Ingredients", f"'{m.group(0)}' not marked natural or artificial",
                "Ask the user; do not classify it yourself", "rules 7")
            break
        if re.search(r"\bgelatin\b", oi_clean, re.I) and not re.search(r"(bovine|porcine|fish|beef|pork)", oi_clean, re.I):
            add("YELLOW", "Other Ingredients", "Gelatin source not stated (fish gelatin is an allergen)",
                basis="rules 7")
        for word, allergen in (("soy", "Soy"), ("milk", "Milk"), ("whey", "Milk"), ("casein", "Milk"),
                               ("wheat", "Wheat"), ("fish", "Fish"), ("peanut", "Peanuts"),
                               ("sesame", "Sesame"), ("egg", "Egg")):
            if re.search(r"\b" + word, oi_clean, re.I) and not spf.get("allergen_statement"):
                add("YELLOW", "Allergens", f"'{word}' appears but there is no Contains statement",
                    f"Contains: {allergen}.", "rules 7")

    panel = {
        "title": "Supplement Facts",
        "serving_size": f"Serving Size: {qty or 'XX'} {ss.get('unit') or 'XX'}",
        "servings_per_container": f"Servings Per Container: {spc if spc is not None else 'XX'}",
        "rows_with_dv": with_dv,
        "rows_without_dv": without_dv,
        "footnote": "† Daily Value not established." if without_dv else None,
        "other_ingredients": ("Other Ingredients: " + oi_clean) if oi_clean else None,
    }

    order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
    issues.sort(key=lambda x: order[x["severity"]])
    out = {"panel": panel, "machine_issues": issues}
    if "--write" in sys.argv:
        spf.update(out)
        path.write_text(json.dumps(spf, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
