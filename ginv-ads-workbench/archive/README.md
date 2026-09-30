# Ginv-Ads 原站采集说明

来源：[Ginv-Ads 广告智库](https://sellerhelp.top/projects/Ginv-Ads%E5%B9%BF%E5%91%8A%E6%99%BA%E5%BA%93/)。

正文采集时间：2026-09-30 16:27（Asia/Shanghai）；JSON 中 `capturedAt` 使用等价的 UTC 标准时间。采集通过新建 HTTP 会话，读取网站真实验证逻辑并提交用户授权的访问码完成。没有读取浏览器 Cookie、本地存储或浏览器账户状态；访问码只进入隐藏的一次性输入，不保存到源文件、归档或输出日志。

## 已保存的内容

| 内容 | 数量 | 保存位置 |
| --- | ---: | --- |
| 主题与核心流程、快速判断、提示 | 13 | `../public/data/source-content.json` 的 `topics` |
| 方法论子文章，含完整正文 HTML 和纯文本 | 54 | JSON 的 `articles` |
| 概念卡，含定义、公式、用途、提示 | 20 | JSON 的 `concepts` |
| 原站计算工具界面与原始函数 | 5 | JSON 的 `tools` |
| 验证后的外层包装页和实际应用页 | 2 | `source/index.html`、`source/app.html` |
| 应用内联脚本与样式 | 2 | `source/inline.js`、`source/styles.css` |
| 引用的真实静态资源 | 24 | `assets/`，逐项 URL、状态码、SHA256 见 `coverage.json` |

24 项静态资源包含 3 个本站公共脚本、3 张本站共享侧栏图片、Font Awesome 两个版本的 CSS 和 16 个字体文件。全部 HTTP 200，保存文件的 SHA256 已核对。CSS 与字体保留原本相对目录关系。

## 覆盖范围和验证

范围为 Ginv-Ads 当前项目和它明确引用的依赖资源。页面目录列出的每个主题均检查；各主题文章数量与目录标注一致，总计 54。54 篇文章的标题与正文 HTML 已逐项同已验证页面 DOM 比较，全部一致。16 个项目内锚点均存在；文章 ID 与概念 ID 全部唯一。

正文、概念卡与工具均直接包含在验证后 HTML 中，没有正文懒加载接口。内联脚本的唯一 `fetch` 是 `/api/track` 访客计数，不承载知识内容，未调用该统计接口。3 个公共脚本也不拉取额外知识内容。原始用词、数值建议和错别字按来源保留；公式审计与工作台的计算实现单独处理，不修改本归档原文。

共享宣传侧栏中还发现 2 个本站其他项目链接、8 个站外推广链接和首页链接。两个本站其他项目链接已检查，当前均返回 HTTP 404；首页返回 HTTP 200。站外推广链接保留来源 URL，不递归抓取。它们不属于 Ginv-Ads 主体内容；详情在 `coverage.json` 的 `injectedNavigationLinks`。

归档 HTML 保留整个验证后页面，移除敏感输入值和监测配置字段；HTML 解析器会标准化属性和空元素语法。归档中的原站脚本仅供查看来源，工作台应使用提取的正文与经审核的工具实现。

## 数据字段

`source-content.json` 使用 `schemaVersion: 1`。

- `source`：源页面 URL、页面标题、应用 HTML 归档路径。
- `topics`：`id`、`title`、`order`、`sourceUrl`、完整 `bodyHtml/bodyText`、流程 `sopHtml/sopText`、判断 `decisionHtml/decisionText`、提示 `tipsHtml/tipsText`、`articleIds`。
- `articles`：`id`、`topicId`、`order`、`title`、`bodyHtml`、`bodyText`、`sourceUrl`、`summary`、`tags`、分段 `sections`。
- `concepts`：`id`、`title`、`subtitle`、`fullName`、`formula`、`meaning`、`use`、`tips`、完整 `bodyHtml/bodyText`、`sourceUrl`。
- `tools`：`id`、`title`、`description`、带原始默认值的 `inputs`、`functionName`、原始 `sourceCode`、完整 `bodyHtml/bodyText`、`sourceUrl`。
- `coverage`：数量对照、锚点检查、数据接口分类、依赖清单、共享导航检查、唯一性和空正文检查。

## 重新采集

在项目根目录 PowerShell 中运行。采集脚本需要 Python，以及 `requests`、`beautifulsoup4` 两个库。

```powershell
python -m pip install requests beautifulsoup4
python scripts/capture-source.py
```

脚本显示 `Access code (hidden):` 后输入访问码，输入内容不会回显。成功时显示 13 个主题、54 篇文章、20 张概念卡、5 个工具，以及 `coverageStatus: complete`。脚本也支持由运行时环境变量 `GINV_ACCESS_CODE` 传入访问码，不要把它写进源文件或提交到项目。

只从现有验证后快照重建正文 JSON（不联网、不会读取访问码）：

```powershell
python scripts/capture-source.py --extract-existing
```

该命令将覆盖正文 JSON，并把覆盖状态设为待审计。随后可重新检查现有快照引用的公共静态资源、内部锚点和共享导航链接：

```powershell
python scripts/capture-source.py --audit-existing
```

该审计命令不重新登录，也不重新获取受保护的项目正文。
