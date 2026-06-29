# Project input and output structure

This reference defines the folder contract for this skill. Explanations to the user should be in Chinese. Customer-facing image copy should stay in English by default.

## Required project folders

The user should place layout images and product information into these folders under the active project root.

### Layout input folders

At least one of these folders must exist:

- `A+排版模板`
- `主图排版模板`

Usage:

- Put A+ layout references, wireframes, or existing A+ image structures into `A+排版模板`.
- Put main-image or secondary-image layout references into `主图排版模板`.
- Supported image files include `.png`, `.jpg`, `.jpeg`, `.webp`.

If neither folder exists, stop and tell the user in Chinese:

```text
请先在项目根目录建立 `A+排版模板` 或 `主图排版模板` 文件夹，然后把需要配文案的排版结构图放进去。
```

If both folders exist, process both unless the user names only one.

### Product information folder

This folder is required:

- `真实产品信息`

The user should put these files inside:

- Supplement Facts image or PDF. Required.
- Product label images. Recommended.
- Product advantages, desired selling points, claim matrix, clinical substantiation, certification proof, or COA. Optional.
- Existing listing title, bullets, A+ copy, backend attribute notes, or target audience notes. Optional.

If `真实产品信息` is missing, stop and tell the user in Chinese:

```text
请先在项目根目录建立 `真实产品信息` 文件夹，并放入真实产品的 Supplement Facts。产品优势、证书、临床依据、现有 Listing 文案可以一起放进去，作为可选参考。
```

If the folder exists but no readable Supplement Facts are present, stop and ask the user to add a clear Supplement Facts image/PDF or typed transcription.

## Backward compatibility aliases

If the project already has older folders, mention the standard names but still inspect these aliases:

- `A+排版结构模板` can be treated as `A+排版模板`.
- `真实产品supplement facts` can be treated as `真实产品信息` only for Supplement Facts extraction.

When using an alias, tell the user in Chinese that the standard folder name should be used in future projects.

## Output folder

Create or use:

- `输出文案`

Do not overwrite older outputs. Save Markdown outputs using this pattern:

```text
输出文案/[YYYYMMDD]-[product-or-project]-[a-plus-or-main-image]-copy.md
```

If the product name is unknown, use:

```text
输出文案/[YYYYMMDD]-amazon-supplement-image-copy.md
```

## Output file sections

Use Chinese for section explanations and review notes. Keep customer-facing copy and alt text in English.

Recommended Markdown structure:

1. `输入文件读取`
   - List layout folders, product info files, and missing items.
2. `Supplement Facts 提取`
   - Table with exact label text.
3. `可用/慎用/禁用表达边界`
   - Explain claim limits in Chinese.
4. `图片文案`
   - For each image: image role, recommended version, safer version, bolder version if useful, alt text, OCR note.
5. `AI 味检查`
   - List stale phrases avoided and the cleaned version.
6. `合规风险表`
   - Phrase, risk, reason, safer version.
7. `Alexa/COSMO 适配`
   - Conversational queries, semantic nodes, alt text strategy.
8. `下一步`
   - Short Chinese action list.
