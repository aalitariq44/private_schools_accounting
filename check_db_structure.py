#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بنية قاعدة البيانات
"""

import sqlite3

def check_database_structure():
    import config
    db_path = config.DATABASE_PATH
    print(f"مسار قاعدة البيانات: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        # عرض الجداول
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print("الجداول الموجودة:", tables)
        
        # فحص بنية جدول students
        if 'students' in tables:
            cur.execute("PRAGMA table_info(students)")
            students_columns = cur.fetchall()
            print("\nأعمدة جدول students:")
            for col in students_columns:
                print(f"  {col[1]} ({col[2]})")
        
        # فحص بنية جدول schools (إذا وجد)
        if 'schools' in tables:
            cur.execute("PRAGMA table_info(schools)")
            schools_columns = cur.fetchall()
            print("\nأعمدة جدول schools:")
            for col in schools_columns:
                print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    check_database_structure()
