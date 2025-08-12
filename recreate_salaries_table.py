#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعادة إنشاء جدول الرواتب بالهيكل الصحيح
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.database.connection import db_manager
import logging

# إعداد نظام التسجيل
logging.basicConfig(level=logging.INFO)

def recreate_salaries_table():
    """إعادة إنشاء جدول الرواتب"""
    try:
        with db_manager.get_cursor() as cursor:
            print("جاري حذف جدول الرواتب القديم...")
            
            # حذف الجدول القديم
            cursor.execute("DROP TABLE IF EXISTS salaries")
            
            print("جاري إنشاء جدول الرواتب الجديد...")
            
            # إنشاء الجدول الجديد
            cursor.execute("""
                CREATE TABLE salaries (
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
            
            print("جاري إنشاء الفهارس...")
            
            # إنشاء الفهارس
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_staff_type ON salaries(staff_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_staff_id ON salaries(staff_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_payment_date ON salaries(payment_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_from_date ON salaries(from_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salaries_to_date ON salaries(to_date)")
            
            print("✅ تم إعادة إنشاء جدول الرواتب بنجاح!")
            
            # التحقق من الجدول
            cursor.execute("PRAGMA table_info(salaries)")
            columns = cursor.fetchall()
            print("أعمدة جدول الرواتب:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
                
    except Exception as e:
        print(f"❌ خطأ في إعادة إنشاء جدول الرواتب: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print('إعادة إنشاء جدول الرواتب...')
    success = recreate_salaries_table()
    
    if success:
        print('✅ تمت العملية بنجاح!')
    else:
        print('❌ فشل في العملية')
