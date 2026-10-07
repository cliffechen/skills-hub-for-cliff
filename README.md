<div align="center">
  <h1>Skills Hub for Cliff</h1>
  <p><strong>把 Amazon US 膳食补充剂的实战经验，沉淀成可复用的 Agent Skills。</strong></p>
  <p>从选品调研、关键词库、Listing 图片与 A+ 文案，到手机预览、广告知识与计算、成分合规与配方重建，这里把反复出现的运营动作整理成能直接交给 AI Agent 使用的工作流与本地工具。</p>
  <p>
    <a href="#技能目录"><img src="https://img.shields.io/badge/Skills-36-00a8e1?style=for-the-badge" alt="36 个 Skill 入口" /></a>
    <img src="https://img.shields.io/badge/Platform-Amazon_US-ff9900?style=for-the-badge" alt="Amazon US" />
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/Status-Continuously_Updated-22c55e?style=for-the-badge" alt="持续更新中" />
    <a href="https://github.com/cliffechen/skills-hub-for-cliff/stargazers"><img src="https://img.shields.io/github/stars/cliffechen/skills-hub-for-cliff?style=for-the-badge&logo=github" alt="GitHub stars" /></a>
  </p>
  <p><a href="#项目目标">项目目标</a> · <a href="#快速选择">快速选择</a> · <a href="#技能目录">技能目录</a> · <a href="#主要业务模块">主要业务模块</a> · <a href="#开始使用">开始使用</a> · <a href="#仓库结构">仓库结构</a> · <a href="#维护流程">维护流程</a> · <a href="#关于">关于</a></p>
</div>

## 项目目标

**把分散的 Amazon US 补充剂运营经验，整理成一个能持续生长的 Agent Skill 库与本地工具集。**

收录与整理的范围：

- **选品与市场调研**：类目扫描、多维度关键词对比、Top100 产品结构、竞品差评归类、站外信号采集、Go / No-Go 评分、成分入场时机速判。
- **关键词与 Listing 运营**：下拉词采集、新品词库与 Search Term 基础、SP 搜索词报告分析、Listing QA 批量生成。
- **图片与 A+ 内容**：主图合规判断、辅图文案、A+ 页面结构、品牌故事、四风格合规文案、手机端浏览预览。
- **广告运营与知识工具**：广告主题与概念阅读、全文搜索、ACoS / CPC / 点击预算计算、本地内容归档与审计。
- **成分合规与配方研发**：成分堆栈拆解、品牌成分与 IP 风险、安全重建、配方升级、成分流量边界。
- **Skill 管理与索引**：扫描仓库、识别各客户端结构、维护 Obsidian 索引、回答「我现在该用哪个 skill」。

覆盖 Codex、Claude Code、QoderWork、WorkBuddy 等 agent 工具；仓库里既有可直接运行的本地项目，也有可复制安装的 Agent Skills。

## 快速选择

