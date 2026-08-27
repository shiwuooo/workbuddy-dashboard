@echo off
setlocal
set "SCRIPT=%~dp0collector.py"
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY ( echo 未找到 Python，请先安装 Python 3.8+ 并勾选“Add to PATH”。 & pause & exit /b 1 )

echo 首次采集一次数据...
"%PY%" "%SCRIPT%"

echo.
echo 注册“每天 09:00 自动采集”的 Windows 计划任务...
schtasks /create /tn "赚钱面板-每日采集" /tr "\"%PY%\" \"%SCRIPT%\"" /sc daily /st 09:00 /f
echo.
echo 完成。以后每天 09:00 自动更新 data.json，打开 index.html 即可看。
pause
