#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال على استخدام نظام الطباعة
"""

from core.printing import print_manager, PrintHelper

# مثال 1: طباعة تقرير طالب
def print_student_example():
    student_data = {
        'id': 1,
        'name': 'أحمد محمد علي',
        'school_name': 'مدرسة النور الأهلية',
        'grade': 'الرابع الابتدائي',
        'section': 'أ',
        'gender': 'ذكر',
        'phone': '07901234567',
        'status': 'نشط',
        'total_fee': 500000,
        'start_date': '2024-09-01'
    }
    
    # طباعة مع معاينة
    print_manager.print_student_report(student_data)

# مثال 2: طباعة قائمة الطلاب
def print_students_list_example():
    students_list = [
        {
            'id': 1,
            'name': 'أحمد محمد',
            'school_name': 'مدرسة النور',
            'grade': 'الرابع',
            'section': 'أ',
            'gender': 'ذكر',
            'phone': '1234567890',
            'status': 'نشط',
            'total_fee': 500000
        },
        {
            'id': 2,
            'name': 'فاطمة أحمد',
            'school_name': 'مدرسة النور',
            'grade': 'الخامس',
            'section': 'ب',
            'gender': 'أنثى',
            'phone': '1234567891',
            'status': 'نشط',
            'total_fee': 550000
        }
    ]
    
    # تنسيق البيانات للطباعة
    formatted_students = PrintHelper.format_students_list_for_print(students_list)
    
    # طباعة مع معاينة
    print_manager.print_students_list(
        formatted_students, 
        "المدرسة: مدرسة النور | جميع الصفوف"
    )

# مثال 3: طباعة إيصال دفع
def print_receipt_example():
    receipt_data = {
        'id': 'REC-001',
        'student_name': 'أحمد محمد علي',
        'school_name': 'مدرسة النور الأهلية',
        'payment_date': '2024-01-15',
        'payment_method': 'نقداً',
        'description': 'رسوم دراسية - شهر كانون الثاني',
        'amount': 100000
    }
    
    print_manager.print_payment_receipt(receipt_data)

if __name__ == "__main__":
    # اختر المثال الذي تريد تجربته
    print_student_example()
    # print_students_list_example()
    # print_receipt_example()
