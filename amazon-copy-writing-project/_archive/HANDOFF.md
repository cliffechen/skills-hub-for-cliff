# HANDOFF｜AC02-M 文案工作台（Copy Workbench）

> **文档版本**：v1.0　|　**生成时间**：2026-09-13　|　**执行方**：zcode（GLM coding plan）
> **交付包**：本文件 + 同目录 `copy.json` + 同目录 `_skill\`（上游写作 skill 的完整资料）。这三份构成完整执行输入，**不需要任何其他资料**。

---

## 0. 给执行方的开工指令

按顺序执行，**不要跳过、不要自行扩大范围**：

1. 通读本文件，尤其 §3 事实基线、§5 系统规格、§7 禁止事项。
2. 在 `D:\Code\WB\AC02\AC02-M-文案草稿\_workbench\` 下按 **§5.1** 建齐文件。
3. **`copy.json` 已由上游定稿并随包提供**——原样保留，**禁止改写、润色、重新生成**。你的职责是读它、渲染它、写回它，不是创作它。
4. `_skill\` 是**只读参考**，仅供你理解文案背后的规则（为什么某些原文被删改）。**不要把 `_skill\` 纳入工作台的功能范围**，不要解析它、不要渲染它、不要在界面上展示它。
5. 按 §5.3–§5.8 实现 `server.py`、`index.html`、`app.js`、`style.css`、启动脚本、`README.md`。
6. 按 **§6 验收标准**逐条自测，回复中给出**逐条通过/不通过**结论 + 关键截图或命令输出。
7. 若有任何一条不通过，**不要声称完成**。

**硬约束**：只用 Python 3 标准库 + 原生 HTML/CSS/JS。不引入 npm、构建工具、框架、CDN 外链。必须完全离线可用。

---

## 1. 项目背景与目标

### 1.1 背景

Cliff 是亚马逊美国站膳食补充剂卖家。产品 **ZABORATORY Algae Calcium Renew+（内部代号 AC02 / AC02-M）** 的详情页（A+ / 图库）设计稿已出图，图内文案槽位待填。目前已产出一份四风格文案稿（Markdown，3000+ 行），存在两个使用痛点：

1. **Markdown 阅读体验差** —— 事实基线、槽位映射、四风格正文、合规自检四层混在一个文件，滚动定位困难。
2. **看图与读文案要来回切软件** —— 设计师给的 `*##*` 占位符在图上，文案在 md 里，需在图片查看器与编辑器间反复切换。

### 1.2 目标

构建**本地运行的单页文案工作台**，达成：

- 左边看设计稿、右边读对应槽位文案，**一屏内完成「看图 → 找槽 → 取文案」**；
- 图上槽位**高亮定位**（hover 双向联动、点击选中）；
- 四风格（A/B/C/D）**一键切换** + **同槽四风格横向对比**；
- 文案可**页内直接修改并写回** `copy.json`（自动备份、原子写入）；
- 可**按风格导出 Markdown**。

### 1.3 交付形态（已由用户确认）

| 决策项 | 结论 |
|---|---|
| 坐标定位 | **做**（图上高亮 + 可视化微调） |
| 页内改稿回写 | **做**（本地 Python 服务 + API 写回） |
| 交付形态 | **同目录引用原图**（不内联 base64，保持体积小） |
| 发布到资料库 | **不发布**（纯本地） |

---

## 2. 输入素材（只读，不得修改）

### 2.1 设计稿图片（10 张）

