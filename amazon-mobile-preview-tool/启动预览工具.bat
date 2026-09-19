@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 server.py %*
    goto :finished
)
where python >nul 2>nul
if not errorlevel 1 (
    python server.py %*
    goto :finished
)
echo 未找到 Python。请先安装 Python 3.10 或更新版本，并启用添加到 PATH。
:finished
if errorlevel 1 echo 启动失败。请查看上方提示。
pause
