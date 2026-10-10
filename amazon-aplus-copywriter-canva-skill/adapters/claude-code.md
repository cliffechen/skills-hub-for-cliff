# Claude Code 适配

2026-10-10 在 Claude 桌面端（Windows，Code 标签页）实测：Canva 连接器读取、**连接器直接写备注**、Claude in Chrome 写备注，三项都跑通，回读逐字一致。下面标「实测」的是这次跑出来的结果，其余按官方文档整理。

## 安装

在项目根目录运行（`{技能目录}` 是本技能所在路径）：

```bash
# 项目级（随仓库走）
bash {技能目录}/install.sh claude            # 复制到 .claude/skills/amazon-aplus-copywriter-canva/
# 用户级（所有项目可用）
bash {技能目录}/install.sh claude --user     # 复制到 ~/.claude/skills/amazon-aplus-copywriter-canva/
```

`${CLAUDE_SKILL_DIR}` 会被替换成技能目录，SKILL.md 里的命令可以原样执行。

## Canva 连接

两种接法，工具集可能不一样，**先看本会话实际列出了哪些工具**再决定走哪条路：

| 接法 | 怎么接 | 工具名 | 能不能直接写备注 |
|---|---|---|---|
| 桌面端 Canva 连接器（实测） | 在桌面端的连接器 / 插件里启用 Canva 并授权 | `mcp__{一串ID}__read-design`、`…__edit-design`、`…__search-designs` 等（前缀是 ID，不是 `canva`） | 能，见「通道 A」 |
| 终端 `claude mcp add`（未测） | `claude mcp add --transport http --scope user canva https://mcp.canva.com/mcp`，再 `/mcp` → canva → Authenticate | `mcp__canva__…` | 看工具列表：`edit-design` 的操作里有 `replace_speaker_notes` 就能 |

工具多为延迟加载，用之前先用 ToolSearch 一次取全：`search-designs`、`read-design`、`edit-design`、`copy-design`、`export-design`。

### 工具对照（实测）

技能正文用的是旧工具名，这个连接器里读取类合并成了 `read-design` 一个工具：

| 技能正文里的说法 | 本连接器的调用 | 备注 |
|---|---|---|
| `get-presenter-notes` | `read-design`，`filter.fields=["presenter_notes"]` | 不传 `page_indices` 即全部页。返回 `{"presenter_notes":[{page_id, page_number, notes}]}`，原样存盘即可，`verify_notes.py` 和 `build_notes.py --before` 两种外形都认 |
| `get-design-content`（逐页） | `read-design`，`filter.fields=["design_content"]`，`page_indices=[N]` | 传了 `page_indices` 只返回该页文字；不传时多页连成一片，仍然要逐页取 |
| `get-design-pages` | `read-design`，`filter.fields=["page_metadata"]` | 返回 `id`（即 `page_id`）、`page_number`、`dimensions` |
| 缩略图 + `fetch_thumbs.py` | `read-design`，`filter.fields=["thumbnails"]`，`thumbnail_pages=[…]` | 447px 图片直接随结果返回，可以当场看，不需要 `fetch_thumbs.py`。实测有一页缩略图是花掉的旧缓存，看不准就用 `export-design` |
| `start/perform/commit-editing-transaction` | `read-design`（`open_transaction: true`）→ `edit-design`（`keep_open`）→ `edit-design`（`commit`） | |

`design_id` 可以填 `D` 开头的 ID，也可以填完整的设计链接。

## 第 C9 步：写备注

在 plan 里写明用哪个通道。

### 通道 A：连接器直接写（首选，实测）

`edit-design` 有 `replace_speaker_notes` 操作，不需要浏览器，不需要登录 Canva 网页。铁律 7、8（不碰画布、写前写后回读）照旧。

1. **写前回读**：`read-design` 取 `presenter_notes`，存 `notes_now.json`，跑 `verify_notes.py --compare notes_before.json notes_now.json`。
2. **备份**：把这份回读存为 `notes_backup_{时间戳}.json`。
3. **开事务**：`read-design`，`open_transaction: true`，`filter.fields=["presenter_notes","thumbnails"]`，记下 `transaction_id`。
4. **写入**：`edit-design`，`finalize: "keep_open"`，`operations` 里每页一条
   `{"type":"replace_speaker_notes","page_id":"…","notes":"p{N}.txt 的全文"}`。
   - 一次调用可以放多页的操作（实测：`page_index=1` 的一次调用里同时写了第 1、2 页）。页数多时分几次调用，每次几页，方便核对。
   - `operations` 里**只放 `replace_speaker_notes`**。同一个工具也能改画布文字、删元素，放错一条就违反铁律 7。
   - `notes` 上限 5000 字符，与网页一致。
   - 返回的 `document.page.notes` 是草稿里的备注；返回的缩略图用来确认画布没变。