根目录：`D:\Code\WB\AC02\AC02-M-文案草稿\`

| 模块 ID | 文件名 | 用途 |
|---|---|---|
| M1 | `1.png` | 详情页页头 |
| M2 | `2.png` | 成分与作用四条 |
| M3 | `3.png` | 软胶囊实拍与规格 |
| M4 | `9.png` | Delivery Matters 对比表 |
| M5 | `10.png` | Supplement Facts 页 |
| M6 | `高级轮播1.png` | 轮播卡 1｜成分全景 |
| M7 | `高级轮播2.png` | 轮播卡 2｜成分卡 1–3 |
| M8 | `高级轮播3.png` | 轮播卡 3｜成分卡 3–5 |
| M9 | `高级轮播4.png` | 轮播卡 4｜利益三连 |
| M10 | `高级轮播4 (2).png` | 轮播卡 5｜交付与用量 |

> ⚠️ `高级轮播4 (2).png` 文件名含**空格与半角括号**。前端需 `encodeURI`，服务端需 `urllib.parse.unquote`。**这是验收项 #3 的考点。**

### 2.2 已定稿文案稿（人工回溯用，只读）

`D:\Code\WB\AC02\AC02-M-文案草稿\AC02-M-详情页文案-四风格-v1.md`

`copy.json` 已完整承载其内容。**程序不需要读取此 md。**

### 2.3 事实来源（资料库在线文档，仅供追溯，**无需访问、无需联网**）

| 文档 | 节点 ID | URL |
|---|---|---|
| AC02-副图四大牌调性文案包-v2 | `JSXj6ChxQpVOiS0oIujPRx` | https://www.workbuddy.cn/space/d/JSXj6ChxQpVOiS0oIujPRx |
| 开发逻辑 | `jSa9TYpWqlhF4fBdiBrAki` | https://www.workbuddy.cn/space/d/jSa9TYpWqlhF4fBdiBrAki |

---

## 3. 事实基线（**文案的唯一依据，禁止偏离**）

### 3.1 产品规格（2026-09-13 版，已由用户确认变更）

| 项 | 值 |
|---|---|
| 产品名 | ZABORATORY Algae Calcium Renew+ |
| 剂型 | **Vegan Softgel**（植物软胶囊） |
| 每份 | **2 softgels per serving** |
| 容器 | **90 softgels ／ 45 servings per container**（45 天） |
| 软胶囊壳 | Modified Food Starch, Glycerin, Purified Water, Carrageenan |
| 其他成分 | Organic MCT Oil, Sunflower Lecithin |

> ⚠️ **与旧版差异（P0）**：旧口径为「60 粒 vegetarian capsule／30 天」。本工作台**一律用新版**：`Vegan Softgel` / `2 softgels per serving` / `90 softgels` / `45 servings`。文案里出现 `capsule`、`60 caps`、`30-day supply` 视为错误。

### 3.2 六项活性

| 成分 | 剂量 | %DV | 形态学名 |
|---|---|---|---|
| Calcium | 400 mg | 31% | from algae-derived mineral complex |
| Vitamin D3 | 25 mcg | 125% | as cholecalciferol |
| Vitamin K2 | 90 mcg | 75% | as menaquinone-7 (MK-7) |
| Astaxanthin | 4 mg | † | — |
| Urolithin A | 250 mg | † | — |
| Nicotinamide Riboside Chloride | 300 mg | † | — |

† Daily Value Not Established

### 3.3 主张边界（合规红线，**§5.5.6 合规检查功能按此实现**）

**白名单（可用）**：`supports healthy bones`、`supports bone structure`、`plant-based calcium`（原料真实时）、`supports everyday wellness`、`supports calcium absorption`、`supports calcium delivery to bone`、`cellular energy metabolism`、`cellular function`、`cellular renewal`、`antioxidant support`、`muscle strength`、`immune function`

**黑名单（出现即报错）**：完整清单见 `copy.json` 的 `meta.banned`（40 项），分组如下——

| 组 | 词 |
|---|---|
| 抗衰 / 逆转 | `anti-aging`、`anti aging`、`reverse aging`、`reverses aging` |
| 骨密度 / 骨折 | `bone-density increase`、`increases bone density`、`prevents bone loss`、`fracture healing` |
| 线粒体 / NAD+ | `mitochondrial repair`、`NAD+` |
| 疾病语境 | `cure`、`cures`、`cured`、`treat`、`prevent`、`diagnose`、`relieve` |
| 减重 / 排毒 / 生发 | `detox`、`fat burn`、`burn fat`、`lose weight`、`weight loss`、`hair growth` |
| 研究等效 | `clinically proven`、`clinically studied` |
| 未获认证 | `fda approved`、`doctor recommended` |
| 吸收主张 | `ready to absorb`、`absorbed faster` |
| 绝对化 | `safe for everyone`、`guaranteed`、`no side effects` |
| 排名式宣传 | `best-selling`、`top-rated`、`number one`、`#1` |
| 竞品商标 | `AlgaeCal`、`Mitopure`、`Niagen`、`Tru Niagen` |

> 说明：`prevent` / `treat` / `cure` 等词会误命中 DSHEA 免责声明本身，合规检查须**跳过 `meta.disclaimer`**。
> 匹配方式为**大小写不敏感子串匹配**。已确认当前 44 个槽位产出中无任何命中（唯一命中在 `M4-P` 的 `note` 字段，而 `note` 不在扫描范围内——见 §5.5.6）。

**竞品商标（禁用）**：`AlgaeCal`、`Mitopure`、`Niagen`、`Tru Niagen`（已含于上表）

**纪律**：
- Urolithin A 250 mg **仅是剂量事实**，不得写 `studied` / `clinically` 等研究挂钩语。
- `Nicotinamide Riboside Chloride` 在**产出英文**中必须全称。
- 信任表述白名单为 `Third-Party Tested`、`Made in a cGMP facility`；`Certified` 无认证机构名时禁用。

### 3.4 必须上图文字（DSHEA 免责声明，全文照抄）

```
*These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.
```

凡带 `*` 的文案，其所在图必须含此声明（右下角，深灰约 60% 字号）。工作台**不负责排版**，但须在界面上提示该模块需要上图。

---

## 4. 四风格定义（文案语气基准）

| 代号 | 名称 | 声线要点 |
|---|---|---|
| **A** | AG1 型（清晰教育） | 完整句；先给结论再给解释；把「里面有什么、为什么这样配」讲明白；克制、无感叹句 |
| **B** | Ritual-HUM 型（简洁透明） | 短句与破折号节奏；逐成分「是什么 + 做什么」；天数与剂量直接可读；不用修饰形容词 |
| **C** | Onnit 型（直接具体） | 动词或数字开句；一句话一件事；不写形容词堆叠；不写全大写口号（设计元素标签除外） |
| **D** | Thorne 型（准确易懂） | 形态学名与剂量口径直接上图；客观陈述句；不煽动；per serving 与 per softgel 口径分明 |

---

## 5. 要构建的系统

### 5.1 目录结构

```
D:\Code\WB\AC02\AC02-M-文案草稿\
├── 1.png  …  高级轮播4 (2).png        ← 已有，只读，勿动
├── AC02-M-详情页文案-四风格-v1.md      ← 已有，只读，勿动
└── _workbench\                        ← 全部新建（copy.json 与 _skill\ 已提供）
    ├── HANDOFF.md                     ← 本文件
    ├── copy.json                      ← 单一数据源（已提供，原样使用）
    ├── _skill\                        ← 上游写作 skill 完整资料（只读参考，勿纳入功能）
    ├── server.py                      ← Python 标准库 HTTP 服务 + 读写 API
    ├── index.html                     ← 工作台页面
    ├── app.js                         ← 前端逻辑
    ├── style.css                      ← 样式
    ├── 启动工作台.bat                  ← Windows 双击启动
    ├── 启动工作台.sh                   ← macOS/Linux
    ├── README.md                      ← 使用说明（中文，简明）
    ├── .backup\                       ← 运行时自动生成，copy.json 历史快照
    └── 导出\                          ← 运行时自动生成，导出的 Markdown
```

