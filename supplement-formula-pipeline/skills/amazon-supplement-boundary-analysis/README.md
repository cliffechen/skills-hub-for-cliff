# amazon-supplement-boundary-analysis

Amazon US 保健品成分和流量边界分析 skill。它从 Sif AI 关键词 Excel、锚定 ASIN 和 Supplement Facts 出发，判断产品可承接的关键词流量、成分延伸机会、合规/IP 风险，并生成边界报告、方案对比、雷达图和候选 Supplement Facts。

## 在 pipeline 中的位置

这个 skill 属于 `supplement-formula-pipeline` 的成分流量边界分析模块，可单独运行，也可作为风险查验、安全重建、配方优化和受众收口链路中的关键输入。

## 必要输入

- Sif AI 关键词调研 Excel 文件
- 锚定 ASIN
- Supplement Facts 文本
- 核心成分或用户指定方向

默认市场为 Amazon US，默认品类为 dietary supplement / health supplement。

## 核心流程

1. 用 `scripts/create_case_workspace.py` 创建隔离案例目录。
2. 用 `scripts/analyze_sif_excel.py` 解析 Sif Excel。
3. 查询 Sorftime 的产品详情、流量词、竞品关键词、关键词详情和趋势。
4. 需要时使用 Exa/Apify 或 web search 做站外验证。
5. 写入案例目录下的正式交付物。
6. 用 `scripts/generate_radar.py` 生成雷达图。

## 输出隔离规则

不要把运行结果写进 skill 目录。所有案例产物应写入：

```text
outputs/cases/{ASIN}-{core-ingredient}-{yyyyMMdd-HHmmss}/
```

输入副本放在 `outputs/inputs/` 或案例目录的 `inputs/` 中；临时文件放在 `outputs/scratch/` 或案例目录的 `scratch/` 中。

## 标准交付物

案例目录中通常包含：

- `{name}-ingredient-traffic-boundary-report.md`
- `{name}-solution-comparison.md`
- `{name}-radar-chart.html`
- `{name}-radar-chart.png`
- 可选：`{name}-scheme-{direction}-supplement-facts-3-variants.md`
- 可选：`{name}-final-{ingredients}-softgel-formula.md`

正式交付物默认使用中文，保留英文产品名、ASIN、成分名、关键词字面量、法规术语和 URL。

## 常用命令

```powershell
python skills/amazon-supplement-boundary-analysis/scripts/create_case_workspace.py --asin B0GKPTBN59 --core-ingredient "C15 Pentadecanoic Acid" --sif-excel "C:\path\to\sif.xlsx"
```

```powershell
python skills/amazon-supplement-boundary-analysis/scripts/analyze_sif_excel.py "outputs\inputs\b0gkptbn59\sif.xlsx" --output-dir "outputs\cases\B0GKPTBN59-C15-Pentadecanoic-Acid-20260421-133715\sources"
```

```powershell
python skills/amazon-supplement-boundary-analysis/scripts/generate_radar.py assets/radar_scores_template.json --output-dir "outputs\cases\case-name"
```

## 目录结构

```text
amazon-supplement-boundary-analysis/
|-- README.md
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|   |-- case_config_template.json
|   `-- radar_scores_template.json
|-- references/
|   |-- workflow.md
|   |-- output-contract.md
|   |-- scoring-rubric.md
|   `-- supplement-facts-guidelines.md
`-- scripts/
    |-- create_case_workspace.py
    |-- analyze_sif_excel.py
    |-- generate_radar.py
    `-- validate_chinese_deliverable.py
```

## 风险规则

- 把品牌成分、专利故事、品牌名和疾病宣称视为边界风险
- 不因关键词流量高就推荐加入某个成分
- 除非用户明确要求，不把采购难度、供应商可得性或原料成本纳入评分
- Supplement Facts 和配方草案必须标注为探索方向，不是最终法规标签或生产配方
