# skills-hub-for-cliff

这是一个面向 **Amazon US 膳食补充剂业务** 的 Agent Skills 与本地工具仓库。

它收纳可复用的 AI 工作流与设计工作台：选品调研、关键词库、Listing 图片/A+ 内容、文案编写与手机预览、成分合规/IP 风险、配方重建，以及 Codex / WorkBuddy / Obsidian 的 skill 索引管理。

## 这个仓库解决什么问题

如果你经常在 Codex、Claude Code、QoderWork、WorkBuddy 等 agent 工具里重复做这些事：

- 调研 Amazon US 补充剂产品机会
- 拓展关键词、整理新品关键词库
- 根据 Supplement Facts 写主图、辅图和 A+ 图片文案
- 在本地工作台编写设计稿文案，预览主副图、A+ 图片、轮播和视频的手机浏览效果
- 检查竞品成分、商标、专利和 Amazon/FDA 风险
- 基于竞品做安全重建和差异化配方
- 维护一份 Obsidian skill 索引，并查询“我现在该用哪个 skill”

这个仓库就是这些流程的集中入口。

## 快速选择：我该用哪个 skill？

### Amazon Design · 图片、文案与手机预览

本分类同时收纳可直接运行的本地项目和 Agent Skills。两个工作台各自保留独立目录，按各自 README 启动。

| 你要做什么 | 推荐项目 / skill | 说明 |
|---|---|---|
| 检查主副图、From the brand 品牌故事、A+ 整图、高级轮播和视频在手机上的浏览效果 | [`amazon-mobile-preview-tool`](./amazon-mobile-preview-tool/) | 本地离线预览工具；Python 3.10+，无需第三方包；主副图、品牌故事与 A+ 独立编辑分区；Windows 双击启动 |
| 在可视化工作台里为详情页 / A+ 设计稿写四风格合规文案，看图定位槽位、改稿、合规检查、导出 | [`amazon-copy-writing-project`](./amazon-copy-writing-project/) | 本地 Python 工作台（离线运行），四视图 + 逐槽位文案 + 发散备选 + 人群研究与场景切入 |
| 根据 Amazon 产品写主图、辅图、A+ 页面结构、设计 brief、生图 prompt | [`amazon-supplement-visual-content`](./amazon-supplement-visual-content/) | Codex/OpenAI 原版，适合正式出图前做内容与合规总控 |
| 在 WorkBuddy 里做补充剂图片/A+ 内容 | [`amazon-supplement-visual-content-WB`](./amazon-supplement-visual-content-WB/) | WorkBuddy 版目录，目前用于和原版区分管理 |
| 快速生成 7 张图和 A+ 图片英文文案 | [`spf-products-advances-to-image-copy`](./spf-products-advances-to-image-copy/) | 偏文案生成，适合已有 SFP 和卖点时快速出稿 |

### 关键词与 Listing 运营

| 你要做什么 | 推荐 skill / 工具 | 说明 |
|---|---|---|
| 采集 Amazon US 搜索框下拉词 | [`amazon-dropdown-expander`](./amazon-dropdown-expander/) | 轻量 Python 工具，输出 CSV |
| 搭建新品关键词库、P0/P1/P2、Search Term 和广告词基础 | [`amazon-new-listing-keyword-library`](./amazon-new-listing-keyword-library/) | 输入 ABA、Sif、下拉词、产品信息图，输出 Excel + 策略报告 |
| 批量生成亚马逊 Listing QA（默认200组，埋词/品牌词/语义痕迹） | [`amz-qa-creator`](./amz-qa-creator/) | 上游接 `amazon-new-listing-keyword-library` 的词库 Excel，配 ASIN/Sorftime VOC，输出 xlsx/csv/txt + 质检报告 |