**服务根目录** = `D:\Code\WB\AC02\AC02-M-文案草稿\`（`_workbench` 的上一级）。
因此图片 URL 为 `/<文件名>`（如 `/1.png`、`/高级轮播4 (2).png`），工作台页面 URL 为 `/_workbench/`。

> 注意：`server.py` 必须用**脚本自身所在目录的上一级**推导服务根目录（`os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`），不得硬编码盘符。

### 5.2 技术栈与约束

- **后端**：Python 3（`http.server`、`json`、`os`、`shutil`、`datetime`、`urllib.parse`、`threading`、`socket`、`webbrowser`）。**仅标准库**。
- **前端**：原生 HTML5 + CSS3 + ES2020。**无框架、无构建、无 CDN**。所有资源本地。
- **主题**：**浅色**。深色底仅出现在图片本身。
- **界面语言**：简体中文；英文仅出现在「槽位产出英文」内容里。
- **字体**：`system-ui, -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif`；英文正文用 `ui-monospace, "Cascadia Mono", Consolas, monospace`。
- **不做**：cookie、登录、任何外网请求。

### 5.3 数据模型（`copy.json` Schema）

**顶层**

```jsonc
{
  "meta": {
    "product": "string",            // 产品名
    "spec": "string",               // 规格一句话（顶部状态条展示）
    "version": "string",            // 数据版本
    "savedAt": "ISO8601 | null",    // 最近保存时间，由服务端写入
    "disclaimer": "string",         // DSHEA 全文
    "banned": ["string"]            // 黑名单词（合规检查用）
  },
  "styles": [                        // 固定 4 项，顺序 A/B/C/D
    { "id": "A", "name": "AG1 型", "desc": "..." }
  ],
  "modules": [ /* Module[] */ ]
}
```

**Module**

```jsonc
{
  "id": "M1",
  "name": "页头",
  "img": "1.png",                   // 相对服务根目录的文件名
  "task": "一眼交代什么剂型、几粒、几天",  // 本图回答的买家问题
  "flags": [                         // 本图事实/合规风险提示
    { "level": "warn", "text": "..." }
    // level: "warn"(琥珀) | "error"(红) | "info"(蓝)
  ],
  "slots": [ /* Slot[] */ ]
}
```

**Slot · `kind = "text"`**

```jsonc
{
  "id": "M1-H",
  "label": "大字 3 行",
  "kind": "text",
  "judge": "槽位",                  // 槽位 | 推定槽位 | 疑似槽位·待确认 | 真实内容·保留
  "insp": "Softgel form / Liquid Inside / Dual-Action",  // 设计稿原始占位（内部参考，不上图）
  "rects": [[3, 33, 45, 27]],       // 坐标，每项 [x%, y%, w%, h%]；支持多 rect
  "values": {                       // 四风格内容
    "A": { "rec": "...", "alt": "..." },
    "B": { "rec": "...", "alt": "..." },
    "C": { "rec": "...", "alt": "..." },
    "D": { "rec": "...", "alt": "..." }
  },
  "note": "中文说明（可选）",
  "needs": "必须上图提示（可选）"
}
```

**Slot · `kind = "card"`**

```jsonc
{
  "id": "M7-C1",
  "label": "成分卡 1",
  "kind": "card",
  "judge": "槽位",
  "insp": "...",
  "rects": [[7, 29, 34, 58]],
  "cards": {
    "A": { "name": "...", "dose": "...", "line1": "...", "line2": "..." },
    "B": { }, "C": { }, "D": { }
  },
  "note": "..."
}
```

**Slot · `kind = "table"`**

```jsonc
{
  "id": "M4-C",
  "label": "对比表 5 行",
  "kind": "table",
  "judge": "推定槽位",
  "insp": "...",
  "rects": [[9, 38, 82, 50]],
  "rows": {
    "A": ["...", "...", "...", "...", "..."],
    "B": [], "C": [], "D": []
  },
  "note": "..."
}
```

**Slot · `kind = "preserve"`**（原稿已定，不接受修改；界面只读展示）

```jsonc
{
  "id": "M4-T",
  "label": "标题",
  "kind": "preserve",
  "judge": "真实内容·保留",
  "rects": [[3, 6, 40, 9]],
  "text": "Delivery Matters",
  "note": "设计师定稿，保留"
}
```

**坐标约定**：百分比，相对图片显示区域左上角，`[x, y, w, h]`。

**分隔符约定**（前端需按此拆分渲染）：
- `\n` → 多行，换行展示
- `｜`（全角竖线）→ 多单元，用于「环绕标签 ×5」「列头左右两列」等
- `  ·  `（空格 + 间隔号 + 空格）→ 同行内的并列单元
- `**xxx**` → 设计高亮词位，**渲染时按设计稿样式加粗，但不显示星号**
- `*`（行尾）→ 该主张需要 DSHEA 脚注

### 5.4 后端 API 规格（`server.py`）

**端口**：从 `8787` 起，被占用则 `8788`、`8789`… 最多试到 `8806`；最终端口打印到控制台。

**启动行为**：启动后自动 `webbrowser.open("http://127.0.0.1:<port>/_workbench/")`；控制台打印中文启动横幅 + 「关闭此窗口即停止服务」。捕获 `KeyboardInterrupt` 后优雅退出。

**路由**

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/` | 302 → `/_workbench/` |
| `GET` | `/_workbench/` | 返回 `_workbench/index.html` |
| `GET` | `/_workbench/<file>` | 静态文件（`app.js` / `style.css` 等） |
| `GET` | `/<图片名>` | 根目录图片（**仅允许** `.png/.jpg/.jpeg/.webp`） |
| `GET` | `/api/data` | 返回 `copy.json`；`Content-Type: application/json; charset=utf-8`；**`Cache-Control: no-store`** |
| `POST` | `/api/data` | 请求体为完整 JSON → 写入 `copy.json`；写前备份；返回 `{"ok":true,"backup":"<文件名>","savedAt":"<ISO>"}` |
| `POST` | `/api/export` | 查询串 `?style=A`；生成 Markdown 到 `导出/`；返回 `{"ok":true,"path":"<绝对路径>","name":"<文件名>"}` |
| `POST` | `/api/open` | 请求体 `{"path":"..."}`；用系统默认程序打开（**仅允许** `导出/` 与 `.backup/` 内路径）；返回 `{"ok":true}` |

