#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح إضافة الأقساط
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def test_installment_insert():
    """اختبار إدخال قسط جديد"""
    try:
        # تهيئة قاعدة البيانات
        db_manager.initialize_database()
        print("تم تهيئة قاعدة البيانات بنجاح")
        
        # الحصول على معلومات الجدول
        table_info = db_manager.get_table_info('installments')
        print("\nهيكل جدول installments:")
        for column in table_info:
            print(f"  {column['name']}: {column['type']} {'NOT NULL' if column['notnull'] else ''}")
        
        # محاولة إدخال قسط تجريبي
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        query = """
            INSERT INTO installments (student_id, amount, payment_date, payment_time, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (1, 500.0, current_date, current_time, "قسط تجريبي")
        
        result = db_manager.execute_query(query, params)
        print("\nتم إدخال قسط تجريبي بنجاح!")
        return True
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    success = test_installment_insert()
    if success:
        print("\n✅ تم إصلاح المشكلة بنجاح!")
    else:
        print("\n❌ لا تزال هناك مشكلة في الإدخال")