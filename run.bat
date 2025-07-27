@echo off
echo تشغيل نظام حسابات المدارس الأهلية
echo =====================================

cd /d "%~dp0"

echo التحقق من Python...
python --version
if errorlevel 1 (
    echo خطأ: Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.8 أو أحدث
    pause
    exit /b 1
)

echo.
echo تشغيل اختبار النظام...
python test_system.py

echo.
echo هل تريد تشغيل التطبيق الرئيسي؟ (y/n)
set /p choice=
if /i "%choice%"=="y" (
    echo تشغيل التطبيق الرئيسي...
    python main.py
)

pause
