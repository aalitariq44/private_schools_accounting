#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للنسخة التجريبية
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def test_student_limit():
    """اختبار حد الطلاب"""
    try:
        query = "SELECT COUNT(*) FROM students WHERE status != 'محذوف'"
        result = db_manager.execute_query(query)
        current_count = result[0][0] if result else 0
        
        print(f"عدد الطلاب الحالي: {current_count}")
        print(f"الحد الأقصى: 10")
        print(f"يمكن إضافة: {'نعم' if current_count < 10 else 'لا - تم الوصول للحد الأقصى'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"خطأ في فحص الطلاب: {e}")

def test_teacher_limit():
    """اختبار حد المعلمين"""
    try:
        query = "SELECT COUNT(*) FROM teachers"
        result = db_manager.execute_query(query)
        current_count = result[0][0] if result else 0
        
        print(f"عدد المعلمين الحالي: {current_count}")
        print(f"الحد الأقصى: 4")
        print(f"يمكن إضافة: {'نعم' if current_count < 4 else 'لا - تم الوصول للحد الأقصى'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"خطأ في فحص المعلمين: {e}")

def test_employee_limit():
    """اختبار حد الموظفين"""
    try:
        query = "SELECT COUNT(*) FROM employees"
        result = db_manager.execute_query(query)
        current_count = result[0][0] if result else 0
        
        print(f"عدد الموظفين الحالي: {current_count}")
        print(f"الحد الأقصى: 4")
        print(f"يمكن إضافة: {'نعم' if current_count < 4 else 'لا - تم الوصول للحد الأقصى'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"خطأ في فحص الموظفين: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("اختبار قيود النسخة التجريبية")
    print("=" * 50)
    
    test_student_limit()
    test_teacher_limit()  
    test_employee_limit()
    
    print("رقم الاتصال للنسخة الكاملة: 07710995922")
    print("=" * 50)
