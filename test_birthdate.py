#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إضافة عمود تاريخ الميلاد
"""

import sys
import os
from pathlib import Path

# إضافة مجلد الجذر إلى مسار Python
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

from core.database.connection import db_manager

def test_birthdate_column():
    """اختبار عمود تاريخ الميلاد"""
    print("اختبار عمود تاريخ الميلاد...")
    
    try:
        # التحقق من وجود العمود في بنية الجدول
        print("1. التحقق من بنية جدول الطلاب...")
        table_info = db_manager.get_table_info('students')
        column_names = [col['name'] for col in table_info]
        
        if 'birthdate' in column_names:
            print("✓ عمود تاريخ الميلاد موجود في جدول الطلاب")
        else:
            print("✗ عمود تاريخ الميلاد غير موجود في جدول الطلاب")
            return False
        
        # طباعة بنية الجدول
        print("\nبنية جدول الطلاب:")
        for col in table_info:
            print(f"  - {col['name']}: {col['type']}")
        
        # اختبار إدراج طالب جديد مع تاريخ الميلاد
        print("\n2. اختبار إدراج طالب جديد مع تاريخ الميلاد...")
        
        # أولاً التحقق من وجود مدرسة
        schools = db_manager.execute_query("SELECT id FROM schools LIMIT 1")
        if not schools:
            print("لا توجد مدارس، إنشاء مدرسة تجريبية...")
            school_id = db_manager.execute_insert(
                "INSERT INTO schools (name_ar, school_types) VALUES (?, ?)",
                ("مدرسة تجريبية", '["ابتدائية"]')
            )
        else:
            school_id = schools[0][0]
        
        # إدراج طالب تجريبي
        student_query = """
            INSERT INTO students (
                name, school_id, grade, section, gender, 
                birthdate, phone, total_fee, start_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        student_data = (
            "طالب تجريبي",
            school_id,
            "الأول الابتدائي",
            "أ",
            "ذكر",
            "2010-01-15",  # تاريخ الميلاد
            "07901234567",
            500000,
            "2024-09-01",
            "نشط"
        )
        
        student_id = db_manager.execute_insert(student_query, student_data)
        print(f"✓ تم إدراج طالب تجريبي بمعرف: {student_id}")
        
        # اختبار استعلام الطالب مع تاريخ الميلاد
        print("\n3. اختبار استعلام بيانات الطالب...")
        student = db_manager.execute_fetch_one(
            "SELECT id, name, birthdate FROM students WHERE id = ?",
            (student_id,)
        )
        
        if student:
            print(f"✓ بيانات الطالب:")
            print(f"  - المعرف: {student[0]}")
            print(f"  - الاسم: {student[1]}")
            print(f"  - تاريخ الميلاد: {student[2]}")
        else:
            print("✗ فشل في استعلام بيانات الطالب")
            return False
        
        # تنظيف - حذف الطالب التجريبي
        print("\n4. تنظيف البيانات التجريبية...")
        db_manager.execute_update("DELETE FROM students WHERE id = ?", (student_id,))
        print("✓ تم حذف الطالب التجريبي")
        
        print("\n✅ جميع الاختبارات نجحت! عمود تاريخ الميلاد يعمل بشكل صحيح.")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في الاختبار: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("=== اختبار إضافة عمود تاريخ الميلاد ===\n")
    
    try:
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        
        # تشغيل الاختبارات
        success = test_birthdate_column()
        
        if success:
            print("\n🎉 التطبيق جاهز! تم إضافة عمود تاريخ الميلاد بنجاح.")
        else:
            print("\n❌ يوجد مشكلة في إضافة عمود تاريخ الميلاد.")
            return 1
            
    except Exception as e:
        print(f"خطأ عام: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input("\nاضغط Enter للخروج...")
    sys.exit(exit_code)
