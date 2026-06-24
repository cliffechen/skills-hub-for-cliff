---
name: spf-products-advances-to-image-copy
description: |
  Generate image copy for Amazon US dietary supplement listings (main images + A+ Content).
  Takes product SFP info and selling points as input, outputs compliant English copy for 7 main images and A+ modules.
  Built-in FDA/Amazon compliance checks and Alexa AI extraction optimization.
  Trigger: "出图", "图片文案", "主图文案", "A+文案", "listing图片", "supplement copy", "image copy", "作图文案", "出图brief".
  Also trigger when user provides Supplement Facts Panel or product parameters and asks for listing image text.
---

# Amazon US Dietary Supplement — Image Copy Generator

Generate compliant English image copy for Amazon US dietary supplement listings, following a proven persuasion framework adapted from top-performing competitor brands.

## Before You Start

Read these reference files for full context:
- [compliance-rules.md](compliance-rules.md) — FDA/Amazon compliance boundaries (CRITICAL)
- [alexa-optimization.md](alexa-optimization.md) — Alexa AI extraction optimization
- [persuasion-framework.md](persuasion-framework.md) — Competitor persuasion structure reference

## Step 1: Gather Product Information

Collect these fields from the user. **Ask for missing items, do not guess.**

| Field | Required | Example |
|-------|----------|---------|
| Brand name | Yes | "VitaCore" |
| Product name | Yes | "Cellular Vitality Complex" |
| Supplement Facts Panel (full) | Yes | Ergothioneine 60mg, PQQ 20mg, CoQ10 100mg... |
| Serving size & per container | Yes | "2 Capsules, 30 Servings" |
| Other Ingredients | Yes | "Vegetable capsule, rice flour" |
| Target audience | Yes | "Women 30+" / "Adults" |
| Core benefit direction | Yes | "Cellular health, antioxidant support" |
| Third-party certifications | Yes | "SGS tested, cGMP, 5 patents" |
| Scientific references (if any) | No | Published papers, clinical studies |
| Usage instructions | Yes | "Take 2 capsules daily with food" |
| Key differentiators | No | Unique ingredient forms, delivery tech |

If user provides a photo of their SFP label, extract all info from it and confirm accuracy.

## Step 2: Generate Copy

Output copy for each image slot in this exact format:

### Main Images (7 images)

```
=== MAIN IMAGE 1: Hero / White Background ===
[Visual direction: product on white background, clean and minimal]
Headline: [Brand] [Product Name]
Subline: [Core specs — e.g., "60 Capsules | 30 Servings"]
Key text: [1-2 lines of core positioning, keyword-rich]

=== MAIN IMAGE 2: Key Ingredients & Benefits ===
[Visual direction: product + ingredient highlights]
Headline: [Keyword-first — e.g., "4 Key Ingredients for Cellular Health Support"]
Ingredient 1: [SFP exact name] [amount] — [Structure/Function claim]
Ingredient 2: [SFP exact name] [amount] — [Structure/Function claim]
Ingredient 3: [SFP exact name] [amount] — [Structure/Function claim]
Ingredient 4: [SFP exact name] [amount] — [Structure/Function claim]
Footer: "*These statements have not been evaluated by the FDA. This product is not intended to diagnose, treat, cure, or prevent any disease."

=== MAIN IMAGE 3: How It Works (Mechanism) ===
[Visual direction: scientific visualization of ingredient action]
Headline: [Keyword-first — e.g., "Cellular Antioxidant Protection — How It Works"]
Step/pathway 1: [Educational description of mechanism]
Step/pathway 2: [Educational description of mechanism]
Step/pathway 3: [Educational description of mechanism]
Footer: [Source citation if applicable]

=== MAIN IMAGE 4: Science & Research ===
[Visual direction: research citations + key findings]
Headline: [e.g., "Backed by Published Research"]
Study 1: [Journal name] — [One-sentence plain English summary, structure/function only]
Study 2: [Journal name] — [One-sentence plain English summary, structure/function only]
Disclaimer: "*For educational purposes only. Individual results may vary."

=== MAIN IMAGE 5: Safety & Certifications ===
[Visual direction: certification icons + "Free From" matrix]
Headline: [e.g., "Third-Party Tested | 15 Patents | cGMP Certified"]
Free From list: [Hormone-Free / Plasticizer-Free / Pesticide-Free / Heavy Metal-Free / Preservative-Free]
Certifications: [List each with icon]

=== MAIN IMAGE 6: How to Use & Who It's For ===
[Visual direction: lifestyle photos + usage instructions]
Headline: [e.g., "Simple Daily Support — 2 Capsules with a Meal"]
Directions: [Exact usage instructions matching label]
Suitable For: [Audience scenarios]
Not Suitable: [e.g., "Not for use during pregnancy or lactation. Consult your healthcare provider."]

=== MAIN IMAGE 7: FAQ ===
[Visual direction: clean Q&A layout]
Headline: "Frequently Asked Questions"
Q1: [Most common question — e.g., "How long until I see results?"]
A1: [Compliant answer]
Q2: [e.g., "Is this product third-party tested?"]
A2: [Compliant answer]
Q3: [e.g., "Can men take this product?"]
A3: [Compliant answer]
Q4: [e.g., "Are there any allergens?"]
A4: [Compliant answer]
Q5: [e.g., "How should I store this product?"]
A5: [Compliant answer]
Q6: [e.g., "Can I take this with other supplements?"]
A6: [Compliant answer]
```

