#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("تشغيل اختبار البيانات...")

try:
    from core.database.connection import db_manager
    print("تم تحميل db_manager بنجاح")
    
    # تحميل بيانات طالب مع معلومات المدرسة
    query = """
        SELECT s.*, sc.name_ar as school_name, sc.name_en as school_name_en, 
               sc.address as school_address, sc.phone as school_phone, 
               sc.logo_path as school_logo_path
        FROM students s
        LEFT JOIN schools sc ON s.school_id = sc.id
        LIMIT 1
    """
    print("تنفيذ الاستعلام...")
    result = db_manager.execute_query(query)
    print(f"النتيجة: {len(result) if result else 0} سجل")
    
    if result:
        student = result[0]
        print(f"بيانات الطالب (العدد: {len(student)}):")
        print("-" * 50)
        
        # عرض البيانات مع التوضيح
        for i, value in enumerate(student):
            print(f"{i}: {value}")
            
        print("\n" + "="*50)
        print("اختبار عرض البيانات في النموذج:")
        print("="*50)
        
        # اختبار العرض كما يتم في student_info_widget
        print(f"الاسم: {student[1] or '--'}")
        print(f"المدرسة: {student[18] if len(student) > 18 and student[18] else '--'}")
        print(f"الصف: {student[4] or '--'}")
        print(f"الشعبة: {student[5] or '--'}")
        print(f"الجنس: {student[7] or '--'}")
        print(f"تاريخ الميلاد: {student[8] or '--'}")
        print(f"الهاتف: {student[9] or '--'}")
        print(f"الحالة: {student[14] or 'نشط'}")
        print(f"تاريخ المباشرة: {student[13] or '--'}")
        print(f"الملاحظات: {student[17] or 'لا توجد ملاحظات'}")
        
        try:
            total_fee = float(student[12] or 0)
            print(f"القسط الكلي: {total_fee:,.0f} د.ع")
        except (ValueError, TypeError):
            print(f"القسط الكلي: خطأ في القيمة: {student[12]}")
            
    else:
        print("لا توجد بيانات طلاب للاختبار")
        
except Exception as e:
    print(f"خطأ في الاختبار: {e}")
    import traceback
    traceback.print_exc()

input("اضغط Enter للمتابعة...")