### 选品、市场调研与出海战略

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 做 Amazon US 膳食补充剂选品和 Go/No-Go 判断 | [`US_Sup_Product_Research_for_Qoderwork`](./US_Sup_Product_Research_for_Qoderwork/) | 重型选品调研，依赖 Sorftime / xCrawl 等工具 |
| 围绕种子词做 Amazon US 选品调研、自动处理关键词漂移，并生成审计报告 | [`amazon-sorftime-mcp-with-serpapi-tavily`](./amazon-sorftime-mcp-with-serpapi-tavily/) | Sorftime 主数据 + SerpApi Google Web Trends + Tavily；固定输出 JSON、Markdown、HTML |
| 调用 Sorftime MCP / ZooData 兼容数据层，查商品、市场、评论、历史趋势 | [`zoodata-amz-marketing-skill/zoodata`](./zoodata-amz-marketing-skill/zoodata/) | 共享数据层，默认优先走 Sorftime MCP |
| 做亚马逊市场、竞品、定价、进入、选品、评论等多工作流分析 | [`zoodata-amz-marketing-skill`](./zoodata-amz-marketing-skill/) | 集中收纳 `zoodata` 与一组 `amazon-*` 数据分析技能 |
| 为跨境出口企业做指定产品+目标市场的深度市场进入/GTM 战略报告（B2B/B2C 通用） | [`GinvSkill-market-entry-report`](./GinvSkill-market-entry-report/) | 麦肯锡式分析框架，按固定七章结构输出可交付客户的 HTML 战略报告 |

### 成分合规与配方研发

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 检查成分、商标、专利、FDA/Amazon 和商业化风险 | [`ingredients-breakdown-compliance-check`](./ingredients-breakdown-compliance-check/) | 适合上架、换标、仿制、改配方前先跑风险报告 |
| 做完整保健品配方研发链路 | [`supplement-formula-pipeline`](./supplement-formula-pipeline/) | 包含风险查验、安全重建、配方优化、流量边界和最终收口 |

### Skill 管理与索引

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 扫描本仓库、更新 Obsidian 索引、查询该用哪个 skill | [`ob-skill-github-organizer`](./ob-skill-github-organizer/) | 本仓库的“索引维护员 + skill 路由员” |

## 顶层目录

```text
.
├── ABAKeywords-tracker-for-codex/
├── ABAKeywords-tracker-for-workbuddy/
├── GinvSkill-market-entry-report/
├── US_Sup_Product_Research_for_Qoderwork/
├── amazon-copy-writing-project/
├── amazon-dropdown-expander/
├── amazon-mobile-preview-tool/
├── amazon-new-listing-keyword-library/
├── amz-qa-creator/
├── amazon-search-term-advisor/
├── amazon-sorftime-mcp-with-serpapi-tavily/
├── amazon-supplement-visual-content/
├── amazon-supplement-visual-content-WB/
├── marketing-distiller/
├── ob-skill-github-organizer/
├── ingredients-breakdown-compliance-check/
├── spf-products-advances-to-image-copy/
├── supplement-formula-pipeline/
└── zoodata-amz-marketing-skill/
```

## 平台区分

这个仓库同时包含 Agent Skills 和独立运行的本地项目。

| 类型 | 怎么判断 | 怎么使用 |
|---|---|---|
| 本地应用项目 | 例如 `amazon-mobile-preview-tool`、`amazon-copy-writing-project`，包含源码、启动入口和项目 README | 下载或克隆后按项目 README 在本机启动；不要求有 `SKILL.md`，无需复制到 skills 目录 |
| Codex/OpenAI 原版 | 通常有根目录 `SKILL.md`，可能有 `agents/openai.yaml` | 适合 Codex / OpenAI 侧直接使用或安装 |
| Claude Code / QoderWork 兼容 | 根目录 `SKILL.md` + `README.md` + `references/` | 多数可作为普通 Agent Skill 使用 |
| WorkBuddy 版目录 | 目录名带 `-WB`，例如 `amazon-supplement-visual-content-WB` | 用于和 Codex 原版分开管理；如需标准分享包，可再整理成 WorkBuddy 包结构 |
| WorkBuddy 标准包 | `README_WORKBUDDY.md` + `SKILL/SKILL.md` | 可作为 WorkBuddy 分享包形态使用 |

