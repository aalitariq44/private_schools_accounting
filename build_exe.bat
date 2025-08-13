@echo off
chcp 65001 >nul
title بناء تطبيق نظام محاسبة المدارس الأهلية

echo =====================================
echo    بناء تطبيق نظام محاسبة المدارس
echo =====================================
echo.

:: التحقق من وجود Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo خطأ: Python غير مثبت أو غير موجود في PATH
    pause
    exit /b 1
)

echo تحديث pip...
python -m pip install --upgrade pip

echo تثبيت PyInstaller...
pip install pyinstaller

echo تثبيت المتطلبات...
pip install -r requirements.txt

echo.
echo بدء عملية البناء...
echo هذا قد يستغرق عدة دقائق...
echo.

:: إنشاء مجلد البناء إذا لم يكن موجوداً
if not exist "dist" mkdir dist
if not exist "build" mkdir build

:: بناء التطبيق
pyinstaller --clean build.spec

if %errorlevel% eq 0 (
    echo.
    echo =====================================
    echo    تم البناء بنجاح!
    echo =====================================
    echo.
    echo يمكنك العثور على التطبيق في:
    echo %cd%\dist\PrivateSchoolsAccounting\
    echo.
    echo ملف التشغيل: PrivateSchoolsAccounting.exe
    echo.
    
    :: فتح مجلد الإخراج
    explorer "dist\PrivateSchoolsAccounting"
    
) else (
    echo.
    echo =====================================
    echo    حدث خطأ أثناء البناء!
    echo =====================================
    echo.
    echo يرجى مراجعة رسائل الخطأ أعلاه
)

echo.
pause
