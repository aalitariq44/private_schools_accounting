@echo off
echo 🚀 تشغيل نظام إدارة الرواتب...
echo.

cd /d "c:\Users\athraa\Desktop\python ali\private_schools_accounting"

echo 📋 فحص الملفات...
if exist "ui\pages\salaries\salaries_page.py" (
    echo ✅ صفحة الرواتب موجودة
) else (
    echo ❌ صفحة الرواتب غير موجودة
)

if exist "ui\pages\salaries\add_salary_dialog.py" (
    echo ✅ نافذة إضافة الراتب موجودة
) else (
    echo ❌ نافذة إضافة الراتب غير موجودة
)

if exist "data\database\schools.db" (
    echo ✅ قاعدة البيانات موجودة
) else (
    echo ❌ قاعدة البيانات غير موجودة
)

echo.
echo 🔧 تشغيل التطبيق...
python main.py

pause
