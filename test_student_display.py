#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عرض بيانات الطالب في صفحة التفاصيل
"""
from core.database.connection import db_manager

def test_student_data_display():
    """اختبار عرض بيانات الطالب"""
    try:
        # تحميل بيانات طالب مع معلومات المدرسة
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
            student = result[0]
            print(f"بيانات الطالب (العدد: {len(student)}):")
            print("-" * 50)
            
            # عرض البيانات مع التوضيح
            print(f"0: ID = {student[0]}")
            print(f"1: الاسم = {student[1]}")
            print(f"2: رقم الهوية = {student[2]}")
            print(f"3: معرف المدرسة = {student[3]}")
            print(f"4: الصف = {student[4]}")
            print(f"5: الشعبة = {student[5]}")
            print(f"6: السنة الدراسية = {student[6]}")
            print(f"7: الجنس = {student[7]}")
            print(f"8: تاريخ الميلاد = {student[8]}")
            print(f"9: الهاتف = {student[9]}")
            print(f"10: اسم الولي = {student[10]}")
            print(f"11: هاتف الولي = {student[11]}")
            print(f"12: القسط الكلي = {student[12]}")
            print(f"13: تاريخ المباشرة = {student[13]}")
            print(f"14: الحالة = {student[14]}")
            print(f"15: تاريخ الإنشاء = {student[15]}")
            print(f"16: تاريخ التحديث = {student[16]}")
            print(f"17: الملاحظات = {student[17]}")
            print("-" * 50)
            print("معلومات المدرسة:")
            print(f"18: اسم المدرسة (عربي) = {student[18]}")
            print(f"19: اسم المدرسة (إنجليزي) = {student[19]}")
            print(f"20: عنوان المدرسة = {student[20]}")
            print(f"21: هاتف المدرسة = {student[21]}")
            print(f"22: شعار المدرسة = {student[22]}")
            
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

if __name__ == "__main__":
    test_student_data_display()