### A+ Content Modules

After main images, generate A+ Content copy following this 12-module sequence. For each module, output:
- Module title
- Headline (keyword-first for Alexa)
- Body copy
- Visual direction notes
- Alexa priority tag (High/Medium/Low)

Module sequence:
1. Product Hero + Core Specs (Alexa: High)
2. Certification Matrix (Alexa: High)
3. Clinical/Study Results — structure/function language (Alexa: High)
4. Whole-Body Benefits — by body system (Alexa: Medium)
5. Health Topic Education — general wellness context (Alexa: Medium)
6. Mechanism of Action — how ingredients work (Alexa: High)
7. Ingredient Deep-Dive — SFP-exact names + amounts (Alexa: High)
8. Research Citations — journal + one-sentence summary (Alexa: Medium)
9. Safety & "Free From" Matrix (Alexa: High)
10. Brand Story & Awards (Alexa: Low)
11. Product Specifications — full SFP (Alexa: High)
12. FAQ — 6-8 Q&As (Alexa: High)

## Step 3: Compliance Self-Check

Before delivering, verify EVERY line of copy against this checklist:

```
Compliance Check:
- [ ] All ingredient names match SFP exactly (character-by-character)
- [ ] All amounts/units match SFP exactly (mg, mcg, IU — no conversions)
- [ ] No disease treatment/prevention/diagnosis/cure claims
- [ ] No "Raw Herb Equivalent" or extraction ratios (10:1, 20:1)
- [ ] No efficacy enhancement narratives ("stronger", "more concentrated", "superior")
- [ ] No implied functions not supported by the label
- [ ] No claims about absorption rate or bioavailability superiority
- [ ] FDA disclaimer present on images with structure/function claims
- [ ] "Not intended to diagnose, treat, cure, or prevent any disease" present
- [ ] All data points have source citations
- [ ] No before/after treatment implication in visuals descriptions
```

If ANY check fails, rewrite before delivering.

## Step 4: Alexa Optimization Self-Check

```
Alexa Check:
- [ ] Every headline contains at least one extractable keyword or data point
- [ ] Ingredient info is structured and parseable (name + amount + function)
- [ ] "What does it do?" has a clear, direct answer
- [ ] "How do I take it?" has a clear, direct answer
- [ ] "Is it safe?" has a clear, direct answer
- [ ] FAQ covers 5+ common questions
- [ ] Comparison-ready data present (serving size, capsule count, cert count)
- [ ] No pure-rhetoric headlines (every title carries information)
- [ ] Q&A format uses natural language matching how customers ask Alexa
```

## Key Rules Summary

1. **SFP is law**: Every ingredient mention in image copy must match the Supplement Facts Panel verbatim.
2. **Structure/Function only**: Use "supports", "promotes", "helps maintain" — never "treats", "cures", "prevents".
3. **Keyword-first headlines**: Alexa extracts titles. "Cellular Antioxidant Support — 4 Ingredients" beats "Unlock Your Inner Radiance".
4. **FAQ is king for Alexa**: The FAQ module is the highest-value content for AI shopping assistants. Make it comprehensive.
5. **Compliance > persuasion**: If a compelling claim can't pass compliance, rewrite it in structure/function language. Never sacrifice compliance for cleverness.
6. **Data with sources**: Every data point needs a citation. Uncited data = compliance risk.
7. **Metaphors must be safe**: "Cellular energy support" is fine. "Garden rejuvenation" implies treatment. When in doubt, use literal language.

## Output Language

- **图片文案本身（出现在图片上的文字）**：全部使用 **英文**，面向亚马逊美国站消费者。
- **所有说明性内容**（视觉方向、字段标签如"标题：""正文：""底部声明："、Alexa 注释、自检备注等）：全部使用 **中文**，面向国内亚马逊运营团队阅读。
- **与用户的沟通**：使用中文（用户的主要语言）。

简单说：运营拿到这份文档后，英文部分直接给设计师/AI 生图用，中文部分帮运营理解每张图的功能和设计方向。

## Visual Direction Notes

For each image slot, include brief visual direction in brackets. These notes help the user brief their designer or configure AI image generation. Keep them practical: color palette suggestions, layout structure, reference imagery type.
