# skills-hub-for-cliff

这是一个面向 **Amazon US 膳食补充剂业务** 的 Agent Skills 仓库。

它不是单一工具，而是一组可复用的 AI 工作流：选品调研、关键词库、Listing 图片/A+ 内容、成分合规/IP 风险、配方重建，以及 Codex / WorkBuddy / Obsidian 的 skill 索引管理。

## 这个仓库解决什么问题

如果你经常在 Codex、Claude Code、QoderWork、WorkBuddy 等 agent 工具里重复做这些事：

- 调研 Amazon US 补充剂产品机会
- 拓展关键词、整理新品关键词库
- 根据 Supplement Facts 写主图、辅图和 A+ 图片文案
- 检查竞品成分、商标、专利和 Amazon/FDA 风险
- 基于竞品做安全重建和差异化配方
- 维护一份 Obsidian skill 索引，并查询“我现在该用哪个 skill”

这个仓库就是这些流程的集中入口。

## 快速选择：我该用哪个 skill？

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 根据 Amazon 产品写主图、辅图、A+ 页面结构、设计 brief、生图 prompt | [`amazon-supplement-visual-content`](./amazon-supplement-visual-content/) | Codex/OpenAI 原版，适合正式出图前做内容与合规总控 |
| 在 WorkBuddy 里做补充剂图片/A+ 内容 | [`amazon-supplement-visual-content-WB`](./amazon-supplement-visual-content-WB/) | WorkBuddy 版目录，目前用于和原版区分管理 |
| 快速生成 7 张图和 A+ 图片英文文案 | [`spf-products-advances-to-image-copy`](./spf-products-advances-to-image-copy/) | 偏文案生成，适合已有 SFP 和卖点时快速出稿 |
| 采集 Amazon US 搜索框下拉词 | [`amazon-dropdown-expander`](./amazon-dropdown-expander/) | 轻量 Python 工具，输出 CSV |
| 搭建新品关键词库、P0/P1/P2、Search Term 和广告词基础 | [`amazon-new-listing-keyword-library`](./amazon-new-listing-keyword-library/) | 输入 ABA、Sif、下拉词、产品信息图，输出 Excel + 策略报告 |
| 做 Amazon US 膳食补充剂选品和 Go/No-Go 判断 | [`US_Sup_Product_Research_for_Qoderwork`](./US_Sup_Product_Research_for_Qoderwork/) | 重型选品调研，依赖 Sorftime / xCrawl 等工具 |
| 调用 Sorftime MCP / ZooData 兼容数据层，查商品、市场、评论、历史趋势 | [`zoodata`](./zoodata/) | 共享数据层，默认优先走 Sorftime MCP |
| 做亚马逊市场、竞品、定价、进入、选品、评论等多工作流分析 | [`amazon-analysis`](./amazon-analysis/) 及 `amazon-*` 数据分析技能 | 基于 `zoodata.py` 的一组 Amazon 数据分析技能 |
| 检查成分、商标、专利、FDA/Amazon 和商业化风险 | [`ingredients-breakdown-compliance-check`](./ingredients-breakdown-compliance-check/) | 适合上架、换标、仿制、改配方前先跑风险报告 |
| 做完整保健品配方研发链路 | [`supplement-formula-pipeline`](./supplement-formula-pipeline/) | 包含风险查验、安全重建、配方优化、流量边界和最终收口 |
| 扫描本仓库、更新 Obsidian 索引、查询该用哪个 skill | [`ob-skill-github-organizer`](./ob-skill-github-organizer/) | 本仓库的“索引维护员 + skill 路由员” |

## 顶层目录

```text
.
├── US_Sup_Product_Research_for_Qoderwork/
├── amazon-dropdown-expander/
├── amazon-analysis/
├── amazon-competitor-intelligence-monitor/
├── amazon-daily-market-radar/
├── amazon-keywords/
├── amazon-listing-audit-pro/
├── amazon-market-entry-analyzer/
├── amazon-market-trend-scanner/
├── amazon-opportunity-discoverer/
├── amazon-pricing-command-center/
├── amazon-review-intelligence-extractor/
├── amazon-new-listing-keyword-library/
├── amazon-supplement-visual-content/
├── amazon-supplement-visual-content-WB/
├── ob-skill-github-organizer/
├── ingredients-breakdown-compliance-check/
├── spf-products-advances-to-image-copy/
├── supplement-formula-pipeline/
└── zoodata/
```

## 平台区分

这个仓库里有几种不同形态的 skill。

| 类型 | 怎么判断 | 怎么使用 |
|---|---|---|
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

[`zoodata`](./zoodata/) 和配套 `amazon-*` 数据分析技能

用于直接走 Sorftime MCP / ZooData 兼容数据层，完成 Amazon US 市场和产品分析：

- `zoodata`：共享数据层，查商品、类目、市场、评论、价格带、品牌、历史趋势
- `amazon-analysis`：综合市场 / 竞品 / 机会 / 定价分析
- `amazon-market-entry-analyzer`：市场进入 GO / CAUTION / AVOID 判断
- `amazon-opportunity-discoverer`：机会产品扫描和评级
- `amazon-competitor-intelligence-monitor`：竞品矩阵、价格地图、趋势和告警
- `amazon-pricing-command-center`：RAISE / HOLD / LOWER 定价信号
- `amazon-review-intelligence-extractor`：评论痛点、购买因素和用户画像
- `amazon-daily-market-radar`：每日市场监控
- `amazon-market-trend-scanner`：品类趋势扫描
- `amazon-keywords`：关键词拓词、搜索结果和 ASIN 流量词分析

默认优先使用已配置的 `sorftime-mcp`；需要 ZooData 时可显式指定 `--provider zoodata`。

### 2. 关键词与运营

[`amazon-dropdown-expander`](./amazon-dropdown-expander/)  
采集 Amazon US 搜索框下拉联想词，适合做长尾词、PPC 精准词、Listing 备选词。

[`amazon-new-listing-keyword-library`](./amazon-new-listing-keyword-library/)  
把 ABA、Sif、下拉词和产品信息图整合成新品关键词词库，输出 P0/P1/P2、否定词、Search Term 和选词策略。

### 3. 图片与 A+ 内容

[`amazon-supplement-visual-content`](./amazon-supplement-visual-content/)  
用于 Amazon US 补充剂主图合规判断、辅图文案、A+ 页面结构、设计 brief 和生图 prompt。

[`amazon-supplement-visual-content-WB`](./amazon-supplement-visual-content-WB/)  
上一个 skill 的 WorkBuddy 版目录。

[`spf-products-advances-to-image-copy`](./spf-products-advances-to-image-copy/)  
偏“图片文案生成”，适合根据 Supplement Facts 和卖点快速产出 7 张图和 A+ 模块文案。

### 4. 成分合规、IP 风险与配方研发

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

### 5. Skill 管理与 Obsidian 索引

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

新增或修改 skill 后，建议按这个顺序维护：

1. 更新或新增对应 skill 文件夹。
2. 确认每个 skill 至少有 `SKILL.md`。
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
