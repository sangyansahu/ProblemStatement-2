# AICTE APAAR Platform PowerShell Launcher
Set-Location -Path $PSScriptRoot

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "  Starting AICTE APAAR Student Data Management & Verification Portal... " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""

$pythonExe = "python"
if (Test-Path "C:\ProgramData\mambaforge\envs\projects_env\python.exe") {
    $pythonExe = "C:\ProgramData\mambaforge\envs\projects_env\python.exe"
}

& $pythonExe run.py
