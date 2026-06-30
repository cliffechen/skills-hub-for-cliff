---
name: ob-skill-github-organizer
description: Maintain and query a GitHub-hosted agent skill library across Codex/OpenAI, WorkBuddy, Claude Code, QoderWork, and Obsidian. Use when the user asks to scan or sync a GitHub skills repository, update an Obsidian Markdown skill index, distinguish Codex vs WorkBuddy skill structures, detect new/duplicate/stale skill directories, standardize WorkBuddy package notes, or asks which skill to use for a business task such as Amazon supplement image copy, keyword research, product research, ingredient compliance, formula rebuild, or A+ content.
---

# OB Skill GitHub Organizer

## Purpose

Use this skill as the user's skill-library operator. It has two jobs:

1. Sync mode: scan a GitHub/local skills repository and update an Obsidian Markdown index.
2. Query mode: answer "which skill should I use?" with a concrete recommendation, platform-specific option, and short usage guide.

Default personal targets when the user does not override them:

- GitHub repo: `cliffechen/skills-hub-for-cliff`
- Local repo path: `C:\Users\Nexus\Documents\GitHub\skills-hub-for-cliff`
- Obsidian index: `C:\Users\Nexus\Documents\Obsidian Vault\坚果云-AMZ Skills索引与备注.md`

## Mode Selection

- If the user says "扫描", "同步", "更新索引", "跑一次", "push 了一个 skill", "新增 skill", "重新整理", use Sync mode.
- If the user asks "我该用哪个 skill", "哪个 skill 适合", "怎么调用", "图片文案用哪个", use Query mode.
- If the user asks "这个是不是 WB 标准", "Codex 还是 WorkBuddy", "帮我区分版本", use Platform Audit mode.

## Sync Mode Workflow

1. Inspect the repository state first.
   - Prefer the local repo path if it exists.
   - Run `git status --short --branch`.
   - If the repo is clean and connected to origin, run `git pull --ff-only` before scanning.
   - Do not overwrite unrelated user changes.

2. Run the scanner when available.
   - Use `scripts/scan_skill_repo.py --repo-path <repo> --output-json <temp-json>`.
   - Use the JSON as the inventory baseline, then read relevant `SKILL.md` / `README.md` files for new or changed skills.

3. Classify every skill.
   - Read `references/platform-detection-rules.md`.
   - Mark each item as Codex/OpenAI original, WorkBuddy directory, WorkBuddy standard package, Agent generic, or WorkBuddy-convertible.
   - When a `-WB` directory has the same file SHAs/content as the original but lacks `README_WORKBUDDY.md` and `SKILL/SKILL.md`, call it "WorkBuddy 版目录；待标准包化", not "WorkBuddy 专用/优化".

4. Update the Obsidian index.
   - Read `references/obsidian-index-schema.md`.
   - Preserve the user's notes where possible, especially `我的备注`.
   - Update the sync timestamp with the user's current timezone.
   - Add new skills to both the quick overview table and the detailed category section.
   - Keep Codex/OpenAI original and WorkBuddy version rows separate when both exist.

5. Validate.
   - Read back the edited Markdown.
   - Confirm the new skill appears in quick overview and detail section.
   - Confirm platform labels are precise.
   - Report changed files and whether a commit/push was made.

## Query Mode Workflow

1. Use the Obsidian index as the first source of truth.
2. If the index may be stale or the user says they just pushed a change, run Sync mode first.
3. Read `references/query-routing-rules.md`.
4. Recommend:
   - one primary skill,
   - one platform-specific alternative when useful,
   - one fallback only if it is genuinely relevant.
5. Answer in Chinese by default and include:
   - skill name,
   - why this skill is the best fit,
   - where to use it: Codex/OpenAI, WorkBuddy, or either,
   - what inputs the user should provide,
   - one copyable invocation sentence.

Example answer shape:

```markdown
推荐用 `amazon-supplement-visual-content`。

如果你在 Codex/OpenAI 里做，用原版；如果你在 WorkBuddy 里做，用 `amazon-supplement-visual-content-WB`。

准备这些输入：产品名、品牌、Supplement Facts、瓶身/标签图、目标图片类型、卖点和认证信息。

可以这样说：
用 amazon-supplement-visual-content 基于这个 Amazon US 补充剂产品，生成主图合规方案、辅图文案和 A+ 页面结构。
```

## Platform Audit Mode

Use this when the task is only to inspect skill structure.

1. Run or manually perform the structure scan.
2. Compare against `references/platform-detection-rules.md`.
3. Return a short audit table:
   - path,
   - detected platform label,
   - evidence,
   - missing pieces,
   - recommended next action.

## Resources

- `scripts/scan_skill_repo.py`: deterministic local repository scanner that outputs skill inventory JSON.
- `references/platform-detection-rules.md`: how to classify Codex/OpenAI, WorkBuddy, and generic agent skills.
- `references/obsidian-index-schema.md`: required Markdown layout for the Obsidian index.
- `references/query-routing-rules.md`: how to answer "which skill should I use?"
- `references/skill-category-map.md`: business categories and known Amazon skill routes.