> 注意：目录名带 `-WB` 不等于已经是完整 WorkBuddy 标准包。是否标准，要看里面有没有 `README_WORKBUDDY.md` 和 `SKILL/SKILL.md`。

## 主要业务模块

### 1. 选品与市场调研

[`US_Sup_Product_Research_for_Qoderwork`](./US_Sup_Product_Research_for_Qoderwork/)

用于围绕某个成分词或产品关键词，分析 Amazon US 膳食补充剂市场：

- 类目和关键词数据
- Top100 产品结构
- 剂型、剂量、价格带、人群、认证标签等维度
- 竞品差评和用户痛点
- 站外信号
- Go / No-Go 评分
- MD、HTML、Dashboard、Excel 四件套交付

[`amazon-sorftime-mcp-with-serpapi-tavily`](./amazon-sorftime-mcp-with-serpapi-tavily/)

用于由种子词出发做 Amazon US 补充剂选品调研，先以 Sorftime 验证语义候选词、搜索结果相关率和消费者真实搜索路径，再自动将完整调研接管到得分最高的主词：

- Sorftime MCP：站内关键词、商品、销量、上架日期和评论证据
- SerpApi：Google Web Trends（不采集 Google Shopping）
- Tavily：站外科学、法规与趋势交叉验证
- 固定交付物：`data.json`、`report.md`、`html/report.html` 和脱敏原始审计文件

[`zoodata-amz-marketing-skill`](./zoodata-amz-marketing-skill/)：`zoodata` 和配套 `amazon-*` 数据分析技能

用于直接走 Sorftime MCP / ZooData 兼容数据层，完成 Amazon US 市场和产品分析：

- [`zoodata`](./zoodata-amz-marketing-skill/zoodata/)：共享数据层，查商品、类目、市场、评论、价格带、品牌、历史趋势
- [`amazon-analysis`](./zoodata-amz-marketing-skill/amazon-analysis/)：综合市场 / 竞品 / 机会 / 定价分析
- [`amazon-market-entry-analyzer`](./zoodata-amz-marketing-skill/amazon-market-entry-analyzer/)：市场进入 GO / CAUTION / AVOID 判断
- [`amazon-opportunity-discoverer`](./zoodata-amz-marketing-skill/amazon-opportunity-discoverer/)：机会产品扫描和评级
- [`amazon-competitor-intelligence-monitor`](./zoodata-amz-marketing-skill/amazon-competitor-intelligence-monitor/)：竞品矩阵、价格地图、趋势和告警
- [`amazon-pricing-command-center`](./zoodata-amz-marketing-skill/amazon-pricing-command-center/)：RAISE / HOLD / LOWER 定价信号
- [`amazon-review-intelligence-extractor`](./zoodata-amz-marketing-skill/amazon-review-intelligence-extractor/)：评论痛点、购买因素和用户画像
- [`amazon-daily-market-radar`](./zoodata-amz-marketing-skill/amazon-daily-market-radar/)：每日市场监控
- [`amazon-market-trend-scanner`](./zoodata-amz-marketing-skill/amazon-market-trend-scanner/)：品类趋势扫描
- [`amazon-keywords`](./zoodata-amz-marketing-skill/amazon-keywords/)：关键词拓词、搜索结果和 ASIN 流量词分析

默认优先使用已配置的 `sorftime-mcp`；需要 ZooData 时可显式指定 `--provider zoodata`。

### 2. 跨品类出海市场进入与 GTM 战略

[`GinvSkill-market-entry-report`](./GinvSkill-market-entry-report/)

作者 Ginv（公众号「Adobe of Amazon」）的市场进入战略报告生成器，不限于亚马逊补充剂业务，任何跨境出口企业的【产品 + 目标市场 + 商业模式】组合都适用：

- 输入三个变量：产品/品类、目标市场（可多国组合）、商业模式（B2B / B2C / 两者皆有）
- 深度研究：PESTEL、市场规模、竞争格局、客户画像与 JTBD、渠道生态、风险
- 按固定七章 MECE 结构写作（执行摘要 → 宏观环境 → 市场规模与竞争 → B2B 客户画像 → 产品需求洞察 → 渠道与 GTM → 行动蓝图）
- 五维自检后输出可直接交付海外渠道伙伴或终端客户的 HTML 战略报告
- B2B 与 B2C 的客户画像、渠道策略框架分别处理；多国市场逐国细颗粒度分析

