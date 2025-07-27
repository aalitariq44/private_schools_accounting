@echo off
echo تثبيت متطلبات نظام حسابات المدارس الأهلية
echo =======================================

cd /d "%~dp0"

echo التحقق من Python...
python --version
if errorlevel 1 (
    echo خطأ: Python غير مثبت
    echo يرجى تثبيت Python 3.8 أو أحدث من python.org
    pause
    exit /b 1
)

echo.
echo تثبيت المتطلبات...
echo.

echo تثبيت PyQt5...
python -m pip install PyQt5
if errorlevel 1 (
    echo تحذير: فشل في تثبيت PyQt5
)

echo.
echo تثبيت Pillow...
python -m pip install Pillow
if errorlevel 1 (
    echo تحذير: فشل في تثبيت Pillow
)

echo.
echo تثبيت python-dotenv...
python -m pip install python-dotenv
if errorlevel 1 (
    echo تحذير: فشل في تثبيت python-dotenv
)

echo.
echo تثبيت bcrypt...
python -m pip install bcrypt
if errorlevel 1 (
    echo تحذير: فشل في تثبيت bcrypt
)

echo.
echo تم الانتهاء من التثبيت!
echo يمكنك الآن تشغيل التطبيق باستخدام run.bat

pause
