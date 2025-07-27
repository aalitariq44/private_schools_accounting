#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لنظام الطباعة
تشغيل: python test_complete_printing.py
"""

import sys
import os
from datetime import datetime

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_printing_imports():
    """اختبار استيراد جميع مكونات نظام الطباعة"""
    print("🔍 اختبار الاستيرادات...")
    
    try:
        from core.printing import print_manager
        print("✅ استيراد print_manager نجح")
    except Exception as e:
        print(f"❌ فشل استيراد print_manager: {e}")
        return False
    
    try:
        from core.printing import TemplateType, PrintSettings, QuickPrintMixin
        print("✅ استيراد الأنواع والإعدادات نجح")
    except Exception as e:
        print(f"❌ فشل استيراد الأنواع: {e}")
        return False
    
    try:
        from core.printing import apply_print_styles, PrintHelper
        print("✅ استيراد المساعدات نجح")
    except Exception as e:
        print(f"❌ فشل استيراد المساعدات: {e}")
        return False
    
    return True

def test_template_manager():
    """اختبار مدير القوالب"""
    print("\n📋 اختبار مدير القوالب...")
    
    try:
        from core.printing.template_manager import TemplateManager
        manager = TemplateManager()
        
        # اختبار إنشاء القوالب
        manager.create_default_templates()
        print("✅ إنشاء القوالب الافتراضية نجح")
        
        # اختبار عرض قالب
        from core.printing import TemplateType
        student_data = {
            'student': {
                'name': 'أحمد محمد',
                'school_name': 'مدرسة النور الأهلية',
                'grade': 'الصف الأول',
                'section': 'أ',
                'gender': 'ذكر',
                'phone': '07701234567',
                'status': 'فعال',
                'total_fee': 1500000
            }
        }
        
        html = manager.render_template(TemplateType.STUDENT_REPORT, student_data)
        if html and len(html) > 100:
            print("✅ عرض قالب تقرير الطالب نجح")
        else:
            print("❌ فشل في عرض القالب")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في مدير القوالب: {e}")
        return False

def test_print_settings():
    """اختبار إعدادات الطباعة"""
    print("\n⚙️ اختبار إعدادات الطباعة...")
    
    try:
        from core.printing.print_config import PrintSettings, PaperSize, PrintOrientation
        
        # إنشاء إعدادات جديدة
        settings = PrintSettings()
        print(f"✅ إعدادات افتراضية: ورق {settings.paper_size.value}, اتجاه {settings.orientation.value}")
        
        # تخصيص الإعدادات
        settings.paper_size = PaperSize.A4
        settings.orientation = PrintOrientation.LANDSCAPE
        settings.margins_mm = (10, 10, 10, 10)
        settings.show_header = True
        settings.show_footer = True
        
        # تخصيص الإعدادات
        settings.paper_size = PaperSize.A4
        settings.margins_mm = (10, 10, 10, 10)
        settings.show_header = True
        settings.show_footer = True
        
        print("✅ تخصيص الإعدادات نجح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعدادات الطباعة: {e}")
        return False

def test_data_formatting():
    """اختبار تنسيق البيانات"""
    print("\n🔤 اختبار تنسيق البيانات...")
    
    try:
        from core.printing.template_manager import TemplateManager
        manager = TemplateManager()
        
        # اختبار فلتر التاريخ العربي
        test_date = "2024-01-15"
        arabic_date = manager.arabic_date(test_date)
        if arabic_date and "يناير" in arabic_date:
            print("✅ تنسيق التاريخ العربي نجح")
        else:
            print("❌ فشل تنسيق التاريخ العربي")
            return False
        
        # اختبار فلتر العملة
        test_amount = 1234567
        formatted_amount = manager.format_currency(test_amount)
        if formatted_amount and "," in formatted_amount:
            print("✅ تنسيق العملة نجح")
        else:
            print("❌ فشل تنسيق العملة")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تنسيق البيانات: {e}")
        return False

def test_file_structure():
    """اختبار هيكل الملفات"""
    print("\n📁 اختبار هيكل الملفات...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        os.path.join(base_dir, 'core', 'printing', '__init__.py'),
        os.path.join(base_dir, 'core', 'printing', 'print_config.py'),
        os.path.join(base_dir, 'core', 'printing', 'template_manager.py'),
        os.path.join(base_dir, 'core', 'printing', 'print_manager.py'),
        os.path.join(base_dir, 'core', 'printing', 'print_utils.py'),
        os.path.join(base_dir, 'core', 'printing', 'simple_print_preview.py')
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} مفقود")
            all_exist = False
    
    # اختبار مجلد القوالب
    templates_dir = os.path.join(base_dir, 'app', 'resources', 'print_templates')
    if os.path.exists(templates_dir):
        template_files = os.listdir(templates_dir)
        print(f"✅ مجلد القوالب موجود ({len(template_files)} ملف)")
    else:
        print("⚠️ مجلد القوالب غير موجود (سيتم إنشاؤه تلقائياً)")
    
    return all_exist

def test_mock_printing():
    """اختبار الطباعة التجريبية (بدون GUI)"""
    print("\n🖨️ اختبار الطباعة التجريبية...")
    
    try:
        from core.printing import print_manager, TemplateType
        
        # بيانات تجريبية للطلاب
        students_data = {
            'students': [
                {'id': 1, 'name': 'أحمد محمد', 'school_name': 'مدرسة النور', 'grade': 'الأول', 'section': 'أ', 'gender': 'ذكر', 'status': 'فعال', 'total_fee': 1500000},
                {'id': 2, 'name': 'فاطمة علي', 'school_name': 'مدرسة النور', 'grade': 'الثاني', 'section': 'ب', 'gender': 'أنثى', 'status': 'فعال', 'total_fee': 1500000},
                {'id': 3, 'name': 'محمد حسن', 'school_name': 'مدرسة النور', 'grade': 'الثالث', 'section': 'أ', 'gender': 'ذكر', 'status': 'فعال', 'total_fee': 1500000}
            ],
            'total': 3
        }
        
        # اختبار تحضير البيانات للطباعة (بدون طباعة فعلية)
        from core.printing.template_manager import TemplateManager
        manager = TemplateManager()
        
        html = manager.render_template(TemplateType.STUDENT_LIST, students_data)
        if html and 'أحمد محمد' in html:
            print("✅ تحضير قائمة الطلاب للطباعة نجح")
        else:
            print("❌ فشل تحضير قائمة الطلاب")
            return False
        
        # اختبار بيانات الإيصال
        receipt_data = {
            'receipt': {
                'id': 'REC-001',
                'student_name': 'أحمد محمد',
                'school_name': 'مدرسة النور الأهلية',
                'payment_date': '2024-01-15',
                'amount': 500000,
                'description': 'رسوم دراسية',
                'payment_method': 'نقداً'
            }
        }
        
        html = manager.render_template(TemplateType.PAYMENT_RECEIPT, receipt_data)
        if html and 'أحمد محمد' in html and '500,000' in html:
            print("✅ تحضير إيصال الدفع للطباعة نجح")
        else:
            print("❌ فشل تحضير إيصال الدفع")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الطباعة التجريبية: {e}")
        return False

def test_integration_example():
    """اختبار مثال التكامل"""
    print("\n🔗 اختبار مثال التكامل...")
    
    try:
        # محاولة استيراد المثال
        import financial_page_print_example
        print("✅ استيراد مثال صفحة المالية نجح")
        
        # اختبار الكلاس
        from financial_page_print_example import FinancialPageWithPrint
        print("✅ كلاس المثال متاح")
        
        # اختبار الوظائف المطلوبة
        test_methods = ['get_current_data_for_print', 'get_current_filters_info']
        for method in test_methods:
            if hasattr(FinancialPageWithPrint, method):
                print(f"✅ دالة {method} موجودة")
            else:
                print(f"❌ دالة {method} مفقودة")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في مثال التكامل: {e}")
        return False

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار نظام الطباعة الشامل")
    print("=" * 50)
    
    tests = [
        ("استيراد المكونات", test_printing_imports),
        ("مدير القوالب", test_template_manager),
        ("إعدادات الطباعة", test_print_settings),
        ("تنسيق البيانات", test_data_formatting),
        ("هيكل الملفات", test_file_structure),
        ("الطباعة التجريبية", test_mock_printing),
        ("مثال التكامل", test_integration_example)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ خطأ في اختبار {test_name}: {e}")
            results.append((test_name, False))
    
    # عرض النتائج النهائية
    print("\n" + "=" * 50)
    print("📊 نتائج الاختبارات:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 النتيجة النهائية: {passed}/{len(results)} اختبارات نجحت")
    
    if passed == len(results):
        print("\n🎉 ممتاز! نظام الطباعة جاهز للاستخدام")
        print("\n📝 الخطوات التالية:")
        print("1. راجع دليل ADD_PRINT_TO_PAGE_GUIDE.md")
        print("2. انسخ كود من financial_page_print_example.py")
        print("3. أضف الطباعة لصفحاتك باستخدام الأمثلة")
        print("4. استخدم QuickPrintMixin للطباعة السريعة")
    else:
        print("\n⚠️ يوجد مشاكل في النظام. راجع الأخطاء أعلاه")
        print("💡 جرب تشغيل: python setup_printing_system.py")

if __name__ == "__main__":
    main()
