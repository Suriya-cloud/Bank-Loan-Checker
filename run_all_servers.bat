@echo off
echo =======================================================
echo   Starting All LoanWise Servers on Different Ports
echo =======================================================
echo.
echo [1/3] Starting Bank (Hybrid AI) on Port 5000...
start "LoanWise - Bank (Hybrid AI) [Port 5000]" cmd /k "cd /d "%~dp0LoanWise" && set PORT=5000 && python app.py"

echo [2/3] Starting Expert System on Port 5001...
start "LoanWise - Expert System [Port 5001]" cmd /k "cd /d "%~dp0..\Expert System\loanwise" && set PORT=5001 && python app.py"

echo [3/3] Starting Simple Expert System on Port 5050...
start "LoanWise - Simple Expert System [Port 5050]" cmd /k "cd /d "%~dp0..\Simple Expert System" && set PORT=5050 && python app.py"

echo.
echo =======================================================
echo All 3 servers launched in separate windows!
echo - Bank (Hybrid AI):        http://127.0.0.1:5000
echo - Expert System:           http://127.0.0.1:5001
echo - Simple Expert System:    http://127.0.0.1:5050
echo =======================================================
