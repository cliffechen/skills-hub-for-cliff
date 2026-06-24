# 跨平台适配指南

本文件说明如何在不同 AI agent 平台上安装和使用本项目。项目包含 5 个串联 skill，所有平台共享同一套 skill 定义、脚本和参考文件。

## 项目 Skill 清单

| # | Skill | 目录 | 作用 |
|---|-------|------|------|
| 1 | 成分风险查验 | `skills/ingredients-breakdown-compliance-check/` | 拆解成分、识别商标/专利/合规风险 |
| 2 | 安全重建 | `skills/supplement-safe-rebuild/` | 在安全边界内做方向重建 |
| 3 | 配方优化 | `skills/formula-reconstruction/` | 关键词+市场需求+科学文献驱动的配方升级 |
| 4 | 成分流量边界分析 | `skills/amazon-supplement-boundary-analysis/` | Sif 关键词解析+流量边界报告+雷达图 |
| 5 | 受众卫星配方收口 | `skills/supplement-audience-satellite-formula-finalizer/` | 以受众为根基的最终配方简报 |

每个 skill 目录内都有 `SKILL.md` 作为入口，`references/` 存放工作流和模板，`scripts/`（部分 skill）存放可复用脚本。

## 共享资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 项目指令 | `AGENTS.md` | 通用项目约定、技术栈、输出规则 |
| Python 依赖 | `requirements.txt` | `openpyxl`、`Pillow` |
| 环境自检 | `scripts/check_portability.py` | 验证依赖和文件结构 |
| 下拉框分析 | `scripts/analyze_autocomplete.py` | 解析亚马逊搜索框建议 |
| 脱敏样例 | `examples/` | 完整公开样例 |
| 设置文档 | `docs/` | 各平台启动说明 |

---

## QoderWork

### 安装方式

本项目作为**套件（Plugin）**安装。套件包含 5 个子技能，由 QoderWork 统一管理和调度。

安装后在 QoderWork 设置 → 套件 中可以看到套件名称和 5 个子技能列表。每个子技能可以独立启用/禁用。

### Skill 发现机制

QoderWork 从套件目录中的 `SKILL.md` 文件发现技能：

- 根目录 `SKILL.md` — 套件编排入口，负责意图识别和子技能路由
- `skills/*/SKILL.md` — 各子技能的具体定义

### 项目上下文加载

将项目文件夹挂载到 QoderWork 工作区后，`AGENTS.md` 会自动作为项目上下文注入对话。无需额外配置。

### MCP 配置

在 QoderWork 设置 → 连接器 中配置：

| MCP 服务 | 用途 | 优先级 |
|----------|------|--------|
| Sorftime MCP | 亚马逊站内数据（ASIN、关键词、竞品、趋势） | 最高 |
| AnySearch MCP | 站外发现（法规、科学文献、品牌官网） | 高 |
| Exa MCP | 站外备用 | 中 |
| Apify MCP | Reddit 社媒抓取 | 低 |

当所有 MCP 不可用时，QoderWork 自动降级到内置 Web Search。

### 调用方式

在 QoderWork 对话中直接用自然语言描述需求，agent 会根据意图自动激活对应子技能。也可以通过 `@技能名` 显式调用。

---

## Claude Code

### 安装方式

将本项目作为 Git 仓库克隆到本地，在仓库目录中启动 Claude Code。

```bash
cd /path/to/repo
claude
```

### Skill 发现机制

Claude Code 自动读取以下文件：

1. `CLAUDE.md` — 入口指针，指向 `AGENTS.md`
2. `AGENTS.md` — 项目级指令，包含完整 skill 清单和工作流说明
3. `skills/*/SKILL.md` — 各 skill 的定义文件，Claude Code 在需要时按需读取

Claude Code 不区分"套件"和"独立技能"，而是将 `skills/` 目录下的每个子目录视为可调用的工作流定义。

### MCP 配置

在 `.claude/` 或全局 Claude Code 设置中配置 MCP server。本项目需要的 MCP 服务：

```json
{
  "mcpServers": {
    "sorftime": { "command": "...", "args": ["..."] },
    "anysearch": { "command": "...", "args": ["..."] },
    "exa": { "command": "...", "args": ["..."] }
  }
}
```

具体安装命令取决于各 MCP 服务的安装方式（npm/npx/自定义）。

### 调用方式

