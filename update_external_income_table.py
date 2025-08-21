#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث بنية جدول external_income لدعم الواردات العامة
"""

import sqlite3
import os

def update_external_income_table():
    """تحديث الجدول لدعم الواردات العامة"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== تحديث بنية جدول external_income ===")
        
        # حذف الجدول القديم وإنشاء جدول جديد
        cursor.execute("DROP TABLE IF EXISTS external_income")
        
        # إنشاء الجدول الجديد مع school_id قابل للإلغاء
        cursor.execute("""
            CREATE TABLE external_income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NULL,
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
        conn.close()
        
        print("✓ تم تحديث جدول external_income بنجاح")
        print("- school_id أصبح قابلاً للإلغاء (NULL) لدعم الواردات العامة")
        
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    update_external_income_table()
