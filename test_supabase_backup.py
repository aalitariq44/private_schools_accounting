#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام النسخ الاحتياطي على Supabase
"""

import sys
import os
from pathlib import Path

# إضافة المجلد الجذر للمشروع إلى مسار Python
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.backup.backup_manager import backup_manager

def test_supabase_connection():
    """اختبار الاتصال بـ Supabase"""
    print("=" * 50)
    print("اختبار اتصال Supabase")
    print("=" * 50)
    
    if backup_manager.supabase is None:
        print("❌ خطأ: عميل Supabase غير متاح")
        print("تحقق من:")
        print("1. تثبيت مكتبة supabase: pip install supabase")
        print("2. صحة إعدادات SUPABASE_URL و SUPABASE_KEY في config.py")
        return False
    
    try:
        # اختبار الاتصال بالتحقق من البكت
        buckets = backup_manager.supabase.storage.list_buckets()
        print(f"✅ تم الاتصال بـ Supabase بنجاح")
        print(f"عدد البكتات المتاحة: {len(buckets)}")
        
        # التحقق من بكت النسخ الاحتياطية
        bucket_exists = any(bucket.name == config.SUPABASE_BUCKET for bucket in buckets)
        if bucket_exists:
            print(f"✅ بكت النسخ الاحتياطية موجود: {config.SUPABASE_BUCKET}")
        else:
            print(f"⚠️ بكت النسخ الاحتياطية غير موجود، سيتم إنشاؤه: {config.SUPABASE_BUCKET}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال بـ Supabase: {e}")
        return False

def test_backup_creation():
    """اختبار إنشاء نسخة احتياطية"""
    print("\n" + "=" * 50)
    print("اختبار إنشاء نسخة احتياطية")
    print("=" * 50)
    
    # التحقق من وجود قاعدة البيانات
    if not config.DATABASE_PATH.exists():
        print(f"❌ قاعدة البيانات غير موجودة: {config.DATABASE_PATH}")
        print("سيتم إنشاء قاعدة بيانات تجريبية...")
        
        # إنشاء قاعدة بيانات تجريبية
        import sqlite3
        with sqlite3.connect(config.DATABASE_PATH) as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test_table (name) VALUES ('test data')")
            conn.commit()
        print("✅ تم إنشاء قاعدة بيانات تجريبية")
    
    # إنشاء نسخة احتياطية تجريبية
    success, message = backup_manager.create_backup("نسخة احتياطية تجريبية - اختبار النظام")
    
    if success:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ فشل في إنشاء النسخة الاحتياطية: {message}")
        return False

def test_list_backups():
    """اختبار جلب قائمة النسخ الاحتياطية"""
    print("\n" + "=" * 50)
    print("اختبار جلب قائمة النسخ الاحتياطية")
    print("=" * 50)
    
    backups = backup_manager.list_backups()
    
    if backups:
        print(f"✅ تم جلب {len(backups)} نسخة احتياطية")
        print("\nأحدث 3 نسخ احتياطية:")
        for i, backup in enumerate(backups[:3], 1):
            print(f"{i}. {backup['filename']}")
            print(f"   التاريخ: {backup['formatted_date']}")
            print(f"   الحجم: {backup['formatted_size']}")
            print()
        return True
    else:
        print("⚠️ لا توجد نسخ احتياطية أو فشل في جلب القائمة")
        return False

def main():
    """دالة رئيسية لتشغيل جميع الاختبارات"""
    print("🔄 بدء اختبار نظام النسخ الاحتياطي على Supabase")
    print(f"URL: {config.SUPABASE_URL}")
    print(f"البكت: {config.SUPABASE_BUCKET}")
    
    tests_passed = 0
    total_tests = 3
    
    # اختبار الاتصال
    if test_supabase_connection():
        tests_passed += 1
    
    # اختبار إنشاء نسخة احتياطية
    if test_backup_creation():
        tests_passed += 1
    
    # اختبار جلب قائمة النسخ
    if test_list_backups():
        tests_passed += 1
    
    # النتيجة النهائية
    print("\n" + "=" * 50)
    print("نتائج الاختبار")
    print("=" * 50)
    print(f"اجتاز {tests_passed} من {total_tests} اختبارات")
    
    if tests_passed == total_tests:
        print("🎉 جميع الاختبارات نجحت! نظام النسخ الاحتياطي يعمل بشكل صحيح")
    else:
        print("⚠️ بعض الاختبارات فشلت، تحقق من الأخطاء أعلاه")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
