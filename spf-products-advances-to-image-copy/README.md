# spf-products-advances-to-image-copy

Amazon US 膳食补充剂 Listing 图片文案生成 skill。输入品牌、产品名、Supplement Facts、卖点和认证信息后，输出可给设计师或生图工具使用的主图与 A+ Content 文案。

## 适用场景

- 需要为 Amazon US 补充剂产品生成主图文案、A+ 文案或出图 brief
- 已有 Supplement Facts Panel，需要把成分、剂量和卖点整理成合规英文图片 copy
- 需要同时考虑 FDA/Amazon 合规边界和 Alexa/AI shopping assistant 的信息提取友好度

常见触发词包括：`出图`、`图片文案`、`主图文案`、`A+文案`、`listing图片`、`supplement copy`、`image copy`。

## 必要输入

| 字段 | 是否必需 | 说明 |
|---|---|---|
| Brand name | 必需 | 品牌名 |
| Product name | 必需 | 产品名 |
| Supplement Facts Panel | 必需 | 成分名称、剂量、单位必须完整 |
| Serving size / servings per container | 必需 | 每份用量和每瓶份数 |
| Other Ingredients | 必需 | 辅料信息 |
| Target audience | 必需 | 目标人群 |
| Core benefit direction | 必需 | 核心结构/功能方向 |
| Certifications | 必需 | 第三方检测、cGMP、专利等 |
| Usage instructions | 必需 | 标签一致的用法 |
| Scientific references | 可选 | 论文、临床或其他来源 |
| Key differentiators | 可选 | 差异化原料、形态、包装或交付方式 |

如果用户提供的是标签图片，先抽取 SFP 信息并让用户确认，不要猜测缺失字段。

## 输出内容

正式输出分两部分：

1. 7 张主图文案
   - Hero / White Background
   - Key Ingredients & Benefits
   - How It Works
   - Science & Research
   - Safety & Certifications
   - How to Use & Who It's For
   - FAQ

2. 12 个 A+ Content 模块
   - Product Hero + Core Specs
   - Certification Matrix
   - Clinical/Study Results
   - Whole-Body Benefits
   - Health Topic Education
   - Mechanism of Action
   - Ingredient Deep-Dive
   - Research Citations
   - Safety & Free From Matrix
   - Brand Story & Awards
   - Product Specifications
   - FAQ

图片上出现的文案默认使用英文；视觉方向、字段说明、合规备注和与用户沟通的内容使用中文。

## 合规重点

- SFP 是唯一事实来源，成分名称、剂量和单位必须逐字匹配
- 只使用 structure/function 语言，例如 `supports`、`helps maintain`、`promotes`
- 不写诊断、治疗、治愈、预防疾病相关表达
- 不写未经支持的吸收率、生物利用度或效果增强叙事
- 所有数据点必须有来源或明确标注为待补充
- 含结构/功能宣称的图片需要 FDA disclaimer

## Alexa 优化重点

- 标题优先放关键词和可提取数据点
- 成分信息保持 `名称 + 剂量 + 功能` 的结构
- FAQ 至少覆盖 5 个自然语言问题
- 避免纯情绪化标题，让每个标题都携带可解析信息

## 目录结构

```text
spf-products-advances-to-image-copy/
|-- README.md
|-- SKILL.md
|-- compliance-rules.md
|-- alexa-optimization.md
`-- persuasion-framework.md
```

## 使用方式

在支持 Agent Skills 的环境中，可以直接用自然语言触发：

```text
用 spf-products-advances-to-image-copy 给这个补充剂做 Amazon US 主图和 A+ 图片文案。
我会提供品牌名、产品名、Supplement Facts、用法和认证信息。
```

如果信息不完整，先补问缺失字段，再生成文案。生成后必须执行合规自检和 Alexa 自检。
