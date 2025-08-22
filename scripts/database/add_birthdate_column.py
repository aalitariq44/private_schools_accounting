#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة عمود تاريخ الميلاد إلى جدول الطلاب
"""

import sys
import os
import logging
from pathlib import Path

# إضافة مجلد الجذر إلى مسار Python
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.insert(0, str(root_dir))

from core.database.connection import db_manager

def add_birthdate_column():
    """إضافة عمود تاريخ الميلاد إلى جدول الطلاب"""
    try:
        # التحقق من وجود العمود أولاً
        table_info = db_manager.get_table_info('students')
        column_names = [col['name'] for col in table_info]
        
        if 'birthdate' in column_names:
            print("عمود تاريخ الميلاد موجود بالفعل في جدول الطلاب")
            return True
        
        print("إضافة عمود تاريخ الميلاد إلى جدول الطلاب...")
        
        # إضافة العمود الجديد
        query = "ALTER TABLE students ADD COLUMN birthdate DATE"
        db_manager.execute_update(query)
        
        print("تم إضافة عمود تاريخ الميلاد بنجاح")
        logging.info("تم إضافة عمود birthdate إلى جدول students")
        
        return True
        
    except Exception as e:
        print(f"خطأ في إضافة عمود تاريخ الميلاد: {e}")
        logging.error(f"خطأ في إضافة عمود birthdate: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("بدء إضافة عمود تاريخ الميلاد...")
    
    try:
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        
        # إضافة العمود
        success = add_birthdate_column()
        
        if success:
            print("تم تنفيذ التحديث بنجاح!")
        else:
            print("فشل في تنفيذ التحديث")
            return 1
            
    except Exception as e:
        print(f"خطأ عام: {e}")
        logging.error(f"خطأ في تنفيذ السكريبت: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input("اضغط Enter للخروج...")
    sys.exit(exit_code)
