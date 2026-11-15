Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  Starting All LoanWise Servers on Different Ports" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Bank (LoanWise Hybrid AI)
Write-Host "[1/3] Starting Bank (Hybrid AI) on Port 5000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\LoanWise'; `$env:PORT='5000'; python app.py"

# 2. Expert System
Write-Host "[2/3] Starting Expert System on Port 5001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\..\Expert System\loanwise'; `$env:PORT='5001'; python app.py"

# 3. Simple Expert System
Write-Host "[3/3] Starting Simple Expert System on Port 5050..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\..\Simple Expert System'; `$env:PORT='5050'; python app.py"

Write-Host "`nAll 3 servers have been launched in separate windows!" -ForegroundColor Yellow
Write-Host "Bank (Hybrid AI):     http://127.0.0.1:5000" -ForegroundColor White
Write-Host "Expert System:        http://127.0.0.1:5001" -ForegroundColor White
Write-Host "Simple Expert System: http://127.0.0.1:5050" -ForegroundColor White
