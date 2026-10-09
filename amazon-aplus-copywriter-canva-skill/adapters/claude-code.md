# Claude Code 适配

## 安装

在项目根目录运行（`{技能目录}` 是本技能所在路径）：

```bash
# 项目级（随仓库走）
bash {技能目录}/install.sh claude            # 复制到 .claude/skills/amazon-aplus-copywriter-canva/
# 用户级（所有项目可用）
bash {技能目录}/install.sh claude --user     # 复制到 ~/.claude/skills/amazon-aplus-copywriter-canva/
```

`${CLAUDE_SKILL_DIR}` 会被替换成技能目录，SKILL.md 里的命令可以原样执行。

## Canva MCP

```bash
claude mcp add --transport http canva https://mcp.canva.com/mcp            # 当前项目
claude mcp add --transport http --scope user canva https://mcp.canva.com/mcp  # 所有项目
```

启动 Claude Code → `/mcp` → 选 canva → Authenticate，在浏览器里完成 Canva 授权。工具名形如 `mcp__canva__get-presenter-notes`。

## 浏览器（第 C9 步）

任选一种，在 plan 里写明用哪种：

| 方式 | 配置 | 写入备注的方法 | 登录 |
|---|---|---|---|
| Claude in Chrome | 装 Chrome 扩展，`claude --chrome` 或会话内 `/chrome` | 操作用户自己的 Chrome；在备注框里用页面输入工具写全文 | 通常沿用用户已登录的 Canva，不用再登录 |
| Playwright MCP | `claude mcp add playwright -- npx @playwright/mcp@latest` | 定位备注 textarea 后 `browser_type` / fill 整段写入，中文可直接写 | 新浏览器配置文件需要登录，按 `computer-use-canva.md` 第 2 步 |
| computer use（API / 远程桌面） | 运行环境提供截图+鼠标键盘工具 | 剪贴板粘贴（`xclip` / `pbcopy`），见 `computer-use-canva.md` 第 4 步 | 同上 |

## 其他

- 选择题用 `AskUserQuestion`。
- 图片用 Read 工具直接查看（PNG/JPG）。
- 工作区约定见技能目录下的 `CLAUDE.md`；把它的内容合并进项目根的 `CLAUDE.md`，Claude Code 才会自动加载。