**写回逻辑（`POST /api/data`）**

1. `json.loads` 校验：必须是合法 JSON 且含 `modules` 数组，否则 `400` + `{"ok":false,"error":"invalid json"}`。
2. 写入 `meta.savedAt` = 当前本地时间 ISO8601。
3. 备份：`copy.json` 若存在，复制为 `.backup/copy-YYYYMMDD-HHMMSS.json`。
4. 备份目录只保留**最近 30 个**，按文件名倒序删除多余项。
5. 原子写入：先写 `copy.json.tmp`，再 `os.replace` 覆盖。
6. 输出统一 `ensure_ascii=False`、`indent=2`，保证中文可读。

**安全（必须实现）**

- 路径穿越防护：静态请求经 `os.path.normpath` 后必须仍在允许根目录内，否则 `403`。
- 仅允许 `GET` / `POST`，其余 `405`。
- **只绑定 `127.0.0.1`**，绝不绑 `0.0.0.0`。
- `/api/open` 的 path 需 `os.path.realpath` 后确认在 `导出/` 或 `.backup/` 之下。
- 中文文件名：请求路径需 `urllib.parse.unquote` 后再做文件系统访问。

**导出 Markdown 格式（`POST /api/export`）**

```markdown
# AC02-M 详情页文案｜风格 {X}：{风格名}

> 产品：{meta.product}　|　规格：{meta.spec}
> 导出时间：{YYYY-MM-DD HH:mm}

## {module.id}｜{module.name}（{module.img}）

**本图任务**：{module.task}

### {slot.id}｜{slot.label}
- 判定：{judge}
- 产出英文：
  ```
  {rec}
  ```
- 备选：
  ```
  {alt}
  ```
- 中文说明：{note}
- 必须上图：{needs}

（`kind=card`：输出「名称 / 剂量 / 说明1 / 说明2」四行；
 `kind=table`：输出 Markdown 表格，行数同 `rows[style]`；
 `kind=preserve`：输出「保留：{text}」）

---

## 未完成项 / 待确认

（列出界面上勾选为「待确认」且未填写的槽位，无则写「无」）

---

*本稿供品牌审阅与设计执行；发布前须确认产品材料、最终图文及适用平台要求，不宣称已获平台批准或已验证转化效果。*
```

### 5.5 前端 UI 规格（`index.html` / `app.js` / `style.css`）

#### 5.5.1 整体布局

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 顶栏：产品名 · 规格 · [A|B|C|D] · [工作台|四风格对比] · [标定] · [合规检查] · [保存] · [导出] · 状态 │
├──────────────────────────────┬─────────────────────────────────────────────┤
│ 左：设计稿画布                │ 右：槽位卡列表（内部滚动）                    │
│ （图片 + 坐标 overlay）       │                                             │
├──────────────────────────────┴─────────────────────────────────────────────┤
│ 底栏：模块导航 M1 … M10（当前高亮） + 键盘提示                                │
└────────────────────────────────────────────────────────────────────────────┘
```

- 左右分栏默认 **55% / 45%**，中间 4px 可拖动分隔条（拖动改比例，存 `localStorage`）。
- 整体 `height: 100vh; overflow: hidden`；左右两栏各自内部滚动。

#### 5.5.2 左侧画布与坐标 overlay

- 容器 `#canvas` 的宽高比**必须等于图片原始宽高比**。
  实现：`<img>` 的 `onload` 后按 `naturalWidth / naturalHeight` 设置容器 `aspect-ratio`；overlay 层 `position:absolute; inset:0`。图片用 `object-fit: contain` 时，容器比例与图一致即天然对齐。
- 每个 slot 渲染 `div.hotspot`，`left/top/width/height` 用 rect 百分比；多 rect 渲染多个，共享同一 slotId。
- 状态样式：

| 状态 | 样式 |
|---|---|
| 默认 | `outline: 1.5px dashed rgba(0,120,90,.55)`，无填充 |
| hover | `background: rgba(0,120,90,.14)`；其他槽位降低不透明度 |
| 选中 | `outline: 2.5px solid #0d7a5f`；`background: rgba(0,120,90,.20)` |
| 已完成（勾选） | `outline-color: #2e9e5b` |
| `judge` 含「推定槽位」 | 虚线改琥珀 `#c98a00` |
| `judge` 含「疑似槽位」 | 虚线改红 `#c0392b` |

