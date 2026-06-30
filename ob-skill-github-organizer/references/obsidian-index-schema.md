# Obsidian Index Schema

Use this structure when updating the user's Markdown index.

## Header

```markdown
# AMZ Skills 索引与备注

> 仓库：[cliffechen/skills-hub-for-cliff](https://github.com/cliffechen/skills-hub-for-cliff)
> 本索引最后同步：YYYY-MM-DD HH:mm +08:00
> 更新时间口径：优先按 GitHub 目录最近提交日期记录；部分目录属于批量提交，业务版本变化仍需看 `SKILL.md` 或 README。
```

## Required Sections

Keep these sections in this order:

1. `平台适配标签说明`
2. `WorkBuddy 标准结构参考`
3. `快速总览`
4. Optional suite-specific overview sections, such as `套件内子 Skills 索引`
5. Business category detail sections
6. `后续维护建议`

## Quick Overview Columns

```markdown
| 分类 | Skill | 一句话作用 | 最近更新 | 平台适配 | 备注 |
```

Rules:

- One row per skill directory.
- Keep Codex/OpenAI original and WorkBuddy version rows separate.
- Use GitHub links for skill names.
- Keep notes short; put details in the detailed card.

## Detail Card Fields

Use this shape for each skill:

```markdown
### skill-name

- 仓库路径：
- 一句话作用：
- 适合场景：
- 需要输入：
- 主要输出：
- 依赖工具：
- 结构扫描：
- 平台备注：
- 最近更新：
- 更新日志：
- 我的备注：
```

For sub-skills, shorter cards are acceptable, but always include path, purpose, structure, platform note, update date, and user note.

## Preservation Rules

- Preserve user-written notes unless they are clearly obsolete.
- If a skill already exists, update only fields that changed.
- If a new skill is found, add it to both quick overview and the relevant category.
- If a `-WB` variant is added, insert it next to its original skill.
- Do not delete old rows unless the user explicitly asks to remove archived skills.
