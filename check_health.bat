@echo off
chcp 65001 >nul
echo =======================================
echo    فحص سلامة النظام قبل التصدير
echo =======================================
echo.

if exist "venv\Scripts\activate.bat" (
    echo تفعيل البيئة الافتراضية...
    call venv\Scripts\activate.bat
)

python check_system_health.py

echo.
echo =======================================
pause
