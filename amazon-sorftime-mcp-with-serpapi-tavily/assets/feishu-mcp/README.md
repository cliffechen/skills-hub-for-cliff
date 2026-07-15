# Codex ↔ 飞书云文档 / 多维表格连接器

这是一个本地 MCP 连接器。MCP 可以理解为给 Codex 增加外部工具的标准插座。

连接器程序具备以下能力：

- 检查飞书连接状态
- 获取新版飞书文档信息
- 读取新版飞书文档纯文本
- 创建新版飞书文档
- 向现有文档末尾追加内容
- 读取多维表格的数据表与字段结构
- 向多维表格安全追加一条记录
- 把不超过 20 MB 的本机报告上传到多维表格“附件”列

当前 Codex 配置采用“编辑专用”模式，开放连接检查、文档追加、多维表格检查和记录追加。读取文档、创建文档等工具默认不暴露给 Codex；如以后需要，可以再调整 `enabled_tools`。

新版文档仍要求地址中包含 `/docx/`。多维表格支持 `/base/` 和 `/wiki/` 链接；如果一个多维表格内有多个数据表，请粘贴包含 `table=tbl...` 的完整链接。

## 一、在飞书开放平台创建自建应用

1. 打开 [飞书开放平台](https://open.feishu.cn/app)，创建“企业自建应用”。
2. 在“凭证与基础信息”中复制 `App ID` 和 `App Secret`。
3. 在“权限管理”中开通以下文档权限：
   - 查看新版文档（只读时需要）
   - 创建及编辑新版文档（创建、追加内容时需要）
   - 获取数据表信息（检查多维表格结构时需要）
   - 查看、评论、编辑和管理多维表格，或“新增记录”（追加记录时需要）
   - 上传图片和附件到云文档中（把 HTML/PDF 报告放入附件列时需要）
   - 如果使用 `/wiki/` 链接，再开通“查看知识空间节点信息”
4. 创建并发布一个应用版本。企业账号通常需要管理员审核。

权限分两层：上面的 API 权限决定应用“能不能调用接口”；文档本身的权限决定应用“能不能碰这篇具体文档”。两层都满足才能成功。

## 二、填写本机密钥

在 PowerShell 中进入本目录：

```powershell
cd "D:\Code\Codex\Amazon Dashboard\feishu-mcp"
Copy-Item .env.example .env
notepad .env
```

把 `.env` 中的示例值换成真实的 App ID 和 App Secret，然后保存。`.env` 已被忽略，不应提交或发送给别人。

## 三、把连接器加入 Codex

推荐使用 Codex 桌面端：

1. 打开 **Settings（设置）**。
2. 进入 **MCP servers**。
3. 选择 **Add server**，类型选 **STDIO**。STDIO 表示 Codex 在本机启动这个小程序。
4. 名称填写 `feishu_docs`。
5. Command 填写 `python`。
6. Arguments 填写：

```text
D:/Code/Codex/Amazon Dashboard/feishu-mcp/server.py
```

7. Working directory 如有该输入框，填写：

```text
D:/Code/Codex/Amazon Dashboard/feishu-mcp
```

8. 保存，然后重启 Codex。

推荐将 `enabled_tools` 设为：

```toml
enabled_tools = ["feishu_connection_check", "feishu_append_document", "feishu_bitable_inspect", "feishu_bitable_append_record"]
```

也可以参考项目中的配置示例：`../.codex/feishu-mcp.example.toml`。

## 四、给应用目标文档权限

应用用 `tenant_access_token`（应用身份令牌）创建的文档归应用所有，应用可以直接继续读写。

如果需要读写个人已经创建的文档，请在目标文档右上角按以下路径操作：

1. 点击“更多”。
2. 选择“添加文档应用”。
3. 添加刚才创建的自建应用，并授予阅读或编辑权限。

如果是文件夹，飞书不支持直接把应用加入为文件夹协作者。常用做法是把应用机器人加入一个群，再把该群设为文件夹协作者。

多维表格也有两层权限：开放平台 API 权限 + 目标多维表格本身的权限。请在目标多维表格的协作设置中添加这个自建应用，至少授予可编辑权限。

## 五、验证

重启 Codex 后，可以直接发送：

```text
检查飞书云文档连接状态
```

看到“已成功取得飞书访问凭证”说明 App ID 和 App Secret 正确。然后用一篇已授权的测试文档继续验证：

```text
读取这篇飞书文档：https://你的企业.feishu.cn/docx/xxxxxxxx
```

```text
把“Codex 与飞书连接测试成功”追加到这篇文档末尾：https://你的企业.feishu.cn/docx/xxxxxxxx
```

成功时会返回文档 ID、创建的内容块数量和文档链接。

多维表格建议先检查字段，再追加记录：

```text
检查这个飞书多维表格有哪些字段：https://你的企业.feishu.cn/base/xxxx?table=tblxxxx
```

```text
向这个多维表格追加一条记录，字段为：关键词=algae calcium，决策=VERIFY
```

连接器会在写入前核对真实列名；如果列名不存在，会停止写入并列出可用字段，避免把数据写错列。

如目标表有“附件”类型列，还可以同时传入本机 HTML 或 PDF 路径。连接器会先上传文件，再把返回的 `file_token` 写入同一条记录。这样摘要可以直接筛选，视觉版报告也能从附件打开。

## 常见错误

| 现象 | 原因 | 处理方法 |
|---|---|---|
| 尚未配置飞书凭证 | `.env` 不存在或未填写 | 从 `.env.example` 复制并填写真实值 |
| App ID 或 App Secret 错误 | 凭证粘贴错误或多了空格 | 回到飞书后台重新复制 |
| `91403` 或 HTTP 403 | API 权限或目标文档权限不足 | 开通 API 权限，并把应用添加为文档应用 |
| 找不到文档 | 链接不是新版 `/docx/` 链接，或文档已删除 | 打开原始文档后重新复制链接 |
| Codex 看不到工具 | MCP 配置未生效 | 保存后重启 Codex，再在 `/mcp` 中查看 |
| 创建文档后自己看不到 | 文档归应用所有，尚未分享给个人 | 先用测试文档；后续可增加“分享给用户”功能 |
| 多维表格返回 403 | 应用缺少 API 权限，或没有目标表编辑权 | 开通多维表格权限，并把自建应用加入目标表协作者 |
| 提示多个数据表 | 链接中没有 `table=tbl...` | 打开要写入的数据表视图后重新复制完整链接 |
| 提示字段不存在 | 提交的列名与目标表不一致 | 先运行 `feishu_bitable_inspect`，按返回的真实列名写入 |
| 提示不是附件类型 | 指定列是文本/链接等类型 | 在飞书中新增“附件”类型列，或不要上传文件 |
| 附件超过 20 MB | 整文件上传接口的大小限制 | 压缩文件，或后续改用分片上传 |

## 本地自动检查

在 PowerShell 中运行：

```powershell
cd "D:\Code\Codex\Amazon Dashboard\feishu-mcp"
python -m unittest discover -s tests -v
```

看到 `OK` 表示连接器协议、链接解析和内容转换都通过。本检查不会访问你的真实飞书数据。

## 安全说明

- 不要把 `.env`、App Secret、访问令牌发到聊天、GitHub 或文档中。
- 默认写入动作只“追加”，不会覆盖或删除原文。
- Codex 配置建议把写操作设为需要确认；示例配置已使用 `default_tools_approval_mode = "writes"`。
