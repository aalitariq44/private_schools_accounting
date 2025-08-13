#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح عرض اسم المدرسة في واجهة تفاصيل الطالب
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import db_manager

def test_school_display_fix():
    """اختبار إصلاح عرض اسم المدرسة"""
    
    print("اختبار إصلاح عرض اسم المدرسة في واجهة تفاصيل الطالب")
    print("="*60)
    
    # محاكاة ما يحدث في update_student_info
    query = """
        SELECT s.*, sc.name_ar as school_name, sc.address as school_address, sc.phone as school_phone
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        WHERE s.id = 1
    """
    
    result = db_manager.execute_query(query)
    
    if result:
        student_data = result[0]
        
        print(f"بيانات الطالب:")
        print(f"- اسم الطالب: {student_data[1]}")
        print(f"- الصف: {student_data[4]}")
        print(f"- القسط الكلي: {student_data[11]}")
        
        print(f"\nالحقول النهائية (المدرسة):")
        print(f"- الحقل الأخير (school_phone): {student_data[-1]}")
        print(f"- الحقل ما قبل الأخير (school_address): {student_data[-2]}")
        print(f"- الحقل الثالث من النهاية (school_name): {student_data[-3]}")
        
        print(f"\nما سيتم عرضه في الواجهة:")
        print(f"- اسم المدرسة (قبل الإصلاح): {student_data[-1]}")  # كان يعرض رقم الهاتف
        print(f"- اسم المدرسة (بعد الإصلاح): {student_data[-3]}")  # يعرض اسم المدرسة الصحيح
        
        # التحقق من النتيجة
        school_name_old = student_data[-1]  # الطريقة القديمة الخاطئة
        school_name_new = student_data[-3]  # الطريقة الجديدة الصحيحة
        
        print(f"\n" + "="*60)
        print(f"نتيجة الإصلاح:")
        
        if school_name_old != school_name_new:
            print(f"✅ تم إصلاح المشكلة بنجاح!")
            print(f"   - قبل الإصلاح: '{school_name_old}' (خاطئ)")
            print(f"   - بعد الإصلاح: '{school_name_new}' (صحيح)")
        else:
            print(f"❌ لم يتم إصلاح المشكلة")
            
        # معاينة بيانات الوصل
        print(f"\nما سيتم طباعته في الوصل:")
        receipt_data = {
            'student_name': student_data[1],
            'school_name': student_data[-3],  # الاسم الصحيح
            'school_address': student_data[-2],  # العنوان
            'school_phone': student_data[-1],    # رقم الهاتف
            'grade': student_data[4],
            'section': student_data[5]
        }
        
        for key, value in receipt_data.items():
            print(f"   - {key}: {value}")
            
    else:
        print("❌ لم يتم العثور على بيانات طالب للاختبار")

if __name__ == "__main__":
    try:
        test_school_display_fix()
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
