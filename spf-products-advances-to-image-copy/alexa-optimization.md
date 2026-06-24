# Alexa AI Extraction Optimization

## How Alexa Shopping Works (2026)

Alexa Shopping (integrated with Rufus) extracts text from listing images and uses it for:
- **AI Smart Overview**: displayed at top of search results
- **Product Comparison**: side-by-side feature/price/review comparisons
- **Personalized Recommendations**: matches products to user queries
- **Category Guides**: generates buying guides for product categories
- **Q&A Responses**: answers customer questions using listing content

Alexa combines Rufus product knowledge + Amazon shopping history + Alexa+ personalization.

## Core Principle

**Image copy is no longer just for human eyes — it's training data for Amazon's AI shopping assistant.** If Alexa can't parse your image text, you're invisible to AI-assisted discovery.

## Optimization Rules

### 1. Keyword-First Headlines

Alexa extracts headlines as primary product descriptors. Every headline must lead with a searchable keyword.

| Bad (pure rhetoric) | Good (keyword-first) |
|---|---|
| "Unlock Your Inner Radiance" | "Cellular Antioxidant Support — Ergothioneine 60mg" |
| "Feel the Difference" | "Skin Firmness & Collagen Support — 4 Key Ingredients" |
| "The Ultimate Solution" | "Third-Party Tested — 15 Patents, SGS Certified" |
| "Embrace Youthful Vitality" | "Women's Wellness Support — Mitochondrial Health Formula" |

### 2. Structured Ingredient Info

Alexa parses structured data for comparison tables. Use consistent format:

```
[Ingredient Name] [Amount][Unit] — [One Structure/Function claim]
```

Example:
```
Ergothioneine 60mg — A potent antioxidant that helps protect cells from oxidative stress
PQQ Disodium Salt 20mg — Supports mitochondrial biogenesis and cellular energy
Coenzyme Q10 (Crystal QH) 100mg — Supports cellular energy metabolism
```

### 3. Pre-Answer Common Questions

Alexa answers customer questions using your listing content. Pre-embed answers to these high-frequency queries:

| Customer asks Alexa | Your image copy should contain |
|---|---|
| "What does this supplement do?" | Clear function statement in Main Image 1 or 2 |
| "What are the key ingredients?" | Full ingredient list with SFP-exact names |
| "How do I take it?" | Directions on Main Image 6 + FAQ |
| "Is it safe?" | Certification info on Main Image 5 + FAQ |
| "How is this different?" | Factual differentiators on Main Image 7 |
| "Are there side effects?" | Safety section + "consult healthcare provider" |
| "Can [specific person] take this?" | Suitable/Not Suitable list |
| "Does it contain [allergen]?" | "Free From" list |

### 4. Comparison-Friendly Data Points

Alexa builds comparison tables from extractable data. Ensure these are present as standalone, parseable text:

- Serving size (e.g., "2 Capsules")
- Servings per container (e.g., "30 Servings")
- Capsule/bottle count (e.g., "60 Capsules")
- Number of key ingredients
- Number of certifications/patents
- Third-party testing body (e.g., "SGS Tested")
- Manufacturing standard (e.g., "cGMP Certified")

### 5. FAQ Format is Critical

The FAQ module has the highest Alexa extraction weight. Format as:

```
Q: [Natural language question matching how customers actually ask]
A: [Direct, factual answer with specific details]
```

Tips:
- Use conversational question phrasing (matches voice search patterns)
- Answers should be 1-2 sentences max
- Include specific numbers where possible (serving size, capsule count, days of use)
- Cover: usage, safety, ingredients, audience, storage, compatibility with other products

### 6. Avoid Anti-Patterns

| Anti-pattern | Why it hurts |
|---|---|
| Pure rhetoric titles ("Embrace the Change") | Alexa skips non-informational text |
| Data buried in long paragraphs | Alexa can't extract structured data from prose |
| Inconsistent ingredient names across images | Confuses AI matching, may flag compliance |
| Claims in visual metaphors only (no text) | Alexa can't read visual metaphors |
| FAQ with vague answers | Reduces Alexa recommendation confidence |

## Priority Map

Content types ranked by Alexa extraction weight:

1. **FAQ Q&A pairs** — highest direct match for customer queries
2. **Ingredient lists with amounts** — core comparison data
3. **Product specs** (serving size, count, certifications) — comparison table data
4. **Headlines with keywords** — AI overview generation
5. **Study/research citations** — trust signal extraction
6. **Safety/certification info** — safety filter data
7. **Brand story/awards** — lowest extraction priority
