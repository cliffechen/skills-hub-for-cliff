# Query Routing Rules

Use these rules when the user asks which skill to use.

## Answer Requirements

Always answer with:

1. Direct recommendation.
2. Why this skill is the best fit.
3. Which platform version to use.
4. Required inputs.
5. One copyable invocation sentence.
6. Optional fallback skill if useful.

Do not give a long list when one answer is clearly best.

## Platform Choice

- If the user says Codex, OpenAI, or this chat: recommend Codex/OpenAI original.
- If the user says WorkBuddy, WB, Tencent, or workbubby: recommend the `-WB` directory when available.
- If a WorkBuddy directory exists but lacks WorkBuddy standard package files, say it is the WB version directory and mention any missing package pieces only if relevant.
- If no platform is specified, recommend the best skill and mention platform-specific variants briefly.

## Common Amazon Task Routes

| User Need | Primary Skill | Platform Note |
|---|---|---|
| 根据 Amazon 产品写图片文案、主图、辅图、A+ 页面结构、设计 brief、生图 prompt | `amazon-supplement-visual-content` | Use `amazon-supplement-visual-content-WB` in WorkBuddy |
| 快速生成补充剂 7 张图和 A+ 文案 | `spf-products-advances-to-image-copy` | Good fallback for copy-first work |
| Amazon US 下拉词拓词 | `amazon-dropdown-expander` | Easy WorkBuddy conversion |
| 新品关键词库、P0/P1/P2、Search Term、广告关键词基础 | `amazon-new-listing-keyword-library` | Needs ABA/Sif/dropdown/product info inputs |
| Amazon US 膳食补充剂选品、市场调研、Top100、Go/No-Go | `US_Sup_Product_Research_for_Qoderwork` | Heavy research; needs Sorftime/xCrawl |
| 成分、商标、专利、FDA/Amazon 风险检查 | `ingredients-breakdown-compliance-check` | Use before copying competitor formula or claims |
| 安全重建配方方向 | `supplement-safe-rebuild` | Needs upstream risk report |
| 配方优化，想知道怎么更有竞争力 | `formula-reconstruction` | Needs risk report + safe rebuild + market/keyword inputs |
| 成分和关键词流量边界、雷达图、候选 Supplement Facts | `amazon-supplement-boundary-analysis` | Needs Sif Excel + anchored ASIN + Supplement Facts |
| 最终配方简报、实验室交接 | `supplement-audience-satellite-formula-finalizer` | Last step after upstream analysis |

## Example

User asks: "我想根据亚马逊产品写图片文案，应该用哪个 skill？"

Recommended answer:

```markdown
推荐用 `amazon-supplement-visual-content`。

它更适合 Amazon US 补充剂的主图合规、辅图文案、A+ 页面结构、设计 brief 和生图 prompt。如果你在 WorkBuddy 里做，用 `amazon-supplement-visual-content-WB`。

准备这些输入：产品名、品牌、Supplement Facts、瓶身/标签图、目标图片类型、核心卖点、认证或检测依据。

可以这样说：
用 amazon-supplement-visual-content 基于这个 Amazon US 补充剂产品，生成主图合规方案、辅图文案和 A+ 页面结构。
```
