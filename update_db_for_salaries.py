#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحديث قاعدة البيانات لإضافة جدول الرواتب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager
import logging

def create_salaries_table():
    """إنشاء جدول الرواتب"""
    try:
        with db_manager.get_cursor() as cursor:
            # إنشاء جدول الرواتب
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS salaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_type TEXT NOT NULL CHECK (staff_type IN ('teacher', 'employee')),
                    staff_id INTEGER NOT NULL,
                    staff_name TEXT NOT NULL,
                    base_salary DECIMAL(10,2) NOT NULL,
                    paid_amount DECIMAL(10,2) NOT NULL,
                    from_date DATE NOT NULL,
                    to_date DATE NOT NULL,
                    days_count INTEGER NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_time TIME NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # إنشاء فهارس للأداء
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_staff_type ON salaries(staff_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_staff_id ON salaries(staff_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_payment_date ON salaries(payment_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_from_date ON salaries(from_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_to_date ON salaries(to_date)")
            
            print("✅ تم إنشاء جدول الرواتب بنجاح")
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء جدول الرواتب: {e}")
        raise

def update_database():
    """تحديث قاعدة البيانات"""
    try:
        print("بدء تحديث قاعدة البيانات لإضافة جدول الرواتب...")
        
        # تهيئة قاعدة البيانات (سيتم إنشاء الجداول الأساسية إذا لم تكن موجودة)
        db_manager.initialize_database()
        
        # إنشاء جدول الرواتب
        create_salaries_table()
        
        print("✅ تم تحديث قاعدة البيانات بنجاح!")
        print("تم إضافة:")
        print("- جدول الرواتب (salaries)")
        print("- فهارس لتحسين الأداء")
        
        # التحقق من وجود الجداول
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("\nالجداول الموجودة:")
            for table in tables:
                print(f"  - {table['name']}")
                
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        logging.error(f"خطأ في تحديث قاعدة البيانات: {e}")

if __name__ == "__main__":
    update_database()
