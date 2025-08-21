#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager
from core.printing.print_manager import print_students_list
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    print("=== اختبار طباعة قائمة الطلاب ===")
    
    # جلب بيانات الطلاب
    students_raw = db_manager.execute_query("""
        SELECT s.id, s.name, sc.name_ar as school_name,
               s.grade, s.section, s.gender,
               s.phone, s.status, s.start_date, s.total_fee,
               COALESCE(SUM(i.amount), 0) as total_paid
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LEFT JOIN installments i ON s.id = i.student_id
        GROUP BY s.id, s.name, sc.name_ar, s.grade, s.section, s.gender, s.phone, s.status, s.start_date, s.total_fee
        LIMIT 3
    """)
    
    print(f"جُلب {len(students_raw)} طلاب من قاعدة البيانات")
    
    # تحضير البيانات للطباعة
    students_for_print = []
    for student in students_raw:
        total_fee = student['total_fee'] if student['total_fee'] else 0
        total_paid = student['total_paid'] if student['total_paid'] else 0
        remaining = total_fee - total_paid
        
        student_data = {
            'id': student['id'],
            'name': student['name'] or "",  # التأكد من عدم وجود None
            'school_name': student['school_name'] or "",
            'grade': student['grade'] or "",
            'section': student['section'] or "",
            'gender': student['gender'] or "",
            'phone': student['phone'] or "",
            'status': student['status'] or "",
            'total_fee': f"{total_fee:,.0f} د.ع",
            'total_paid': f"{total_paid:,.0f} د.ع",
            'remaining': f"{remaining:,.0f} د.ع"
        }
        students_for_print.append(student_data)
        
        print(f"طالب {student['id']}: {student['name']}")
        print(f"  البيانات المحضرة: {student_data}")
        print()
    
    print("=== البيانات النهائية للطباعة ===")
    for i, student in enumerate(students_for_print):
        print(f"الطالب {i+1}:")
        for key, value in student.items():
            print(f"  {key}: '{value}'")
        print()
    
    # اختبار الطباعة
    print("=== اختبار الطباعة ===")
    filter_info = "اختبار - أول 3 طلاب"
    
    # طباعة القائمة (ستظهر نافذة المعاينة)
    print("سيتم فتح نافذة المعاينة...")
    print_students_list(students_for_print, filter_info, parent=None)
    
except Exception as e:
    print(f"خطأ: {e}")
    import traceback
    traceback.print_exc()
