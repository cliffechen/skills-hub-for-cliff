@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  .venv\Scripts\python -m pip install pyinstaller
)
.venv\Scripts\python build_exe.py
pause
