@echo off
echo تثبيت المتطلبات الجديدة لنظام التراخيص...
echo.

echo تثبيت cryptography...
pip install cryptography>=41.0.0

echo.
echo تثبيت requests...
pip install requests>=2.31.0

echo.
echo تحديث جميع المتطلبات...
pip install -r requirements.txt --upgrade

echo.
echo تم الانتهاء من تثبيت المتطلبات الجديدة!
pause
