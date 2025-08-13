#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح عرض اسم المدرسة في صفحة تفاصيل الطالب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def test_student_data_query():
    """اختبار استعلام بيانات الطالب للتحقق من ترتيب الحقول"""
    
    print("اختبار استعلام بيانات الطالب...")
    
    query = """
        SELECT s.*, sc.name_ar as school_name, sc.address as school_address, sc.phone as school_phone
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LIMIT 1
    """
    
    result = db_manager.execute_query(query)
    
    if result:
        student_data = result[0]
        print(f"عدد الحقول المستلمة: {len(student_data)}")
        print(f"الحقل الأخير (school_phone): {student_data[-1]}")
        print(f"الحقل ما قبل الأخير (school_address): {student_data[-2]}")
        print(f"الحقل الثالث من النهاية (school_name): {student_data[-3]}")
        
        # طباعة جميع الحقول للتحقق
        print("\nجميع الحقول:")
        for i, field in enumerate(student_data):
            print(f"الحقل {i}: {field}")
            
    else:
        print("لم يتم العثور على بيانات طالب")

def test_schools_data():
    """اختبار بيانات المدارس"""
    
    print("\n" + "="*50)
    print("اختبار بيانات المدارس...")
    
    query = "SELECT id, name_ar, address, phone FROM schools"
    result = db_manager.execute_query(query)
    
    if result:
        print(f"عدد المدارس: {len(result)}")
        for school in result:
            print(f"المدرسة: الرقم={school[0]}, الاسم={school[1]}, العنوان={school[2]}, الهاتف={school[3]}")
    else:
        print("لم يتم العثور على بيانات مدارس")

if __name__ == "__main__":
    print("بدء اختبار إصلاح عرض اسم المدرسة")
    print("="*50)
    
    try:
        test_student_data_query()
        test_schools_data()
        
        print("\n" + "="*50)
        print("تم الانتهاء من الاختبار بنجاح!")
        
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
