# GitHub Upload Checklist

Use this checklist before pushing the repository.

## Must Commit

- `.gitignore`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `requirements.txt`
- `docs/`
- `scripts/check_portability.py`
- `skills/amazon-supplement-boundary-analysis/`
- `.kiro/` if skill definitions should travel with the repo
- `.vscode/settings.json` if intentionally empty/minimal

## Must Not Commit

- Raw Sif Excel workbooks
- Customer/user-provided input files
- Generated case reports unless intentionally sanitized as examples
- Scratch outputs
- Large PNG/HTML outputs from private runs
- Legacy output folders unless intentionally published

## Verify

```bash
python scripts/check_portability.py
git status --short --ignored
```

Confirm ignored data appears under ignored output paths, not as staged files.

