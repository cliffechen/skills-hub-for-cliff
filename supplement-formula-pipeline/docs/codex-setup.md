# Agent 启动说明（详细版）

> 本文件提供各 agent 平台的详细启动说明。快速启动请参考 `docs/agent-setup.md`。

Use this guide after cloning the repository on a new machine.

## 1. Install Python Dependencies

```bash
python -m pip install -r requirements.txt
```

Required runtime packages:

- `openpyxl` for Sif Excel parsing.
- `Pillow` for PNG radar chart rendering.

## 2. Use the Repo-Local Skill

The reusable skill lives in:

```text
skills/amazon-supplement-boundary-analysis/SKILL.md
```

When asking the agent to run this workflow, reference the repo-local skill explicitly:

```text
Use the repo-local skill at skills/amazon-supplement-boundary-analysis to analyze this Amazon US supplement case.
```

This keeps the GitHub project self-contained and avoids depending on a machine-specific global skills directory.

## 3. Optional: Install the Skill Globally for Codex

If you want Codex to discover the skill automatically on one machine, copy the folder into your Codex skills directory:

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R skills/amazon-supplement-boundary-analysis "$CODEX_HOME/skills/"
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$env:CODEX_HOME\skills"
Copy-Item -Recurse -Force "skills\amazon-supplement-boundary-analysis" "$env:CODEX_HOME\skills\"
```

If `CODEX_HOME` is not configured, use the Codex app's configured skills location.

### Claude Code

Claude Code discovers skills and project instructions via `AGENTS.md` in the project root. No global install is needed -- simply ensure `AGENTS.md` and `skills/` are present in the repo. Claude Code reads them automatically when you start a session in the project directory.

### QoderWork

Select the project folder in QoderWork to auto-load `AGENTS.md` and the repo-local skill definitions. No global install step is required.

## 4. Create a Case Workspace

```bash
python skills/amazon-supplement-boundary-analysis/scripts/create_case_workspace.py \
  --asin B0GKPTBN59 \
  --core-ingredient "C15 Pentadecanoic Acid" \
  --sif-excel "/path/to/Sif.xlsx"
```

Outputs go under:

```text
outputs/cases/{ASIN}-{core-ingredient}-{yyyyMMdd-HHmmss}/
```

The original Excel file is copied; it should not be committed to Git.

## 5. Run Portability Check

```bash
python scripts/check_portability.py
```

The check verifies:

- `AGENTS.md` and `CLAUDE.md` exist.
- Skill files exist.
- Required scripts and templates exist.
- Documentation files exist (including `docs/agent-setup.md`).
- Python dependencies are importable.
- Radar generation works in `outputs/scratch/`.
- Skill metadata is structurally valid.

## 6. Git Hygiene

Do not commit:

- `outputs/cases/*`
- `outputs/inputs/*`
- `outputs/scratch/*`
- `outputs/legacy/*`
- Raw Sif Excel files.

Commit:

- `skills/`
- `docs/`
- `scripts/`
- `requirements.txt`
- `.gitignore`
- `README.md`

