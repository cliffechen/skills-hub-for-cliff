# Monitoring methodology

## Metric direction

Amazon ABA Search Frequency Rank (SFR) is the trend source of truth:

- Rank 1 is the most popular search term.
- A smaller current rank means improvement.
- `rank_change = previous_rank - current_rank`.
- A positive `rank_change` means the keyword rose.
- A zero or negative value is excluded from the opportunity tiers.

Sorftime monthly search volume estimates absolute demand and CPC estimates ad cost. Neither overrides ABA direction.

## Tier behavior

The analyzer first applies breakout thresholds and then retains other rising supplement-related terms by their current rank band:

- Tier 1: current ABA rank at or above the top 1,000 band.
- Tier 2: current rank from 1,001 through 50,000.
- Tier 3: current rank below the top 50,000 band.

Primary breakout checks include a 50% or 1,000-position jump for top-ranked terms and large cross-band movements for lower-ranked terms. Because the code keeps all positive movers as a broad watchlist, do not describe every Tier 1 result as having met the strongest breakout threshold.

## Burst types

- `first_burst`: no top-1,000 rank in the available 24-month Sorftime window.
- `rebound`: previously reached a strong historical rank and returned.
- `steady_rise`: the latest three monthly ABA ranks improve consecutively.
- `long_tail_expansion`: a new long-tail term contains an existing Tier 1 root term.
- `declining`: medium-term ABA rank worsens and monthly volume also falls sharply.
- `unknown`: insufficient Sorftime history.

A falling monthly volume with an improving ABA rank is a possible high-level pullback, not enough by itself to mark a decline.

## Interpretation order

For every Tier 1 analysis:

1. State current and previous ABA ranks and direction.
2. Compare rank momentum with recent Sorftime history.
3. Assess CPC and keyword-extension evidence when present.
4. Distinguish early signal, rebound, established demand, and weak/uncertain evidence.
5. State practical next research action, such as validating ASIN competition, formula feasibility, compliance, or ad economics.

Do not turn a keyword signal into a product-launch recommendation without separate ASIN, margin, formulation, trademark, patent, and regulatory checks.

## Known coverage limitations

- AMZ123 HTML changes can break scraping; the minimum-count guard prevents a partial run from looking complete.
- New ingredients without any known health marker may never reach Agent classification.
- Sorftime data may be missing, delayed, or estimated.
- Tier labels are opportunity-watchlist buckets, not probability scores.
- The local dictionary learns from validated Agent classifications, so classification discipline directly affects future coverage.
