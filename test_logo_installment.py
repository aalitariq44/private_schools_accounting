#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار طباعة إيصال قسط مع شعار المدرسة
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.printing.reportlab_print_manager import ReportLabPrintManager
from pathlib import Path
import config

def test_installment_receipt_with_logo():
    """اختبار طباعة إيصال قسط مع شعار المدرسة"""
    
    # بيانات تجريبية لإيصال قسط
    receipt_data = {
        'receipt': {
            'id': 'TEST001',
            'installment_id': 'TEST001',
            'student_name': 'أحمد محمد علي',
            'school_name': 'مدرسة النور الثانوية',
            'school_address': 'شارع الجامعة، بغداد',
            'school_phone': '07701234567',
            'school_logo_path': '',  # سنختبر مع شعار افتراضي أولاً
            'grade': 'الصف الثالث',
            'section': 'أ',
            'payment_date': '2025-08-21',
            'payment_method': 'نقدي',
            'description': 'قسط شهري',
            'amount': 150000,
            'total_paid': 450000,
            'total_fee': 1500000,
            'remaining': 1050000,
            'installment_number': 3,
            'receipt_number': 'R202508210001'
        }
    }
    
    print("اختبار 1: طباعة إيصال قسط مع الشعار الافتراضي...")
    manager = ReportLabPrintManager()
    output_path = manager.create_installment_receipt(receipt_data)
    print(f"تم إنشاء الإيصال: {output_path}")
    
    # اختبار مع شعار مدرسة مخصص (إذا وجد)
    custom_logo_path = Path(config.UPLOADS_DIR) / "school_logos" / "test_logo.png"
    if custom_logo_path.exists():
        print("\nاختبار 2: طباعة إيصال قسط مع شعار مدرسة مخصص...")
        receipt_data['receipt']['school_logo_path'] = str(custom_logo_path)
        receipt_data['receipt']['school_name'] = 'مدرسة الأمل الابتدائية'
        output_path2 = manager.create_installment_receipt(receipt_data)
        print(f"تم إنشاء الإيصال مع الشعار المخصص: {output_path2}")
    else:
        print("\nلا يوجد شعار مخصص للاختبار")
    
    return output_path

def test_additional_fees_receipt_with_logo():
    """اختبار طباعة إيصال رسوم إضافية مع شعار المدرسة"""
    
    try:
        from core.printing.additional_fees_print_manager import AdditionalFeesPrintManager
        
        # بيانات تجريبية لإيصال رسوم إضافية
        fees_data = {
            'student': {
                'id': 1,
                'name': 'فاطمة عبد الله',
                'grade': 'الصف الثاني',
                'section': 'ب',
                'school_name': 'مدرسة الزهراء المتوسطة',
                'school_logo_path': ''  # شعار افتراضي
            },
            'fees': [
                {
                    'id': 1,
                    'fee_type': 'رسوم المختبر',
                    'amount': 25000,
                    'paid': True,
                    'payment_date': '2025-08-21',
                    'created_at': '2025-08-15',
                    'notes': 'رسوم استخدام المختبر'
                },
                {
                    'id': 2,
                    'fee_type': 'رسوم النشاط',
                    'amount': 15000,
                    'paid': True,
                    'payment_date': '2025-08-21',
                    'created_at': '2025-08-15',
                    'notes': 'رسوم الأنشطة الرياضية'
                }
            ],
            'summary': {
                'fees_count': 2,
                'total_amount': 40000,
                'paid_amount': 40000,
                'unpaid_amount': 0
            },
            'receipt_number': 'AF202508210001',
            'print_date': '2025-08-21',
            'print_time': '14:30:00'
        }
        
        print("\nاختبار 3: طباعة إيصال رسوم إضافية مع الشعار الافتراضي...")
        manager = AdditionalFeesPrintManager()
        output_path = manager.create_additional_fees_receipt(fees_data)
        print(f"تم إنشاء إيصال الرسوم الإضافية: {output_path}")
        
        return output_path
        
    except ImportError as e:
        print(f"لا يمكن اختبار الرسوم الإضافية: {e}")
        return None

if __name__ == "__main__":
    print("=== اختبار طباعة الإيصالات مع شعار المدرسة ===")
    
    try:
        # اختبار إيصال القسط
        installment_receipt = test_installment_receipt_with_logo()
        
        # اختبار إيصال الرسوم الإضافية
        fees_receipt = test_additional_fees_receipt_with_logo()
        
        print("\n=== انتهى الاختبار بنجاح ===")
        print("يمكنك فتح الملفات المنشأة للتحقق من ظهور الشعار بشكل صحيح")
        
        if installment_receipt:
            print(f"إيصال القسط: {installment_receipt}")
        if fees_receipt:
            print(f"إيصال الرسوم الإضافية: {fees_receipt}")
            
        # فتح الملف الأول للمعاينة
        if installment_receipt and os.path.exists(installment_receipt):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(installment_receipt)
                print("تم فتح إيصال القسط للمعاينة")
            except Exception as e:
                print(f"لا يمكن فتح الملف تلقائياً: {e}")
    
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
