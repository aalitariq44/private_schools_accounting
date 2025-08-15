# -*- coding: utf-8 -*-
"""
اختبار طباعة الرسوم الإضافية
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_additional_fees_print():
    """اختبار طباعة الرسوم الإضافية"""
    try:
        from core.printing.additional_fees_print_manager import print_additional_fees_receipt
        
        # بيانات اختبار
        test_data = {
            'student_id': 1,
            'student_name': 'أحمد محمد علي',
            'school_name': 'مدرسة الأمل الأهلية',
            'grade': 'الأول الابتدائي',
            'section': 'أ',
            'selected_fees': [
                {
                    'id': 1,
                    'fee_type': 'رسوم النشاطات',
                    'amount': 50000,
                    'due_date': '2025-08-15',
                    'payment_date': '2025-08-15',
                    'notes': 'رسوم الأنشطة الرياضية'
                },
                {
                    'id': 2,
                    'fee_type': 'رسوم الكتب',
                    'amount': 75000,
                    'due_date': '2025-08-20',
                    'payment_date': '2025-08-15',
                    'notes': 'رسوم الكتب الدراسية'
                }
            ],
            'total_amount': 125000,
            'receipt_number': 'TEST-FEES-001',
            'date_printed': '2025-08-15'
        }
        
        print("تجربة طباعة الرسوم الإضافية...")
        receipt_path = print_additional_fees_receipt(test_data, preview_only=True)
        
        if receipt_path and os.path.exists(receipt_path):
            print(f"✅ تم إنشاء الإيصال: {receipt_path}")
            
            # فتح الملف للتحقق
            if os.name == 'nt':  # Windows
                os.startfile(receipt_path)
            return True
        else:
            print("❌ فشل في إنشاء الإيصال")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 اختبار طباعة الرسوم الإضافية")
    print("=" * 50)
    
    success = test_additional_fees_print()
    
    if success:
        print("\n✅ الاختبار نجح! الرسوم الإضافية تعمل بشكل صحيح.")
    else:
        print("\n❌ الاختبار فشل! يحتاج إلى مراجعة.")
    
    input("\nاضغط Enter للخروج...")
