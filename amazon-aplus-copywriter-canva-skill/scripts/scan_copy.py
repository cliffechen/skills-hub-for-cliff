#!/usr/bin/env python3
"""Scan copy JSON (same format as build_xlsx.py) for compliance and conflict problems.

Usage:
  python3 scan_copy.py copy.json [--forbid "1000mg,softgel,OldBrand"] [--supplement] [--listing] [--max-over 10]

Checks the "copy" and "alt" fields of every row:
  - --forbid terms (this run's conflict list: wrong dose, wrong dosage form, placeholder brand, benchmark brand);
    matched at the start of a word, so "GMP Certified" does not hit "cGMP Certified"
  - --supplement: high-risk supplement claim words; claim asterisks need an FDA disclaimer row
  - --listing: gallery images (主图/副图). Headline-like slots (slot contains 标题 / H1 / headline) over 45 chars or 2 lines
    get a WARN; any Chinese character left in copy is a FLAG (placeholder not replaced)
  - A+ content policy words (price/promo, buy now, now/new/limited, reviews/stars, guarantee/refund,
    best-selling/#1) are a FLAG in every row (the FDA disclaimer row is exempt)
  - ALT rows (id starts with "ALT") longer than 100 characters
  - copy much longer than the placeholder (> --max-over characters)
  - brand-voice rows ("voice": "brand", incl. their ALT row; see references/brand-voice.md):
    digits or spec/proof words (mg, capsule, serving, cGMP, lab tested, COA, vegan...) are a FLAG;
    a run of 4+ words shared with any non-brand row (repeating earlier images) is a FLAG;
    copy over 16 words is a WARN

Also checks the optional "marketing" list (see references/persuasion-psychology.md):
  - every row: --forbid terms and fear wording (too late, damage, disease, sick, dying...) are a FLAG;
    --supplement high-risk words are a WARN
  - channel "A+": A+ policy words and unfilled [placeholders] are a FLAG; level ⛔ on an A+ row is a FLAG;
    claim asterisks count toward the FDA disclaimer check
  - channel "站外": A+ policy words are allowed; unfilled [placeholders] are a WARN (fill with real data)
  - 损失厌恶 rows without "negative_read" are a WARN

Also checks the optional "explainers" list (see references/ingredient-eli5.md): fields essence / analogy /
  detail / so_what / on_image get the --forbid, fear, A+ policy (FLAG) and --supplement (WARN) checks;
  claim asterisks count toward the FDA disclaimer check.

Also checks the optional "excipients" block (see references/dosage-form-excipients.md): fields headline /
  subheadline / points get the --forbid, fear, A+ policy (FLAG) and --supplement (WARN) checks, plus:
  "no fillers / filler-free" and absorption / bioavailability wording are a FLAG (excipients can't back them);
  vegan / non-GMO / gluten-free / gelatin-free / sugar-free / "free from|of" are a WARN (need label or supplier proof).

Claim guard (all rows + marketing + explainers + excipients), per product: meta.claims.blocked lists the benefit
  directions this product's listing does not cover (decided in the plan, see references/ingredient-research.md),
  e.g. {"claims": {"allowed": ["energy metabolism"], "blocked": ["gut health", "digestive", "immune"]}}.
  Any blocked phrase is a FLAG. Without meta.claims a WARN reminds you to define them.
Exit code 1 if any FLAG was found, else 0. WARN items are informational.
"""
import argparse
import json
import re
import sys

