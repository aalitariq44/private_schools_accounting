#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام الطباعة المزدوج
HTML + ReportLab
"""

import sys
import os
from datetime import datetime

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.printing.print_manager import PrintManager, print_installment_receipt, print_payment_receipt
from core.printing.print_config import TemplateType, PrintMethod, TEMPLATE_PRINT_METHODS


def test_print_methods():
    """اختبار طرق الطباعة المختلفة"""
    print("🧪 اختبار نظام الطباعة المزدوج")
    print("=" * 50)
    
    # عرض مصفوفة طرق الطباعة
    print("\n📋 طرق الطباعة المحددة لكل قالب:")
    for template_type, print_method in TEMPLATE_PRINT_METHODS.items():
        method_name = "ReportLab" if print_method == PrintMethod.REPORTLAB_CANVAS else "HTML"
        print(f"  • {template_type.value}: {method_name}")
    
    print("\n" + "=" * 50)
    
    # بيانات تجريبية لإيصال دفع قسط
    sample_installment_data = {
        'student_name': 'أحمد محمد علي',
        'amount': 250000,
        'payment_date': datetime.now().strftime('%Y-%m-%d'),
        'installment_number': 3,
        'school_name': 'مدرسة النور الأهلية',
        'receipt_number': f'R{datetime.now().strftime("%Y%m%d%H%M%S")}'
    }
    
    # بيانات تجريبية لتقرير طالب
    sample_student_report = {
        'student': {
            'name': 'فاطمة عبد الله',
            'class': 'الصف السادس الابتدائي',
            'grades': [
                {'subject': 'الرياضيات', 'grade': 85},
                {'subject': 'العلوم', 'grade': 92},
                {'subject': 'اللغة العربية', 'grade': 88}
            ]
        }
    }
    
    try:
        # إنشاء مدير الطباعة
        pm = PrintManager()
        
        print("\n🔍 اختبار 1: إيصال دفع قسط (ReportLab)")
        print("سيتم إنشاء إيصال PDF بتصميم دقيق ودعم عربي...")
        
        # معاينة إيصال قسط
        pm.preview_document(TemplateType.INSTALLMENT_RECEIPT, sample_installment_data)
        print("✅ تم إنشاء إيصال الدفع بنجاح")
        
        print("\n🔍 اختبار 2: تقرير طالب (HTML)")
        print("سيتم إنشاء تقرير HTML عبر محرك الويب...")
        
        # معاينة تقرير طالب
        pm.preview_document(TemplateType.STUDENT_REPORT, sample_student_report)
        print("✅ تم إنشاء تقرير الطالب بنجاح")
        
        print("\n🎉 جميع الاختبارات نجحت!")
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()


def test_reportlab_only():
    """اختبار ReportLab منفرداً"""
    print("\n🧪 اختبار ReportLab منفرداً")
    print("=" * 30)
    
    try:
        from core.printing.reportlab_print_manager import ReportLabPrintManager
        
        # بيانات تجريبية
        sample_data = {
            'student_name': 'عبد الرحمن أحمد',
            'amount': 150000,
            'payment_date': datetime.now().strftime('%Y-%m-%d'),
            'installment_number': 2,
            'school_name': 'مدرسة المستقبل الأهلية',
            'receipt_number': f'R{datetime.now().strftime("%Y%m%d%H%M%S")}'
        }
        
        manager = ReportLabPrintManager()
        pdf_path = manager.preview_installment_receipt(sample_data)
        
        print(f"✅ تم إنشاء PDF: {pdf_path}")
        
    except ImportError as e:
        print(f"❌ مكتبات ReportLab أو دعم العربية غير متوفرة: {e}")
        print("💡 تشغيل الأمر لتثبيت المكتبات:")
        print("   pip install arabic-reshaper python-bidi")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار ReportLab: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # اختبار النظام المزدوج
    test_print_methods()
    
    # اختبار ReportLab منفرداً
    test_reportlab_only()
    
    print("\n🏁 انتهى الاختبار")
