@echo off
chcp 65001 > nul
echo تشغيل تطبيق محاسبة المدارس الأهلية...
echo.

cd /d "%~dp0"

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.8 أو أحدث
    pause
    exit /b 1
)

REM تثبيت المتطلبات إذا لم تكن موجودة
if not exist "venv\" (
    echo إنشاء بيئة افتراضية...
    python -m venv venv
)

echo تفعيل البيئة الافتراضية...
call venv\Scripts\activate

echo تثبيت المتطلبات...
pip install -r requirements.txt

echo تشغيل التطبيق...
python main.py

if errorlevel 1 (
    echo.
    echo حدث خطأ في تشغيل التطبيق
    pause
)

deactivate
