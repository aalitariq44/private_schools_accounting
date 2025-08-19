@echo off
chcp 65001 >nul
echo ================================================
echo      بناء التطبيق - توزيع احترافي
echo      Private Schools Accounting Distribution
echo ================================================
echo.

echo [1/5] تنظيف الملفات السابقة...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo ✓ تم تنظيف الملفات السابقة

echo.
echo [2/5] التحقق من متطلبات البناء...
python -c "import PyQt5; print('✓ PyQt5 موجود')" 2>nul || (echo ✗ PyQt5 غير موجود && pause && exit /b 1)
python -c "import reportlab; print('✓ ReportLab موجود')" 2>nul || (echo ✗ ReportLab غير موجود && pause && exit /b 1)
python -c "import supabase; print('✓ Supabase موجود')" 2>nul || (echo ✗ Supabase غير موجود && pause && exit /b 1)
python -c "import PyInstaller; print('✓ PyInstaller موجود')" 2>nul || (echo ✗ PyInstaller غير موجود && pause && exit /b 1)

echo.
echo [3/5] بناء التطبيق...
echo جاري إنشاء توزيع احترافي...
pyinstaller build_distribution.spec --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ فشل في بناء التطبيق
    echo يرجى مراجعة الأخطاء أعلاه
    pause
    exit /b 1
)

echo.
echo [4/5] تنظيم ملفات التوزيع...

set DIST_DIR=dist\PrivateSchoolsAccounting_Distribution

if not exist "%DIST_DIR%" (
    echo ✗ مجلد التوزيع غير موجود
    pause
    exit /b 1
)

:: إنشاء ملف README للتوزيع
echo إنشاء ملف README...
echo تطبيق محاسبة المدارس الخاصة > "%DIST_DIR%\README_التشغيل.txt"
echo =============================== >> "%DIST_DIR%\README_التشغيل.txt"
echo. >> "%DIST_DIR%\README_التشغيل.txt"
echo لتشغيل التطبيق: >> "%DIST_DIR%\README_التشغيل.txt"
echo انقر نقراً مزدوجاً على ملف PrivateSchoolsAccounting.exe >> "%DIST_DIR%\README_التشغيل.txt"
echo. >> "%DIST_DIR%\README_التشغيل.txt"
echo متطلبات النظام: >> "%DIST_DIR%\README_التشغيل.txt"
echo - Windows 10 أو أحدث >> "%DIST_DIR%\README_التشغيل.txt"
echo - 4GB ذاكرة عشوائية على الأقل >> "%DIST_DIR%\README_التشغيل.txt"
echo - 500MB مساحة فارغة >> "%DIST_DIR%\README_التشغيل.txt"
echo. >> "%DIST_DIR%\README_التشغيل.txt"
echo للدعم الفني: >> "%DIST_DIR%\README_التشغيل.txt"
echo البريد الإلكتروني: support@example.com >> "%DIST_DIR%\README_التشغيل.txt"

:: إنشاء ملف batch لتشغيل التطبيق
echo إنشاء ملف تشغيل...
echo @echo off > "%DIST_DIR%\تشغيل_التطبيق.bat"
echo chcp 65001 ^>nul >> "%DIST_DIR%\تشغيل_التطبيق.bat"
echo echo تشغيل تطبيق محاسبة المدارس الخاصة... >> "%DIST_DIR%\تشغيل_التطبيق.bat"
echo start "" "PrivateSchoolsAccounting.exe" >> "%DIST_DIR%\تشغيل_التطبيق.bat"

echo.
echo [5/5] فحص نتائج البناء...
if exist "%DIST_DIR%\PrivateSchoolsAccounting.exe" (
    echo ✓ الملف التنفيذي موجود
) else (
    echo ✗ الملف التنفيذي غير موجود
    pause
    exit /b 1
)

if exist "%DIST_DIR%\app" (
    echo ✓ مجلد الموارد موجود
) else (
    echo ✗ مجلد الموارد غير موجود
)

if exist "%DIST_DIR%\core" (
    echo ✓ مجلد النواة موجود
) else (
    echo ✗ مجلد النواة غير موجود
)

echo.
echo ================================================
echo           ✓ تم بناء التطبيق بنجاح!
echo ================================================
echo.
echo مكان التوزيع: %DIST_DIR%
echo.
echo محتويات التوزيع:
dir /b "%DIST_DIR%"
echo.
echo لاختبار التطبيق:
echo cd "%DIST_DIR%" && PrivateSchoolsAccounting.exe
echo.
echo أو استخدم ملف: تشغيل_التطبيق.bat
echo.
pause
