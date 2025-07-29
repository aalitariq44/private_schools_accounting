#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لميزة طباعة إيصال الرسوم الإضافية
"""

import os
import sys
from pathlib import Path

# إضافة المجلد الجذر للمشروع
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """اختبار استيراد الوحدات"""
    try:
        print("🔍 اختبار استيراد الوحدات...")
        
        # اختبار استيراد مدير الطباعة
        from core.printing.additional_fees_print_manager import AdditionalFeesPrintManager, print_additional_fees_receipt
        print("✅ تم استيراد مدير طباعة الرسوم الإضافية بنجاح")
        
        # اختبار استيراد نافذة الطباعة
        from ui.pages.students.additional_fees_print_dialog import AdditionalFeesPrintDialog
        print("✅ تم استيراد نافذة طباعة الرسوم الإضافية بنجاح")
        
        # اختبار إنشاء مدير الطباعة
        manager = AdditionalFeesPrintManager()
        print("✅ تم إنشاء مدير الطباعة بنجاح")
        
        return True
        
    except Exception as e:
        print(f"❌ فشل في اختبار الاستيراد: {e}")
        return False

def test_simple_print():
    """اختبار طباعة بسيط"""
    try:
        print("\n🔍 اختبار الطباعة البسيط...")
        
        from core.printing.additional_fees_print_manager import print_additional_fees_receipt
        
        # بيانات بسيطة للاختبار
        test_data = {
            'student': {
                'name': 'طالب تجريبي',
                'grade': 'الأول',
                'section': 'أ',
                'school_name': 'مدرسة تجريبية'
            },
            'fees': [
                {
                    'fee_type': 'رسوم كتب',
                    'amount': 25000,
                    'paid': True,
                    'payment_date': '2025-01-29',
                    'created_at': '2025-01-20',
                    'notes': 'رسوم تجريبية'
                }
            ],
            'summary': {
                'fees_count': 1,
                'total_amount': 25000,
                'paid_amount': 25000,
                'unpaid_amount': 0
            },
            'receipt_number': 'TEST001'
        }
        
        # محاولة إنشاء إيصال
        receipt_path = print_additional_fees_receipt(test_data, preview_only=True)
        
        if receipt_path and os.path.exists(receipt_path):
            print(f"✅ تم إنشاء إيصال تجريبي بنجاح: {receipt_path}")
            return True
        else:
            print("❌ فشل في إنشاء الإيصال التجريبي")
            return False
            
    except Exception as e:
        print(f"❌ فشل في اختبار الطباعة: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 اختبار بسيط لميزة طباعة الرسوم الإضافية")
    print("=" * 50)
    
    success = True
    
    # اختبار الاستيراد
    if not test_imports():
        success = False
    
    # اختبار الطباعة
    if success and not test_simple_print():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 جميع الاختبارات نجحت!")
    else:
        print("❌ بعض الاختبارات فشلت!")
        sys.exit(1)
