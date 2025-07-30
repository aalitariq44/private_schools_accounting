#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بنية جدول الطلاب
"""

import sqlite3
import os

def check_students_table():
    """فحص بنية جدول الطلاب"""
    db_path = os.path.join(os.path.dirname(__file__), "data", "database", "schools.db")
    
    if not os.path.exists(db_path):
        print(f"ملف قاعدة البيانات غير موجود: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص بنية جدول students
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        
        print("بنية جدول students:")
        print("-" * 50)
        for col in columns:
            print(f"العمود: {col[1]:<20} النوع: {col[2]:<15} NOT NULL: {col[3]}")
        
        # فحص الأعمدة الموجودة التي تحتوي على كلمة name
        print("\nالأعمدة التي تحتوي على كلمة 'name':")
        name_columns = [col[1] for col in columns if 'name' in col[1].lower()]
        for col in name_columns:
            print(f"- {col}")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ في فحص قاعدة البيانات: {e}")

if __name__ == "__main__":
    check_students_table()
