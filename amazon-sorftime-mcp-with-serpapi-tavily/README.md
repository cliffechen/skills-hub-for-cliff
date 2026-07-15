# Amazon Sorftime + SerpApi + Tavily Research

这是一个可迁移到另一台 Windows 电脑的 Codex Skill，用于 Amazon US 选品调研。技能 ID 为 `amazon-sorftime-mcp-with-serpapi-tavily`；主动流程使用 Sorftime、SerpApi Google Web Trends 和 Tavily。

主要能力：

- **Sorftime MCP**：Amazon 类目、关键词、产品、销量、上架日期和评论证据。
- **主调研词自动接管**：LLM 生成语义候选词，Sorftime 验证搜索量与 Top20，固定脚本按相关率、购买意图、市场覆盖度和销量支持选出主词。
- **关键词漂移分析**：区分泛词、同义/来源词、功效配方词、品牌根词、品牌产品词和拼写变体，并保留品牌/非品牌需求边界。
- **SerpApi**：只采集 Google Web Trends，不再采集 Google Shopping。
- **Tavily MCP**：站外科学、法规、用户需求和趋势信息交叉验证。
- **数据源统计**：在 Markdown 和 HTML 中汇总工具/API 调用次数、状态与返回规模。
- **独立 HTML 渲染器**：生成自包含的可视化报告。
- **飞书多维表格连接器（可选）**：把摘要和 HTML 附件写入指定表格。

技能不做利润、毛利、ROI、采购成本、广告成本或回本测算。

## 包内结构

```text
amazon-sorftime-mcp-with-serpapi-tavily/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── scripts/
│   ├── install.ps1
│   ├── preflight.py
│   ├── fetch_serpapi_google_trends.py
│   ├── analyze_google_trends.py
│   ├── analyze_keyword_drift.py
│   ├── validate_research_data.py
│   ├── render_report.py
│   └── package_smoke_test.py
├── references/
└── assets/
    ├── config/
    ├── feishu-mcp/
    └── examples/algae-calcium/
```

## 最低要求

| 依赖 | 用途 | 是否必须 |
| --- | --- | --- |
| Codex Desktop | 运行技能和 MCP | 必须 |
| Python 3.10+ | 本地校验、趋势分析、HTML 渲染 | 必须 |
| PowerShell 5.1+ | Windows 安装脚本 | 必须 |
| Sorftime API Key | Amazon 核心数据 | 必须 |
| Tavily API Key | 站外交叉验证 | 必须 |
| SerpApi API Key | Google Web Trends | 建议；手工 Web CSV 可回退 |
| 飞书 App ID / Secret | 写入飞书多维表格 | 可选 |

## 安装主技能

解压后在技能目录打开 PowerShell：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1
```

更新已有安装：

```powershell
.\scripts\install.ps1 -Force
```

安装目标为：

```text
%USERPROFILE%\.codex\skills\amazon-sorftime-mcp-with-serpapi-tavily
```

也可以手工把整个目录复制到该位置。

## 配置 Sorftime MCP

在 Codex 的 MCP 设置中添加远程 Streamable HTTP 服务：

```text
名称：sorftime_mcp
URL：https://mcp.sorftime.com?key=你的_SORFTIME_API_KEY
```

也可以把 `assets/config/codex-config.example.toml` 中的 Sorftime 段复制到 `%USERPROFILE%\.codex\config.toml`，然后只在本机替换占位符。含真实 Key 的配置文件不要提交或分享。

## 配置 Tavily MCP

把 Key 保存为 Windows 用户环境变量：

```powershell
[Environment]::SetEnvironmentVariable("TAVILY_API_KEY", "YOUR_TAVILY_API_KEY", "User")
```

在 Codex MCP 配置中加入：

```toml
[mcp_servers.tavily_remote]
url = "https://mcp.tavily.com/mcp/"
bearer_token_env_var = "TAVILY_API_KEY"
enabled = true
```

## 配置 SerpApi

```powershell
[Environment]::SetEnvironmentVariable("SERPAPI_KEY", "YOUR_SERPAPI_KEY", "User")
```

重启 Codex 后，采集脚本对美国过去五年的 Web Search 发出一次请求，保存不含密钥的原始 JSON、CSV 和周度点数。Google Shopping 已从采集、分析和决策流程中删除。

## 可选：飞书多维表格

1. 把 `assets/feishu-mcp` 复制到稳定目录。
2. 在该目录新建 `.env`，填入 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。
3. 给应用开放读取数据表、编辑多维表格、新增记录和上传附件权限。
4. 把应用添加为目标表格协作者。
5. 按 `assets/config/codex-config.example.toml` 添加连接器并替换本机路径。

`.env` 不能放进 ZIP、GitHub 或聊天记录。

## 验证

配置完成后完全退出并重新打开 Codex，再运行：

```powershell
python scripts\preflight.py
python scripts\package_smoke_test.py
```

冒烟测试通过时显示 `SMOKE_TEST_OK`。

在 Codex 中可这样调用：

```text
使用 $amazon-sorftime-mcp-with-serpapi-tavily，调研 Amazon US 的 algae calcium，生成 Markdown 和 HTML 报告，不做利润测算。
```

技能会先把 `algae calcium` 当作种子词，生成并验证候选词；如果固定评分脚本选出更强的消费者路径词，例如 `algaecal`，后续完整调研将自动由该词接管，报告会展示全部系数、得分和淘汰原因。

## 正常输出位置

```text
research/<关键词>-<日期>/
├── raw/
│   ├── sorftime/keyword-selection-input.json
│   ├── sorftime/keyword-drift-analysis.json
│   ├── google-trends/analysis.json
│   ├── tavily/retained-sources.json
│   └── source-usage.json
├── data.json
├── report.md
└── html/report.html
```

不要把运行结果、`.env` 或 API Key 写进已安装技能目录。

完成报告渲染后，执行以下命令确认固定交付物完整；即使某个数据源不可用，对应 JSON 也必须保留脱敏的状态和缺失原因。

```powershell
python scripts\validate_deliverables.py research\<关键词>-<日期>
```

## 常见问题

| 现象 | 常见原因 | 处理方法 |
| --- | --- | --- |
| Codex 看不到新技能 | 尚未重启，或目录多套一层 | 确认 `SKILL.md` 直接位于技能目录并重启 |
| Sorftime 认证失败 | URL 中 Key 错误或过期 | 回到 MCP 设置更新 Key |
| Sorftime 参数错误 | 文档与实时工具参数漂移 | 以当前暴露的参数为准，并查看 `references/sorftime-tool-map.md` |
| Tavily 工具无法调用 | 当前进程没读到环境变量 | 完全退出 Codex 后重新打开 |
| SerpApi 不可用 | 环境变量缺失或额度不足 | 提供同口径的 Google Web Trends CSV，并在报告中标记回退 |
| HTML 打不开 | 输出不完整或路径错误 | 重新运行 `render_report.py` |
| 飞书返回 403 | API 或表格协作者权限不足 | 同时检查开放平台权限和目标表协作权限 |

## 安全检查

每次迁移或打包前运行：

```powershell
python scripts\package_smoke_test.py
```

包内只能出现占位符和示例假 token，不能出现真实 Sorftime、Tavily、SerpApi、飞书密钥或访问令牌。

Sorftime 上游参考：<https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill>
