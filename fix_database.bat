@echo off
chcp 65001 > nul
echo 🔧 إصلاح مشاكل قيود قاعدة البيانات
echo =====================================
echo.

echo ⚠️  تحذير: سيتم حذف قاعدة البيانات الحالية وإعادة إنشائها
echo هل تريد المتابعة؟ (y/n)
set /p choice=

if /i "%choice%"=="y" (
    echo.
    echo 🚀 بدء عملية الإصلاح...
    python recreate_db_simple.py
    
    if %errorlevel%==0 (
        echo.
        echo 🧪 تشغيل اختبارات التحقق...
        python test_fixed_database.py
        
        if %errorlevel%==0 (
            echo.
            echo ✅ تم إصلاح قاعدة البيانات بنجاح!
            echo 📋 بيانات تسجيل الدخول الافتراضية:
            echo    المستخدم: admin
            echo    كلمة المرور: admin123
            echo.
            echo يمكنك الآن تشغيل التطبيق بدون مشاكل.
        ) else (
            echo.
            echo ⚠️  تم الإصلاح ولكن هناك مشاكل في الاختبارات
        )
    ) else (
        echo.
        echo ❌ فشل في إصلاح قاعدة البيانات
    )
) else (
    echo تم إلغاء العملية.
)

echo.
echo اضغط أي مفتاح للخروج...
pause > nul
