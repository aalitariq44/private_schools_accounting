#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بيانات الطالب - للتحقق من صحة عرض البيانات
"""

from core.database.connection import db_manager

def test_student_data():
    """اختبار عرض بيانات الطلاب"""
    print("=== اختبار بيانات الطلاب ===")
    
    # استعلام مشابه لما يستخدم في صفحة تفاصيل الطالب
    query = """
        SELECT s.*, sc.name_ar as school_name, sc.name_en as school_name_en, 
               sc.address as school_address, sc.phone as school_phone, sc.logo_path as school_logo_path
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LIMIT 3
    """
    
    results = db_manager.execute_query(query)
    
    if not results:
        print("لا توجد بيانات طلاب")
        return
    
    for i, student in enumerate(results, 1):
        print(f"\n--- الطالب رقم {i} ---")
        print(f"ID: {student[0]}")
        print(f"الاسم (فهرس 1): {student[1]}")
        print(f"الرقم الوطني (فهرس 2): {student[2]}")
        print(f"معرف المدرسة (فهرس 3): {student[3]}")
        print(f"الصف (فهرس 4): {student[4]}")
        print(f"الشعبة (فهرس 5): {student[5]}")
        print(f"السنة الدراسية (فهرس 6): {student[6]}")
        print(f"الجنس (فهرس 7): {student[7]}")
        print(f"الهاتف (فهرس 8): {student[8]}")
        print(f"اسم ولي الأمر (فهرس 9): {student[9]}")
        print(f"هاتف ولي الأمر (فهرس 10): {student[10]}")
        print(f"القسط الكلي (فهرس 11): {student[11]}")
        print(f"تاريخ المباشرة (فهرس 12): {student[12]}")
        print(f"الحالة (فهرس 13): {student[13]}")
        print(f"تاريخ الإنشاء (فهرس 14): {student[14]}")
        print(f"تاريخ التحديث (فهرس 15): {student[15]}")
        print(f"الملاحظات (فهرس 16): {student[16]}")
        print(f"تاريخ الميلاد (فهرس 17): {student[17]}")
        
        # بيانات المدرسة من JOIN
        if len(student) > 18:
            print(f"اسم المدرسة (فهرس 18): {student[18]}")
            print(f"اسم المدرسة بالإنجليزية (فهرس 19): {student[19]}")
            print(f"عنوان المدرسة (فهرس 20): {student[20]}")
            print(f"هاتف المدرسة (فهرس 21): {student[21]}")
            print(f"شعار المدرسة (فهرس 22): {student[22]}")

if __name__ == "__main__":
    test_student_data()
