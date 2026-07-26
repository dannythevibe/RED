# RED Core Bulletproof PowerShell Launcher
# Ensures 100% UTF-8 encoding across Windows Console, PowerShell, and Python

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

chcp 65001 | Out-Null

Write-Host "==================================================" -ForegroundColor Red
Write-Host " RED CORE OS -- Launching in Full UTF-8 Mode..." -ForegroundColor Yellow
Write-Host " Creator: Daniel Iwayemi (Danny)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Red

# Launch RED Core Python entry point
python red.py