- 每个 hotspot 左上角显示小标签 `slot.id`。

#### 5.5.3 右侧槽位卡

自上而下：

1. **卡头**：`槽位 ID`（等宽）+ `label` + 判定徽章 + `[定位]` + `[ ] 完成`
2. **英文正文**：当前风格的 `rec`；`white-space: pre-wrap`；后方 `[复制]`
3. **备选行**（折叠）：展开显示 `alt` + `[复制]` + `[用此版]`（alt 提升为 rec，原 rec 转 alt）
4. **编辑区**：点击正文进入编辑态（换 `<textarea>`，自动高度）；`blur` 或 `Ctrl+Enter` 提交；提交后标 `dirty`
5. **折叠区（默认收起）**：`指令原文`（insp）/ `中文说明`（note）/ `必须上图`（needs，红色高亮）/ `当前坐标`

`kind=card` 渲染「名称 / 剂量 / 说明1 / 说明2」四个字段，各自可编辑与复制。
`kind=table` 渲染行列表，每行可编辑与复制。
`kind=preserve` 只读展示，卡片整体灰底，无编辑控件。

**双向联动**：hover hotspot → 对应卡片高亮并 `scrollIntoView({block:'nearest', behavior:'smooth'})`；hover 卡片 → 图上对应 hotspot 高亮。

#### 5.5.4 四风格对比视图

- 顶栏切到「四风格对比」后，左侧画布保留，右侧换成对比区。
- **已选中槽位**：横向并排四列（列头为风格代号 + 名称），每列含该风格 `rec` 全文与 `[复制]`。
- **未选中**：显示该模块全部槽位的四风格表格（行 = 槽位，列 = A/B/C/D）。
- 该视图**只读**；编辑回「工作台」视图操作。

#### 5.5.5 键盘快捷键

| 键 | 行为 |
|---|---|
| `←` / `→` | 上一个 / 下一个模块（M1…M10） |
| `↑` / `↓` | 上一个 / 下一个槽位 |
| `1` `2` `3` `4` | 切换风格 A / B / C / D |
| `Tab` | 在「工作台 / 四风格对比」间切换 |
| `Ctrl+S` | 保存 |
| `Esc` | 退出标定模式 / 取消编辑态 |
| `?` | 弹出快捷键说明浮层 |

> 输入框 / textarea 聚焦时，除 `Ctrl+S` 与 `Esc` 外全部禁用。

#### 5.5.6 合规检查

顶栏 `[合规检查]` 按钮，扫描**当前风格**全部槽位，**仅**扫描以下字段：`values.rec`、`values.alt`、`cards.*`（name/dose/line1/line2）、`rows.*`。
**不扫描** `note`、`insp`、`text`、`meta.disclaimer`（其中 `note` 与 `insp` 会引用被删除的原文，属正常内容，误报会干扰使用）。

- 对 `meta.banned` 做**大小写不敏感子串匹配**，列出 `模块ID / 槽位ID` + 命中词 + 前后各 24 字符上下文。
- 额外校验：含 `*` 的槽位，其所属模块是否有任一槽位声明了 `needs`（免责声明）；未声明则列为「提醒」。
- 无命中显示「未发现黑名单词」。
- 浮层内每项可点击 → 跳转对应槽位。

> ⚠️ 已知正常误报说明：`M4-P` 的 `note` 中引用被删除的原文 `Ready to absorb.`，以及 `M4-C` 的 `insp` 中引用原表 5 行——这些在 `note`/`insp` 中，按上述规则**不会**被扫描到。若实现后仍报出，说明扫描范围写错了。

#### 5.5.7 保存与状态

- 编辑 / 勾选 / 坐标调整 → `dirty`。
- 顶栏状态三态：`● 有未保存修改`（琥珀）/ `✓ 已保存 HH:mm:ss`（绿）/ `✗ 保存失败：<原因>`（红）。
- `[保存]` → `POST /api/data` 全量提交。
- `beforeunload` 时若 `dirty` 则拦截提示。
- 「完成」勾选状态存 `localStorage`（key `ac02m.done`），**不写入 `copy.json`**。

### 5.6 标定模式

- 顶栏 `[标定]` 进入 / 退出（`Esc` 亦可）。
- 进入后：当前选中槽位的 hotspot 显示 **8 个缩放手柄 + 可拖动本体**。
- 拖动实时更新百分比并同步到卡片「当前坐标」区；也支持直接手工输入 4 个数字。
- 改动标 `dirty`，`[保存]` 写回 `copy.json`。
- `[重置本槽坐标]` 恢复为页面加载时缓存的原始值。
- 精度 `0.5%`。

### 5.7 导出

- 顶栏 `[导出]` 下拉：`导出当前风格（A/B/C/D）为 Markdown` / `打开导出目录`。
- 导出成功弹提示，含文件名与 `[打开文件]`（调 `POST /api/open`）。

### 5.8 启动方式

**`启动工作台.bat`**

```bat
@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul && (python server.py) || (py server.py)
pause
```

**`启动工作台.sh`**

```sh
#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
exec python3 server.py
```

**`README.md`** 须含：一句话说明、双击启动方法、快捷键表、数据文件位置、备份位置、常见问题（端口占用 / 图片不显示 / 中文乱码 / 如何回滚到历史版本）。

### 5.9 视觉规范

