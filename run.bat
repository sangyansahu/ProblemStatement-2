@echo off
title AICTE APAAR Platform Launcher (Previous Workspace: Flask + Vue)
cd /d "%~dp0"

echo =========================================================================
echo   Launching AICTE APAAR Portal (Flask Backend + Vue 3 Frontend)...
echo =========================================================================
echo.

set PYTHON_CMD=python
if exist "C:\ProgramData\mambaforge\envs\projects_env\python.exe" (
    set PYTHON_CMD="C:\ProgramData\mambaforge\envs\projects_env\python.exe"
)

%PYTHON_CMD% run.py
pause
