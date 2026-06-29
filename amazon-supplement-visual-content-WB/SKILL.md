---
name: amazon-supplement-visual-content
description: Create Amazon US dietary supplement main-image directions, compliant product hero concepts, secondary image copy, A+ image copy, A+ page content architecture and module copy, and designer/image-generation handoffs from Supplement Facts, bottle or label images, product briefs, and layout references. Use when the user asks for Amazon supplement "main image", "listing image", "image copy", "主图", "辅图", "A+图片", "A+页面", "A+内容设计", "保健品主图", Supplement Facts based image text, FDA-aware image claims, product-language to user-language messaging, The Ordinary style supplement visuals, or Amazon-ready product image prompts.
---

# Amazon Supplement Visual Content

## Purpose

Use this skill to turn supplement facts, bottle/label assets, and product positioning into Amazon-ready image and A+ content deliverables. Keep the first Amazon main image compliant and text-free; use secondary gallery images and A+ modules for claims, ingredient education, comparison, and image copy. When the user asks for A+ page work, design the content structure and copy only unless they explicitly ask for image generation.

Default output language:
- Customer-facing image copy, alt text, and generation prompts: English for Amazon US.
- Review notes, risk flags, and next steps: Chinese unless the user asks otherwise.

## Load References

Always read:
- [main-image-policy.md](references/main-image-policy.md) for Amazon main-image guardrails and the main-vs-secondary decision.
- [compliance.md](references/compliance.md) for FDA, Amazon, and Supplement Facts claim boundaries.
- [style-and-output.md](references/style-and-output.md) for the clinical minimalist image-copy format.
- [message-hierarchy.md](references/message-hierarchy.md) for product-language to user-language translation, visual hierarchy, and memory-point discipline.

Read when relevant:
- [project-io.md](references/project-io.md) when the user gives a project folder with templates, Supplement Facts, or output folders.
- [a-plus-content-design.md](references/a-plus-content-design.md) when the user asks for A+ pages, A+ module copy, brand story, comparison charts, FAQ, or content architecture instead of actual image generation.
- [humanizer-principles.md](references/humanizer-principles.md) for hero lines, slogans, and high-visibility copy.
- [the-ordinary-brand-guide.md](references/the-ordinary-brand-guide.md) when the user wants The Ordinary-inspired tone.
- [alexa-cosmo.md](references/alexa-cosmo.md) when the user asks about Rufus, Alexa Shopping, COSMO, SEO, OCR, alt text, or AI shopping visibility.
- [amazon-seo-guide.md](references/amazon-seo-guide.md) when the task includes listing SEO, keywords, backend terms, or cross-listing consistency.

## Intake

Collect or infer:
- Product name, brand, marketplace, image type requested, and target output: final image prompt, copy deck, designer handoff, or review.
- Exact Supplement Facts: serving size, servings per container, active ingredients, forms, dose, units, Daily Value status, warnings, and other ingredients.
- Visual inputs: bottle photo, label artwork, box/carton, cap color, capsule/product photo, template screenshot, competitor reference, or desired crop.
- Product proof: certifications, testing, clinical references, ingredient sourcing, dietary attributes, and any user-provided claim boundaries.
- Listing context: title, bullets, A+ text, target keywords, ASIN, competitors, or existing image sequence.
- A+ page needs: Basic A+, Premium A+, Brand Story, module count, target objections, comparison products, FAQ topics, and whether the user wants content design only.

If Supplement Facts are unreadable or missing, do not invent ingredient names, doses, forms, or claims. Ask for clearer facts or produce only a placeholder art-direction draft.

## Workflow

1. Classify the request.
   - First Amazon main image: produce a white-background product hero with no text overlays, badges, ingredient callouts, icons, claims, lifestyle props, or inset panels unless the user provides current category-specific permission.
   - Secondary gallery image or A+ image: produce image copy, ingredient education, comparison, FAQ, routine, proof, and alt text.
   - A+ page content design: produce module strategy, module order, English copy, visual direction notes, comparison/FAQ content, and compliance notes. Do not generate images unless explicitly requested.
   - "主图" ambiguity: state whether the deliverable is an Amazon first main image or a Chinese-style gallery hero. For Amazon US, keep the first image compliant and move text to Image 2+.

2. Extract the factual boundary.
   - Transcribe Supplement Facts exactly.
   - Mark each potential claim as Allowed, Caution, or Blocked.
   - Treat the label and user evidence as the ceiling. Do not upscale claims from ingredient folklore.

3. Build the message hierarchy.
   - Choose one core memory point for the page or image set.
   - Translate product language into user language: ingredient, dose, format, or mechanism must become a plain buyer benefit or reduced hassle.
   - Use scientific language as proof, not as the first thing the shopper must decode.
   - Follow the decision path: first explain what it is, then why it matters, then reduce purchase uncertainty.

