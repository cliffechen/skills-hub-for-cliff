# Canva 接入：三层能力与读取配方

## 先查本 agent 有哪几层

| 层 | 需要的能力 | 怎么确认 | 没有时 |
|---|---|---|---|
| 读 | Canva MCP（远程 `https://mcp.canva.com/mcp`，OAuth；或 agent 自带的 Canva 连接器） | 调一次 `search-designs`（limit 1）有结果 | 按 `adapters/` 让用户添加并授权；或退回"用户导出 PNG 放进 `工作区/`" |
| 看 | 能查看本地图片文件（多模态） | 打开一张下载好的缩略图能描述内容 | 接视觉 MCP（如 ZCode 的 `zai-mcp-server`）；再不行只做文字层审查，并在 plan 里写明"未看图" |
| 写备注 | Canva MCP 的 `edit-design`（`replace_speaker_notes` 操作）；没有时用浏览器自动化或 computer use | 工具列表里 `edit-design` 的操作含 `replace_speaker_notes`；或能打开网页、点击、输入，最好能截图 | 交付 `notes/p{N}.txt`，请用户自己粘贴；或作为设计评论发出（见下文"退路"） |

Canva MCP 用 `read-design` 读（文字、页面信息、缩略图、备注），用 `edit-design` 改：先 `read-design`（`open_transaction: true`）开事务，`edit-design`（`finalize: "keep_open"`）提交操作，再 `edit-design`（`finalize: "commit"`）保存。`edit-design` 的 `replace_speaker_notes` 操作可以直接写备注，步骤见 `adapters/claude-code.md`「通道 A」（不限于 Claude Code）。同一个工具也能改画布文字和元素，写备注时 `operations` 里只放 `replace_speaker_notes`，不要“顺便”改画布，也不要把备注内容写成画布上的隐藏文本框。工具列表里没有这个操作时，写备注走浏览器（`computer-use-canva.md`）。

工具名在不同 agent 里会带前缀（如 `mcp__canva__read-design`、`mcp__{一串ID}__read-design`、`Canva.read-design`，或经 `CallDynamicTool` 调用），以本 agent 实际列出的为准；下文用裸名。

## 读取配方

**定位设计**
- 链接：`canva.com/d/{短码}` 可直接给 `read-design` 等工具（`design_id` 也接受完整链接）；`canva.com/design/{D开头的ID}/…` 里的 ID 就是 `design_id`。`canva.link/…` 短链用 `resolve-shortlink` 先解析。
- 标题：`search-designs`，`query` 填标题，`sort_by=relevance`。
- 最近的：`search-designs`，`sort_by=modified_descending`，`limit` 3–5。`updated_at` 是 Unix 秒，换成用户时区再说。

**每页三样东西**（存进 `工作区/05-输出/canva/`）

| 内容 | 工具 | 要点 |
|---|---|---|
| 图上文字 | `read-design`（`filter.fields=["design_content"]`，`page_indices=[N]`） | **一次只取一页**，不传页码时多页合并返回、分不清页界。存 `onimage/p{N}.txt`。同一文本框里的换行会被吞掉（"Urolithin A.Here's"），比对时忽略空白 |
| 页面清单与缩略图 | `read-design`（`filter.fields=["page_metadata","thumbnails"]`，`thumbnail_pages=[…]`） | `page_metadata` 返回 `id`（即 `page_id`）、`page_number`、`dimensions`（判断图片类型）；447px 缩略图直接随结果返回，可当场查看。缩略图可能是花的旧缓存，这种页用 `export-design`，或在 plan 里写明“画面未看清” |
| 原备注 | `read-design`（`filter.fields=["presenter_notes"]`，不传 `page_indices` 即全部） | 把返回的 JSON 原样存成 `notes_before.json`（`{"presenter_notes":[{page_id, page_number, notes}]}`，空备注的页没有 `notes` 字段）。对 custom 尺寸的副图设计同样有效 |

**需要看清小字时**：`export-design` 导出指定页 PNG（先 `get-export-formats` 看支持的格式），下载后再看。447px 缩略图看不清 Supplement Facts、徽章文字，涉及这类判断时要么导出，要么在 plan 里写"缩略图判断，请在原图核对"。

**同一设计会被多人编辑。** 读取后到写入前，备注和画布都可能变化（实际遇到过：两次读取间隔一小时，第 3 页备注已被改写）。所以写入前必须重读比对（SKILL.md 第 C9 步）。

## 旧工具名对照

有的环境里 Canva MCP 还是拆开的旧工具，按下表对应；旧工具集没有写备注的接口，写备注只能走浏览器。

| 本文的调用 | 旧工具名 | 差别 |
|---|---|---|
| `read-design` 取 `design_content` | `get-design-content`（`content_types=["richtexts"]`，`pages=[N]`） | 同样要逐页取 |
| `read-design` 取 `page_metadata`、`thumbnails` | `get-design-pages`（`offset`、`limit`） | 缩略图是签名链接（约 2 小时过期），把返回 JSON 存成 `pages.json`，用 `scripts/fetch_thumbs.py pages.json 工作区/05-输出/canva/thumbs` 下载 |
| `read-design` 取 `presenter_notes` | `get-presenter-notes`（不传 `pages` 即全部） | 返回的是数组，脚本两种外形都认 |
| `read-design`（开事务）→ `edit-design` | `start-editing-transaction` → `perform-editing-operations` → `commit-editing-transaction` | 没有 `replace_speaker_notes` |

## 退路

1. **用户粘贴**：给出 `all_notes.md`，每页一段，用户逐页复制。
2. **设计评论**：`comment-on-design` 每条 ≤1000 字符、挂在整个设计上（不能挂到页）、对所有协作者可见。只在用户同意时用，每条开头写 `[P{N}]`。
3. **不要**：把备注写进画布、用编辑事务改图上文字来"标注"、抓取 Canva 网页内部接口。
