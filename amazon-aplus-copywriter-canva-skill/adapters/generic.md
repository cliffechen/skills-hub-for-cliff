# 通用适配：任何能用 computer use / 浏览器的 agent

本技能只依赖四种能力，不依赖某个 agent 的专有工具名。接入新 agent 时逐项找到对应工具，写一份 `adapters/{agent}.md`。

| 能力 | 技能里的说法 | 找什么 |
|---|---|---|
| 读写本地文件、跑 Python | Read / Write / Bash | 文件工具、shell 工具 |
| 读 Canva | `search-designs`、`get-design-pages`、`get-design-content`、`get-presenter-notes`、`export-design` | 接入 Canva 远程 MCP `https://mcp.canva.com/mcp`（OAuth）。不支持远程 MCP 的 agent 用 `npx -y mcp-remote@latest https://mcp.canva.com/mcp` 走 stdio |
| 看图 | "逐张查看" | 能读取图片文件的多模态工具；没有就接视觉 MCP |
| 操作浏览器 | 第 C9 步 | 截图+点击式 computer use，或 DOM 级浏览器自动化（Playwright MCP：`npx @playwright/mcp@latest`） |
| 问用户选择题 | AskUserQuestion | 有选择题工具就用；没有就在对话里列编号选项，等用户回复 |

## 安装位置

- 技能目录必须是单层：`{skills根}/amazon-aplus-copywriter-canva/SKILL.md`，不要再套分组文件夹。
- 跨 agent 共享时优先放 `.agents/skills/`（ZCode 等会读），再按需复制到各 agent 的原生目录。仓库根的 `install.sh` 负责复制。
- `SKILL.md` 里的 `${CLAUDE_SKILL_DIR}`：Claude Code、ZCode 会替换；其他 agent 换成技能目录的绝对路径。

## 模型差异

- 本技能的步骤是逐条清单，不依赖模型"自觉"。较弱或偏快的模型容易跳过的三步，执行时要显式打勾：第 4 步停下等确认、第 C9 步写前回读、写后 `verify_notes.py`。
- 子代理 / computer use 代理看不到主对话。交给它时要把编辑链接、页码范围、文件路径、"只改备注不碰画布""不输入密码"这些约束写进任务描述。
- 同一个浏览器会话尽量复用同一个子代理（保持登录态），不要每步新开。

## 最低可用

只有"读 Canva"没有浏览器：照常审图、出 plan、写文案、生成 `notes/`，第 C9 步改为交付 `all_notes.md` 让用户粘贴。

连"读 Canva"也没有：退回原技能流程，请用户从 Canva 导出 PNG 放进 `工作区/`，备注文本照样生成。
