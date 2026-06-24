# ingredients-breakdown-compliance-check

这是一个 agent-agnostic 的 workspace skill，用于对补充剂产品进行成分拆解与合规风险查验。

本 skill 兼容所有主流 AI agent 平台（Claude Code、OpenAI Codex、QoderWork 等）。

放置位置采用 workspace scope 路径：

- `.kiro/skills/ingredients-breakdown-compliance-check/`

## 设计思路

- 保留 Agent Skills 标准的 `SKILL.md`
- 去掉对特定 agent 平台或 MCP 工具名的硬绑定
- 强化中文固定输出和可复制的模板化报告
- 适合在任何支持 workspace skill 的 agent 对话、slash command 或 spec 草稿中直接复用

## 使用方式

在任何 agent 中可以用自然语言触发，例如：

```text
用 ingredients-breakdown-compliance-check 分析 ASIN B09ZQ74495，
输出中文固定结构报告，并标出专利、商标、合规、平台风险。
```

也可以在 agent 的技能列表中显式调用这个 workspace skill。

## 超短调用模板

可以直接贴进 agent 对话窗口：

```text
分析 ASIN B09ZQ74495，中文固定结构输出，拆成分层并标 patent / TM / compliance / marketplace 风险。
```

```text
分析这行成分：Calcium (as AlgaeCal(R) Mesophyllum superpositum) 750 mg。
先拆层，再判断 generic / branded / likely proprietary / unclear。
```

```text
分析 ASIN B0DNBL1D2J，告诉我 C15:0、FA15(TM)、fatty15 brand story 哪些能保留概念，哪些必须 avoid。
```

## 目录结构

```text
ingredients-breakdown-compliance-check/
├─ README.md
├─ SKILL.md
└─ references/
   ├─ prompt-library.md
   ├─ report-template.md
   ├─ workflow.md
   └─ examples/
      ├─ b09zq74495-upstream.md
      └─ b0dnbl1d2j-upstream.md
```
