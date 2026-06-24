# ingredients-breakdown-compliance-check

成分拆解与合规审查 skill。用于对补充剂、健康产品、品牌成分或 ASIN 做结构化成分拆解，并识别商标、专利、专有成分、FDA/Amazon 合规和商业化风险信号。

## 适用场景

- 分析竞品 Listing、品牌配方、Supplement Facts 或成分标签
- 判断成分是 generic、branded、likely proprietary 还是 unclear identity
- 识别 `TM`、`R`、`(R)`、特殊大写或品牌化成分名称风险
- 判断某个术语作为通用描述是否比直接引用品牌成分更安全
- 在上架、换标、仿制或配方重建前准备风险报告

## 支持输入

- ASIN
- 品牌名称
- 产品标题
- 成分名称
- Supplement Facts 或成分列表文本
- Listing 截图或标签图片

如果输入不完整，先标注缺失字段，再基于明确证据继续，不要默默补全或猜测。

## 核心流程

1. 标准化输入信息，明确产品、平台、区域和审查范围。
2. 构建成分别名列表，包括拼写变体、缩写、拉丁名、盐类、酯类、提取物、发酵形式和品牌形式。
3. 将每个成分分类为 generic、branded、likely proprietary 或 unclear identity。
4. 检查商标、专利、独家供应、专有工艺和 freedom-to-operate 信号。
5. 对膳食补充剂和健康产品执行 FDA/Amazon 风险审查。
6. 交叉验证站内市场数据和站外官方、专利、文献、品牌来源。
7. 输出结构化风险报告和下一步文件请求。

## 信息源策略

优先使用直接产品和市场数据，其次查找品牌所有者、制造商、供应商页面，再查官方监管、知识产权、专利和文献数据库。AnySearch 可作为主要站外发现工具，Exa 作为备用发现工具，Sorftime 用于 Amazon 市场背景。

任何工具发现都不能替代法律或监管结论所需的官方验证。

## 输出要求

报告应包含：

- 执行摘要
- 标准化输入信息和实际审查范围
- 成分拆解表格
- 成分分类和依据
- 商标、专利、合规、市场风险矩阵
- 主要结论的置信度标签
- 缺失证据点
- 3-5 个下一步文件或检查建议

## 安全边界

- 不把输出写成法律建议
- 不断言某产品确定不侵权
- 不指导用户规避专利或未经授权使用商标
- 不把缺少商标符号视为通用成分的充分证据
- 不仅凭单一市场页面下决定性结论
- 不声称某补充剂获得 FDA 批准，除非有官方来源明确支持

## 目录结构

```text
ingredients-breakdown-compliance-check/
|-- README.md
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
`-- references/
    |-- prompt-library.md
    |-- source-strategy.md
    |-- ingredient-breakdown.md
    |-- ip-and-proprietary-risk.md
    |-- compliance-and-marketplace-risk.md
    `-- report-template.md
```

## 使用方式

```text
用 ingredients-breakdown-compliance-check 分析 ASIN B09ZQ74495，
输出中文结构化风险报告，并标出 patent / TM / compliance / marketplace 风险。
```

```text
分析这行成分：Calcium (as AlgaeCal(R) Mesophyllum superpositum) 750 mg。
先拆层，再判断 generic / branded / likely proprietary / unclear。
```
