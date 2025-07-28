#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط لنظام الطباعة
"""

print("اختبار نظام الطباعة")

# اختبار المكتبات
try:
    import arabic_reshaper
    import bidi.algorithm
    print("[نجاح] مكتبات دعم العربية متوفرة")
except ImportError as e:
    print(f"[فشل] مكتبات دعم العربية غير متوفرة: {e}")

try:
    import reportlab
    print(f"[نجاح] ReportLab متوفر، الإصدار: {reportlab.Version}")
except ImportError as e:
    print(f"[فشل] ReportLab غير متوفر: {e}")

# اختبار التكوين
try:
    from core.printing.print_config import TemplateType, PrintMethod, TEMPLATE_PRINT_METHODS
    print(f"[نجاح] تم استيراد التكوين، عدد القوالب: {len(TEMPLATE_PRINT_METHODS)}")
    
    # عرض التكوين
    print("\n[تكوين] تكوين طرق الطباعة:")
    for template_type, print_method in TEMPLATE_PRINT_METHODS.items():
        method_name = "ReportLab" if print_method == PrintMethod.REPORTLAB_CANVAS else "HTML"
        print(f"  • {template_type.value}: {method_name}")
        
except Exception as e:
    print(f"[فشل] خطأ في استيراد التكوين: {e}")

# اختبار مدير ReportLab
try:
    from core.printing.reportlab_print_manager import ReportLabPrintManager
    manager = ReportLabPrintManager()
    print("[نجاح] تم إنشاء مدير ReportLab بنجاح")
    
    # بيانات تجريبية بسيطة
    sample_data = {
        'student_name': 'أحمد محمد',
        'amount': 100000,
        'payment_date': '2025-01-15',
        'installment_number': 1,
        'school_name': 'مدرسة النور',
        'receipt_number': 'R20250115001'
    }
    
    print("[جاري] إنشاء إيصال تجريبي...")
    pdf_path = manager.create_installment_receipt(sample_data)
    print(f"[نجاح] تم إنشاء الإيصال: {pdf_path}")
    
except Exception as e:
    print(f"[فشل] خطأ في اختبار ReportLab: {e}")
    import traceback
    traceback.print_exc()

print("\n[انتهى] انتهى الاختبار")