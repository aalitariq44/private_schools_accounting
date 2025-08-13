# -*- coding: utf-8 -*-
"""
اختبار طباعة وصل الأقساط مع بيانات المدرسة الحقيقية
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.printing.reportlab_print_manager import ReportLabPrintManager
import datetime

def test_print_with_school_data():
    """اختبار طباعة وصل مع بيانات المدرسة"""
    
    # بيانات تجريبية تحاكي البيانات الحقيقية
    test_data = {
        'receipt': {
            'student_name': 'أحمد محمد علي',
            'school_name': 'مدرسة النور الأهلية',
            'school_address': 'شارع الجامعة، حي المنصور، بغداد',
            'school_phone': '07701234567 - 07709876543',
            'grade': 'الرابع الابتدائي',
            'section': 'أ',
            'amount': 250000,
            'payment_date': '2025-01-15',
            'total_fee': 1000000,
            'total_paid': 500000,
            'remaining': 500000,
            'installment_id': 123,
            'receipt_number': 'R202501150001'
        }
    }
    
    print("إنشاء وصل أقساط مع بيانات المدرسة الحقيقية...")
    
    try:
        # إنشاء مدير الطباعة
        manager = ReportLabPrintManager()
        
        # إنشاء الوصل
        output_path = manager.create_installment_receipt(test_data)
        
        print(f"✅ تم إنشاء الوصل بنجاح!")
        print(f"📁 المسار: {output_path}")
        print(f"📋 بيانات المدرسة المستخدمة:")
        print(f"   - اسم المدرسة: {test_data['receipt']['school_name']}")
        print(f"   - العنوان: {test_data['receipt']['school_address']}")
        print(f"   - الهاتف: {test_data['receipt']['school_phone']}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الوصل: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_print_without_school_data():
    """اختبار طباعة وصل بدون بيانات المدرسة (النصوص الافتراضية)"""
    
    # بيانات بدون معلومات المدرسة
    test_data = {
        'receipt': {
            'student_name': 'سارة أحمد محمود',
            'school_name': 'مدرسة الأمل الأهلية',
            # بدون school_address و school_phone
            'grade': 'الثالث المتوسط',
            'section': 'ب',
            'amount': 180000,
            'payment_date': '2025-01-15',
            'total_fee': 750000,
            'total_paid': 300000,
            'remaining': 450000,
            'installment_id': 456,
            'receipt_number': 'R202501150002'
        }
    }
    
    print("\nإنشاء وصل أقساط بدون بيانات المدرسة (استخدام النص الافتراضي)...")
    
    try:
        # إنشاء مدير الطباعة
        manager = ReportLabPrintManager()
        
        # إنشاء الوصل
        output_path = manager.create_installment_receipt(test_data)
        
        print(f"✅ تم إنشاء الوصل بنجاح!")
        print(f"📁 المسار: {output_path}")
        print(f"📋 بيانات المدرسة المستخدمة:")
        print(f"   - اسم المدرسة: {test_data['receipt']['school_name']}")
        print(f"   - العنوان: عنوان المدرسة: (نص افتراضي)")
        print(f"   - الهاتف: للتواصل (نص افتراضي)")
        
        return output_path
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الوصل: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 اختبار طباعة الوصولات مع بيانات المدرسة")
    print("=" * 60)
    
    # اختبار مع بيانات المدرسة
    path1 = test_print_with_school_data()
    
    # اختبار بدون بيانات المدرسة
    path2 = test_print_without_school_data()
    
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    
    if path1:
        print(f"✅ الوصل مع بيانات المدرسة: تم إنشاؤه")
    else:
        print(f"❌ الوصل مع بيانات المدرسة: فشل")
        
    if path2:
        print(f"✅ الوصل بدون بيانات المدرسة: تم إنشاؤه")
    else:
        print(f"❌ الوصل بدون بيانات المدرسة: فشل")
    
    print("=" * 60)
