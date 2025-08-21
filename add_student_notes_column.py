#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة عمود ملاحظات لجدول الطلاب
"""
import logging
from core.database.connection import db_manager

logging.basicConfig(level=logging.INFO)

def add_student_notes_column():
    """إضافة عمود الملاحظات لجدول الطلاب"""
    try:
        # فحص إذا كان العمود موجود بالفعل
        columns_info = db_manager.execute_query('PRAGMA table_info(students)')
        existing_columns = [column[1] for column in columns_info]
        
        if 'notes' in existing_columns:
            print("عمود الملاحظات موجود بالفعل في جدول الطلاب")
            return True
        
        # إضافة عمود الملاحظات
        print("إضافة عمود الملاحظات لجدول الطلاب...")
        db_manager.execute_query("""
            ALTER TABLE students 
            ADD COLUMN notes TEXT DEFAULT ''
        """)
        
        print("تم إضافة عمود الملاحظات بنجاح!")
        
        # التحقق من إضافة العمود
        columns_info = db_manager.execute_query('PRAGMA table_info(students)')
        print("\nهيكل جدول الطلاب بعد التحديث:")
        for column in columns_info:
            print(f"  {column[1]} - {column[2]}")
        
        return True
        
    except Exception as e:
        logging.error(f"خطأ في إضافة عمود الملاحظات: {e}")
        return False

if __name__ == "__main__":
    success = add_student_notes_column()
    if success:
        print("\n✅ تم تحديث قاعدة البيانات بنجاح")
    else:
        print("\n❌ فشل في تحديث قاعدة البيانات")
