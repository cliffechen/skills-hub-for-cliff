# Alexa and COSMO Reference

## Current Context

As of the checked 2026 Amazon announcement, Amazon describes Alexa for Shopping as combining Rufus product expertise with Alexa+ personalization across the Amazon Shopping app, website, and Echo Show. It can answer questions in the search bar, compare products, generate AI overviews, use visual shopping, and personalize recommendations.

Use this as a practical writing constraint: the listing must be easy for a shopping AI to retrieve, understand, quote, and compare without hallucinating.

## Optimization Principles

1. Structured facts beat vague claims
   - Use clear facts from the label and product attributes.
   - Avoid contradictions between image text, A+ text, bullets, backend fields, and Supplement Facts.

2. Write answer-ready noun phrases
   - Use natural phrases that answer buyer questions.
   - Example pattern: "[product form] with [exact ingredient] for [normal wellness support]."
   - Do not keyword-stuff.

3. Make A+ a product knowledge base
   - Each module should answer one buyer question.
   - Include serving facts, ingredient role, use occasion, storage or routine fit, and comparison information only when true and supported.

4. Support OCR and visual search
   - Image text should be short, high contrast, and readable.
   - Put the core noun phrase on the relevant visual, not hidden in decorative text.
   - Avoid stylized fonts that OCR may misread.

5. Add alt text
   - Write alt text as factual image descriptions plus product context.
   - Include exact ingredient names only when visible or directly relevant.
   - Avoid adding unsupported claims in alt text.

6. Reduce AI hallucination risk
   - If the product facts are incomplete, say so.
   - Prefer "not specified on label" over guessing.
   - Do not let style override evidence.

## Useful Output Fields

For each image or A+ module, include:

- `Buyer question answered`
- `Visible copy`
- `Alt text`
- `OCR note`
- `Semantic nodes`
- `Consistency check`

## Official Source

- Amazon Alexa for Shopping announcement: https://www.aboutamazon.com/news/retail/alexa-for-shopping-ai-assistant