- 背景 `#f5f7f6`；卡片 `#ffffff`；主色 `#0d7a5f`（品牌绿，取自设计稿）；正文 `#1f2a26`；次要文本 `#6b7a74`；边框 `#e2e8e5`。
- 卡片圆角 `10px`；`box-shadow: 0 1px 3px rgba(0,0,0,.06)`。
- 判定徽章：圆角胶囊、小号字、颜色按 §5.5.2。
- 动效克制：仅 hover / 选中用 `transition: 120ms ease`。

---

## 6. 验收标准（逐条自测并在回复中给出结论）

| # | 验收项 | 通过判据 |
|---|---|---|
| 1 | 文件齐全 | §5.1 列出的 8 个新文件全部存在 |
| 2 | 双击启动 | `启动工作台.bat` 双击后控制台显示端口，浏览器自动打开 `/_workbench/` |
| 3 | 图片显示 | M1–M10 十张图**全部**正常渲染，含文件名带空格与括号的 `高级轮播4 (2).png` |
| 4 | 坐标对齐 | 随机抽 3 个槽位，hover 高亮框落在图上**对应文案位置**（允许 ±3% 偏差） |
| 5 | 风格切换 | 按 `1/2/3/4` 后右侧全部卡片英文**立即**切换，且与 `copy.json` 一致 |
| 6 | 双向联动 | hover 图上 hotspot → 右侧卡片滚动到可见并高亮；hover 卡片 → 图上 hotspot 高亮 |
| 7 | 编辑回写 | 改任一槽位英文 → 顶栏显示「有未保存修改」→ `Ctrl+S` → 提示已保存 → 用记事本打开 `copy.json` 可见改动 → `.backup/` 有快照 |
| 8 | 备份轮转 | 连续保存 3 次，`.backup/` 下有 3 个不同时间戳快照 |
| 9 | 对比视图 | `Tab` 切换后可见四列并排，同一槽位四风格文本互不相同 |
| 10 | 复制按钮 | 点击后剪贴板内容 == 该槽位当前风格 `rec` 全文 |
| 11 | 合规检查 | 人为在某槽位写入 `anti-aging` → 点合规检查 → 能列出该处并可定位 |
| 12 | 导出 Markdown | 导出风格 A → `导出/` 生成 md，含全部 10 模块、全部槽位与 DSHEA 声明 |
| 13 | 标定模式 | 进入标定 → 拖动 hotspot → 坐标数值变化 → 保存 → 刷新后坐标保持新值 |
| 14 | 完全离线 | 断网刷新页面，功能与样式完全正常（无任何 CDN 请求） |
| 15 | 仅标准库 | `server.py` 的 import 只有 Python 标准库 |
| 16 | 只绑本机 | 服务监听地址为 `127.0.0.1`（`netstat -ano \| findstr <port>` 可验证） |

---

## 7. 禁止事项

1. **不得改写 `copy.json` 的文案内容**——原样使用。若发现明显问题（拼写、与 §3 事实冲突），在回复中**单列一条「疑似问题」**，不要自行修改。
2. **不得修改根目录的 10 张 PNG 与 `AC02-M-详情页文案-四风格-v1.md`**。
3. **不得引入任何外部依赖**（npm / pip 包 / CDN / 字体外链）。
4. **不得绑定 `0.0.0.0`**，不得对外暴露端口。
5. **不得把服务做成需要联网**。
6. **不得删除 `_workbench/` 以外的任何文件**。
7. 不得增加原文没有的营销表述；界面用中文，产出英文严格照抄 `copy.json`。
8. 不得声称「已获平台批准」「转化已验证」。

---

## 8. 已知待确认项（继承自文案稿，工作台需在界面上体现，但**不由执行方解决**）

| # | 待确认 | 影响 | 优先级 |
|---|---|---|---|
| G1 | `90 softgels / 45 servings` 与旧版 `60 粒 / 30 份` 不一致，装量是否已改 | 全部数字行与天数账 | P0 |
| G2 | 藻源矿物能否提供 400 mg 元素钙且资料完整 | 主星真实度 | P0 |
| G3 | `10.png` 的 GLUTEN FREE 徽章是否有无交叉污染依据 | 徽章去留 | P1 |
| G4 | Third-Party Tested 的检测机构与报告是否齐备 | `9.png` 对比表首行 | P1 |
| G5 | 设计指令写「五种成分」，SF 面板为六项活性 | 轮播卡数（5 或 6） | P1 |
| G6 | `高级轮播1.png` 列表仅 4 行，卫星为 5 项 | 需增 1 行或合并 | P1 |
| G7 | Urolithin A 的法规 / FTO 状态 | 第二卫星能否保留 | P0 |
| G8 | `3.png` 左侧深色块与右上白块的设计字数上限未标 | 文案长度 | P2 |
| G9 | `9.png` 对比表 Others 列是否整列删除 | 版式变更 | P1 |

> 执行方**无需**处理以上内容。工作台只需：把 `flags` 渲染成模块级提示条，把 `judge` 为「疑似槽位·待确认」的槽位在卡片上以红色标注即可。

---

## 9. 上游 Skill 与合规关卡（供理解上下文，**执行方不需要运行该 skill**）

本次文案由 WorkBuddy 的 **`amazon-supplement-copywriting`** skill 产出。其关键规则已内化进本文件（§3 事实基线、§4 风格定义、§3.3 主张边界）。此处仅补录其**交付前合规七项关卡**，供理解「为什么有些原文被删改」：