在对话中引用 skill 名称或描述需求，Claude Code 会自动读取对应的 `SKILL.md`。也可以显式指定：

```
请使用 skills/ingredients-breakdown-compliance-check 对 ASIN B0XXXXXXXXX 做风险查验。
```

---

## OpenAI Codex

### 安装方式

将项目克隆到本地。Codex 读取 `AGENTS.md` 作为项目指令。

### Skill 发现机制

Codex 自动读取 `AGENTS.md`，其中列出了所有 skill 及其路径。在对话中引用 skill 路径即可激活。

如需 Codex 自动发现 skill，可以将 skill 目录链接到 Codex 全局 skills 路径：

```bash
# Linux/macOS
mkdir -p "$CODEX_HOME/skills"
ln -s /path/to/repo/skills/amazon-supplement-boundary-analysis "$CODEX_HOME/skills/"

# Windows PowerShell
New-Item -ItemType Directory -Force -Path "$env:CODEX_HOME\skills"
New-Item -ItemType SymbolicLink -Target "skills\amazon-supplement-boundary-analysis" -Path "$env:CODEX_HOME\skills\amazon-supplement-boundary-analysis"
```

### MCP 配置

Codex 通过 `AGENTS.md` 中的 MCP 说明了解可用的数据服务。实际 MCP 连接需要在 Codex 运行环境中配置。

### 调用方式

```
使用 skills/formula-reconstruction 基于上游报告做配方优化。
```

---

## Kiro（AWS AI IDE）

### 安装方式

Kiro 使用 `.kiro/` 目录管理 skill 和 steering 规则。本项目已统一到顶层 `skills/` 目录，如需在 Kiro 中使用，需要做一步映射。

### Skill 发现机制

Kiro 从 `.kiro/skills/` 目录发现 skill，从 `.kiro/steering/` 目录加载项目规则。

**适配方法：** 将顶层 `skills/` 下的 skill 符号链接到 `.kiro/skills/`：

```bash
mkdir -p .kiro/skills
ln -s ../../skills/ingredients-breakdown-compliance-check .kiro/skills/
ln -s ../../skills/supplement-safe-rebuild .kiro/skills/
ln -s ../../skills/formula-reconstruction .kiro/skills/
ln -s ../../skills/amazon-supplement-boundary-analysis .kiro/skills/
ln -s ../../skills/supplement-audience-satellite-formula-finalizer .kiro/skills/
```

Steering 文件需要手动创建，内容可从 `AGENTS.md` 中提取：

- `.kiro/steering/product.md` — 从 AGENTS.md 的"项目概述"和"默认参数"提取
- `.kiro/steering/structure.md` — 从 AGENTS.md 的"项目结构"提取
- `.kiro/steering/tech.md` — 从 AGENTS.md 的"技术栈"提取

### MCP 配置

在 `.kiro/settings/mcp.json` 中配置 MCP server。

### 调用方法

Kiro 在需要时自动加载 `.kiro/skills/` 下的 SKILL.md。也可以通过 steering 文件中的 prompt 触发。

---

## 跨平台通用约定

无论使用哪个平台，以下约定始终生效：

1. **输出语言**：中文为主，保留英文品牌名、商标、拉丁学名、法规编号和 URL。
2. **交付物命名**：以成分或产品英文短名开头（小写，`-` 连接），禁止通用文件名。
3. **输出隔离**：交付物写入 `outputs/cases/` 或 `output-{skill}/` 目录，不写入 `skills/` 目录。
4. **边界规则**：不为流量硬加成分、不复制品牌/专利成分、不使用疾病 claim、标注为探索方案。
5. **MCP 降级**：专用 MCP 不可用时，自动降级到 agent 内置 Web Search。
6. **依赖安装**：`python -m pip install -r requirements.txt`，运行 `python scripts/check_portability.py` 自检。

## 文件索引

| 文件 | 用途 | 读取时机 |
|------|------|----------|
| `PLATFORM-ADAPTER.md` | 本文件，跨平台适配说明 | 首次安装或切换平台时 |
| `AGENTS.md` | 项目级权威指令 | 每次会话自动加载 |
| `CLAUDE.md` | Claude Code 入口指针 | Claude Code 启动时 |
| `SKILL.md` | 套件/项目编排入口 | 意图识别和技能路由 |
| `skills/*/SKILL.md` | 各子技能定义 | 按需读取 |
| `README.md` | 项目总览和 21 个 Prompt | 用户查阅时 |
