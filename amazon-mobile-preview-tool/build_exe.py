"""Build the portable Windows exe: dist/AmazonMobilePreview.exe.

Usage (Windows): double-click 打包exe.bat, or run `python build_exe.py`
with PyInstaller installed. Only the bundled example project is packed;
personal projects under data/ stay out of the exe.
"""
from __future__ import annotations

import os
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent
SAMPLE = Path("data") / "示例 · 现有设计稿"
STATIC = ("index.html", "app.js", "style.css", "preview.js", "preview.css", "slicer.js")


def main() -> None:
    os.chdir(ROOT)
    args = ["--noconfirm", "--clean", "--onefile", "--console", "--name", "AmazonMobilePreview"]
    for name in STATIC:
        args += ["--add-data", f"{name}{os.pathsep}."]
    args += ["--add-data", f"{SAMPLE}{os.pathsep}{SAMPLE}"]
    PyInstaller.__main__.run([*args, "launcher.py"])


if __name__ == "__main__":
    main()
