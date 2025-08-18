@echo off
chcp 65001 >nul
echo ========================================
echo     نظام محاسبة المدارس الخاصة
echo      إنشاء النسخة النهائية للتوزيع
echo ========================================
echo.

echo [1/6] تنظيف الملفات السابقة...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo تم تنظيف الملفات السابقة ✓

echo.
echo [2/6] التحقق من البيئة الافتراضية...
if not exist "venv" (
    echo إنشاء البيئة الافتراضية...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo تم تفعيل البيئة الافتراضية ✓

echo.
echo [3/6] تحديث pip وتثبيت المتطلبات...
python -m pip install --upgrade pip
pip install -r requirements_final.txt
echo تم تثبيت المتطلبات ✓

echo.
echo [4/6] بناء التطبيق النهائي...
pyinstaller build_final.spec --clean --noconfirm
echo تم بناء التطبيق ✓

echo.
echo [5/6] إنشاء الملفات الإضافية للتوزيع...

REM إنشاء ملف التشغيل
echo @echo off > "dist\PrivateSchoolsAccounting_Distribution\تشغيل_النظام.bat"
echo chcp 65001 ^>nul >> "dist\PrivateSchoolsAccounting_Distribution\تشغيل_النظام.bat"
echo start "" "PrivateSchoolsAccounting.exe" >> "dist\PrivateSchoolsAccounting_Distribution\تشغيل_النظام.bat"

REM إنشاء دليل الاستخدام
(
echo نظام محاسبة المدارس الخاصة
echo ===============================
echo.
echo طريقة التشغيل:
echo 1. انقر نقراً مزدوجاً على ملف "تشغيل_النظام.bat"
echo 2. أو انقر نقراً مزدوجاً على "PrivateSchoolsAccounting.exe"
echo.
echo الملفات المطلوبة:
echo - يجب أن تبقى جميع الملفات في نفس المجلد
echo - لا تحذف أي ملف من المجلد
echo - احتفظ بنسخة احتياطية من مجلد data
echo.
echo للدعم الفني:
echo اتصل بمطور النظام
) > "dist\PrivateSchoolsAccounting_Distribution\اقرأني_أولاً.txt"

REM نسخ ملفات إضافية مهمة
if exist "README.md" copy "README.md" "dist\PrivateSchoolsAccounting_Distribution\"
if exist "TRIAL_VERSION_README.md" copy "TRIAL_VERSION_README.md" "dist\PrivateSchoolsAccounting_Distribution\"

echo تم إنشاء الملفات الإضافية ✓

echo.
echo [6/6] إنشاء أرشيف للتوزيع...
cd dist
if exist "PrivateSchoolsAccounting_Final.zip" del "PrivateSchoolsAccounting_Final.zip"
powershell Compress-Archive -Path "PrivateSchoolsAccounting_Distribution" -DestinationPath "PrivateSchoolsAccounting_Final.zip"
cd ..
echo تم إنشاء أرشيف التوزيع ✓

echo.
echo ========================================
echo          تم الانتهاء بنجاح!
echo ========================================
echo.
echo المجلد: dist\PrivateSchoolsAccounting_Distribution
echo الأرشيف: dist\PrivateSchoolsAccounting_Final.zip
echo.
echo يمكنك الآن توزيع النظام على أي حاسوب ويندوز
echo.
pause
