#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص بيانات الطلاب لحل مشكلة الخلط في صفحة التفاصيل
"""
from core.database.connection import db_manager

try:
    # فحص بنية جدول students
    result = db_manager.execute_query('PRAGMA table_info(students)')
    print('بنية جدول students:')
    for i, col in enumerate(result):
        print(f'{i}: {col[1]} ({col[2]})')
    
    print('\n' + '='*50)
    
    # فحص بيانات طالب واحد
    students = db_manager.execute_query('SELECT * FROM students LIMIT 1')
    if students:
        student = students[0]
        print(f'مثال على بيانات طالب (العدد: {len(student)}):')
        for i, value in enumerate(student):
            print(f'{i}: {value}')
            
    print('\n' + '='*50)
    
    # فحص بيانات مع JOIN للمدارس
    query = """
        SELECT s.*, sc.name_ar as school_name, sc.name_en as school_name_en, 
               sc.address as school_address, sc.phone as school_phone, 
               sc.logo_path as school_logo_path
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LIMIT 1
    """
    result = db_manager.execute_query(query)
    if result:
        student_with_school = result[0]
        print(f'مثال على بيانات طالب مع معلومات المدرسة (العدد: {len(student_with_school)}):')
        for i, value in enumerate(student_with_school):
            print(f'{i}: {value}')
            
    print('\n' + '='*50)
    
    # فحص بيانات مدرسة
    schools = db_manager.execute_query('SELECT * FROM schools LIMIT 1')
    if schools:
        school = schools[0]
        print(f'مثال على بيانات مدرسة (العدد: {len(school)}):')
        for i, value in enumerate(school):
            print(f'{i}: {value}')

except Exception as e:
    print(f'خطأ: {e}')
