# Agent 启动说明

本文件说明如何在各 AI agent 平台上启动本项目。详细的跨平台适配指南见 `PLATFORM-ADAPTER.md`。

## 通用启动步骤

1. 安装依赖：

```bash
python -m pip install -r requirements.txt
```

2. 运行环境自检：

```bash
python scripts/check_portability.py
```

3. 自检通过后即可在任意 agent 平台上使用。

## QoderWork

在 QoderWork 中选择项目文件夹，`AGENTS.md` 会自动作为项目上下文加载。本项目以套件（Plugin）形式安装，包含 5 个子技能。

QoderWork 会发现：

- `AGENTS.md`（项目指令）
- `SKILL.md`（套件编排入口）
- `skills/*/SKILL.md`（5 个子技能定义）

## Claude Code

Claude Code 自动读取仓库根目录的 `AGENTS.md` 和 `CLAUDE.md`。无需额外配置，在仓库目录中启动对话即可。

```bash
cd /path/to/repo
claude
```

Claude Code 会发现：

- `AGENTS.md`（通用项目指令）
- `CLAUDE.md`（Claude Code 指针）
- `skills/*/SKILL.md`（5 个 skill 定义）

## OpenAI Codex

Codex 读取 `AGENTS.md` 作为项目指令。在对话中引用 skill 路径即可激活对应工作流：

```
使用 skills/amazon-supplement-boundary-analysis 对 ASIN B0XXXXXXXXX 做流量边界分析。
```

如需 Codex 自动发现 skill，可以复制到 Codex 全局 skills 目录：

```bash
# Linux/macOS
mkdir -p "$CODEX_HOME/skills"
cp -R skills/* "$CODEX_HOME/skills/"

# Windows PowerShell
New-Item -ItemType Directory -Force -Path "$env:CODEX_HOME\skills"
Copy-Item -Recurse -Force "skills\*" "$env:CODEX_HOME\skills\"
```

## Kiro（AWS AI IDE）

Kiro 使用 `.kiro/skills/` 目录发现 skill。需将顶层 `skills/` 下的 skill 符号链接到 `.kiro/skills/`。详见 `PLATFORM-ADAPTER.md` 的 Kiro 章节。

## 输出规则

生成的文件写入以下目录：

```text
outputs/cases/{ASIN}-{core-ingredient}-{yyyyMMdd-HHmmss}/
output-risk-check/{产品英文短名}/
output-safe-rebuild/{产品英文短名}/
output-formula-reconstruction/{产品英文短名}/
outputs/scratch/
```

不要将生成的报告写入 `skills/` 目录。