SUPPLEMENT_RISK = [
    r"\bcure[sd]?\b", r"\btreat(s|ment)?\b", r"\bprevent(s|ion)?\b", r"\bheal(s|ing)?\b", r"\bdiagnos",
    r"anti-?aging", r"revers(e|es|ing) aging", r"guarantee", r"\binstant(ly)?\b", r"works for everyone",
    r"#1\b", r"\bbest\b", r"most effective", r"strongest", r"100%", r"\d+x (better|more)",
    r"fda[- ]approved", r"clinically proven", r"doctor recommended", r"made in (the )?usa",
]
APLUS_POLICY = [
    r"\$\s?\d", r"\bprice[ds]?\b", r"(?<![-\w])free\b(?!\s+(from|of)\b)", r"\bbonus\b", r"\baffordable\b",
    r"\bdiscount", r"\bcoupon", r"\bsale\b", r"buy now", r"add to cart", r"get yours", r"order now",
    r"shop (now|with us)", r"\bnow\b", r"\bnew\b", r"\blatest\b", r"\blimited\b", r"\bhurry\b",
    r"only \d+ left", r"today only", r"\bguarantee", r"\brefund", r"money[- ]back", r"risk[- ]free",
    r"best[- ]?sell", r"#1\b", r"top[- ](rated|selling)", r"\breviews?\b", r"\b\d(\.\d)?[- ]?stars?\b",
    r"\bstar rating", r"\bholiday", r"black friday", r"christmas", r"prime day",
]
FEAR = [r"too late", r"\bdamag", r"deteriorat", r"\bdiseases?\b", r"\bsick", r"\billness", r"\bdying\b", r"\bdie\b"]
CLAIM_GUARD = []  # filled per product from meta.claims.blocked in main()


def blocked_patterns(phrases):
    """Turn plain blocked phrases into word-bounded regexes ("gut health" -> r"\bgut health\b")."""
    return [r"\b" + re.escape(p.strip().lower()) + r"\b" for p in phrases if p and p.strip()]
EXPLAINER_FIELDS = ("essence", "analogy", "detail", "so_what", "on_image")
EXCIPIENT_FIELDS = ("headline", "subheadline", "points")
EXCIPIENT_BANNED = [r"no fillers?\b", r"filler[- ]free", r"absor", r"bioavailab", r"fast[- ]acting"]
EXCIPIENT_PROOF = [r"\bvegan\b", r"non-?gmo", r"gluten[- ]free", r"gelatin[- ]free", r"\bno gelatin\b",
                   r"sugar[- ]free", r"\bfree (from|of)\b"]
PLACEHOLDER = re.compile(r"\[[^\]]+\]")
FDA_MARK = "not intended to diagnose"
BRAND_SPEC = [
    r"\d", r"\bmg\b", r"\bmcg\b", r"capsules?", r"softgels?", r"servings?", r"\bdose\b", r"\bdaily\b",
    r"\bc?gmp\b", r"lab[- ]tested", r"third[- ]party", r"\bcoa\b", r"certificate", r"\bvegan\b",
    r"non-?gmo", r"gluten", r"supply",
]
WORD_RE = re.compile(r"[a-z']+")
DISCLAIMER_EXEMPT = re.compile(r"not been evaluated by the food and drug administration", re.I)


def claim_star(text):
    """True if text carries a structure/function asterisk (not just **bold** markup)."""
    stripped = re.sub(r"\*\*[^*]+\*\*", "", text)       # remove **bold**
    stripped = re.sub(r"\*[^*\n]+\*", "", stripped)     # remove *accent*
    return "*" in stripped


def first_hit(patterns, low):
    for pat in patterns:
        if re.search(pat, low):
            return pat
    return None


