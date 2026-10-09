# 用浏览器 / computer use 写 Canva 备注：操作手册

适用于任何能操作浏览器的 agent：截图+点击式的 computer use（Claude computer use、Cursor 云电脑 computerUse 子代理）、DOM 级浏览器自动化（Playwright MCP、Claude in Chrome、agent-browser 等）。两类的差别只在"怎么把文字放进输入框"，其余步骤一样。各 agent 的具体工具见 `adapters/`。

开始前准备好：设计编辑链接、`notes_{时间戳}/p{N}.txt`、`manifest.json`（每页字符数）、`notes_before.json`。

## 1. 打开设计

- 打开 `edit_url`（`https://www.canva.com/d/…` 会跳到 `canva.com/design/{ID}/…/edit`）。
- 浏览器窗口最大化。Cloudflare"正在验证"页通常几秒自动通过；出现需要点选的人机验证时停下，请用户在桌面上自己完成。

## 2. 登录（只在出现登录页时）

按铁律 6：

| 用户选择 | agent 做什么 | 用户做什么 |
|---|---|---|
| 邮箱 | 点 "Continue with email" → 输入用户给的邮箱 → Continue → 停在验证码页 | 把邮箱验证码发给 agent |
| 验证码 | 输入 → Continue → 等跳转到编辑器 | — |
| Google / Facebook / Apple / 工作邮箱 SSO | 不点授权，只把页面停在登录页 | 在桌面上自己完成 |
| 密码 | 不代填 | 在桌面上自己输入 |

- 验证码通常几分钟内有效。用户回得晚、提示失效时，问用户后再点"重新发送"，不要自己连续重发。
- 登录后若落在 Canva 首页，再打开一次 `edit_url`。
- 关掉新手引导、弹窗；不要点画布。

## 3. 打开备注面板

- 编辑器底部工具栏左侧的"备注 / Notes"按钮。面板一般出现在左侧，标题形如"第 N 页 - 演讲者备注 / Page N notes"，底部有 `字数/5000` 计数。
- 翻页：滚动画布，面板会跟着当前可见页切换；或用右下角网格视图 / 页面缩略图点到第 N 页。**每次写之前先确认面板标题的页码**——这是最容易出错的一步。

## 4. 写入一页

1. 确认面板标题是第 N 页。
2. 点进备注输入框，确认光标在输入框里（不是画布）。
3. 全选：Linux/Windows `Ctrl+A`，macOS `Cmd+A`。焦点不在输入框时全选会选中画布元素，紧接着的粘贴会往画布里贴东西——这时立刻撤销。
4. 放入文字：
   - **截图+点击式**：先把文件放进剪贴板，再 `Ctrl/Cmd+V`。中文、全角符号、`·` `†` `—` 不要用模拟键盘逐字键入。
     - Linux X11：`xclip -selection clipboard -i p{N}.txt`（必要时加 `DISPLAY=:1` 或 `:0`；`xclip -selection clipboard -o | head -3` 验证）
     - Linux Wayland：`wl-copy < p{N}.txt`
     - macOS：`pbcopy < p{N}.txt`
     - Windows：`powershell -c "Get-Content -Raw -Encoding UTF8 p{N}.txt | Set-Clipboard"`（不要用 `clip.exe`，会乱码）
   - **DOM 级**：定位备注 textarea，用 fill / insertText 一次写入文件全文（Playwright `fill` 会替换原内容，不需要全选）。
5. 点面板标题区域让输入框失焦（不要点画布）。
6. 看计数：应等于 `manifest.json` 里该页 `chars`（允许 ±1，结尾换行可能被去掉）。不一致就重做这一页。

页与页之间不要并行，写完一页确认后再翻下一页。

## 5. 保存与核验

- Canva 自动保存。全部写完后等几秒，看顶部保存状态（云图标 / "所有更改已保存"）。
- 回到 agent 侧用 `get-presenter-notes` 回读，跑 `verify_notes.py`。截图里的计数只是辅助，以回读结果为准。

## 6. 故障处理

| 现象 | 处理 |
|---|---|
| 粘贴后备注是乱码或问号 | 剪贴板编码问题：换上面对应系统的命令；DOM 级改用 fill |
| 粘贴进了画布（出现新文本框） | 立即 `Ctrl/Cmd+Z`，直到画布恢复；用 `get-design-content` 抽查该页，告诉用户 |
| 面板页码和预期不符 | 不写，重新翻页 |
| 计数停在 5000 | 文本超长被截断：回到第 7 步压缩该页②区 |
| 回读与预期不符 | 重写该页一次；仍不符就报告差异（通常是别人同时在编辑） |
| 编辑器提示"他人正在编辑" | 暂停，告诉用户，等用户决定 |
| 登录态丢失 | 回到第 2 步，验证码仍问用户要 |

## 7. 收尾

- 不改画布：抽查一页 `get-design-content`，与 `onimage/p{N}.txt` 一致。
- 问用户是否退出 Canva 登录（右上角头像 → 退出）。
- 汇报：写了哪几页、备份文件位置、`verify_notes.py` 结果、①区仍"未上图"的条目数。
