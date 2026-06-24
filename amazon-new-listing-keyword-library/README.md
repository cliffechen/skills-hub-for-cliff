# amazon-new-listing-keyword-library

亚马逊美国站新品关键词词库搭建系统 — Claude Code Skill。

输入4类文件(ABA品牌分析CSV / Sif关键词调研xlsx / 亚马逊下拉框txt / 产品信息图),输出分级关键词词库Excel(P0/P1/P2/否定清单/SearchTerm成品)+ 选词策略报告(选词理由/新品打法节奏/广告策略方向)。

## 目录结构

```
amazon-new-listing-keyword-library/
├── SKILL.md                  # skill主文件(流程+判断标准+可调参数)
├── README.md                 # 本文件
├── mcp-config-template.json  # Sorftime MCP配置模板(可选依赖)
├── references/               # 方法论资料(skill运行时会引用)
│   ├── 项目思路总览.png
│   ├── 关键词收集术.md
│   ├── 整理一份亚马逊广告打法全策略手册_广告心得.md
│   ├── 【listing优化】2026亚马逊listing优化适配Alexa指南.docx
│   └── POPE-Listing打造SOP-截图.png
└── examples/
    ├── input-templates/      # 4类输入文件的格式样例
    └── sample-output/        # Urolithin A 首单成品(词库xlsx+报告md)
```

## 安装(另一台电脑的 Claude Code)

把整个文件夹拷到目标项目或用户目录:

```bash
# 项目级(仅该项目可用)
cp -r amazon-new-listing-keyword-library /path/to/your-project/.claude/skills/

# 或用户级(所有项目可用)
cp -r amazon-new-listing-keyword-library ~/.claude/skills/
```

重启 Claude Code 后,提交4类输入文件并说"搭建新品词库",skill 会自动触发;也可显式调用。

## 可选依赖:Sorftime MCP(市场定标与竞争透视)

skill 的"第二层市场级定标"依赖 Sorftime MCP(查关键词搜索量/趋势/首页竞争结构)。**未配置时 skill 自动降级运行**,只跳过市场定标,核心词库流程不受影响。

配置方法:把 `mcp-config-template.json` 的内容合并进目标机器的 MCP 配置(项目级 `.mcp.json` 或 Claude Code 的 MCP 设置),填入你的 Sorftime API 凭据。

## 运行环境要求

- Python 3 + openpyxl(生成/读取xlsx;Claude Code 会按需安装:`pip install openpyxl --break-system-packages`)
- 无其他硬依赖

## 使用方法

1. 准备4类文件(格式参照 `examples/input-templates/`):
   - ABA品牌分析CSV:卖家后台 品牌分析→热门搜索词,输入3个竞品种子ASIN生成下载
   - Sif关键词调研xlsx:Sif工具反查3-5个核心竞品ASIN导出
   - 下拉框txt:前台搜索框输入核心词,抄录下拉联想词
   - 产品信息图:Supplement Facts/产品规格截图
2. 在 Claude Code 中提交文件,说明"用新品词库skill跑词库"
3. 回答前置澄清问题(打法基调/输出格式等,均有默认值)
4. 获得词库xlsx + 策略报告md

## 版本记录

| 版本 | 日期 | 变更内容 |
|---|---|---|
| v1.1 | 2026-06-21 | Search Term 成品新增程序化字节校验(强制 ≤249 bytes);增加结构化版本记录 |
| v1.0 | 2026-06-11 | 首版,基于 Urolithin A 首单验证 |
