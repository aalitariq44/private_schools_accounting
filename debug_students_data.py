#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager
import logging

logging.basicConfig(level=logging.DEBUG)

# تجربة البحث عن مشكلة في البيانات
try:
    print("=== فحص شامل لبيانات الطلاب ===")
    
    # جلب بيانات الطلاب من نفس الاستعلام المستخدم في الكود
    students_raw = db_manager.execute_query("""
        SELECT s.id, s.name, sc.name_ar as school_name,
               s.grade, s.section, s.gender,
               s.phone, s.status, s.start_date, s.total_fee,
               COALESCE(SUM(i.amount), 0) as total_paid
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LEFT JOIN installments i ON s.id = i.student_id
        WHERE 1=1
        GROUP BY s.id, s.name, sc.name_ar, s.grade, s.section, s.gender, s.phone, s.status, s.start_date, s.total_fee
        ORDER BY s.name
        LIMIT 10
    """)
    
    print(f"عدد الطلاب: {len(students_raw)}")
    print()
    
    # فحص كل طالب بحثاً عن قيم None
    for i, student in enumerate(students_raw):
        print(f"=== الطالب {i+1} ===")
        # تحويل sqlite3.Row إلى dict للفحص
        student_dict = dict(student)
        for key, value in student_dict.items():
            if value is None:
                print(f"  ⚠️  {key}: None")
            else:
                print(f"  ✓ {key}: '{value}'")
        print()
        
        # تحضير البيانات كما يتم في الكود الأصلي
        total_fee = student['total_fee'] if student['total_fee'] else 0
        total_paid = student['total_paid'] if student['total_paid'] else 0
        remaining = total_fee - total_paid
        
        student_data = {
            'id': student['id'],
            'name': student['name'] or "",  
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
        
        print("البيانات المحضرة:")
        for key, value in student_data.items():
            print(f"  {key}: '{value}'")
        print("-" * 50)

except Exception as e:
    print(f"خطأ: {e}")
    import traceback
    traceback.print_exc()
