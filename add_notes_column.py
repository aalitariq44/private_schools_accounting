#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة عمود الملاحظات لجدول students
"""
from core.database.connection import db_manager

# التحقق من وجود عمود notes
try:
    result = db_manager.execute_query('PRAGMA table_info(students)')
    columns = [col[1] for col in result]
    print('أعمدة جدول students:')
    print(columns)
    
    if 'notes' not in columns:
        print('\nإضافة عمود notes...')
        db_manager.execute_query('ALTER TABLE students ADD COLUMN notes TEXT')
        print('تم إضافة عمود notes بنجاح')
    else:
        print('\nعمود notes موجود بالفعل')
        
    # فحص البيانات الجديدة
    print('\nفحص البنية الجديدة:')
    result = db_manager.execute_query('PRAGMA table_info(students)')
    for i, col in enumerate(result):
        print(f'{i}: {col[1]} ({col[2]})')
        
except Exception as e:
    print(f'خطأ: {e}')
