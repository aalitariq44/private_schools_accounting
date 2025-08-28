@echo off
echo ================================
echo   نظام التراخيص - إعداد سريع
echo ================================
echo.

echo 1. تثبيت المتطلبات الجديدة...
pip install cryptography>=41.0.0 requests>=2.31.0
echo.

echo 2. اختبار جمع معلومات الهارد وير...
python -c "from core.licensing.hardware_info import HardwareInfo; h = HardwareInfo(); info = h.get_all_hardware_info(); print('معلومات الهارد وير:'); [print(f'{k}: {v}') for k, v in info.items()]"
echo.

echo 3. إنشاء رمز تفعيل تجريبي...
python create_test_code.py
echo.

echo 4. تشغيل اختبار شامل للنظام...
python test_license.py
echo.

echo ================================
echo   تم الانتهاء من الإعداد!
echo ================================
echo.
echo الخطوات التالية:
echo 1. تشغيل create_licenses_table.sql في Supabase
echo 2. استخدام license_generator.py لإنشاء رموز تفعيل جديدة
echo 3. تشغيل التطبيق لاختبار نظام التراخيص
echo.
pause