5. **保存**：`edit-design`，只传 `transaction_id` 和 `finalize: "commit"`，不带 `operations`。commit 不可撤销，所以它排在用户在第 8 步说"写"之后；发现草稿不对就用 `finalize: "cancel"` 丢弃。
6. **写后回读**：`read-design` 取 `presenter_notes`，存 `notes_after.json`，跑 `verify_notes.py --expected … --readback notes_after.json`。全部 MATCH 才算完成。

实测结果：中文、全角空格、`① · † ‡ ® ™ ≤ ½ — –`、弯引号、结尾换行全部原样保留；提交后在 Canva 网页编辑器的备注面板里能看到，字数计数正确。

### 通道 B：Claude in Chrome（备用，实测）

连接器没有 `replace_speaker_notes`，或用户想看着写时用。配置：装 Chrome 扩展，终端里 `claude --chrome` 或会话内 `/chrome`；桌面端直接可用。操作的是用户自己的 Chrome，沿用已登录的 Canva，不用再登录。

1. 打开 `https://www.canva.com/design/{design_id}/edit`，等编辑器加载完。
2. 点左下角「备注」。面板标题是「第 N 页 - {页面标题}」，底部是 `字数/5000`。
3. 翻页：在画布区域滚动，面板跟着当前页切换（实测）。写之前读面板标题确认页码，并核对输入框现有内容的第一行。
4. 写入：`find` 找到 `textbox "备注"`（中文界面下是 `<textarea aria-label="备注">`），用 `form_input` 把 `p{N}.txt` 全文作为 value 一次填入。它会替换原内容，不需要全选，也不走剪贴板。
5. 核对：底部计数应等于 `manifest.json` 的 `chars`；顶部云图标的提示为「已保存所有更改」。
6. 回到通道 A 的第 6 步，用 `read-design` 回读并跑 `verify_notes.py`。

注意：

- **不要点面板标题来失焦。** `computer-use-canva.md` 第 4 步让点面板标题，但标题本身是可编辑的页面标题输入框（实测：点上去焦点落在 `INPUT`），这时打字会改页面标题。`form_input` 填完不需要失焦，Canva 会自动保存；要移开焦点就按 `Esc`。
- 页面上有三种文本输入要分清：`设计名称`、`页面标题`、`备注`。只动 `备注`。

### 通道 C：其他浏览器方式

| 方式 | 状态 | 说明 |
|---|---|---|
| 桌面端内置浏览器 | 实测：未登录 | 和用户的 Chrome 是两套登录态，打开设计链接直接跳到 Canva 登录页。用户先在内置浏览器面板里自己登录后，步骤同通道 B。一般没有理由选它 |
| Playwright MCP | 未测 | `claude mcp add playwright -- npx @playwright/mcp@latest`；定位备注 textarea 后 fill 整段写入。新浏览器配置文件需要登录 |
| computer use（API / 远程桌面） | 未测 | 剪贴板粘贴，见 `computer-use-canva.md` 第 4 步 |

### 账号（铁律 6 在 Claude Code 上的做法）

通道 A 不涉及网页登录。其他通道遇到登录页时：停在登录页，请用户自己完成登录（密码、验证码、Google 等第三方授权都由用户操作），登录后再继续。不走"用户把验证码发给 agent 代填"这条路。

## 先在副本上试

第一次在某个环境跑 C9，或连接器更新后，先用 `copy-design`（`page_numbers` 选 1–2 页）做一个副本，在副本上写一页、回读一致，再写正式设计。副本会继承原设计的标题和备注，用 `update_title` 改成带"测试"字样的名字，用完请用户在 Canva 里删除（连接器没有删除设计的工具）。

## Windows（实测，Git Bash）

- `python` 和 `python3` 可能是两个不同的解释器（实测机器上分别是 3.12 和 WindowsApps 下的 3.14）。`openpyxl` 装在哪个就用哪个，SKILL.md 里的 `python3` 相应替换。
- `build_notes.py`、`verify_notes.py` 已自行把输出设为 UTF-8。其他脚本在控制台打印中文报 `UnicodeEncodeError` 时，命令前加 `PYTHONUTF8=1`。

## 其他

- 选择题用 `AskUserQuestion`。
- 图片用 Read 工具直接查看（PNG/JPG）。
- 工作区约定见技能目录下的 `CLAUDE.md`；把它的内容合并进项目根的 `CLAUDE.md`，Claude Code 才会自动加载。

## 还没测的

- 终端 `claude mcp add` 接的 Canva MCP 是否与桌面端连接器工具集相同。
- 整份设计（十几页）一次写完；实测只写了两页的副本。
- 多人同时编辑时，连接器事务与网页端改动冲突的表现。
- `export-design` 导出单页 PNG。
