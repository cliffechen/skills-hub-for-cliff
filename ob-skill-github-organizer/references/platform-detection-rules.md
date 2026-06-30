# Platform Detection Rules

Use evidence, not directory names alone.

## Labels

| Label | Use When | Strong Evidence |
|---|---|---|
| Codex/OpenAI original | Skill is built for Codex/OpenAI-style agent execution | root `SKILL.md`; `agents/openai.yaml`; references written for OpenAI/Codex behavior |
| Codex/Claude/QoderWork compatible | Standard Agent Skills shape, not platform-specific | root `SKILL.md`; `README.md`; `references/`; no WorkBuddy wrapper |
| Agent generic | The skill explicitly says agent-agnostic or workspace skill | text contains `agent-agnostic`, `workspace skill`, or says it supports Codex/Claude/QoderWork |
| WorkBuddy directory | A separate repo directory exists for WorkBuddy but is not a full WorkBuddy package | directory name ends with `-WB` or contains `workbuddy`, but only has root `SKILL.md` |
| WorkBuddy standard package | Ready to treat as a WorkBuddy package | `README_WORKBUDDY.md` at package root and `SKILL/SKILL.md` inside |
| WorkBuddy convertible | Not a WorkBuddy package, but easy to convert | root `SKILL.md` with `references/`; no complex scripts or platform-only tools |
| WorkBuddy high-cost conversion | Possible but needs careful adaptation | many scripts, MCP dependencies, dashboards, generated files, or multi-skill pipeline |

## Important Distinctions

- A folder named `xxx-WB` is not automatically a full WorkBuddy package.
- If `xxx-WB` and `xxx` have the same `SKILL.md` and references, describe the WB folder as a WorkBuddy version directory or install target, not as a rewritten WorkBuddy-optimized skill.
- Only use "WorkBuddy 专用/优化" when the structure follows the user's reference package:

```text
package/
├── README_WORKBUDDY.md
└── SKILL/
    ├── SKILL.md
    ├── assets/
    └── references/
```

## Evidence to Record

For each skill, record:

- entry path,
- `SKILL.md` location,
- whether `README_WORKBUDDY.md` exists,
- whether `SKILL/SKILL.md` exists,
- direct child folders such as `agents`, `references`, `scripts`, `assets`, `examples`,
- latest commit date and message,
- whether it looks duplicated from another directory.
