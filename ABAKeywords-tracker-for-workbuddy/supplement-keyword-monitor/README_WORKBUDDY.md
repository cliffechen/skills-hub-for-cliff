# Amazon Supplement Keyword Monitor — WorkBuddy 分享包

| 项目 | 内容 |
|---|---|
| Skill 名称 | Amazon Supplement Keyword Monitor |
| 注册名 | `supplement-keyword-monitor` |
| 版本 | `1.0.0` |
| 适用环境 | WorkBuddy |
| Python | 3.9+ |

## 这是什么

这是一个面向 Amazon 美国站膳食补充剂运营的周度关键词监测 Skill。它抓取 AMZ123 的 Amazon Brand Analytics（ABA）热搜排名，识别保健品相关词，按趋势分层，并可结合 Sorftime 的搜索量、CPC 和延伸词数据生成中文 HTML 机会周报。

## 输入与输出

输入：

- AMZ123 ABA 热搜榜单；
- 包内的保健品种子词典和排除规则；
- WorkBuddy 对待分类词的判断与中文翻译；
- 可选的 Sorftime API Key；
- WorkBuddy 对 Tier 1 关键词的中文商业分析。

输出：

- `reports/supplement_monitor_YYYY-WXX.html`：本周 HTML 报告；
- `reports/run_YYYY-WXX.log`：三阶段运行日志；
- `reports/.exchange/*.json`：WorkBuddy 与脚本之间的中间文件；
- `.supplement-keyword-monitor/data/history.db`：本地历史数据库；
- 可选 CSV 导出。

## 可以怎样触发

在 WorkBuddy 中可以直接说：

- “用 supplement-keyword-monitor 运行本周 Amazon US 保健品关键词监测。”
- “继续上次没完成的 ABA 保健品趋势周报。”
- “查看最新一周 Tier 1 关键词。”
- “查询 kava 的历史 ABA 排名。”
- “把这个监测流程改成另一个 Amazon 类目。”

第一次运行建议说：

> 用 supplement-keyword-monitor 先做安装自检，再在当前文件夹运行本周 Amazon US 保健品关键词监测；缺少配置时告诉我具体需要补什么。

## 安装

这个分享包的外层用于阅读说明。真正安装时，复制内层 `SKILL` 文件夹中的全部内容。

Windows 目标目录：

```text
C:\Users\<用户名>\.workbuddy\skills\supplement-keyword-monitor\
```

macOS / Linux 目标目录：

```text
~/.workbuddy/skills/supplement-keyword-monitor/
```

安装完成后应直接看到：

```text
supplement-keyword-monitor/
├── SKILL.md
├── scripts/
├── references/
├── templates/
├── data/
├── requirements.txt
└── .env.example
```

注意：不要形成 `supplement-keyword-monitor/SKILL/SKILL.md` 的双层目录。

## 配置

在你准备存放报告的工作目录中，把安装包内的 `.env.example` 复制为 `.env`，然后填写：

```text
SORFTIME_API_KEY=
VERIFY_SSL=true
```

不要把填写后的 `.env` 提交到 Git，也不要发送给 WorkBuddy 以外的人。没有 Sorftime Key 时仍可运行，但报告不会包含完整趋势、CPC 与延伸词数据。

安装 Python 依赖：

```text
python -m pip install -r <安装目录>/requirements.txt
```

成功时命令会正常结束，不会出现红色错误信息。

## 首次自检

在准备存放报告的工作目录中运行：

```text
python <安装目录>/scripts/smoke_test.py
```

成功标志：

```text
SMOKE_TEST_OK
```

这个自检不访问 AMZ123 或 Sorftime，也不会消耗 Sorftime 调用次数。

## 正常工作流

| 阶段 | 执行者 | 结果 |
|---|---|---|
| Step 1 | Python | 抓取 ABA 数据并生成待分类 JSON |
| 分类 | WorkBuddy | 分类并翻译每个候选词 |
| Step 2 | Python | 排除、分层、Sorftime 丰富、写历史库 |
| 分析 | WorkBuddy | 写 Tier 1 分析、赛道聚类、核心发现 |
| Step 3 | Python | 校验并生成 HTML 报告 |

同一周重复运行会覆盖同周 HTML；Step 1 新建本轮日志，Step 2 和 Step 3 追加到同一日志。

## 查看历史

```text
python <安装目录>/scripts/view_data.py
python <安装目录>/scripts/view_data.py --tier 1
python <安装目录>/scripts/view_data.py --keyword kava
python <安装目录>/scripts/view_data.py --weeks
python <安装目录>/scripts/view_data.py --export
```

CSV 会输出到当前工作目录的 `reports/`。

## 注意事项

- 完整运行需要访问外部网站；上游网页结构改变时，抓取可能失败。
- Sorftime 可能有调用费用、频率限制或数据缺失，具体以你的账号为准。
- ABA 排名数字越小越热门；趋势方向以 ABA 为准，搜索量只作辅助。
- 这是选品信号研究，不替代 ASIN 竞争、利润、配方、商标、专利和 FDA/Amazon 合规检查。
- 分享包中不得加入真实 `.env`、历史数据库、报告、日志、交换 JSON、`__pycache__` 或 `*.pyc`。
