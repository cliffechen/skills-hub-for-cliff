# Canva 接入：三层能力与读取配方

## 先查本 agent 有哪几层

| 层 | 需要的能力 | 怎么确认 | 没有时 |
|---|---|---|---|
| 读 | Canva MCP（远程 `https://mcp.canva.com/mcp`，OAuth） | 调一次 `search-designs`（limit 1）有结果 | 按 `adapters/` 让用户添加并授权；或退回"用户导出 PNG 放进 `工作区/`" |
| 看 | 能查看本地图片文件（多模态） | 打开一张下载好的缩略图能描述内容 | 接视觉 MCP（如 ZCode 的 `zai-mcp-server`）；再不行只做文字层审查，并在 plan 里写明"未看图" |
| 写备注 | 浏览器自动化或 computer use | 能打开网页、点击、输入，最好能截图 | 交付 `notes/p{N}.txt`，请用户自己粘贴；或作为设计评论发出（见下文"退路"） |

Canva MCP 能读备注（`get-presenter-notes`）、改画布文字和元素（`start-editing-transaction` → `perform-editing-operations` → `commit-editing-transaction`）、发评论（`comment-on-design`），但旧版工具集**没有写备注的接口**，写备注要走浏览器。新版连接器（工具为 `read-design` / `edit-design`）的 `edit-design` 带 `replace_speaker_notes` 操作，可以直接写，工具对照和步骤见 `adapters/claude-code.md`；先看本 agent 的工具列表属于哪一种。不要尝试用编辑事务"顺便"改备注，也不要把备注内容写成画布上的隐藏文本框。

工具名在不同 agent 里会带前缀（如 `mcp__canva__get-presenter-notes`、`Canva.get-presenter-notes`，或经 `CallDynamicTool` 调用），以本 agent 实际列出的为准；下文用裸名。

## 读取配方

**定位设计**
- 链接：`canva.com/d/{短码}` 可直接给 `get-design-content` 等工具；`canva.com/design/{D开头的ID}/…` 里的 ID 就是 `design_id`。短链用 `resolve-shortlink` 先解析。
- 标题：`search-designs`，`query` 填标题，`sort_by=relevance`。
- 最近的：`search-designs`，`sort_by=modified_descending`，`limit` 3–5。`updated_at` 是 Unix 秒，换成用户时区再说。

**每页三样东西**（存进 `工作区/05-输出/canva/`）

| 内容 | 工具 | 要点 |
|---|---|---|
| 图上文字 | `get-design-content`（`content_types=["richtexts"]`，`pages=[N]`） | **一次只取一页**，多页合并返回时分不清页界。存 `onimage/p{N}.txt`。同一文本框里的换行会被吞掉（"Urolithin A.Here's"），比对时忽略空白 |
| 页面清单与缩略图 | `get-design-pages`（`offset`、`limit`） | 返回 `page_id`、`dimensions`（判断图片类型）、447px 缩略图签名链接（约 2 小时过期）。把返回 JSON 存成 `pages.json`，再 `python3 scripts/fetch_thumbs.py pages.json 工作区/05-输出/canva/thumbs` 批量下载 |
| 原备注 | `get-presenter-notes`（不传 `pages` 即全部） | 原样存 `notes_before.json`（数组：`page_id` / `page_number` / `notes`）。描述里写"presentation"，但对 custom 尺寸的副图设计同样有效 |

**需要看清小字时**：`export-design` 导出指定页 PNG（先 `get-export-formats` 看支持的格式），下载后再看。447px 缩略图看不清 Supplement Facts、徽章文字，涉及这类判断时要么导出，要么在 plan 里写"缩略图判断，请在原图核对"。

**同一设计会被多人编辑。** 读取后到写入前，备注和画布都可能变化（实际遇到过：两次读取间隔一小时，第 3 页备注已被改写）。所以写入前必须重读比对（SKILL.md 第 C9 步）。

## 退路

1. **用户粘贴**：给出 `all_notes.md`，每页一段，用户逐页复制。
2. **设计评论**：`comment-on-design` 每条 ≤1000 字符、挂在整个设计上（不能挂到页）、对所有协作者可见。只在用户同意时用，每条开头写 `[P{N}]`。
3. **不要**：把备注写进画布、用编辑事务改图上文字来"标注"、抓取 Canva 网页内部接口。
