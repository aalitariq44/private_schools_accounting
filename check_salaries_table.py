#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بنية جدول الرواتب
"""

import sqlite3
import os

def check_salaries_table():
    """فحص بنية جدول الرواتب"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== بنية جدول salaries ===")
        cursor.execute("PRAGMA table_info(salaries)")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"العمود: {col[1]}, النوع: {col[2]}, NULL: {col[3]}, افتراضي: {col[4]}")
        else:
            print("الجدول غير موجود أو فارغ")
        
        # فحص بعض البيانات إذا كانت موجودة
        cursor.execute("SELECT COUNT(*) FROM salaries")
        count = cursor.fetchone()[0]
        print(f"\nإجمالي السجلات: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM salaries LIMIT 3")
            sample_data = cursor.fetchall()
            print("عينة من البيانات:")
            for row in sample_data:
                print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ في فحص قاعدة البيانات: {e}")

if __name__ == "__main__":
    check_salaries_table()
