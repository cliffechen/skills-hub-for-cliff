# AMZ-QA-Creator（亚马逊 Listing QA 批量生成系统）

亚马逊 Listing QA 批量生成 Skill —— 基于"QA 是流量工具"方法论：词库下漏 → VOC 痛点提炼 → 四合一质检生成 → 全量自动质检，输出默认 200 组结构化 QA（xlsx + csv + txt）。

## 上下游关系（流水线定位）

```text
amazon-new-listing-keyword-library（上游：词库搭建）
  └─ 产出：六 sheet 词库 xlsx（P0/P1/P2/品牌词否定清单/SearchTerm）
       ↓ 作为本 skill 的"必要输入1"
amz-qa-creator（本 skill：QA 批量生成）
  └─ 产出：200 组结构化 QA（xlsx/csv/txt + 质检报告）
       ↓ 下游联动
手动广泛广告：承接 QA 中高频品牌词的搜索订单（先建相关性、再承接流量）
```

- **上游依赖**：[`amazon-new-listing-keyword-library`](https://github.com/cliffechen/skills-hub-for-cliff/tree/main/amazon-new-listing-keyword-library) 的词库 xlsx 是本 skill 的标准输入；其"品牌词否定清单"（Listing/广告不可用的词）正是 QA 唯一合法承接的品牌词库，两个 skill 形成闭环。
- **兜底**：无上游产物时，接受通用中间格式 CSV（`keyword, tier, source, note`）。

## 安装（另一台电脑的 WorkBuddy）

把整个 `amz-qa-creator` 文件夹拷贝到目标机器的 skills 目录：

```bash
# 项目级（仅该项目可用）
cp -r amz-qa-creator /path/to/your-project/.workbuddy/skills/

# 或用户级（所有项目可用）
cp -r amz-qa-creator ~/.workbuddy/skills/
```

重启 WorkBuddy 后，提交输入文件并说"批量生成亚马逊QA / 搭建QA"，skill 自动触发。

## 运行环境

- Python 3 + `openpyxl`（脚本唯一第三方依赖：`pip install openpyxl`）
- 可选：Sorftime MCP（读 ASIN 信息/评论；未配置时走手动粘贴 fallback）
- 可选：SerpApi Key（站外 PAA 问句旁路；不提供则自动跳过）

## 输入（2 必要 + 2 可选）

| 信息源 | 说明 |
|---|---|
| 必要1：词库 xlsx | 词库 Skill（amazon-new-listing-keyword-library）的六 sheet 输出；或通用 CSV：`keyword, tier(core/longtail), source, note` |
| 必要2：ASIN 或 Listing 信息 | 首选 ASIN（Sorftime MCP 读 listing + VOC）；fallback：手动粘贴标题/五点/描述/参数 |
| 可选1：手动卖点补充 | 产品优势、需突出的点 |
| 可选2：SerpApi Key | 启用 Google PAA 问句旁路（key 只走环境变量，不落盘） |

## 目录结构

```
amz-qa-creator/
├── SKILL.md                        # skill 主文件（流程+质检标准+可调参数）
├── README.md                       # 本文件
├── scripts/
│   ├── inspect_kws.py              # 词库xlsx解析 → JSON
│   ├── serpapi_paa.py              # SerpApi PAA 旁路（key 仅环境变量）
│   └── build_qa_xlsx.py            # 合并批次+全量质检+导出 xlsx/csv/txt（含断点续跑）
└── references/
    ├── AMZ-QA-Creator-方法论.md    # 完整方法论（三大价值/三大技巧/四合一标准/输入Schema）
    └── banned_words.txt            # 医疗声明禁用词清单（红线/警告两级）
```

## 输出

`QA_<产品>_<日期>.xlsx / .csv / .txt`：
- xlsx：QA总表（问/答/类型/埋词/维度/来源/建议动作，微调行标黄）+ 统计与质检 sheet
- 质检：总数/来源占比/品牌词频次/形态错配/问句重复与句式分布/敏感词双层扫描/事实锚点比对/参数覆盖，FAIL 必须修正后重构

## 版本

- v1.1 (2026-08-02)：敏感词双层过滤、事实锚点校验、断点续跑 manifest、问句多样性约束、多竞品 VOC fallback、CSV/TXT 导出、脚本参数化
- v1.0 (2026-08-01)：首版（ZAB Urolithin A 204 组 QA 验证）
