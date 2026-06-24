# supplement-safe-rebuild

这是一个 agent-agnostic 的下游安全重建版 skill，用于基于上游风险报告生成低风险功能替代方案。

本 skill 兼容所有主流 AI agent 平台（Claude Code、OpenAI Codex、QoderWork 等）。

放置位置采用 workspace scope 路径：

- `.kiro/skills/supplement-safe-rebuild/`

这样做的好处是：

- 不污染全局 skills
- 任何 agent 都可以直接在当前项目内发现和使用
- 你可以把上游报告直接喂给它，做固定结构的中文 rebuild 输出

## 设计思路

- 保留 Agent Skills 标准
- 去掉对特定 agent 平台的专用元数据和工具耦合
- 强化"safe rebuild，不是 reverse copy"的边界
- 强化中文输出和可复用模板

## 使用方式

在任何 agent 中可以直接这样说：

```text
用 supplement-safe-rebuild 基于上游风险报告做低风险功能重建，
输出中文固定结构，并给出 3 条 rebuild 方向。
```

## 超短调用模板

可以直接贴进 agent 对话窗口：

```text
基于上游风险报告，给我 3 条低风险 rebuild 方案，中文固定结构输出。
```

```text
尽量保留 AlgaeCal 类产品的植物源钙和骨支持卖点，但不要碰 branded source、exclusive story、骨密度增长 claims。
```

```text
基于 Fatty15 上游报告，保留 broad cellular wellness 目标，但避开 FA15(TM)、essential fatty acid 定位和 longevity 强 claim。
```

## 目录结构

```text
supplement-safe-rebuild/
├─ README.md
├─ SKILL.md
└─ references/
   ├─ output-template.md
   ├─ prompt-library.md
   ├─ workflow.md
   └─ examples/
      ├─ b09zq74495-rebuild.md
      └─ b0dnbl1d2j-rebuild.md
```
