#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار طباعة إيصالات مع أسماء المدارس بالعربية والإنجليزية
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.printing.reportlab_print_manager import ReportLabPrintManager
from core.printing.additional_fees_print_manager import AdditionalFeesPrintManager
from pathlib import Path
import config

def test_installment_with_english_name():
    """اختبار إيصال قسط مع اسم المدرسة بالعربية والإنجليزية"""
    
    receipt_data = {
        'receipt': {
            'id': 'TEST002',
            'installment_id': 'TEST002',
            'student_name': 'سارة أحمد محمد',
            'school_name': 'مدرسة الأمل الثانوية',
            'school_name_en': 'Al-Amal Secondary School',  # اسم إنجليزي
            'school_address': 'شارع الحرية، بغداد',
            'school_phone': '07701234567',
            'school_logo_path': '',
            'grade': 'الصف الثاني',
            'section': 'ب',
            'payment_date': '2025-08-21',
            'amount': 200000,
            'total_paid': 600000,
            'total_fee': 1800000,
            'remaining': 1200000,
            'receipt_number': 'R202508210002'
        }
    }
    
    print("=== اختبار إيصال قسط مع الاسم الإنجليزي ===")
    manager = ReportLabPrintManager()
    output_path = manager.create_installment_receipt(receipt_data)
    print(f"تم إنشاء إيصال القسط: {output_path}")
    
    return output_path

def test_installment_without_english_name():
    """اختبار إيصال قسط بدون اسم إنجليزي"""
    
    receipt_data = {
        'receipt': {
            'id': 'TEST003',
            'installment_id': 'TEST003',
            'student_name': 'علي حسن محمد',
            'school_name': 'مدرسة النور الابتدائية',
            'school_name_en': '',  # بدون اسم إنجليزي
            'school_address': 'شارع الجامعة، بغداد',
            'school_phone': '07709876543',
            'school_logo_path': '',
            'grade': 'الصف الخامس',
            'section': 'أ',
            'payment_date': '2025-08-21',
            'amount': 120000,
            'total_paid': 360000,
            'total_fee': 1200000,
            'remaining': 840000,
            'receipt_number': 'R202508210003'
        }
    }
    
    print("=== اختبار إيصال قسط بدون اسم إنجليزي ===")
    manager = ReportLabPrintManager()
    output_path = manager.create_installment_receipt(receipt_data)
    print(f"تم إنشاء إيصال القسط: {output_path}")
    
    return output_path

def test_additional_fees_with_english_name():
    """اختبار إيصال رسوم إضافية مع اسم المدرسة بالإنجليزية"""
    
    fees_data = {
        'student': {
            'id': 1,
            'name': 'نور فاطمة علي',
            'grade': 'الصف الثالث',
            'section': 'ج',
            'school_name': 'مدرسة الزهراء المتوسطة',
            'school_name_en': 'Al-Zahra Middle School',  # اسم إنجليزي
            'school_logo_path': ''
        },
        'fees': [
            {
                'id': 1,
                'fee_type': 'رسوم الكتب',
                'amount': 50000,
                'paid': True,
                'payment_date': '2025-08-21',
                'created_at': '2025-08-15',
                'notes': 'رسوم شراء الكتب المدرسية'
            },
            {
                'id': 2,
                'fee_type': 'رسوم الرحلة',
                'amount': 30000,
                'paid': True,
                'payment_date': '2025-08-21',
                'created_at': '2025-08-15',
                'notes': 'رسوم الرحلة العلمية'
            }
        ],
        'summary': {
            'fees_count': 2,
            'total_amount': 80000,
            'paid_amount': 80000,
            'unpaid_amount': 0
        },
        'receipt_number': 'AF202508210002',
        'print_date': '2025-08-21',
        'print_time': '14:45:00'
    }
    
    print("=== اختبار إيصال رسوم إضافية مع الاسم الإنجليزي ===")
    manager = AdditionalFeesPrintManager()
    output_path = manager.create_additional_fees_receipt(fees_data)
    print(f"تم إنشاء إيصال الرسوم الإضافية: {output_path}")
    
    return output_path

def test_additional_fees_without_english_name():
    """اختبار إيصال رسوم إضافية بدون اسم إنجليزي"""
    
    fees_data = {
        'student': {
            'id': 2,
            'name': 'أحمد محمود حسن',
            'grade': 'الصف الرابع',
            'section': 'د',
            'school_name': 'مدرسة الفرات الابتدائية',
            'school_name_en': '',  # بدون اسم إنجليزي
            'school_logo_path': ''
        },
        'fees': [
            {
                'id': 3,
                'fee_type': 'رسوم القرطاسية',
                'amount': 35000,
                'paid': True,
                'payment_date': '2025-08-21',
                'created_at': '2025-08-15',
                'notes': 'رسوم الأدوات المكتبية'
            }
        ],
        'summary': {
            'fees_count': 1,
            'total_amount': 35000,
            'paid_amount': 35000,
            'unpaid_amount': 0
        },
        'receipt_number': 'AF202508210003',
        'print_date': '2025-08-21',
        'print_time': '15:00:00'
    }
    
    print("=== اختبار إيصال رسوم إضافية بدون اسم إنجليزي ===")
    manager = AdditionalFeesPrintManager()
    output_path = manager.create_additional_fees_receipt(fees_data)
    print(f"تم إنشاء إيصال الرسوم الإضافية: {output_path}")
    
    return output_path

if __name__ == "__main__":
    print("=== اختبار عرض أسماء المدارس بالعربية والإنجليزية ===\n")
    
    try:
        # اختبار إيصالات الأقساط
        installment_with_en = test_installment_with_english_name()
        print()
        installment_without_en = test_installment_without_english_name()
        print()
        
        # اختبار إيصالات الرسوم الإضافية
        fees_with_en = test_additional_fees_with_english_name()
        print()
        fees_without_en = test_additional_fees_without_english_name()
        print()
        
        print("=== ملخص الملفات المنشأة ===")
        print(f"1. إيصال قسط مع اسم إنجليزي: {installment_with_en}")
        print(f"2. إيصال قسط بدون اسم إنجليزي: {installment_without_en}")
        print(f"3. إيصال رسوم مع اسم إنجليزي: {fees_with_en}")
        print(f"4. إيصال رسوم بدون اسم إنجليزي: {fees_without_en}")
        
        print("\n=== توقعات النتائج ===")
        print("• الإيصالات مع اسم إنجليزي: يجب أن تظهر اسم المدرسة بالعربية ثم بالإنجليزية تحتها")
        print("• الإيصالات بدون اسم إنجليزي: يجب أن تظهر اسم المدرسة بالعربية فقط")
        
        # فتح الملف الأول للمعاينة
        if installment_with_en and os.path.exists(installment_with_en):
            try:
                if os.name == 'nt':  # Windows
                    import subprocess
                    subprocess.run(['start', '', installment_with_en], shell=True)
                print(f"\nتم فتح الملف الأول للمعاينة: {installment_with_en}")
            except Exception as e:
                print(f"لا يمكن فتح الملف تلقائياً: {e}")
    
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
