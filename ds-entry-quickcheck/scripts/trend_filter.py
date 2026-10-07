"""Rule 3: classify a keyword's ABA weekly search series.

Input: weekly searches oldest->newest, ending at the last CLEAN (non-promo) week.
Optionally the promo week value(s) after it, used only to check the signal holds.

Labels
  steady_rise : >=12 weeks history, recent 4w avg >= 1.5x baseline, >=3 of last 4 weeks >= 1.2x baseline
  new_rising  : <12 weeks of non-zero history, last 3 weeks strictly increasing
  pulse       : last week >= 2x baseline but fewer than 3 of last 4 weeks elevated
  flat        : everything else
A signal is "held" if the promo-week value stays >= 1.5x baseline (or keeps rising for new words).
"""
from statistics import median


def classify(series, promo=None, baseline_weeks=12, recent_weeks=4):
    nz = [v for v in series if v > 0]
    recent = series[-recent_weeks:]
    if len(nz) < baseline_weeks:
        tail = series[-3:]
        label = "new_rising" if len(tail) == 3 and tail[0] < tail[1] < tail[2] else "flat"
        held = bool(promo) and promo[-1] >= series[-1] * 0.8
        return {"label": label, "baseline": None, "ratio": None, "held": held}

    base = median(series[-(baseline_weeks + recent_weeks):-recent_weeks])
    ratio = (sum(recent) / len(recent)) / base if base else None
    elevated = sum(1 for v in recent if v >= 1.2 * base)
    if ratio and ratio >= 1.5 and elevated >= 3:
        label = "steady_rise"
    elif series[-1] >= 2 * base and elevated < 3:
        label = "pulse"
    else:
        label = "flat"
    held = bool(promo) and promo[-1] >= 1.5 * base
    return {"label": label, "baseline": round(base), "ratio": round(ratio, 2) if ratio else None,
            "elevated_weeks": elevated, "held": held}


if __name__ == "__main__":
    # Weekly searches 2026-06-13 .. 2026-09-26 (clean), then 2026-10-03 (promo-affected)
    data = {
        "hyaluronic acid powder": ([2561, 2149, 2241, 2006, 2051, 2086, 2699, 2005, 2101, 2047, 2087, 2018, 1989, 2130, 2838, 5863], [2253]),
        "golden seal root powder organic": ([270, 294, 367, 353, 395, 426, 561, 706, 696, 782, 670, 613, 504, 1233, 707, 1577], [1225]),
        "sodium ascorbate powder": ([2010, 1837, 1615, 1646, 1763, 2475, 1573, 1294, 1145, 1208, 1151, 1312, 1325, 1281, 1117, 5125], [2320]),
        "whey protein concentrate powder": ([106, 166, 259, 303, 384, 348, 286, 286, 332, 280, 313, 367, 332, 483, 629, 1341], [1634]),
        "vitamin b10 paba": ([1546, 3396], [2270]),
        "vitamin b2 for sleep": ([296, 582, 899, 5335], [12506]),
    }
    for kw, (s, p) in data.items():
        print(f"{kw:36s} {classify(s, p)}")