### 3. 关键词与运营

[`amazon-dropdown-expander`](./amazon-dropdown-expander/)  
采集 Amazon US 搜索框下拉联想词，适合做长尾词、PPC 精准词、Listing 备选词。

[`amazon-new-listing-keyword-library`](./amazon-new-listing-keyword-library/)  
把 ABA、Sif、下拉词和产品信息图整合成新品关键词词库，输出 P0/P1/P2、否定词、Search Term 和选词策略。

[`amz-qa-creator`](./amz-qa-creator/)  
`amazon-new-listing-keyword-library` 的下游：消费词库 Excel（P0/P1/P2 + 品牌词否定清单接力复用），结合 ASIN/Listing 信息（Sorftime MCP + 竞品 VOC）批量生成 200 组亚马逊 QA；含敏感词双层过滤、事实锚点校验、断点续跑，输出 xlsx/csv/txt 三件套 + 质检报告。

### 4. Amazon Design · 图片、文案与手机预览

[`amazon-mobile-preview-tool`](./amazon-mobile-preview-tool/)

Canva → 亚马逊手机预览工具。在本地导入主副图、From the brand 品牌故事、A+ 整图、高级轮播、MP4 视频及封面，检查不同手机视口下的浏览效果。品牌故事支持背景、Logo 和可横向滑动的竖版卡片，位于普通 A+ 内容前。左侧主副图、品牌故事与 A+ 独立分区，前两者分别使用 `#24333F`、`#242321` 底色；支持拖拽、粘贴换图、组内排序与自动保存。卡片悬停以 `#FFA41C` 高亮，点击品牌故事或 A+ 卡片会定位右侧模块并闪烁两次。

需要 Python 3.10+，无需第三方包或前端构建，可离线运行。Windows 双击项目内的 `启动预览工具.bat`；项目与素材保存在 `data/<项目名称>/`，主副图位于 `assets/main/`，A+ 图片、轮播、视频和封面位于 `assets/aplus/`。附带可直接打开的示例设计稿，操作与备份方式见[项目 README](./amazon-mobile-preview-tool/README.md)。

[`amazon-supplement-visual-content`](./amazon-supplement-visual-content/)  
用于 Amazon US 补充剂主图合规判断、辅图文案、A+ 页面结构、设计 brief 和生图 prompt。

[`amazon-supplement-visual-content-WB`](./amazon-supplement-visual-content-WB/)  
上一个 skill 的 WorkBuddy 版目录。

[`spf-products-advances-to-image-copy`](./spf-products-advances-to-image-copy/)  
偏“图片文案生成”，适合根据 Supplement Facts 和卖点快速产出 7 张图和 A+ 模块文案。

[`amazon-copy-writing-project`](./amazon-copy-writing-project/)  
可复用的本地「文案工作台」项目：为产品详情页 / A+ / 轮播设计稿撰写四风格合规文案。单页工作台左边看设计稿、右边改槽位文案，内置黑名单合规检查、高亮框坐标标定、日/夜主题与按风格导出 Markdown；配套「资料/」产品材料目录规范和换新产品标准流程。

四个视图（`Tab` 键循环）：**工作台**（逐槽位落版文案，按设计稿文本块容量收口，每槽位含 3 条发散备选可一键换入）、**四风格对比**、**自由创作**（每图 3 个不受槽位约束的创意角度）、**消费人群画像**（逐成分功效与证据强度 + 受众三层画像 + 定位风险 + 场景切入，附换产品时的重新生成指令）。

### 5. 成分合规、IP 风险与配方研发

[`ingredients-breakdown-compliance-check`](./ingredients-breakdown-compliance-check/)  
用于拆解成分堆栈，识别 branded ingredient、TM/R、专利、FDA/Amazon 和商业化风险。

[`supplement-formula-pipeline`](./supplement-formula-pipeline/)  
完整配方研发链路，内部包含：

