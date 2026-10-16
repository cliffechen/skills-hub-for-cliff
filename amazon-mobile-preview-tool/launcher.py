"""Entry point for the portable Windows exe (see build_exe.py).

- Tool pages (index.html / *.js / *.css) are read from inside the exe.
- Project data lives in a "data" folder next to the exe, so it survives
  restarts and travels with the exe when the folder is copied.
- On first run the bundled example project is copied into that folder.
- Ports blocked for any reason are skipped (see make_server below).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import server

if getattr(sys, "frozen", False):
    BUNDLE = Path(sys._MEIPASS)
    EXE_DIR = Path(sys.executable).resolve().parent
else:
    BUNDLE = EXE_DIR = Path(__file__).resolve().parent

server.ROOT = BUNDLE


def make_server(store, port: int, auto_port: bool = True):
    """Like server.make_server, but skips ports that fail for any reason.

    On some PCs ports are reserved by Hyper-V / WSL / Docker or blocked by
    security software (WinError 10013), which server.make_server treats as
    fatal. Here every failing candidate is skipped, and as a last resort the
    OS picks a free port.
    """
    if not auto_port:
        try:
            return server.PreviewServer(("127.0.0.1", port), store)
        except OSError as error:
            print(f"端口 {port} 不可用：{error}", file=sys.stderr)
            raise
    errors = []
    for candidate in [*range(port, min(port + 30, 65536)), 0]:
        try:
            return server.PreviewServer(("127.0.0.1", candidate), store)
        except OSError as error:
            errors.append(f"{candidate}: {error}")
    print("端口尝试失败：\n  " + "\n  ".join(errors[-3:]), file=sys.stderr)
    raise OSError("No available local port")


server.make_server = make_server


def seed_data(data_dir: Path) -> None:
    sample = BUNDLE / "data"
    if data_dir.exists() or not sample.is_dir() or sample.resolve() == data_dir.resolve():
        return
    shutil.copytree(sample, data_dir)


def main() -> int:
    if not any(arg == "--data-dir" or arg.startswith("--data-dir=") for arg in sys.argv[1:]):
        data_dir = EXE_DIR / "data"
        seed_data(data_dir)
        sys.argv[1:1] = ["--data-dir", str(data_dir)]
    try:
        return server.main() or 0
    except SystemExit as exit_:
        if exit_.code not in (0, None) and getattr(sys, "frozen", False):
            input("\n按回车键关闭窗口……")
        raise


if __name__ == "__main__":
    sys.exit(main())
