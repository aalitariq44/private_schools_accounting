@echo off
chcp 65001 >nul
title تحضير وبناء تطبيق نظام محاسبة المدارس الأهلية

echo =====================================
echo   تحضير وبناء التطبيق - الإصدار الكامل
echo =====================================
echo.

:: التحقق من وجود Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ خطأ: Python غير مثبت أو غير موجود في PATH
    echo يرجى تثبيت Python 3.8 أو أحدث من: https://python.org
    pause
    exit /b 1
)

echo 📦 تحديث أدوات Python...
python -m pip install --upgrade pip setuptools wheel

echo 📦 تثبيت المتطلبات الأساسية...
pip install pyinstaller pillow

echo 📦 تثبيت متطلبات التطبيق...
pip install -r requirements.txt

echo.
echo 🔧 تحضير المشروع للبناء...
python prepare_build.py

if %errorlevel% neq 0 (
    echo ❌ فشل في تحضير المشروع
    pause
    exit /b 1
)

echo.
echo 🏗️ بدء عملية البناء...
echo ⏱️ هذا قد يستغرق 5-10 دقائق حسب سرعة الجهاز...
echo.

:: بناء التطبيق
pyinstaller --clean --noconfirm build.spec

if %errorlevel% eq 0 (
    echo.
    echo =====================================
    echo        ✅ تم البناء بنجاح!
    echo =====================================
    echo.
    echo 📁 موقع التطبيق:
    echo %cd%\dist\PrivateSchoolsAccounting\
    echo.
    echo 🚀 ملف التشغيل: PrivateSchoolsAccounting.exe
    echo.
    echo 📋 معلومات إضافية:
    echo - التطبيق يعمل على جميع أجهزة Windows
    echo - لا يحتاج إلى تثبيت Python على الجهاز المستهدف  
    echo - يمكن نسخ المجلد كاملاً إلى أي جهاز آخر
    echo.
    
    :: إنشاء ملف تعليمات
    echo إنشاء ملف التعليمات...
    (
        echo تعليمات تشغيل نظام محاسبة المدارس الأهلية
        echo ==========================================
        echo.
        echo 1. تأكد من وجود المجلد كاملاً في نفس المكان
        echo 2. قم بتشغيل ملف PrivateSchoolsAccounting.exe
        echo 3. إذا ظهرت رسالة من Windows Defender، اختر "Run anyway"
        echo 4. للنسخ إلى جهاز آخر، انسخ المجلد كاملاً
        echo.
        echo متطلبات النظام:
        echo - Windows 7 أو أحدث
        echo - 4 جيجا رام على الأقل
        echo - 500 ميجا مساحة فارغة
        echo.
        echo في حالة وجود مشاكل:
        echo - تأكد من إغلاق برامج الحماية مؤقتاً
        echo - قم بتشغيل التطبيق كمدير ^(Run as Administrator^)
        echo - تأكد من اتصال الإنترنت للاتصال بقاعدة البيانات
    ) > "dist\PrivateSchoolsAccounting\تعليمات التشغيل.txt"
    
    :: فتح مجلد الإخراج
    echo 📂 فتح مجلد التطبيق...
    explorer "dist\PrivateSchoolsAccounting"
    
) else (
    echo.
    echo =====================================
    echo       ❌ حدث خطأ أثناء البناء!
    echo =====================================
    echo.
    echo 🔍 الأخطاء المحتملة:
    echo - نقص في المساحة التخزينية
    echo - تعارض مع برامج الحماية  
    echo - ملفات مفقودة من المشروع
    echo.
    echo 💡 الحلول المقترحة:
    echo 1. تأكد من وجود مساحة فارغة كافية ^(على الأقل 2 جيجا^)
    echo 2. أغلق برامج الحماية مؤقتاً
    echo 3. قم بتشغيل الأمر كمدير
    echo 4. تأكد من عدم وجود ملفات مفتوحة من المشروع
)

echo.
echo 🏁 انتهت العملية
pause
