@echo off
echo بدء تشغيل نظام حسابات المدارس الأهلية مع النسخ الاحتياطية...
echo.

REM التحقق من تثبيت المكتبات المطلوبة
echo فحص المكتبات المطلوبة...
python -c "import supabase; import storage3; print('جميع المكتبات مثبتة بشكل صحيح')" 2>nul
if errorlevel 1 (
    echo تحتاج إلى تثبيت مكتبات النسخ الاحتياطي أولاً...
    echo تشغيل install_backup_libs.bat...
    call install_backup_libs.bat
    echo.
)

echo تشغيل التطبيق...
python main.py

if errorlevel 1 (
    echo.
    echo حدث خطأ أثناء تشغيل التطبيق
    echo تحقق من ملف error.log للحصول على التفاصيل
)

echo.
pause
