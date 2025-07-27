@echo off
cd /d "c:\Users\athraa\Desktop\python ali\private_schools_accounting"
echo تشغيل اختبار Supabase المفصل...
python test_supabase_detailed.py
echo.
echo ============================================
echo.
echo تشغيل اختبار نظام النسخ الاحتياطي...
python test_supabase_backup.py
echo.
pause
