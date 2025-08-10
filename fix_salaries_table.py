#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح جدول الرواتب - إضافة الأعمدة المفقودة
"""

import sqlite3
import os

def fix_salaries_table():
    """إصلاح بنية جدول الرواتب"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== بدء إصلاح جدول الرواتب ===")
        
        # فحص الأعمدة الموجودة
        cursor.execute("PRAGMA table_info(salaries)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print(f"الأعمدة الموجودة: {existing_columns}")
        
        # الأعمدة المطلوبة
        required_columns = [
            ('staff_name', 'TEXT'),
            ('staff_type', 'TEXT'), 
            ('paid_amount', 'DECIMAL(10,2)'),
            ('from_date', 'DATE'),
            ('to_date', 'DATE'),
            ('days_count', 'INTEGER')
        ]
        
        # إضافة الأعمدة المفقودة
        for column_name, column_type in required_columns:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE salaries ADD COLUMN {column_name} {column_type}")
                print(f"✓ تم إضافة عمود {column_name}")
        
        # تحديث البيانات الموجودة بقيم افتراضية
        cursor.execute("UPDATE salaries SET staff_type = employee_type WHERE staff_type IS NULL")
        cursor.execute("UPDATE salaries SET paid_amount = final_salary WHERE paid_amount IS NULL")
        cursor.execute("UPDATE salaries SET staff_name = 'غير محدد' WHERE staff_name IS NULL")
        
        print("✓ تم تحديث البيانات الافتراضية")
        
        # فحص النتيجة النهائية
        cursor.execute("PRAGMA table_info(salaries)")
        final_columns = cursor.fetchall()
        print("\n=== بنية الجدول النهائية ===")
        for col in final_columns:
            print(f"العمود: {col[1]}, النوع: {col[2]}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ تم إصلاح جدول الرواتب بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح جدول الرواتب: {e}")
        return False

if __name__ == "__main__":
    fix_salaries_table()