4. Build the image or A+ sequence.
   - Assign one role per image: compliant main image, ingredient story, mechanism education, daily routine, formula facts, proof/certification, comparison, FAQ, or trust close.
   - For A+ pages, assign one job per module: hero positioning, ingredient translation, mechanism education, formula facts, routine fit, proof, comparison, FAQ, or brand story.
   - Prevent semantic repetition across images. Do not repeat dose, serving count, support area, slogan, or buyer question unless the layout requires it.
   - Keep claims consistent with title, bullets, A+ copy, alt text, and product label.

5. Draft deliverables.
   - For main image: provide composition, crop, lighting, background, packaging accuracy checklist, generation/edit prompt, and upload risk notes.
   - For secondary/A+ image: provide visible copy slots, alt text, compliance notes, OCR notes, and Alexa/COSMO semantic nodes when relevant.
   - For A+ page content design: provide module order, purpose, customer question, headline, body copy, image brief note, proof anchor, compliance notes, and mobile/readability notes.
   - For designers: include text hierarchy, safe zones, max copy length, and what must not be shown.

6. Review.
   - Run FDA/Amazon risk check before finalizing.
   - Run humanizer pass on slogans and hero text.
   - Flag missing evidence, label conflicts, disease claims, overstated absorption/bioavailability, Amazon main-image violations, and A+ content risks such as price, promotion, refund, warranty, review, QR, or external-link wording.

## Main Image Output Contract

When the user asks for an Amazon first main image, output:

```markdown
## Amazon Main Image Plan

### Asset Requirements
- Required inputs:
- Missing inputs:

### Composition
- Canvas:
- Background:
- Product placement:
- Crop:
- Lighting:
- Packaging details to preserve:

### Prompt / Designer Brief
[English prompt or designer brief]

### Negative Prompt / Do Not Include
- Text overlays
- Badges, seals, icons, arrows, ingredient callouts
- Props or lifestyle scene
- Unverified label facts

### Compliance Check
| Check | Status | Note |
|---|---|---|

### Upload Risk
[Low/Medium/High with reason]
```

## Secondary Image Output Contract

When the user asks for gallery images, A+ modules, or image copy, output the sequence from [style-and-output.md](references/style-and-output.md), then add:

```markdown
### Sequence Summary
| Image | Role | Buyer question | Evidence anchor | Repetition risk |
|---|---|---|---|---|

### Compliance Risk Table
| Draft phrase | Risk | Reason | Safer version |
|---|---:|---|---|

### Designer Notes
- Text hierarchy:
- Max copy length:
- OCR/contrast:
- Keep off this image:
```

## A+ Content Design Output Contract

When the user asks for A+ page content design, module strategy, or A+ copy without image generation, output:

```markdown
## A+ Page Content Design

### Strategy
- Core memory point:
- Product language -> user language translation:
- Simple language / science language ratio:
- Primary shopper problem:
- Proof boundary:

### Module Map
| Module | Role | Shopper question | Evidence anchor | Copy level |
|---|---|---|---|---|

### Module Copy
#### Module [number] - [role]
- Headline: [English]
- Subhead: [English]
- Body: [English, 1-3 short sentences]
- Callouts:
  - [English]
  - [English]
- Visual direction note: [Chinese, content-only direction]
- Compliance note: [Chinese]
- Mobile/readability note: [Chinese]

### FAQ / Comparison / Brand Story
[Include only the sections relevant to the requested A+ type.]

### Compliance Risk Table
| Draft phrase | Risk | Reason | Safer version |
|---|---:|---|---|

### Implementation Notes
- Amazon A+ review risks:
- Facts needing proof:
- Claims to keep out of images/text:
```

## Hard Rules

- Do not make disease claims or implied disease claims.
- Do not say FDA approved, FDA certified, doctor recommended, clinically proven, proven results, treats, cures, prevents, heals, reverses, detoxifies, anti-inflammatory, pain relief, anxiety relief, depression relief, cancer, diabetes, arthritis, Alzheimer's, hypertension, UTI, IBS, fatty liver, or similar wording unless the user explicitly provides a legal/regulatory basis and asks for review.
- Do not invent Supplement Facts, certifications, certifications logos, clinical study numbers, ingredient forms, "more bioavailable" claims, extraction ratios, or potency multipliers.
- Do not create first-main-image copy overlays for Amazon US. Move selling copy to secondary images.
- Do not put price, discount, shipping, refund, guarantee, warranty, review, star rating, QR code, external URL, external contact, or competitor attack language into A+ content.
- Do not imitate The Ordinary, Timeline, Amazon, FDA, or Alexa wording or imply affiliation. Use the style direction only.
- If generating or editing an actual image, preserve the product label exactly when a real label is supplied. If exact label preservation is not possible, produce a concept mockup and label it as not final upload art.
