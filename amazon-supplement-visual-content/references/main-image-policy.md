# Amazon Main Image Policy Notes

Use this file as the first guardrail when the user asks for an Amazon supplement main image. If the user needs a legally final upload decision, tell them to verify the current Seller Central image rules for the exact category and marketplace.

Official starting points:
- Amazon Seller Central product image requirements: https://sellercentral.amazon.com/help/hub/reference/external/G1881
- Amazon product images overview: https://sell.amazon.com/blog/amazon-product-images

## Main Image vs Secondary Image

Amazon first main image means the primary image shown in search results and on the product detail page. Treat it differently from secondary gallery images.

For Amazon US supplement first main images, default to:
- Pure white background.
- Product only: bottle, box, pouch, or legitimate included packaging/components.
- Product large enough to clearly identify, generally filling most of the frame.
- Accurate packaging, count, flavor, net quantity, and label facts.
- Sharp focus, realistic lighting, no distortion, no misleading scale.

Avoid on the first main image:
- Text overlays, claims, slogans, badges, icons, arrows, inset panels, comparison charts, certification stickers that are not physically on the package, before/after imagery, lifestyle scenes, hands, models, props, capsules spilling as a decorative claim cue, artificial ingredient piles, or backgrounds other than white.
- Any generated label text unless the user supplies exact label artwork and the tool can preserve it.

Use secondary gallery images or A+ images for:
- Ingredient education.
- Supplement Facts callouts.
- Mechanism diagrams.
- Routine or use-case images.
- Certification explanations.
- Comparison tables.
- FAQ and objection handling.
- Rufus/Alexa/COSMO-readable copy and alt text.

## Supplement-Specific Risk

Main images for supplements are often rejected or weakened by:
- Medical implication from props, such as hospital objects, disease symbols, or pain imagery.
- Claims that exceed the label or evidence.
- "Clinically proven", "doctor recommended", "FDA approved", or disease wording.
- Artificial badges such as "No. 1", "Best", "Guaranteed", "100% safe", or "Pharmaceutical grade" without approved substantiation.
- Label mismatch between image, title, bullets, and Supplement Facts.

## Safe First-Main-Image Brief

Use this structure:

```text
Create a compliant Amazon US supplement first main image on a pure white background. Show only the product packaging supplied by the user. Preserve the label, cap, color, count, flavor, net quantity, and brand layout exactly. Use clean studio lighting, front three-quarter angle or straight-on front view, sharp focus, natural shadows, and enough scale for the bottle/box to dominate the frame. Do not add text, badges, icons, ingredients, props, hands, lifestyle elements, comparison panels, claims, or decorative graphics.
```

If no real product image or label artwork is supplied, write:

```text
This can be a concept mockup only. A final Amazon upload image needs the real product photo or exact packaging artwork.
```

## Review Checklist

| Check | Pass condition |
|---|---|
| Background | White, clean, no scene or texture |
| Product truth | Packaging and label facts match supplied files |
| No overlay | No added copy, icons, badges, arrows, panels |
| No claims | No visual or textual health claims beyond package |
| No disease cue | No disease, symptom, treatment, or medical imagery |
| Crop | Product is large, clear, not cut off unnaturally |
| Quality | Sharp, realistic, no warped label or unreadable key text |
| Consistency | Matches title, bullets, Supplement Facts, and product attributes |