按你要做的事找入口，每一行都能直接打开对应目录。装法和启动方式见[开始使用](#开始使用)。

### Amazon Design · 图片、文案与手机预览

本分类同时收纳可直接运行的本地项目和 Agent Skills。两个工作台各自保留独立目录，按各自 README 启动。

| 你要做什么 | 推荐项目 / skill | 说明 |
|---|---|---|
| 检查主副图、From the brand 品牌故事、A+ 整图、高级轮播和视频在手机上的浏览效果 | [`amazon-mobile-preview-tool`](./amazon-mobile-preview-tool/) | 本地离线预览工具；Python 3.10+，无需第三方包；主副图、品牌故事与 A+ 独立编辑分区；Windows 双击启动 |
| 在可视化工作台里为详情页 / A+ 设计稿写四风格合规文案，看图定位槽位、改稿、合规检查、导出 | [`amazon-copy-writing-project`](./amazon-copy-writing-project/) | 本地 Python 工作台（离线运行），四视图 + 逐槽位文案 + 发散备选 + 人群研究与场景切入 |
| 根据 Amazon 产品写主图、辅图、A+ 页面结构、设计 brief、生图 prompt | [`amazon-supplement-visual-content`](./amazon-supplement-visual-content/) | Codex/OpenAI 原版，适合正式出图前做内容与合规总控 |
| 在 WorkBuddy 里做补充剂图片/A+ 内容 | [`amazon-supplement-visual-content-WB`](./amazon-supplement-visual-content-WB/) | WorkBuddy 版目录，目前用于和原版区分管理 |
| 快速生成 7 张图和 A+ 图片英文文案 | [`spf-products-advances-to-image-copy`](./spf-products-advances-to-image-copy/) | 偏文案生成，适合已有 SFP 和卖点时快速出稿 |
| 为 Canva 设计稿逐个文字位写英文文案（A+、品牌故事、Listing 主副图），出可直接复制给美工的 Excel | [`amazon-aplus-copywriter-skill`](./amazon-aplus-copywriter-skill/) | 先出 plan 待确认；事实来自 ASIN 或手动填写，对标品牌 md 库可随时更换；含补剂合规包与扫描脚本 |

### 关键词与 Listing 运营

| 你要做什么 | 推荐 skill / 工具 | 说明 |
|---|---|---|
| 采集 Amazon US 搜索框下拉词 | [`amazon-dropdown-expander`](./amazon-dropdown-expander/) | 轻量 Python 工具，输出 CSV |
| 搭建新品关键词库、P0/P1/P2、Search Term 和广告词基础 | [`amazon-new-listing-keyword-library`](./amazon-new-listing-keyword-library/) | 输入 ABA、Sif、下拉词、产品信息图，输出 Excel + 策略报告 |
| 批量生成亚马逊 Listing QA（默认200组，埋词/品牌词/语义痕迹） | [`amz-qa-creator`](./amz-qa-creator/) | 上游接 `amazon-new-listing-keyword-library` 的词库 Excel，配 ASIN/Sorftime VOC，输出 xlsx/csv/txt + 质检报告 |

### 关键词监控、搜索词与情报蒸馏

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 每周监控 Amazon US 补充剂爆发型关键词，分级机会词并产出中文 HTML 报告 | [`ABAKeywords-tracker-for-codex`](./ABAKeywords-tracker-for-codex/) | Codex 版；ABA/SFR 排名 → 成分词分类与翻译 → Tier 1/2 用 Sorftime 补趋势与 CPC → 维护周度历史 |
| 在 WorkBuddy 里跑同一套周度关键词监控 | [`ABAKeywords-tracker-for-workbuddy`](./ABAKeywords-tracker-for-workbuddy/) | WorkBuddy 标准包形态（`README_WORKBUDDY.md` + `SKILL/SKILL.md`）；与 Codex 版逻辑一致，择一使用 |
| 把 Amazon Ads SP 搜索词报告变成可读的多标签页 Excel，并给出每个词的操作建议 | [`amazon-search-term-advisor`](./amazon-search-term-advisor/) | 中英文表头都能识别；输出 Spend/Sales/Orders 占比、CTR、CVR、CPC、ACOS，以及 harvest / negate / scale 建议 |
| 输入任意行业、品牌、网站或话题，产出一套「全域认知系统」 | [`marketing-distiller`](./marketing-distiller/) | 全域蒸馏器分享包；含数据库、竞品拆解、内容生态、知识地图与情报系统，自带 Google 高级搜索语法库 |

### 选品、市场调研与出海战略

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 做 Amazon US 膳食补充剂选品和 Go/No-Go 判断 | [`US_Sup_Product_Research_for_Qoderwork`](./US_Sup_Product_Research_for_Qoderwork/) | 重型选品调研，依赖 Sorftime / xCrawl 等工具 |
| 围绕种子词做 Amazon US 选品调研、自动处理关键词漂移，并生成审计报告 | [`amazon-sorftime-mcp-with-serpapi-tavily`](./amazon-sorftime-mcp-with-serpapi-tavily/) | Sorftime 主数据 + SerpApi Google Web Trends + Tavily；固定输出 JSON、Markdown、HTML |
| 只看需求端：判断一个关键词及周边词的需求真假、趋势走向，并预测上架那个月（默认 +4–6 个月）的位置 | [`AMZOn-site-Keyword-Trend-Analysis`](./AMZOn-site-Keyword-Trend-Analysis/) | 卖家精灵 + SIF + Sorftime 三个 MCP；多源交叉、脉冲剔除、7 类趋势原型、三情景预测；输出 Excel + 离线 HTML 趋势图；不看成本与供应链 |
| 以跟随者视角快速判断某个成分现在跟进晚不晚、好不好推 | [`ds-entry-quickcheck`](./ds-entry-quickcheck/) | 卖家精灵 + SIF；入场曲线、供需增速比、后来者出单率、新头部、核心词转化率五个指标 → 可跟进 / 谨慎 / 不建议；结论句加逐点文字分析；lite / plus / compare 三档；HTML 报告按需生成 |
| 调用 Sorftime MCP / ZooData 兼容数据层，查商品、市场、评论、历史趋势 | [`zoodata-amz-marketing-skill/zoodata`](./zoodata-amz-marketing-skill/zoodata/) | 共享数据层，默认优先走 Sorftime MCP |
| 做亚马逊市场、竞品、定价、进入、选品、评论等多工作流分析 | [`zoodata-amz-marketing-skill`](./zoodata-amz-marketing-skill/) | 集中收纳 `zoodata` 与一组 `amazon-*` 数据分析技能 |
| 为跨境出口企业做指定产品+目标市场的深度市场进入/GTM 战略报告（B2B/B2C 通用） | [`GinvSkill-market-entry-report`](./GinvSkill-market-entry-report/) | 麦肯锡式分析框架，按固定七章结构输出可交付客户的 HTML 战略报告 |

### 成分合规与配方研发

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 检查成分、商标、专利、FDA/Amazon 和商业化风险 | [`ingredients-breakdown-compliance-check`](./ingredients-breakdown-compliance-check/) | 适合上架、换标、仿制、改配方前先跑风险报告 |
| 做完整保健品配方研发链路 | [`supplement-formula-pipeline`](./supplement-formula-pipeline/) | 包含风险查验、安全重建、配方优化、流量边界和最终收口 |

### 广告运营与知识工具

| 你要做什么 | 推荐项目 | 说明 |
|---|---|---|
| 查阅广告知识、搜索操作流程，计算 ACoS、CPC、首单预算与 0 单点击阈值 | [`ginv-ads-workbench`](./ginv-ads-workbench/) | 本地离线工作台；13 个主题、54 篇正文、20 张概念卡、5 个计算工具；Node.js，无需安装第三方包；Windows 双击启动 |

### Skill 管理与索引

| 你要做什么 | 推荐 skill | 说明 |
|---|---|---|
| 扫描本仓库、更新 Obsidian 索引、查询该用哪个 skill | [`ob-skill-github-organizer`](./ob-skill-github-organizer/) | 本仓库的“索引维护员 + skill 路由员” |

## 技能目录

截至 **2026-10-08**，仓库包含 **36 个 `SKILL.md` 入口**，以及本地应用项目，共 **23 个顶层目录**。`amazon-mobile-preview-tool` 与 `ginv-ads-workbench` 不提供 `SKILL.md`，按项目 README 启动，不计入 Skills 数量。

| 集合 | Skills | 内容方向 | 入口 |
|---|---:|---|---|
| Amazon Design | 5 | 主副图、品牌故事、A+ 与轮播的设计稿文案、手机端预览 | [amazon-mobile-preview-tool](./amazon-mobile-preview-tool/) · [amazon-copy-writing-project](./amazon-copy-writing-project/) · [amazon-aplus-copywriter-skill](./amazon-aplus-copywriter-skill/) · [amazon-supplement-visual-content](./amazon-supplement-visual-content/) · [amazon-supplement-visual-content-WB](./amazon-supplement-visual-content-WB/) · [spf-products-advances-to-image-copy](./spf-products-advances-to-image-copy/) |
| 关键词与 Listing 运营 | 3 | 下拉词拓词、新品词库、Search Term 与广告词基础、Listing QA | [amazon-dropdown-expander](./amazon-dropdown-expander/) · [amazon-new-listing-keyword-library](./amazon-new-listing-keyword-library/) · [amz-qa-creator](./amz-qa-creator/) |
| 关键词监控、搜索词与情报蒸馏 | 4 | 周度爆发词监控、SP 搜索词报告分析、全域情报蒸馏 | [ABAKeywords-tracker-for-codex](./ABAKeywords-tracker-for-codex/) · [ABAKeywords-tracker-for-workbuddy](./ABAKeywords-tracker-for-workbuddy/) · [amazon-search-term-advisor](./amazon-search-term-advisor/) · [marketing-distiller](./marketing-distiller/) |
| 选品、市场调研与出海战略 | 16 | 市场与竞品数据、关键词需求趋势与预测、成分入场时机速判、机会与定价、市场进入判断、GTM 战略报告 | [US_Sup_Product_Research_for_Qoderwork](./US_Sup_Product_Research_for_Qoderwork/) · [amazon-sorftime-mcp-with-serpapi-tavily](./amazon-sorftime-mcp-with-serpapi-tavily/) · [AMZOn-site-Keyword-Trend-Analysis](./AMZOn-site-Keyword-Trend-Analysis/) · [ds-entry-quickcheck](./ds-entry-quickcheck/) · [zoodata-amz-marketing-skill](./zoodata-amz-marketing-skill/) · [GinvSkill-market-entry-report](./GinvSkill-market-entry-report/) |
| 成分合规与配方研发 | 7 | 成分与 IP 风险、安全重建、配方升级、成分流量边界、受众收口 | [ingredients-breakdown-compliance-check](./ingredients-breakdown-compliance-check/) · [supplement-formula-pipeline](./supplement-formula-pipeline/) |
| 广告运营与知识工具 | 0 | 本地广告知识工作台、全文搜索、五个计算工具、内容归档与审计 | [ginv-ads-workbench](./ginv-ads-workbench/) |
| Skill 管理与索引 | 1 | 扫描仓库、识别客户端结构、维护 Obsidian 索引与 skill 路由 | [ob-skill-github-organizer](./ob-skill-github-organizer/) |
| **合计** | **36** | **持续更新中** | 23 个顶层目录 |

关于这张表的几点说明：

- **同名入口变体**：`supplement-keyword-monitor` 在 `ABAKeywords-tracker-for-codex` 与 `ABAKeywords-tracker-for-workbuddy` 下各有一份，逻辑一致、目标客户端不同，**择一安装到同一命名空间，不要两份都装**。
- **`zoodata-amz-marketing-skill` 内含 11 个入口**：`zoodata` 共享数据层加 10 个 `amazon-*` 分析技能，默认优先走 Sorftime MCP，需要时显式指定 ZooData。
- **`supplement-formula-pipeline` 内含 6 个入口**：主 skill 加 `skills/` 下的 5 个子技能，属于同一条链路，建议整体保留。
- **`-WB` 目录不等于完整 WorkBuddy 标准包**：是否标准，要看目录里有没有 `README_WORKBUDDY.md` 和 `SKILL/SKILL.md`。`ABAKeywords-tracker-for-workbuddy/supplement-keyword-monitor` 与 `marketing-distiller/全域蒸馏器Skill分享包` 目前是标准包形态；`amazon-supplement-visual-content-WB` 只有根目录 `SKILL.md`，还不是标准分享包。

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

[`AMZOn-site-Keyword-Trend-Analysis`](./AMZOn-site-Keyword-Trend-Analysis/)

只看需求端、以趋势为主线的关键词选品：输入一个种子词（或竞品 ASIN、或类目扫描），扩出周边候选词，回答"需求是不是真的、在往哪走、到上架那个月会处在什么位置"。不看成本、利润、供应链和库存，"推荐"只代表需求面值得做。

- 三个 MCP 分工：SIF（ABA 搜索历史、生命周期、竞争集中度）、卖家精灵（Google Trends、单品销量与类目节点）、Sorftime（类目 Top100 销量、扩词、评论、TikTok / Reddit 站外信号）
- 多源交叉：三家的 ABA 搜索量同源只算 1 个源，结论至少要 2 个独立源（站内搜索 / 销量 / Google / TikTok）
- 先剔除脉冲、单品事件和措辞迁移，再归入 7 类趋势原型（结构性增长、加速新兴、真季节性、成熟平稳、见顶回落、一次性脉冲、结构性下滑）
- 定性预测：方向与阶段、距峰谷周数、保守 / 基准 / 乐观三情景、置信度、证实与证伪信号
- 交付 Excel（8 个 sheet）+ 离线 HTML 趋势图；功效与品牌词只做红旗提示，不影响结论

[`ds-entry-quickcheck`](./ds-entry-quickcheck/)

以跟随者的视角，快速回答"这个成分现在跟进，晚不晚、好不好推"。不追求第一批入场，关注的是入场潮走到了哪一步、后来者还能不能卖起来：

- 五个指标：
  - 逐月入场曲线：近 3 个月新进场多少、是否还在加速
  - 同一半年窗口内的需求增速 ÷ 供给增速
  - 近期新品的出单率
  - 近一年冒出的新头部（评分数过 300）
  - 核心词点击→购买转化率：<8% 不建议 / 8–10% 谨慎 / 10–12% 观望 / 12–15% 潜力 / ≥15% 重点关注
- 输出以文字为主：一句结论加逐点分析，每一点先给一两个关键数字再说"这说明什么"；明细表另存，HTML 报告按需生成
- lite（单成分）/ plus（加剂型、定价、卖家构成）/ compare（2–5 个成分排序）三档
- 脚本直连卖家精灵与 SIF 的 MCP HTTP 端点，带缓存与限流重试；样本截断时自动降级为下限或标注"判断不了"

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
- [`amazon-listing-audit-pro`](./zoodata-amz-marketing-skill/amazon-listing-audit-pro/)：Listing 审计

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

[`amazon-search-term-advisor`](./amazon-search-term-advisor/)  
把 Amazon Ads「Sponsored Products 搜索词报告」转成多标签页 Excel，逐词给出 Spend / Sales / Orders 占比、CTR、CVR、CPC 与 ACOS，并附 harvest / negate / scale up / scale down / observe 的动作建议和理由；中英文表头都能识别，输出语言跟随输入报告。

### 4. Amazon Design · 图片、文案与手机预览

[`amazon-mobile-preview-tool`](./amazon-mobile-preview-tool/)

Canva → 亚马逊手机预览工具。在本地导入主副图、From the brand 品牌故事、A+ 整图、高级轮播、MP4 视频及封面，检查不同手机视口下的浏览效果。品牌故事支持背景、Logo 和可横向滑动的竖版卡片，位于普通 A+ 内容前。左侧主副图、品牌故事与 A+ 独立分区，前两者分别使用 `#24333F`、`#242321` 底色；支持拖拽、粘贴换图、组内排序与自动保存。卡片悬停以 `#FFA41C` 高亮，点击品牌故事或 A+ 卡片会定位右侧模块并闪烁两次。

需要 Python 3.10+，无需第三方包或前端构建，可离线运行。Windows 双击项目内的 `启动预览工具.bat`；项目与素材保存在 `data/<项目名称>/`，主副图位于 `assets/main/`，A+ 图片、轮播、视频和封面位于 `assets/aplus/`。附带可直接打开的示例设计稿，操作与备份方式见[项目 README](./amazon-mobile-preview-tool/README.md)。

[`amazon-supplement-visual-content`](./amazon-supplement-visual-content/)  
用于 Amazon US 补充剂主图合规判断、辅图文案、A+ 页面结构、设计 brief 和生图 prompt。

[`amazon-supplement-visual-content-WB`](./amazon-supplement-visual-content-WB/)  
上一个 skill 的 WorkBuddy 版目录。

[`spf-products-advances-to-image-copy`](./spf-products-advances-to-image-copy/)  
偏“图片文案生成”，适合根据 Supplement Facts 和卖点快速产出 7 张图和 A+ 模块文案，内置 FDA/Amazon 合规检查和 Alexa AI 抽取优化。

[`amazon-aplus-copywriter-skill`](./amazon-aplus-copywriter-skill/)  
把设计稿里的每个文字位替换成以产品事实为依据的英文文案，交付美工可直接复制的 Excel（英文新文案 + 备选句 + 中文释义 + 事实编号 + 字符数/差值公式 + 设计修改清单）。覆盖 A+ 模块图、品牌故事、Listing 主副图三类；产品事实可来自 ASIN 抓取或手动填写，对标品牌 markdown 库可随时更换；写作前先出 plan 等用户确认，写完后用脚本扫描禁用词、星号声明和残留占位。

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

### 6. 关键词监控与情报蒸馏

[`ABAKeywords-tracker-for-codex`](./ABAKeywords-tracker-for-codex/)  
从 AMZ123 的 ABA/SFR 排名抓取 Amazon US 补充剂爆发型关键词，做成分词分类与翻译、机会词分级，Tier 1/2 用 Sorftime 补趋势 / CPC / 拓词，维护周度历史并产出中文 HTML 机会报告。Codex 版。

[`ABAKeywords-tracker-for-workbuddy`](./ABAKeywords-tracker-for-workbuddy/)  
同一套监控逻辑的 WorkBuddy 标准包形态，入口在 `supplement-keyword-monitor/SKILL/SKILL.md`。

[`marketing-distiller`](./marketing-distiller/)  
「全域蒸馏器」分享包：输入任意行业、品牌、网站或话题，产出完整的全域认知系统——数据库、竞品拆解、内容生态、知识地图与情报系统，自带 Google 高级搜索语法武器库与 URL 验证机制。标准包位于 `全域蒸馏器Skill分享包/`。

### 7. Skill 管理与 Obsidian 索引

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

### 8. 广告运营与知识工具

[`ginv-ads-workbench`](./ginv-ads-workbench/)

GinvAds 广告智库的本地工作台，内容快照日期为 **2026-09-30**。白色与钴蓝界面收录 **13 个主题、54 篇正文、20 张概念卡、5 个计算工具**，支持全文搜索、文章阅读与打印，以及手机、平板和桌面访问。

五个工具用于计算 ACoS 盈亏平衡、点击期望值、目标 ACoS 对应 CPC、首单测试预算与 0 单点击阈值。完整采集归档、来源核对记录、工具公式审计和工作台源码均随项目保留；17 项测试与 105 项独立计算案例已通过。

默认在本机离线使用，安装 Node.js（建议 22 或以上）即可启动，**无需 `npm install`**。Windows 进入项目目录双击 `启动工作台.cmd`；也可运行 `npm start` 后在浏览器打开 `http://127.0.0.1:4173`。启动、验证与更新快照的方法见[项目 README](./ginv-ads-workbench/README.md)。

## 开始使用

克隆仓库：

```bash
git clone https://github.com/cliffechen/skills-hub-for-cliff.git
cd skills-hub-for-cliff
```

在上方[技能目录](#技能目录)或[快速选择](#快速选择)里找到要用的目录，读取它的 `SKILL.md`，或把整个目录复制到你使用的 Agent 所支持的 skills 目录。保留目录里的 `references/`、`assets/`、`scripts/`，以便使用配套材料。

例如：

```text
使用 amazon-aplus-copywriter-skill。
设计稿：A+ 模块图 6 张 + 品牌故事 4 张（图中文字为占位符）
产品事实来源：ASIN B0XXXXXXXX
对标品牌文案库：examples/03-对标品牌文案库-OLENPHOGY
目标：为每个文字位写英文文案，先出 plan 等我确认，确认后再写，最后交付 Excel。
```

### 本地应用项目

下载本仓库 ZIP 并解压，或克隆后进入对应项目目录。请保留完整项目文件夹，包括静态文件和随附的示例素材。

- **手机预览工具**：进入 [`amazon-mobile-preview-tool`](./amazon-mobile-preview-tool/)，安装 Python 3.10+ 后双击 `启动预览工具.bat`。也可在该目录运行 `python server.py`，浏览器默认打开 `http://127.0.0.1:8877`；端口占用时自动顺延。关闭启动窗口即停止服务。
- **文案工作台**：进入 [`amazon-copy-writing-project`](./amazon-copy-writing-project/)，按其[工作台 README](./amazon-copy-writing-project/_workbench/README.md)准备资料，双击 `_workbench/启动工作台.bat` 启动。
- **广告知识工作台**：进入 [`ginv-ads-workbench`](./ginv-ads-workbench/)，安装 Node.js（建议 22 或以上）后双击 `启动工作台.cmd`。也可在该目录运行 `npm start`，浏览器打开 `http://127.0.0.1:4173`；无需 `npm install`，默认离线使用。详细操作见[项目 README](./ginv-ads-workbench/README.md)。

这三个项目直接在本机运行，不要求 `SKILL.md`，无需复制到 skills 目录。下面的安装方式适用于提供 `SKILL.md` 的 Agent Skills。

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

### 平台与包形态区分

这个仓库同时包含 Agent Skills 和独立运行的本地项目，按下表判断你拿到的是哪一种：

| 类型 | 怎么判断 | 怎么使用 |
|---|---|---|
| 本地应用项目 | 例如 `amazon-mobile-preview-tool`、`amazon-copy-writing-project`、`ginv-ads-workbench`，包含源码、启动入口和项目 README | 下载或克隆后按项目 README 在本机启动；不要求有 `SKILL.md`，无需复制到 skills 目录 |
| Codex/OpenAI 原版 | 通常有根目录 `SKILL.md`，可能有 `agents/openai.yaml` | 适合 Codex / OpenAI 侧直接使用或安装 |
| Claude Code / QoderWork 兼容 | 根目录 `SKILL.md` + `README.md` + `references/` | 多数可作为普通 Agent Skill 使用 |
| WorkBuddy 版目录 | 目录名带 `-WB`，例如 `amazon-supplement-visual-content-WB` | 用于和 Codex 原版分开管理；如需标准分享包，可再整理成 WorkBuddy 包结构 |
| WorkBuddy 标准包 | `README_WORKBUDDY.md` + `SKILL/SKILL.md` | 可作为 WorkBuddy 分享包形态使用 |

> 注意：目录名带 `-WB` 不等于已经是完整 WorkBuddy 标准包。是否标准，要看里面有没有 `README_WORKBUDDY.md` 和 `SKILL/SKILL.md`。

## 整理原则

- **提炼可复用的工作流**：保留能改变判断或指导操作的方法，整理成可独立使用的 Skill，而不是转载原文。
- **区分事实、案例与推断**：当前事实、历史案例、估算值和假设分别标注；无法核实的内容明确标记，不靠猜测补全数据。
- **不提交私有与临时内容**：缓存、日志、运行输出、本机路径、凭证和客户数据不进入仓库；示例素材需脱敏后保留。
- **尊重第三方权利**：收录他人作品时保留其授权声明，例如 `GinvSkill-market-entry-report` 自带 `LICENSE.txt`、`zoodata-amz-marketing-skill` 由 SerendipityOneInc 维护；品牌名、商标和成分名按各自权利人主张使用。
- **诊断与线上执行分开**：分析和方案可以离线复现；涉及账户、预算、Listing、广告或标签的线上变更，先核对授权并保留执行与回读记录。

## 仓库结构

```text
skills-hub-for-cliff/
├── amazon-mobile-preview-tool/                 # 本地项目：主副图 / 品牌故事 / A+ 手机预览
├── amazon-copy-writing-project/                # 本地项目：四风格合规文案工作台
├── amazon-aplus-copywriter-skill/              # A+ / 品牌故事 / Listing 主副图文案 → Excel
├── amazon-supplement-visual-content/           # 主图合规判断 + 辅图 / A+ 文案与设计 brief
├── amazon-supplement-visual-content-WB/        # 上者的 WorkBuddy 版目录
├── spf-products-advances-to-image-copy/        # Supplement Facts → 7 张图 + A+ 英文文案
├── amazon-dropdown-expander/                   # Amazon US 下拉框拓词 → CSV
├── amazon-new-listing-keyword-library/         # 新品关键词词库 + 选词策略报告
├── amz-qa-creator/                             # Listing QA 批量生成（默认 200 组）
├── ABAKeywords-tracker-for-codex/              # 补充剂爆发词周度监控（Codex 版）
├── ABAKeywords-tracker-for-workbuddy/          # 同上（WorkBuddy 标准包）
├── amazon-search-term-advisor/                 # SP 搜索词报告 → 多标签页 Excel + 动作建议
├── ginv-ads-workbench/                         # 本地项目：广告知识、全文搜索与五个计算工具
├── marketing-distiller/                        # 全域蒸馏器分享包（WorkBuddy 标准包）
├── US_Sup_Product_Research_for_Qoderwork/      # 补充剂选品调研套件（Sorftime + xCrawl）
├── amazon-sorftime-mcp-with-serpapi-tavily/    # 种子词选品调研（Sorftime + SerpApi + Tavily）
├── AMZOn-site-Keyword-Trend-Analysis/          # 需求端关键词趋势选品与预测（卖家精灵 + SIF + Sorftime）
├── ds-entry-quickcheck/                        # 成分入场时机速判：入场曲线 + 供需 + 转化率（卖家精灵 + SIF）
├── zoodata-amz-marketing-skill/                # ZooData 数据层 + 10 个 amazon-* 分析技能
├── GinvSkill-market-entry-report/              # 市场进入 / GTM 战略报告（作者 Ginv）
├── ingredients-breakdown-compliance-check/     # 成分拆解、IP 与合规风险报告
├── supplement-formula-pipeline/                # 配方研发链路（含 5 个子技能）
└── ob-skill-github-organizer/                  # Skill 索引维护与路由（元 skill）
```

这是带注释的阅读视图；仓库实际是平铺结构，23 个顶层目录都在根下。`marketing-distiller` 与 `ABAKeywords-tracker-for-workbuddy` 的实际入口在它们各自的 `SKILL/SKILL.md`。

## 维护流程

新增或修改 skill / 本地项目后，建议按这个顺序维护：

1. 更新或新增对应文件夹，并同步本 README 的[快速选择](#快速选择)、[技能目录](#技能目录)、[主要业务模块](#主要业务模块)与[仓库结构](#仓库结构)。
2. Agent Skill 至少提供 `SKILL.md`；本地应用提供 README、启动入口和运行所需源码 / 示例资源，并验证可以启动。不要提交缓存、日志和本机私有数据。
3. 使用 `ob-skill-github-organizer` 扫描仓库。
4. 更新 Obsidian 索引。
5. 如果新增 WorkBuddy 版本，确认是否只是 `-WB` 目录，还是完整 WorkBuddy 标准包。
6. 回到[技能目录](#技能目录)，核对 Skills 计数与总入口数是否同步更新。
7. 提交并推送到 GitHub。

扫描命令示例：

```bash
python ob-skill-github-organizer/scripts/scan_skill_repo.py --repo-path .
```

## 合规边界

本仓库中的成分、合规、FDA/Amazon、商标和专利相关 skill 用于 **业务研究和风险初筛**。

正式上架、标签、广告、专利、商标和 FDA/FTC 风险，请结合专业人士或官方政策进行最终确认。

## 关于

本仓库由 **cliffechen** 维护，面向 Amazon US 膳食补充剂的运营与内容生产场景，把反复出现的调研、写作、合规与配方工作沉淀成可复用的 Skills。仓库持续更新中。

欢迎提交新的 skill、失效链接修复或工作流改进；提交 Issue 或 Pull Request 时，请只描述业务问题与提炼后的方法，并先脱敏具体品牌、客户与账户数据。

如果这个仓库对你有帮助，欢迎 [Star](https://github.com/cliffechen/skills-hub-for-cliff/stargazers)。

<div align="center">
  <p><strong>经验持续沉淀，工作流持续复用。</strong></p>
  <p><a href="#技能目录">浏览技能目录</a> · <a href="https://github.com/cliffechen/skills-hub-for-cliff">查看仓库</a></p>
</div>
