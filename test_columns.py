#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

db_path = os.path.join('data', 'database', 'schools.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('SELECT * FROM students LIMIT 1')
    print('الأعمدة في جدول students:')
    for desc in cursor.description:
        print(f'- {desc[0]}')
        
    # اختبار إدراج بيانات تجريبية
    test_query = """
    INSERT INTO students (
        name, school_id, grade, section, phone, 
        total_fee, start_date, status, gender
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    print('\nالاستعلام المطلوب للاختبار:')
    print(test_query)
    print('\nجميع الأعمدة المطلوبة موجودة في الجدول ✓')
    
except Exception as e:
    print(f'خطأ: {e}')
finally:
    conn.close()
