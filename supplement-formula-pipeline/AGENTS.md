# 项目指令

本文件是项目级权威指令，适用于所有 AI agent（Claude Code、OpenAI Codex、QoderWork 等）。

## 项目概述

Amazon US 保健品（Supplement）成分与流量边界分析平台。

核心用途：从亚马逊产品数据（ASIN、Supplement Facts、关键词报告）出发，判断产品的核心主成分、可承接流量边界、成分延伸方向和合规/IP 风险，输出分析报告、方案对比、雷达图和候选配方。

项目包含 5 个 skill，形成完整的保健品竞品分析与配方研发流水线：

1. **成分风险查验（Skill 1）** — `skills/ingredients-breakdown-compliance-check/` — 拆解成分、识别商标/专利/合规风险
2. **安全重建（Skill 2）** — `skills/supplement-safe-rebuild/` — 在安全边界内做方向重建
3. **配方优化（Skill 3）** — `skills/formula-reconstruction/` — 关键词、市场需求、科学文献驱动的配方升级
4. **成分流量边界分析（Skill 4）** — `skills/amazon-supplement-boundary-analysis/` — Sif 关键词解析 + 流量边界报告 + 雷达图
5. **受众卫星配方收口（Skill 5）** — `skills/supplement-audience-satellite-formula-finalizer/` — 以受众为根基的最终配方简报

## 技术栈

- Python 3（纯脚本项目，无框架）
- 依赖：`openpyxl`（Excel 读写）、`Pillow`（雷达图 PNG 生成）
- MCP 数据层：Sorftime MCP（站内）、AnySearch MCP（站外主发现）、Exa MCP（站外备用）、Apify MCP（社媒）

## 常用命令

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 环境自检
python scripts/check_portability.py

# 创建案例工作区
python skills/amazon-supplement-boundary-analysis/scripts/create_case_workspace.py \
  --asin <ASIN> --core-ingredient "<成分名>" --sif-excel "<Excel路径>"

# 解析 Sif Excel
python skills/amazon-supplement-boundary-analysis/scripts/analyze_sif_excel.py \
  "<Excel路径>" --output-dir "<输出目录>" --name <前缀名>

# 解析亚马逊下拉框搜索词
python scripts/analyze_autocomplete.py <suggestions.txt> \
  --output-dir <输出目录> --name <前缀名>

# 生成雷达图
python skills/amazon-supplement-boundary-analysis/scripts/generate_radar.py \
  <scores.json> --output-dir "<输出目录>" --name <前缀名>
```

## 项目结构

```text
.
├── AGENTS.md                                ← 通用项目指令（本文件）
├── CLAUDE.md                                ← Claude Code 指针
├── SKILL.md                                 ← 套件/项目编排入口
├── PLATFORM-ADAPTER.md                      ← 跨平台适配指南（QoderWork/Claude Code/Codex/Kiro）
├── README.md                                ← 项目总览和 21 个可调用 Prompt
├── skills/
│   ├── ingredients-breakdown-compliance-check/  ← Skill 1：成分风险查验
│   │   ├── SKILL.md
│   │   └── references/                      ← 工作流、报告模板、示例
│   ├── supplement-safe-rebuild/                 ← Skill 2：安全重建
│   │   ├── SKILL.md
│   │   └── references/                      ← 工作流、输出模板、示例
│   ├── formula-reconstruction/                  ← Skill 3：配方优化
│   │   ├── SKILL.md
│   │   └── references/                      ← 工作流、输出模板
│   ├── amazon-supplement-boundary-analysis/     ← Skill 4：成分流量边界分析
│   │   ├── SKILL.md
│   │   ├── agents/                          ← Agent 配置
│   │   ├── assets/                          ← 模板（雷达图评分、案例配置）
│   │   ├── references/                      ← 工作流、输出合同、评分标准、SF 规则
│   │   └── scripts/                         ← 可复用 Python 脚本
│   └── supplement-audience-satellite-formula-finalizer/  ← Skill 5：受众收口
│       ├── SKILL.md
│       ├── agents/
│       └── references/
├── scripts/
│   ├── check_portability.py                 ← 项目级环境自检
│   └── analyze_autocomplete.py              ← 亚马逊下拉框搜索词分析
├── docs/                                    ← 设置和检查文档
├── research-inputs/                         ← 调研前置文件暂存区（Git 忽略）
├── output-risk-check/                       ← Skill 1 交付物
├── output-safe-rebuild/                     ← Skill 2 交付物
├── output-formula-reconstruction/           ← Skill 3 交付物
├── outputs/                                 ← Skill 4/5 运行产物（Git 忽略）
│   ├── cases/                               ← 正式案例交付物
│   └── scratch/                             ← 测试、中间稿
├── examples/                                ← 公开脱敏样例（进 Git）
├── requirements.txt
└── README.md
```

首次安装或切换 agent 平台时，阅读 `PLATFORM-ADAPTER.md` 了解各平台的 skill 发现机制和 MCP 配置方式。

## 关键约定

- `skills/` 只放可复用能力定义，不放案例交付物。
- `research-inputs/` 存放调研前置文件，按 `{成分名}/` 分子文件夹，Git 忽略。
- `output-risk-check/`、`output-safe-rebuild/`、`output-formula-reconstruction/` 分别存放 Skill 1/2/3 的交付物。
- `outputs/cases/` 只放 Boundary Analysis 正式案例交付物。
- `outputs/` 下所有内容被 `.gitignore` 忽略。
- 交付物文件名必须以成分或产品英文短名开头（小写，`-` 连接），禁止通用文件名。
- 文件夹命名使用小写英文，用 `-` 连接，不用空格。

## 输出语言

中文为主，保留英文品牌名、商标、拉丁学名、法规编号和 URL。

## 目标用户

亚马逊保健品卖家和产品开发人员。

## 默认参数

- 市场：Amazon US
- 品类：dietary supplement / health supplement
- 默认包装：90 粒
- 默认剂型：softgels 或 capsules
- 默认辅料：`Distilled Water, Maltitol Syrup, Maltitol Powder, Isomalt, Pectin, Citric Acid, Sodium Citrate, Natural Flavor, Natural Color, Carnauba Wax.`

## 无构建步骤

项目为纯脚本，无编译、打包或构建流程。无测试框架。
