# 输出契约

这个 skill 的目标不是继续制造更多文件，而是把前面多轮分析收成一个清晰终稿。

## 1. 唯一正式输出位置

默认只写入当前案例目录：

```text
outputs/cases/{case}/deliverables/final/
```

## 2. 默认产出 2 份成对文档

默认文件名：

```text
{name}-final-formula-brief.md
{name}-final-supplement-facts.html
```

其中：

- `final-formula-brief.md` 内必须包含：

- 受众与痛点
- 主星/卫星架构
- 精简配方
- 营养师视角功能审视
- 关键词与人群承接
- 声明边界
- 实验室对接清单
- 剩余风险

- `final-supplement-facts.html` 必须是极简标签页，只保留：
  - `Supplement Facts` 主体
  - `Other Ingredients`
  - `Suggested Use`
  - `Caution`

不要在 `final-supplement-facts.html` 中加入：

- 实验室清单
- 草案说明
- Free From 列表
- Lab Review Focus
- 营销文案

除非用户明确要求，否则不要再额外拆出：

- 单独实验室文档
- 单独人群文档
- 单独配方草案
- 新的 `result/`、`output/`、`final/` 根级目录

## 3. 与项目其他目录的关系

- `outputs/cases/`：当前项目唯一正式案例目录
- `result/`：历史遗留，仅供参考
- `formula-reconstruction-result/`：历史遗留，仅供参考

这个 skill 不应把正式输出再写进 `result/` 或 `formula-reconstruction-result/`。

## 4. 语言要求

正式交付文档必须是中文。

可保留英文的内容仅限：

- 成分正式名
- ASIN
- 关键词原词
- 法规术语
- URL

如果出现英文模板骨架或英文章节标题，必须在交付前改掉，并运行：

```powershell
python skills/amazon-supplement-boundary-analysis/scripts/validate_chinese_deliverable.py "outputs/cases/{case}/deliverables/final/*-final-formula-brief.md"
```