- `ingredients-breakdown-compliance-check`
- `supplement-safe-rebuild`
- `formula-reconstruction`
- `amazon-supplement-boundary-analysis`
- `supplement-audience-satellite-formula-finalizer`

推荐顺序：

```text
成分风险查验
→ 安全重建
→ 配方优化 / 成分流量边界分析
→ 受众卫星配方收口
→ 实验室沟通简报
```

### 6. Skill 管理与 Obsidian 索引

[`ob-skill-github-organizer`](./ob-skill-github-organizer/)

这是一个元 skill，用来管理本仓库里的其他 skill。

它可以：

- 扫描 GitHub/local skills 仓库
- 识别 Codex/OpenAI、WorkBuddy、Agent 通用等结构
- 更新 Obsidian Markdown 索引
- 判断 `-WB` 目录是否已经是 WorkBuddy 标准包
- 回答“我现在应该用哪个 skill”

示例：

```text
用 ob-skill-github-organizer 扫描我的 skills-hub 仓库并更新 Obsidian 索引
```

```text
我想根据 Amazon 产品写图片文案，应该用哪个 skill？
```

## 安装与使用方式

### 本地应用项目

下载本仓库 ZIP 并解压，或克隆后进入对应项目目录。请保留完整项目文件夹，包括静态文件和随附的示例素材。

- **手机预览工具**：进入 [`amazon-mobile-preview-tool`](./amazon-mobile-preview-tool/)，安装 Python 3.10+ 后双击 `启动预览工具.bat`。也可在该目录运行 `python server.py`，浏览器默认打开 `http://127.0.0.1:8877`；端口占用时自动顺延。关闭启动窗口即停止服务。
- **文案工作台**：进入 [`amazon-copy-writing-project`](./amazon-copy-writing-project/)，按其[工作台 README](./amazon-copy-writing-project/_workbench/README.md)准备资料，双击 `_workbench/启动工作台.bat` 启动。

这些项目直接在本机运行。下面的 skills 目录安装方式适用于提供 `SKILL.md` 的 Agent Skills。

### Codex / OpenAI

把需要的 skill 文件夹复制到你的 Codex skills 目录，或在项目中保留此仓库作为 skill 来源。

常见目录形态：

```text
~/.codex/skills/
└── skill-name/
    └── SKILL.md
```

### Claude Code

通常可以把某个 skill 文件夹复制到项目级或用户级 `.claude/skills/` 下。

```text
.claude/
└── skills/
    └── skill-name/
        └── SKILL.md
```

### WorkBuddy

WorkBuddy 更推荐标准包结构：

```text
skill-package/
├── README_WORKBUDDY.md
└── SKILL/
    ├── SKILL.md
    ├── references/
    └── assets/
```

当前 `amazon-supplement-visual-content-WB` 是 WorkBuddy 版目录，但还不是完整标准分享包。后续如果要正式分发，可以再补 `README_WORKBUDDY.md` 并调整入口到 `SKILL/SKILL.md`。

## 维护流程

新增或修改 skill / 本地项目后，建议按这个顺序维护：

1. 更新或新增对应文件夹，并同步本 README 的分类入口与顶层目录。
2. Agent Skill 至少提供 `SKILL.md`；本地应用提供 README、启动入口和运行所需源码 / 示例资源，并验证可以启动。不要提交缓存、日志和本机私有数据。
3. 使用 `ob-skill-github-organizer` 扫描仓库。
4. 更新 Obsidian 索引。
5. 如果新增 WorkBuddy 版本，确认是否只是 `-WB` 目录，还是完整 WorkBuddy 标准包。
6. 提交并推送到 GitHub。

扫描命令示例：

```bash
python ob-skill-github-organizer/scripts/scan_skill_repo.py --repo-path .
```

## 合规边界

本仓库中的成分、合规、FDA/Amazon、商标和专利相关 skill 用于 **业务研究和风险初筛**。

正式上架、标签、广告、专利、商标和 FDA/FTC 风险，请结合专业人士或官方政策进行最终确认。
