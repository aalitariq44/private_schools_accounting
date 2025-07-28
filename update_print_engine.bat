@echo off
echo تحديث نظام الطباعة...
echo.

echo تثبيت محرك الويب الحديث...
pip install PyQtWebEngine==5.15.6

echo.
echo تم تثبيت المحرك الحديث بنجاح!
echo.

echo اختبار النظام...
python test_print_engines.py

pause