| # | 关卡 | 本次结论 |
|---|---|---|
| 1 | **主张 ↔ 材料**：每条明示或暗示的主张都能指到一份本品材料及其适用范围 | 删 `Ready to absorb.`（吸收主张无材料） |
| 2 | **疾病语境**：无 diagnose／treat／cure／prevent／relieve 症状等表达，也无疾病暗示的画面元素 | 通过 |
| 3 | **绝对化与保证**：无 safe for everyone／guaranteed／no side effects 类；检测或认证未被放大成安全保证或功效 | 删 `Premium`／`Exceptional Purity`／`No Artificial Additives`；`Certified` 降级为 `Tested` |
| 4 | **数值口径**：每份与每粒、净含量与有效成分、天数与标签用法一致；商品标题写明计量对象 | 全篇统一 `2 softgels per serving` / `90 softgels` / `45 servings` |
| 5 | **声明与脚注**：需要上图的声明已列为上图文字并靠近对应主张 | DSHEA 全文列为必须上图（见 §3.4） |
| 6 | **禁止借用**：无竞品商标、口号、代言、数据或排名式宣传 | 删 `C15:0`／`CoQ10`／`Phosphatidylcholine` 残留；`Others` 列 ✗ 比较改中性 |
| 7 | **整体印象**：标题、支撑句、事实标签与视觉建议合读不产生误导 | 删 `The Full Healthy Aging Cycle.` 整体承诺 |

**skill 的核心纪律（工作台需体现，不需执行）**：
- 产出英文与设计稿槽位是**一对一映射**，不增不删版式单元；
- `[槽位]`／`[推定槽位]`／`[疑似槽位·待确认]`／`[真实内容·保留]` 四类判定必须可见（对应本工作台的判定徽章）；
- 数字与剂量槽若无依据即留占位（如 `[待补数字]`）并登记缺口，不为凑特点编值；
- 交付物是**可供品牌审阅与设计执行的草稿**，不得宣称已获平台批准或已验证转化效果。

> 上述纪律已全部编码进 `copy.json` 的 `judge`、`flags`、`note`、`needs` 字段。

---

## 附录 A：坐标标定速查表

以下为 `copy.json` 中已写入的坐标（`[x%, y%, w%, h%]`），**仅供人工核对**。若发现某槽高亮框明显偏位，用工作台的**标定模式**拖动修正后保存，不需要改 `copy.json`。

| 模块 | 图 | 槽位 | 坐标 | 说明 |
|---|---|---|---|---|
| M1 | 1.png | M1-H | 3, 33, 45, 27 | 大字 3 行 |
| M1 | 1.png | M1-S | 20, 67, 62, 15 | 三数值单元 |
| M1 | 1.png | M1-B | 8, 89, 84, 8 | 底部说明句 |
| M2 | 2.png | M2-T | 4, 5, 45, 11 | 页标题 |
| M2 | 2.png | M2-B1 | 4, 25, 30, 11 | 利益句 1 |
| M2 | 2.png | M2-B2 | 4, 39, 25, 11 | 利益句 2 |
| M2 | 2.png | M2-B3 | 12, 66, 34, 11 | 利益句 3（原镁位） |
| M2 | 2.png | M2-B4 | 4, 78, 30, 11 | 利益句 4 |
| M2 | 2.png | M2-R | 5 处：80/23、84/42、82/73、48/77、42/34（均 18×5） | 环绕标签，5 个 rect |
| M3 | 3.png | M3-T | 13, 15, 40, 11 | 页标题 |
| M3 | 3.png | M3-X | 8, 53, 27, 37 | 左侧深色块 |
| M3 | 3.png | M3-Y | 66, 33, 28, 34 | 右上白块 |
| M3 | 3.png | M3-N | 62, 72, 30, 10 | 数字行 |
| M3 | 3.png | M3-F | 62, 82, 34, 11 | 底部利益句 |
| M4 | 9.png | M4-T | 3, 6, 40, 9 | 标题 |
| M4 | 9.png | M4-S | 3, 14, 55, 8 | 副标 |
| M4 | 9.png | M4-P | 3, 22, 52, 10 | 说明段 |
| M4 | 9.png | M4-C | 9, 38, 82, 50 | 对比表 |
| M4 | 9.png | M4-CN | 80, 27, 14, 6 | 列头 |
| M5 | 10.png | M5-T | 3, 15, 32, 8 | 页标题 |
| M5 | 10.png | M5-ST | 3, 24, 32, 7 | 页副标题 |
| M5 | 10.png | M5-BT | 6, 65, 22, 7 | 左框标题 |
| M5 | 10.png | M5-BD | 6, 71, 26, 8 | 左框文案 |
| M5 | 10.png | M5-SF | 46, 3, 52, 72 | SF 面板（保留） |
| M5 | 10.png | M5-BG | 57, 76, 42, 18 | 徽章组（保留） |
| M6 | 高级轮播1.png | M6-CAP | 41, 1, 18, 7 | 顶部剂型标签 |
| M6 | 高级轮播1.png | M6-H | 8, 15, 45, 11 | 主标题 |
| M6 | 高级轮播1.png | M6-L | 6, 27, 45, 22 | 成分列表 |
| M6 | 高级轮播1.png | M6-K | 35, 61, 47, 10 | One Formula（保留） |
| M6 | 高级轮播1.png | M6-C | 33, 72, 52, 22 | 收尾句 |
| M7 | 高级轮播2.png | M7-T | 14, 17, 72, 10 | 主标题 |
| M7 | 高级轮播2.png | M7-C1 | 7, 29, 34, 58 | 卡 1 |
| M7 | 高级轮播2.png | M7-C2 | 42, 29, 34, 58 | 卡 2 |
| M7 | 高级轮播2.png | M7-C3 | 76, 29, 24, 58 | 卡 3（**右侧被画布截断**，属正常） |
| M8 | 高级轮播3.png | M8-T | 11, 17, 76, 10 | 主标题 |
| M8 | 高级轮播3.png | M8-C3 | 0, 29, 23, 58 | 卡 3（**左侧被画布截断**，属正常） |
| M8 | 高级轮播3.png | M8-C4 | 25, 29, 34, 58 | 卡 4 |
| M8 | 高级轮播3.png | M8-C5 | 59, 29, 34, 58 | 卡 5 |
| M8 | 高级轮播3.png | M8-C6 | 93, 29, 7, 58 | 六卡方案扩充位（**仅右侧 7% 细边可见**，属正常） |
| M9 | 高级轮播4.png | M9-B | 3 处：14/15、14/28、14/41（均 22×10） | 三条利益标签 |
| M10 | 高级轮播4 (2).png | M10-CAP | 41, 2, 18, 7 | 顶部剂型标签 |
| M10 | 高级轮播4 (2).png | M10-T | 8, 39, 45, 9 | 标题（保留） |
| M10 | 高级轮播4 (2).png | M10-S | 8, 48, 58, 8 | 副标 |
| M10 | 高级轮播4 (2).png | M10-D | 8, 58, 36, 12 | 数字块（保留） |

