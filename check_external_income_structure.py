#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بنية جدول external_income
"""

import sqlite3
import os

def check_external_income_structure():
    """فحص بنية جدول external_income"""
    db_path = 'private_schools.db'
    
    # أيضا تحقق من مسار data/database
    if not os.path.exists(db_path):
        data_db_path = 'data/database/schools.db'
        if os.path.exists(data_db_path):
            db_path = data_db_path
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== الجداول الموجودة ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"جدول: {table[0]}")
        
        # تحقق من وجود الجدول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='external_income'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("\nجدول external_income غير موجود! سيتم إنشاؤه...")
            # إنشاء الجدول
            cursor.execute("""
                CREATE TABLE external_income (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_id INTEGER,
                    income_type TEXT NOT NULL,
                    description TEXT,
                    amount DECIMAL(10,2) NOT NULL,
                    category TEXT,
                    income_date DATE NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(id)
                )
            """)
            conn.commit()
            print("✓ تم إنشاء جدول external_income")
        
        print("\n=== بنية جدول external_income ===")
        cursor.execute("PRAGMA table_info(external_income)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"العمود: {col[1]}, النوع: {col[2]}, NOT NULL: {col[3]}, القيمة الافتراضية: {col[4]}")
        
        print("\n=== عينة من البيانات ===")
        cursor.execute("SELECT * FROM external_income LIMIT 3")
        sample_data = cursor.fetchall()
        
        if sample_data:
            # طباعة أسماء الأعمدة
            column_names = [description[0] for description in cursor.description]
            print("الأعمدة:", column_names)
            
            for row in sample_data:
                print("الصف:", row)
        else:
            print("لا توجد بيانات في الجدول")
        
        conn.close()
        
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    check_external_income_structure()
