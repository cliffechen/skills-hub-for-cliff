# ZCode 适配

依据 ZCode 官方文档（zcode.z.ai/cn/docs：Skill、MCP、Plugin 三页，2026-10 查阅）整理；第 C9 步的浏览器写入尚未在 ZCode 上实机跑通，首次使用时请按 `computer-use-canva.md` 逐步确认。

## 安装

在项目根目录运行（`{技能目录}` 是本技能所在路径）：

```bash
bash {技能目录}/install.sh zcode             # 复制到 .zcode/skills/amazon-aplus-copywriter-canva/
bash {技能目录}/install.sh zcode --user      # 复制到 ~/.zcode/skills/amazon-aplus-copywriter-canva/
bash {技能目录}/install.sh agents            # 复制到 .agents/skills/（ZCode 也会读，可与其他工具共享）
```

- 技能目录必须单层：`skills/<技能名>/SKILL.md`，嵌套分组目录不会被识别。
- frontmatter 的 `description` 上限 1024 字符，超出整个技能被丢弃（本技能约 300 字符）。
- `${CLAUDE_SKILL_DIR}` 和 `${ZCODE_SKILL_DIR}` 都会被替换成技能目录，SKILL.md 里的命令可以原样执行。
- 也可以在 设置 → 技能 → 导入，从 Claude Code 等已装目录扫描导入。

## Canva MCP

在 设置 → MCP 添加远程服务 `https://mcp.canva.com/mcp`；或手工写配置：

| 作用域 | 文件 | 键 |
|---|---|---|
| 工作区 | `<项目根>/.zcode/config.json` | `mcp.servers` |
| 用户 | `~/.zcode/cli/config.json` | `mcp.servers` |
| 通用兜底 | `.agents/mcp.json` | `mcpServers` |

```json
{"mcp": {"servers": {"canva": {"type": "http", "url": "https://mcp.canva.com/mcp"}}}}
```

字段以设置页生成的为准。远程 HTTP 不可用时改 stdio：`"command": "npx", "args": ["-y", "mcp-remote@latest", "https://mcp.canva.com/mcp"]`。首次调用完成 Canva OAuth。

## 看图

模型不能直接看图时，接智谱的视觉 MCP `zai-mcp-server`（需智谱 API Token），用它描述 `thumbs/p{N}.png` 的版式、人物、徽章、小字。

## 浏览器（第 C9 步）

ZCode 没有内置 computer use，接一个浏览器自动化 MCP，推荐 Playwright MCP：

```json
{"mcp": {"servers": {"playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}}}}
```

写入走 `computer-use-canva.md` 第 4 步的 DOM 级方法（fill 整段写入，中文可直接写）。Playwright 打开的是独立浏览器配置文件，需要登录一次，按第 2 步由用户提供邮箱和验证码。

## 其他

- 选择题：没有专用工具时，在对话里列编号选项。
- 工作区约定见技能目录下的 `AGENTS.md`；ZCode 读取项目根的 `AGENTS.md`，把内容合并过去。
- 疑难排查可用 ZCode 自带的 `$zcode-configuration-guide` 技能（技能没被识别、MCP 连不上等）。