def ngrams(text, n=4):
    w = WORD_RE.findall(text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def check_brand_voice(rows, flags, warns):
    brand = [r for r in rows if r.get("voice") == "brand"]
    others = [r for r in rows if r.get("voice") != "brand" and not DISCLAIMER_EXEMPT.search(r.get("copy") or "")]
    seen = set()
    for r in others:
        for field in ("copy", "alt"):
            seen |= ngrams(r.get(field) or "")
    for r in brand:
        rid = r.get("id", "?")
        for field in ("copy", "alt"):
            t = r.get(field) or ""
            if not t or t == "—" or DISCLAIMER_EXEMPT.search(t):
                continue
            low = t.lower()
            pat = first_hit(BRAND_SPEC, low)
            if pat:
                flags.append(f"{rid} [{field}] brand voice has spec/proof wording /{pat}/ - leave specs to earlier images: {t!r}")
            shared = ngrams(t) & seen
            if shared:
                flags.append(f"{rid} [{field}] brand voice repeats earlier copy {sorted(shared)[:3]}: {t!r}")
            words = len(WORD_RE.findall(low))
            if not rid.upper().startswith("ALT") and words > 16:
                warns.append(f"{rid} [{field}] brand voice is {words} words - aim for two short beats")


def has_term(term, low):
    """Forbidden term at the start of a word: 'softgel' hits 'softgels', 'GMP Certified' does not hit 'cGMP Certified'."""
    return re.search(r"(?<![a-z])" + re.escape(term.lower()), low) is not None


def common_checks(rid, field, t, a, forbid, flags, warns):
    """Checks shared by marketing and explainer lines: forbid terms, fear, claim guard, supplement risk."""
    low = t.lower()
    for term in forbid:
        if has_term(term, low):
            flags.append(f"{rid} [{field}] contains forbidden term '{term}': {t!r}")
    pat = first_hit(FEAR, low)
    if pat:
        flags.append(f"{rid} [{field}] fear wording /{pat}/ - frame the loss without scaring: {t!r}")
    pat = first_hit(CLAIM_GUARD, low)
    if pat:
        flags.append(f"{rid} [{field}] benefit direction /{pat}/ not covered by the listing - confirm evidence or drop: {t!r}")
    if a.supplement:
        pat = first_hit(SUPPLEMENT_RISK, low)
        if pat:
            warns.append(f"{rid} [{field}] high-risk wording /{pat}/: {t!r}")


def check_explainers(items, a, forbid, flags, warns, star_rows):
    for e in items:
        eid = e.get("id", "?")
        for field in EXPLAINER_FIELDS:
            t = e.get(field) or ""
            if not t or t == "—":
                continue
            common_checks(eid, field, t, a, forbid, flags, warns)
            pat = first_hit(APLUS_POLICY, t.lower())
            if pat:
                flags.append(f"{eid} [{field}] A+ policy wording /{pat}/: {t!r}")
            if claim_star(t) and eid not in star_rows:
                star_rows.append(eid)


def check_excipients(items, a, forbid, flags, warns, star_rows):
    for e in items:
        eid = e.get("id", "?")
        for field in EXCIPIENT_FIELDS:
            t = e.get(field) or ""
            if not t or t == "—":
                continue
            low = t.lower()
            common_checks(eid, field, t, a, forbid, flags, warns)
            pat = first_hit(APLUS_POLICY, low)
            if pat:
                flags.append(f"{eid} [{field}] A+ policy wording /{pat}/: {t!r}")
            pat = first_hit(EXCIPIENT_BANNED, low)
            if pat:
                flags.append(f"{eid} [{field}] excipient copy can't claim /{pat}/ - fillers are on the label / no absorption data: {t!r}")
            pat = first_hit(EXCIPIENT_PROOF, low)
            if pat:
                warns.append(f"{eid} [{field}] /{pat}/ needs label or supplier proof: {t!r}")
            if claim_star(t) and eid not in star_rows:
                star_rows.append(eid)


def check_marketing(items, a, forbid, flags, warns, star_rows):
    for m in items:
        mid = m.get("id", "?")
        offsite = m.get("channel") == "站外"
        if not offsite and str(m.get("level", "")).startswith("⛔"):
            flags.append(f"{mid} is marked ⛔ but channel is A+ - set channel to 站外 or fix the line")
        if "损失厌恶" in (m.get("principle") or "") and not (m.get("negative_read") or "").strip():
            warns.append(f"{mid} loss-aversion line has no negative_read - write what the shopper infers")
        for field in ("copy", "alt"):
            t = m.get(field) or ""
            if not t or t == "—":
                continue
            low = t.lower()
            common_checks(mid, field, t, a, forbid, flags, warns)
            if offsite:
                if PLACEHOLDER.search(t):
                    warns.append(f"{mid} [{field}] off-Amazon line has unfilled {PLACEHOLDER.findall(t)} - fill with real data before use")
                continue
            pat = first_hit(APLUS_POLICY, low)
            if pat:
                flags.append(f"{mid} [{field}] A+ policy wording /{pat}/ - not allowed on A+ images: {t!r}")
            if PLACEHOLDER.search(t):
                flags.append(f"{mid} [{field}] A+ line has unfilled placeholder {PLACEHOLDER.findall(t)}: {t!r}")
            if field == "copy" and claim_star(t):
                star_rows.append(mid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--forbid", default="")
    ap.add_argument("--supplement", action="store_true")
    ap.add_argument("--listing", action="store_true")
    ap.add_argument("--max-over", type=int, default=10)
    a = ap.parse_args()

    data = json.load(open(a.json, encoding="utf-8"))
    rows = data["rows"]
    marketing = data.get("marketing") or []
    explainers = data.get("explainers") or []
    excipients = (data.get("excipients") or {}).get("items") or []
    forbid = [t.strip() for t in a.forbid.split(",") if t.strip()]
    flags, warns = [], []
    claims = (data.get("meta") or {}).get("claims") or {}
    CLAIM_GUARD[:] = blocked_patterns(claims.get("blocked") or [])
    if (marketing or explainers) and not claims:
        warns.append("meta.claims not set - define allowed/blocked benefit directions in the plan "
                     "(references/ingredient-research.md) so off-listing claims get caught")
    has_fda = any(FDA_MARK in (r.get("copy") or "").lower() for r in rows)
    star_rows = []
    cjk = re.compile(r"[一-鿿]")

    for r in rows:
        rid = r.get("id", "?")
        for field in ("copy", "alt"):
            t = r.get(field) or ""
            if not t or t == "—":
                continue
            if DISCLAIMER_EXEMPT.search(t):
                continue
            low = t.lower()
            for term in forbid:
                if has_term(term, low):
                    flags.append(f"{rid} [{field}] contains forbidden term '{term}': {t!r}")
            pat = first_hit(APLUS_POLICY, low)
            if pat:
                flags.append(f"{rid} [{field}] A+ policy wording /{pat}/: {t!r}")
            pat = first_hit(CLAIM_GUARD, low)
            if pat:
                flags.append(f"{rid} [{field}] blocked benefit direction /{pat}/ (meta.claims.blocked): {t!r}")
            if a.supplement:
                for pat in SUPPLEMENT_RISK:
                    if re.search(pat, low):
                        warns.append(f"{rid} [{field}] high-risk wording /{pat}/: {t!r}")
            if a.listing and field == "copy" and cjk.search(t):
                flags.append(f"{rid} [copy] still contains Chinese characters (placeholder not replaced?): {t!r}")
            if a.listing and field == "copy" and re.search(r"标题|H1|headline", r.get("slot") or "", re.I):
                plain = re.sub(r"\*", "", t)
                if len(plain) > 45 or plain.count("\n") > 1:
                    warns.append(f"{rid} headline is {len(plain)} chars / {plain.count(chr(10))+1} lines - long for a 1600px gallery thumbnail")
            if field == "copy" and claim_star(t):
                star_rows.append(rid)
        copy = r.get("copy") or ""
        if rid.upper().startswith("ALT") and len(copy) > 100:
            flags.append(f"{rid} alt text is {len(copy)} chars (>100)")
        ph = r.get("placeholder") or ""
        if ph and ph != "—" and not ph.startswith("（") and not rid.upper().startswith("ALT"):
            over = len(copy) - len(ph)
            if over > a.max_over:
                warns.append(f"{rid} copy is {over} chars longer than placeholder ({len(copy)} vs {len(ph)}) - check fit or offer shorter alt")

    check_brand_voice(rows, flags, warns)
    check_marketing(marketing, a, forbid, flags, warns, star_rows)
    check_explainers(explainers, a, forbid, flags, warns, star_rows)
    check_excipients(excipients, a, forbid, flags, warns, star_rows)

    if a.supplement and star_rows and not has_fda:
        flags.append(f"claim asterisks in {star_rows} but no FDA disclaimer row found")

    print(f"rows scanned: {len(rows)} | marketing: {len(marketing)} | explainers: {len(explainers)} | "
          f"excipients: {len(excipients)} | claim-asterisk rows: {star_rows} | "
          f"FDA disclaimer present: {has_fda}")
    for f in flags:
        print("FLAG ", f)
    for w in warns:
        print("WARN ", w)
    if not flags:
        print("OK: no FLAG items")
    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
