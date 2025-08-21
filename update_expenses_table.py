#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تحديث جدول المصروفات لدعم المصروفات العامة
"""

import sqlite3
import logging
from core.database.connection import db_manager

def update_expenses_table():
    """تحديث جدول المصروفات لجعل school_id قابل للإلغاء"""
    try:
        # التحقق من وجود الجدول
        check_query = """
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='expenses'
        """
        result = db_manager.execute_query(check_query)
        
        if not result:
            print("جدول المصروفات غير موجود، سيتم إنشاؤه عند فتح الصفحة")
            return
        
        table_sql = result[0]['sql']
        print(f"بنية الجدول الحالية: {table_sql}")
        
        # التحقق إذا كان school_id قابل للإلغاء بالفعل
        if 'school_id INTEGER NULL' in table_sql or 'school_id INTEGER,' in table_sql:
            print("جدول المصروفات يدعم المصروفات العامة بالفعل")
            return
        
        # إنشاء جدول جديد مؤقت
        print("إنشاء جدول مؤقت بالبنية المحدثة...")
        temp_table_query = """
            CREATE TABLE expenses_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NULL,
                expense_type TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                expense_date DATE NOT NULL,
                description TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools(id)
            )
        """
        db_manager.execute_update(temp_table_query)
        
        # نسخ البيانات إلى الجدول المؤقت
        print("نسخ البيانات الموجودة...")
        copy_data_query = """
            INSERT INTO expenses_temp 
            (id, school_id, expense_type, amount, expense_date, description, notes, created_at, updated_at)
            SELECT id, school_id, expense_type, amount, expense_date, description, notes, created_at, updated_at
            FROM expenses
        """
        db_manager.execute_update(copy_data_query)
        
        # حذف الجدول القديم
        print("حذف الجدول القديم...")
        db_manager.execute_update("DROP TABLE expenses")
        
        # إعادة تسمية الجدول المؤقت
        print("إعادة تسمية الجدول الجديد...")
        db_manager.execute_update("ALTER TABLE expenses_temp RENAME TO expenses")
        
        print("✅ تم تحديث جدول المصروفات بنجاح لدعم المصروفات العامة")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث جدول المصروفات: {e}")
        logging.error(f"خطأ في تحديث جدول المصروفات: {e}")

def add_test_general_expenses():
    """إضافة بيانات تجريبية للمصروفات العامة"""
    try:
        test_expenses = [
            {
                'school_id': None,
                'expense_type': 'الصيانة',
                'amount': 150.00,
                'expense_date': '2025-01-15',
                'description': 'صيانة عامة للمباني',
                'notes': 'صيانة دورية شاملة'
            },
            {
                'school_id': None,
                'expense_type': 'المكتبية',
                'amount': 75.50,
                'expense_date': '2025-01-10',
                'description': 'أدوات مكتبية عامة',
                'notes': 'قرطاسية للإدارة العامة'
            }
        ]
        
        for expense in test_expenses:
            insert_query = """
                INSERT INTO expenses (school_id, expense_type, amount, expense_date, description, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            db_manager.execute_update(insert_query, (
                expense['school_id'],
                expense['expense_type'],
                expense['amount'],
                expense['expense_date'],
                expense['description'],
                expense['notes']
            ))
        
        print("✅ تم إضافة البيانات التجريبية للمصروفات العامة")
        
    except Exception as e:
        print(f"❌ خطأ في إضافة البيانات التجريبية: {e}")
        logging.error(f"خطأ في إضافة البيانات التجريبية: {e}")

if __name__ == "__main__":
    print("🔄 بدء تحديث جدول المصروفات...")
    update_expenses_table()
    add_test_general_expenses()
    print("✅ انتهاء التحديث")
