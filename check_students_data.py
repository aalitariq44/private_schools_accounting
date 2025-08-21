#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.database.connection import db_manager
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    # فحص هيكل جدول students
    print("=== هيكل جدول students ===")
    columns = db_manager.execute_query('PRAGMA table_info(students)')
    for col in columns:
        print(f"  {col}")

    print("\n=== عينة من بيانات الطلاب ===")
    # فحص بعض العينات من البيانات
    students = db_manager.execute_query("""
        SELECT s.id, s.name, sc.name_ar as school_name,
               s.grade, s.section, s.gender,
               s.phone, s.status, s.start_date, s.total_fee,
               COALESCE(SUM(i.amount), 0) as total_paid
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LEFT JOIN installments i ON s.id = i.student_id
        GROUP BY s.id, s.name, sc.name_ar, s.grade, s.section, s.gender, s.phone, s.status, s.start_date, s.total_fee
        LIMIT 5
    """)
    
    for student in students:
        print(f"  ID: {student['id']}, Name: '{student['name']}', School: '{student['school_name']}'")
        print(f"    Grade: '{student['grade']}', Section: '{student['section']}', Gender: '{student['gender']}'")
        print(f"    Phone: '{student['phone']}', Status: '{student['status']}'")
        print(f"    Total Fee: {student['total_fee']}, Total Paid: {student['total_paid']}")
        print()

except Exception as e:
    print(f"خطأ: {e}")
    import traceback
    traceback.print_exc()
