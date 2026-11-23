@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher 'py' not found.
    echo Install Python 3.12 for Windows and rerun P01.bat.
    pause
    exit /b 1
)
py -3.12 "%~dp0research_console.py"
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
    echo Research console ended with code %STATUS%.
    pause
)
exit /b %STATUS%
