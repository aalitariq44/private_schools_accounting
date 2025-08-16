#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث جدول الرواتب لإضافة عمود school_id
"""

import sqlite3
import logging
from pathlib import Path
import sys
import os

# إضافة مسار المشروع إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def update_salaries_table():
    """تحديث جدول الرواتب لإضافة عمود school_id"""
    try:
        print("🔄 بدء تحديث جدول الرواتب...")
        
        with db_manager.get_cursor() as cursor:
            # التحقق من وجود العمود
            cursor.execute("PRAGMA table_info(salaries)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'school_id' not in column_names:
                print("➕ إضافة عمود school_id...")
                cursor.execute("""
                    ALTER TABLE salaries 
                    ADD COLUMN school_id INTEGER
                """)
                
                # إضافة فهرس للعمود الجديد
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_salaries_school_id 
                    ON salaries(school_id)
                """)
                
                print("✅ تم إضافة عمود school_id بنجاح")
            else:
                print("ℹ️ عمود school_id موجود بالفعل")
            
            # تحديث البيانات الموجودة لإضافة school_id
            print("🔄 تحديث البيانات الموجودة...")
            
            # تحديث رواتب المعلمين
            cursor.execute("""
                UPDATE salaries 
                SET school_id = (
                    SELECT school_id 
                    FROM teachers 
                    WHERE teachers.id = salaries.staff_id
                )
                WHERE staff_type = 'teacher' AND school_id IS NULL
            """)
            teacher_updates = cursor.rowcount
            
            # تحديث رواتب الموظفين
            cursor.execute("""
                UPDATE salaries 
                SET school_id = (
                    SELECT school_id 
                    FROM employees 
                    WHERE employees.id = salaries.staff_id
                )
                WHERE staff_type = 'employee' AND school_id IS NULL
            """)
            employee_updates = cursor.rowcount
            
            print(f"✅ تم تحديث {teacher_updates} راتب معلم")
            print(f"✅ تم تحديث {employee_updates} راتب موظف")
            print("🎉 تم تحديث جدول الرواتب بنجاح!")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في تحديث جدول الرواتب: {e}")
        logging.error(f"خطأ في تحديث جدول الرواتب: {e}")
        return False

if __name__ == "__main__":
    update_salaries_table()
