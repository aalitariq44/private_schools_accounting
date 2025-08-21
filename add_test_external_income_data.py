#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة بيانات تجريبية للواردات الخارجية
"""

import sqlite3
import os
from datetime import datetime, date

def add_test_external_income_data():
    """إضافة بيانات تجريبية"""
    db_path = 'data/database/schools.db'
    
    if not os.path.exists(db_path):
        print("ملف قاعدة البيانات غير موجود!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود مدارس
        cursor.execute("SELECT id FROM schools LIMIT 1")
        school = cursor.fetchone()
        school_id = school[0] if school else None
        
        # إضافة بيانات تجريبية
        test_data = [
            {
                'school_id': school_id,
                'income_type': 'تبرع نقدي من الأهالي',
                'description': 'تبرع لتطوير المختبرات العلمية',
                'amount': 5000.00,
                'category': 'التبرعات',
                'income_date': '2024-01-15',
                'notes': 'تبرع سخي من أولياء الأمور'
            },
            {
                'school_id': None,  # وارد عام
                'income_type': 'منحة حكومية',
                'description': 'دعم مالي للتعليم الرقمي',
                'amount': 15000.00,
                'category': 'إيجارات',
                'income_date': '2024-01-20',
                'notes': 'منحة من وزارة التربية والتعليم'
            },
            {
                'school_id': school_id,
                'income_type': 'إيرادات الحانوت المدرسي',
                'description': 'مبيعات الكتب والقرطاسية',
                'amount': 2500.00,
                'category': 'الحانوت',
                'income_date': '2024-01-25',
                'notes': 'إيرادات شهر يناير'
            },
            {
                'school_id': None,  # وارد عام آخر
                'income_type': 'رعاية شركة تقنية',
                'description': 'رعاية لمشروع التحول الرقمي',
                'amount': 8000.00,
                'category': 'أخرى',
                'income_date': '2024-02-01',
                'notes': 'رعاية من شركة محلية للتقنية'
            }
        ]
        
        insert_query = """
            INSERT INTO external_income 
            (school_id, income_type, description, amount, category, income_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        for data in test_data:
            cursor.execute(insert_query, (
                data['school_id'],
                data['income_type'],
                data['description'],
                data['amount'],
                data['category'],
                data['income_date'],
                data['notes']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ تم إضافة {len(test_data)} سجل تجريبي بنجاح")
        print("تتضمن البيانات:")
        print("- واردات مرتبطة بمدرسة محددة")
        print("- واردات عامة (غير مرتبطة بمدرسة)")
        print("- فئات متنوعة: التبرعات، الحانوت، إيجارات، أخرى")
        
    except Exception as e:
        print(f"خطأ: {e}")

if __name__ == "__main__":
    add_test_external_income_data()
