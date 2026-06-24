# US 膳食补充剂选品分析器（US Supplement Product Research）

基于 **Sorftime MCP + xCrawl MCP** 的 Amazon US 膳食补充剂专用选品分析 Skill，帮助发现高潜力成分赛道、验证竞争格局、测算投入产出，并补充 Google、Reddit、论坛、竞品官网和媒体页面里的站外讨论与成分反馈。

## 前置条件

- **Sorftime MCP 已配置并启用**
- **xCrawl MCP 建议配置并启用**（用于站外网络信号；未配置时报告需标注未采集）
- Python 3.9+，安装 `openpyxl`（`pip install openpyxl`）

### xCrawl MCP 配置

复制项目根目录的 `.mcp.example.json` 为 `.mcp.json`，并在本机设置环境变量 `XCRAWL_API_KEY`。不要把真实 Key 写进可提交文件。

## 使用方法

```
/US_Sup_Product_Research SAM-e
```

或自然语言：
```
帮我分析一下美国站膳食补充剂市场中以"SAM-e"为核心关键词词或核心成分词的产品市场情况。
```

## 核心流程

1. **类目定位** - 在 Dietary Supplements 大类中定位目标成分
2. **关键词多维度对比** - 成分词/功效词/剂型词/人群词（至少 3 维度）
3. **属性标注** - 保健品 9 维度（成分大类、剂型、剂量标注、功效方向、目标人群、包装规格、认证标签、配方类型、价格带）
4. **交叉分析** - 至少 3 对：成分大类×剂型、成分大类×价格带、剂型×价格带
5. **xCrawl 站外网络信号** - Google、Reddit、论坛、竞品官网、媒体讨论、情绪和成分反馈
6. **竞品差评分析** - 按保健品痛点维度归类（效果、味道、吞咽、消化、包装、气味、成分、价格、质量）
7. **进入壁垒评估** - 合规壁垒标注「需另行评估」
8. **Go/No-Go 综合评分** - 5 维度加权
9. **⛔ 四件套交付** - 无论结论如何都必须输出

## 不做的事

- ⛔ 不做 FDA/FTC 合规分析
- ⛔ 不做专利/商标风险查验
- ⛔ 不做 Supplement Facts 标签设计
- ⛔ 不给出具体成分剂量建议

## 主要 Sorftime MCP 工具

- `category_search_from_product_name` - 按成分名搜索类目
- `category_report` - 类目 Top100 报告
- `keyword_detail` - 关键词详情
- `keyword_extends` - 关键词延伸词
- `keyword_search_results` - 关键词搜索结果自然位产品
- `keyword_trend` - 关键词历史趋势
- `product_detail` - 产品详情（标题+五点描述提取成分/剂量/剂型）
- `product_reviews` - 产品评论（差评分析）
- `product_trend` - 产品销量趋势

## 输出（四件套）

| 类型 | 文件命名 | 用途 |
|------|----------|------|
| 报告 | `{date}_US_{成分名}_市场调研报告_{version}.md` | 完整分析报告（10-11 章结构） |
| 精简 | `{date}_US_{成分名}_精简报告_{version}.html` | 快速浏览关键结论 |
| 看板 | `{date}_US_{成分名}_可视化看板_{version}.html` | 交互式 Dashboard |
| 数据 | `{date}_US_{成分名}_市场调研_数据_{version}.xlsx` | 多 Sheet 明细数据 |

**输出目录**：`工作成果/{成分名}_{YYYYMMDD}/`（不上传 GitHub）

启用 xCrawl 后会额外保存：

- `web_signal_raw.json`
- `web_signal_sources.json`
- `web_signal_analysis.json`
- Excel Sheet：`Web情报_搜索结果`、`Web情报_抓取明细`、`Web情报_综合洞察`

## 生成与校验脚本

```bash
python skills/US_Sup_Product_Research/scripts/render_deliverables.py all --input payload.json
```

**保健品标题解析脚本**：

```bash
python skills/US_Sup_Product_Research/scripts/parse_supplement_title.py --input top100_raw.json --output-dir ./
```

**Windows 用户注意**：在 Windows 上运行脚本如遇编码或路径问题，请参考 [`scripts/WINDOWS_USAGE.md`](./scripts/WINDOWS_USAGE.md) 获取详细指南。

## 下游对接

选品报告可作为后续合规 Skill（风险查验/安全重建/配方优化）的输入。

详见 `SKILL.md` 场景 5（膳食补充剂定向分析）。
