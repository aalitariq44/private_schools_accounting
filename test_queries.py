#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager
import logging

def test_queries():
    """اختبار الاستعلامات للتأكد من عدم وجود أخطاء"""
    
    try:
        # اختبار استعلام الطلاب
        print("=== اختبار استعلام الطلاب ===")
        students_query = """
            SELECT s.id, s.full_name, sc.name_ar as school_name,
                   s.grade, s.section, s.gender,
                   s.phone, s.status, s.start_date
            FROM students s
            LEFT JOIN schools sc ON s.school_id = sc.id
            LIMIT 5
        """
        result = db_manager.execute_query(students_query)
        print(f"استعلام الطلاب نجح - عدد النتائج: {len(result)}")
        
        # اختبار استعلام الأقساط
        print("\n=== اختبار استعلام الأقساط ===")
        installments_query = """
            SELECT i.id, s.name as student_name, sc.name_ar as school_name,
                   i.amount, i.payment_date, i.payment_time, i.notes
            FROM installments i
            LEFT JOIN students s ON i.student_id = s.id
            LEFT JOIN schools sc ON s.school_id = sc.id
            LIMIT 5
        """
        result = db_manager.execute_query(installments_query)
        print(f"استعلام الأقساط نجح - عدد النتائج: {len(result)}")
        
        # اختبار استعلام الرسوم الإضافية
        print("\n=== اختبار استعلام الرسوم الإضافية ===")
        fees_query = """
            SELECT af.id, s.name as student_name, sc.name_ar as school_name,
                   af.fee_type, af.notes, af.amount, af.created_at,
                   af.collection_date, af.collected_amount, af.status, af.notes
            FROM additional_fees af
            LEFT JOIN students s ON af.student_id = s.id
            LEFT JOIN schools sc ON s.school_id = sc.id
            LIMIT 5
        """
        result = db_manager.execute_query(fees_query)
        print(f"استعلام الرسوم الإضافية نجح - عدد النتائج: {len(result)}")
        
        print("\n✅ جميع الاستعلامات تعمل بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاستعلام: {e}")
        return False

if __name__ == "__main__":
    test_queries()
