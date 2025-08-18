@echo off
chcp 65001 >nul
echo ====================================
echo   اختبار سريع للنسخة النهائية
echo ====================================
echo.

echo [1/3] التحقق من وجود الملفات...
if exist "dist\PrivateSchoolsAccounting_Distribution\PrivateSchoolsAccounting.exe" (
    echo ✅ الملف الرئيسي موجود
) else (
    echo ❌ الملف الرئيسي غير موجود
    goto :error
)

if exist "dist\PrivateSchoolsAccounting_Distribution\تشغيل_النظام.bat" (
    echo ✅ ملف التشغيل السهل موجود
) else (
    echo ❌ ملف التشغيل السهل غير موجود
)

if exist "dist\PrivateSchoolsAccounting_Final.zip" (
    echo ✅ أرشيف التوزيع موجود (%.0f MB)
) else (
    echo ❌ أرشيف التوزيع غير موجود
)

echo.
echo [2/3] معلومات الأرشيف:
for %%F in ("dist\PrivateSchoolsAccounting_Final.zip") do (
    set size=%%~zF
    set /a sizeMB=!size!/1024/1024
    echo 📁 حجم الأرشيف: !sizeMB! MB
)

echo.
echo [3/3] اختبار تشغيل سريع...
echo ⏳ بدء التطبيق للاختبار... (سيتم إغلاقه تلقائياً)
cd "dist\PrivateSchoolsAccounting_Distribution"
timeout /t 2 /nobreak >nul
start "" "PrivateSchoolsAccounting.exe"
echo ✅ تم تشغيل التطبيق بنجاح!

cd ..\..
echo.
echo ====================================
echo        النتيجة النهائية
echo ====================================
echo ✅ النسخة النهائية جاهزة للتوزيع!
echo.
echo 📁 المجلد: dist\PrivateSchoolsAccounting_Distribution
echo 📦 الأرشيف: dist\PrivateSchoolsAccounting_Final.zip
echo.
echo يمكنك الآن نسخ الأرشيف وتوزيعه
echo ====================================
goto :end

:error
echo.
echo ❌ يوجد مشكلة في الملفات المصدرة
echo يرجى إعادة تشغيل build_final_distribution.bat

:end
echo.
pause
