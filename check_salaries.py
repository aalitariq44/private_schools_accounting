#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_salaries_database():
    """فحص قاعدة البيانات وتفاصيل جدول الرواتب"""
    
    db_path = os.path.join("data", "database", "schools.db")
    
    if not os.path.exists(db_path):
        print("❌ ملف قاعدة البيانات غير موجود")
        return
    
    print(f"✅ ملف قاعدة البيانات موجود: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # فحص الجداول الموجودة
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n📋 الجداول الموجودة: {[table[0] for table in tables]}")
        
        # فحص جدول الرواتب
        if 'salaries' in [table[0] for table in tables]:
            print("\n✅ جدول الرواتب موجود")
            
            # فحص بنية الجدول
            cursor.execute("PRAGMA table_info(salaries);")
            columns = cursor.fetchall()
            print("\n📊 أعمدة جدول الرواتب:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # فحص عدد السجلات
            cursor.execute("SELECT COUNT(*) FROM salaries;")
            count = cursor.fetchone()[0]
            print(f"\n📈 عدد سجلات الرواتب: {count}")
            
        else:
            print("\n❌ جدول الرواتب غير موجود")
            
        # فحص جدول المعلمين
        cursor.execute("SELECT COUNT(*) FROM teachers;")
        teachers_count = cursor.fetchone()[0]
        print(f"\n👨‍🏫 عدد المعلمين: {teachers_count}")
        
        # فحص جدول الموظفين
        cursor.execute("SELECT COUNT(*) FROM employees;")
        employees_count = cursor.fetchone()[0]
        print(f"👥 عدد الموظفين: {employees_count}")
        
    except Exception as e:
        print(f"❌ خطأ في فحص قاعدة البيانات: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_salaries_database()
