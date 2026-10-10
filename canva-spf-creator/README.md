# canva-spf-creator

把一份膳食补充剂的 Supplement Facts 资料（截图、Excel、PDF、文字）变成 Canva 设计里的一页 SPF 面板，版式对齐美国 FDA 的要求（21 CFR 101.36）。

**转录 SPF → 缺陷检查 → 克隆模板页建面板 → 直接保存 → 回读核验 → 和用户来回修改**

## 它做什么

- **先查缺陷再建页**。每份 SPF 都过一遍检查，分三级交付清单：
  - 🔴 数算不通或 FDA 必填项缺失（%DV 与含量对不上、缺份数、软糖缺热量和碳水）。页面上用 `XX` 占位，清单里给出算出来的数，等用户确认。
  - 🟡 写法有歧义，需要用户补信息（缺来源形式、香精没标 natural / artificial、明胶没标来源、矿物质元素量与胶囊装量对不上）。
  - 🟢 顺序、版式、拼写标点，按 FDA 直接改好（有 Daily Value 的成分按法定顺序排在前、粗线分隔、脚注符号统一、英式拼写改美式）。
- **克隆模板页来保住字体**。Canva 接口新建的文字不能指定字体，所以从设计里已有的一页 SPF 克隆，再改字、删多余行、重排。
- **动手的页面左上角标 `create by canva mcp`**。提醒协作者别在生成期间动这一页，也方便分辨哪页是自动生成的。导出前要删。
- **保存后逐个元素回读坐标**。只核文字不够，实测出现过文字保存了、位置却回到模板原处的情况。

## 需要什么

- Canva 连接器（MCP）：`resolve-shortlink`、`read-design`、`merge-designs`、`edit-design`。
- 目标设计里有一页 SPF 可作模板；没有时见 `references/canva-build.md` §6。
- Python 3.10+，只用标准库。

## 怎么用

```text
使用 canva-spf-creator。
SPF 资料：<截图 / Excel / PDF 路径>
Canva 设计：<链接>
放在：最后一页（或"第 N 页后面"）
```

单独跑缺陷检查：

```bash
python scripts/check_spf.py spf.json
```

`spf.json` 的结构见脚本文件头。

## 目录结构

```
canva-spf-creator/
├── SKILL.md                    # 铁律 + 五步流程 + 每轮总结要求
├── README.md                   # 本文件
├── references/
│   ├── fda-spf-rules.md        # 面板必备内容与顺序、%DV、单位、来源形式、剂型对应营养项、缺陷检查表
│   ├── daily-values.json       # FDA Daily Value 表、成分排序、英美拼写对照
│   └── canva-build.md          # 克隆、打标记、认槽位、可用操作与坑、排版数值、保存核验、接口限制
└── scripts/
    └── check_spf.py            # %DV 重算、FDA 排序、份数算术、剂型营养项、Other Ingredients 扫描
```

## 已知限制

- 不能选字体、不能复制元素、不能改单页标题、不能对同一段文字里的个别词设斜体（如拉丁学名）。
- 成分行数超过模板行数时，多出的行只能用默认字体新建，需要手动换字体，或换一页行数够的模板。
- `daily-values.json` 的 Daily Value 与排序是按 FDA 现行规定整理的工作摘要，用于正式标签前请对照法规原文核一遍。
- 只做 SPF 面板页。写营销文案用 [`amazon-aplus-copywriter-canva-skill`](../amazon-aplus-copywriter-canva-skill/)。
