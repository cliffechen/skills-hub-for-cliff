# Cursor 适配（本地编辑器、Cloud Agent；任意模型，含 Grok）

## 安装

在项目根目录运行（`{技能目录}` 是本技能所在路径）：

```bash
bash {技能目录}/install.sh cursor            # 复制到 .cursor/skills/amazon-aplus-copywriter-canva/
bash {技能目录}/install.sh cursor --user     # 复制到 ~/.cursor/skills/amazon-aplus-copywriter-canva/
```

Cursor 不替换 `${CLAUDE_SKILL_DIR}`：执行脚本时换成技能目录的绝对路径，如 `python3 .cursor/skills/amazon-aplus-copywriter-canva/scripts/build_notes.py …`。

## Canva MCP

- 本地：Cursor Settings → MCP → Add，或在 `.cursor/mcp.json` 写：
  ```json
  {"mcpServers": {"canva": {"url": "https://mcp.canva.com/mcp"}}}
  ```
  首次调用时按提示完成 Canva 授权。
- Cloud Agent：在 Cursor 后台为 Cloud Agent 接好 Canva 连接器后，工具出现在 `Canva` 命名空间里。先用 `GetDynamicTools`（namespace `Canva`）看参数，再用 `CallDynamicTool` 调用，`mcpDetails.description` 用一句话写本次要做什么。

## 浏览器（第 C9 步）

| 环境 | 方式 |
|---|---|
| Cloud Agent | 用 `Task` 起 `computerUse` 子代理操作云电脑里的 Chrome。**第一次调用后记下 agent ID，后续每一步用 `resume` 继续同一个子代理**，登录态和打开的页面才会保留。子代理看不到主对话，任务描述里写全：链接、页码、文件路径、"只改备注不碰画布""不输入密码、不点 OAuth"。云电脑剪贴板用 `xclip -selection clipboard -i p{N}.txt`（`DISPLAY=:1`） |
| 本地编辑器 | 用 Cursor 自带的浏览器工具或 Playwright MCP，写入方法按 `computer-use-canva.md` 第 4 步 DOM 级处理 |

实测顺序（2026-10-09，UA1000GUM 第 1–8 页）：子代理打开链接 → 停在登录页 → 用户选邮箱登录并给出邮箱 → 子代理输入邮箱停在验证码页 → 用户给验证码 → 进入编辑器、打开备注面板 → 逐页剪贴板粘贴 → 主代理 `get-presenter-notes` 回读，8 页逐字一致。

## 其他

- 选择题：有 `AskQuestion` 类工具就用；没有就在对话里列编号选项。
- 图片：Read 工具可直接查看 PNG/JPG。
- 工作区约定见技能目录下的 `AGENTS.md`（Cursor 会读取项目根的 `AGENTS.md`，把内容合并过去）。
- 模型无关：Grok 等模型一样按 SKILL.md 的清单执行；对执行偏快的模型，在第 4、C9 步明确要求"先停下汇报再继续"。
