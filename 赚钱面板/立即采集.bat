@echo off
setlocal
set "SCRIPT=%~dp0collector.py"
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY ( echo 未找到 Python，请先安装 Python 3.8+ 并勾选“Add to PATH”。 & pause & exit /b 1 )

echo 正在采集资讯 + 同步 AI 每日解读...
"%PY%" "%SCRIPT%"
echo.
echo 完成。用 start.bat 打开面板查看（http://127.0.0.1:8000）。
pause
