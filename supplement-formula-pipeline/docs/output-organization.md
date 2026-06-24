# 输出组织规则

本项目历史上同时存在 `outputs/`、`result/`、`formula-reconstruction-result/` 等目录，容易让人分不清哪些是当前正式交付、哪些是历史阶段产物。自本规则生效后，统一按下面的方式理解和新增文件。

## 1. 唯一正式案例目录

所有新的正式案例都只认：

```text
outputs/cases/{ASIN}-{core-ingredient}-{timestamp}/
```

这是唯一的案例根目录。

## 2. 案例目录内的职责

```text
outputs/cases/{case}/
├── inputs/         原始输入副本
├── sources/        证据、抓取摘要、解析结果
├── scratch/        临时草稿或中间文件
└── deliverables/   对外可读交付物
    └── final/      最终收口文档
```

规则：

- `inputs/` 只放用户提供或脚本复制的原始输入。
- `sources/` 只放证据和解析摘要，不放最终结论。
- `scratch/` 只放临时文件，随时可丢弃。
- `deliverables/` 放阶段性交付物。
- `deliverables/final/` 只放最后一层“可以直接拿去决策或对接工厂”的最终文档。

## 3. 最终技能的输出原则

`supplement-audience-satellite-formula-finalizer` 从现在起只输出：

```text
outputs/cases/{case}/deliverables/final/{name}-final-formula-brief.md
outputs/cases/{case}/deliverables/final/{name}-final-supplement-facts.html
```

默认生成 2 份成对交付物。

- `final-formula-brief.md`：最终收口文档，包含受众、主星/卫星、精简配方、实验室清单等。
- `final-supplement-facts.html`：极简标签页，只保留 `Supplement Facts` 主体、`Other Ingredients`、`Suggested Use`、`Caution`。

不要在 HTML 标签页里再放实验室清单、Free From 列表、草案说明或营销文案。

## 4. 旧目录的定位

- `result/`：历史 Skill 1/2 输出沉淀，保留参考，不再作为新项目正式输出目录。
- `formula-reconstruction-result/`：历史 Skill 3 输出沉淀，保留参考，不再作为最终交付目录。

这两个目录视为 `legacy`。

## 5. 实操建议

- 做新案例时，所有新增正式文件优先写到当前 case 目录。
- 做最终收口时，不再新增 `result`、`formula-reconstruction-result`、独立命名的根级输出目录。
- 若某个阶段需要很多工作草稿，优先写到 `sources/` 或 `scratch/`，不要污染 `deliverables/final/`。
