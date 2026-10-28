@echo off
title AICTE APAAR Platform Launcher
cd /d "%~dp0"

echo =========================================================================
echo   Starting AICTE APAAR Student Data Management & Verification Portal...
echo =========================================================================
echo.

set PYTHON_CMD=python
if exist "C:\ProgramData\mambaforge\envs\projects_env\python.exe" (
    set PYTHON_CMD="C:\ProgramData\mambaforge\envs\projects_env\python.exe"
)

%PYTHON_CMD% run.py
pause