**关于「越界」坐标**：`M7-C3`、`M8-C3`、`M8-C6` 的 rect 会有意超出或贴近画布边缘，因为它们表现的是**轮播卡片在滚动中被截断**的真实状态。验收项 #4 的 ±3% 偏差判定对这三项应放宽，或按其可见部分判断。

---

## 附录 B：模块与设计稿对应关系（含未被文案覆盖的图）

| 文件 | 是否纳入本次工作台 | 原因 |
|---|---|---|
| `1.png` `2.png` `3.png` `9.png` `10.png` | ✅ 纳入（M1–M5） | 详情页主体模块 |
| `高级轮播1–4.png`、`高级轮播4 (2).png` | ✅ 纳入（M6–M10） | A+ 轮播模块 |
| `New-AC02-0910\` 目录下 7 张 | ❌ 不纳入 | 属**图库副图**（gallery images），已在另一份文案包 v2 中覆盖，不在本次「详情页」范围 |

---

## 附录 C：`_skill\` 上游写作 skill 资料索引

`_skill\` 是本次文案所用 skill（`amazon-supplement-copywriting`）的完整资料副本，**共 18 个文件 / 约 112 KB**。

> ⚠️ **对执行方的定位：只读参考，不是功能需求。** 工作台**不解析、不渲染、不展示**这些文件。它们的作用是让你（或在需要时让品牌的文案/法务）能追溯「为什么某些原文被删改」。若你发现 §3.3 的黑名单与实际文案有出入，以 `references/compliance-fda-ftc.md` 为准，但**仍不得改动 `copy.json`**，只能作为「疑似问题」上报。

### C.1 文件清单

| 文件 | 大小 | 与本次构建的关系 |
|---|---|---|
| `SKILL.md` | 15 KB | 主流程：写作简报 → 加载参考 → 排图 → 美式编辑 → 合规七关卡 → 交付。§9 已摘要其核心 |
| `references/compliance-fda-ftc.md` | 8 KB | **最相关**。`meta.banned` 的词表来源。含 FDA 403(r)(6) / FTC 健康产品指南的判断框架、免责声明适用范围 |
| `references/dosage-forms.md` | 9 KB | 剂型事实清单（软胶囊的可用事实、每份 vs 每粒口径、禁止推断项）。§3.1 规格来源 |
| `references/amazon-layout.md` | 7 KB | 版式与字段规则（主图/商品标题/副图/A+ 的区别，标题 75 字符上限） |
| `references/american-image-copy.md` | 8 KB | 美式图片文案编辑指南（自然搭配、节奏、防中文直译） |
| `references/frameworks.md` | 5 KB | 场景与写作结构框架 |
| `references/voice-ag1.md` | 4 KB | **风格 A** 声线参考 |
| `references/voice-ritual-hum.md` | 4 KB | **风格 B** 声线参考 |
| `references/voice-onnit.md` | 4 KB | **风格 C** 声线参考 |
| `references/voice-thorne.md` | 4 KB | **风格 D** 声线参考 |
| `references/examples/example-*.md`（7 个） | 39 KB | 各品牌历史案例，仅供理解语气，不作规则 |
| `assets/copy-package-template.md` | 8 KB | 交付模板（本工作台的导出格式参考了它） |

### C.2 已排除、以及排除理由

| 目录 | 体量 | 排除理由 |
|---|---|---|
| `research/` | 84 个文件 / **约 15.9 MB** | AG1、Ritual、Onnit、Thorne、Humble、Bulletproof、Nature Made 的 A+ 与副图**竞品截图**。仅供文案撰稿期观察表达，**与构建工具无关**，且体量大、含第三方品牌素材，不宜随包外发 |
| `evals/` | 7 个文件 / 约 102 KB | skill 维护期自测资料（场景、验证报告、输出基线），与本次任务无关 |
| `安装说明.txt` | 5 KB | 本机 skill 安装说明，与本次任务无关 |

> 若后续需要竞品视觉参考，直接从 `C:\Users\Nexus\.workbuddy\skills\amazon-supplement-copywriting\research\` 取，**不要**复制进交付包。

---

*本 HANDOFF 由上游文案环节产出，供执行方构建工具使用。文案内容版权与合规责任归品牌方（Cliff）所有。*
