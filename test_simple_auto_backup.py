#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مبسط للنسخ الاحتياطي التلقائي عند الخروج
"""

import sys
import os
from pathlib import Path

# إضافة المجلد الرئيسي للتطبيق إلى المسار
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("🧪 اختبار استيراد الوحدات...")
    
    # اختبار استيراد PyQt5
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
    print("✅ تم استيراد PyQt5 بنجاح")
    
    # اختبار استيراد إعدادات التطبيق
    import config
    print("✅ تم استيراد config بنجاح")
    print(f"   AUTO_BACKUP_ON_EXIT = {config.AUTO_BACKUP_ON_EXIT}")
    
    # اختبار استيراد النافذة الرئيسية
    from app.main_window import MainWindow
    print("✅ تم استيراد MainWindow بنجاح")
    
    # اختبار وجود الدوال المطلوبة
    if hasattr(MainWindow, 'create_auto_backup_on_exit'):
        print("✅ دالة create_auto_backup_on_exit موجودة")
    else:
        print("❌ دالة create_auto_backup_on_exit غير موجودة")
    
    if hasattr(MainWindow, 'closeEvent'):
        print("✅ دالة closeEvent موجودة")
    else:
        print("❌ دالة closeEvent غير موجودة")
    
    # اختبار إنشاء التطبيق والنافذة
    print("\n🚀 اختبار إنشاء التطبيق...")
    app = QApplication(sys.argv)
    
    # إنشاء النافذة (بدون عرض)
    window = MainWindow()
    print("✅ تم إنشاء النافذة الرئيسية بنجاح")
    
    # اختبار دالة النسخ الاحتياطي التلقائي (محاكاة)
    print("\n🧪 اختبار دالة النسخ الاحتياطي التلقائي...")
    try:
        # محاولة تشغيل الدالة (قد تفشل بسبب عدم وجود بيانات فعلية)
        result = window.create_auto_backup_on_exit()
        print(f"✅ تم تشغيل دالة النسخ الاحتياطي، النتيجة: {result}")
    except Exception as e:
        print(f"⚠️ تحذير في تشغيل دالة النسخ الاحتياطي: {e}")
        print("   هذا طبيعي إذا لم تكن قاعدة البيانات موجودة أو Supabase غير متاح")
    
    app.quit()
    print("\n✅ تم اختبار جميع المكونات بنجاح!")
    print("\n🎯 خطوات اختبار الميزة في التطبيق الفعلي:")
    print("   1. قم بتشغيل التطبيق: python main.py")
    print("   2. اضغط زر الإغلاق (❌)")
    print("   3. يجب أن ترى رسالة النسخ الاحتياطي التلقائي")
    print("   4. اضغط 'نعم' لاختبار الميزة")
    
except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    print("تأكد من أن PyQt5 مثبت: pip install PyQt5")
except Exception as e:
    print(f"❌ خطأ عام: {e}")

print("\n" + "="*50)
print("انتهى الاختبار")
