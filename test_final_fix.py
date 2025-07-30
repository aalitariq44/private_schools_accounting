#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح نافذة إضافة مجموعة الطلاب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)

def test_import():
    """اختبار استيراد النافذة"""
    try:
        from ui.pages.students.add_group_students_dialog import AddGroupStudentsDialog
        print("✓ تم استيراد نافذة إضافة مجموعة الطلاب بنجاح")
        return True
    except Exception as e:
        print(f"✗ فشل في استيراد النافذة: {e}")
        return False

def test_database_columns():
    """اختبار توافق أعمدة قاعدة البيانات"""
    try:
        import sqlite3
        db_path = os.path.join('data', 'database', 'schools.db')
        
        if not os.path.exists(db_path):
            print("✗ ملف قاعدة البيانات غير موجود")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص وجود الأعمدة المطلوبة
        cursor.execute("PRAGMA table_info(students)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = [
            'name', 'school_id', 'grade', 'section', 'phone',
            'total_fee', 'start_date', 'status', 'gender'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"✗ أعمدة مفقودة في جدول students: {missing_columns}")
            return False
        else:
            print("✓ جميع الأعمدة المطلوبة موجودة في جدول students")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ خطأ في فحص قاعدة البيانات: {e}")
        return False

def main():
    """الاختبار الرئيسي"""
    print("=== اختبار إصلاح نافذة إضافة مجموعة الطلاب ===\n")
    
    tests = [
        ("فحص استيراد النافذة", test_import),
        ("فحص توافق قاعدة البيانات", test_database_columns),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"جاري تشغيل: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"=== النتائج ===")
    print(f"نجح: {passed}/{total}")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! الإصلاحات مكتملة.")
        print("\nيمكنك الآن:")
        print("1. تشغيل التطبيق: python main.py")
        print("2. الانتقال إلى صفحة الطلاب")
        print("3. النقر على 'إضافة مجموعة طلاب'")
        print("4. إضافة الطلاب والحفظ")
    else:
        print("❌ هناك مشاكل تحتاج إلى إصلاح")

if __name__ == "__main__":
    main()
