#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تثبيت وتهيئة نظام الطباعة
"""

import os
import sys
import logging
from pathlib import Path

# إضافة المسار للاستيراد
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_printing_system():
    """إعداد وتهيئة نظام الطباعة"""
    
    print("🖨️ بدء تهيئة نظام الطباعة...")
    
    # المسارات المطلوبة
    project_root = Path(__file__).parent
    printing_dir = project_root / "core" / "printing"
    templates_dir = project_root / "app" / "resources" / "print_templates"
    
    try:
        # 1. التحقق من وجود المجلدات المطلوبة
        print("📁 التحقق من المجلدات...")
        
        if not printing_dir.exists():
            print("❌ مجلد نظام الطباعة غير موجود!")
            return False
            
        if not templates_dir.exists():
            print("📁 إنشاء مجلد القوالب...")
            templates_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. التحقق من المتطلبات
        print("📦 التحقق من المتطلبات...")
        
        try:
            import jinja2
            print("✅ jinja2 متوفر")
        except ImportError:
            print("❌ jinja2 غير متوفر - يرجى تثبيته: pip install jinja2")
            return False
        
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            print("✅ PyQt5 WebEngine متوفر")
        except ImportError:
            print("⚠️ PyQt5 WebEngine غير متوفر - المعاينة قد لا تعمل بشكل مثالي")
            print("   يمكن تثبيته: pip install PyQtWebEngine")
        
        try:
            from PyQt5.QtPrintSupport import QPrinter
            print("✅ PyQt5 PrintSupport متوفر")
        except ImportError:
            print("❌ PyQt5 PrintSupport غير متوفر - الطباعة لن تعمل")
            return False
        
        # 3. التحقق من القوالب
        print("📄 التحقق من القوالب...")
        
        try:
            from core.printing import TemplateManager
            template_manager = TemplateManager()
            template_manager.create_default_templates()
            print("✅ تم إنشاء القوالب الافتراضية")
        except Exception as e:
            print(f"❌ خطأ في إنشاء القوالب: {e}")
            return False
        
        # 4. اختبار النظام
        print("🧪 اختبار النظام...")
        
        try:
            from core.printing import print_manager
            print("✅ تم تحميل مدير الطباعة بنجاح")
        except Exception as e:
            print(f"❌ خطأ في تحميل نظام الطباعة: {e}")
            return False
        
        # 5. إنشاء ملف الإعدادات إذا لم يكن موجوداً
        config_file = project_root / "printing_config.json"
        if not config_file.exists():
            print("⚙️ إنشاء ملف الإعدادات...")
            default_config = {
                "paper_size": "A4",
                "orientation": "Portrait",
                "quality": "Normal",
                "margins": {
                    "top": 20,
                    "bottom": 20,
                    "left": 20,
                    "right": 20
                },
                "font_family": "Arial",
                "font_size": 12,
                "header_enabled": True,
                "footer_enabled": True,
                "page_numbers": True
            }
            
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print("✅ تم إنشاء ملف الإعدادات")
        
        print("\n🎉 تم تهيئة نظام الطباعة بنجاح!")
        print("\n📖 لمزيد من المعلومات، راجع ملف PRINTING_SYSTEM_GUIDE.md")
        print("🚀 يمكنك الآن استخدام نظام الطباعة في تطبيقك")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في تهيئة النظام: {e}")
        return False

def test_printing_system():
    """اختبار سريع لنظام الطباعة"""
    
    print("\n🧪 اختبار نظام الطباعة...")
    
    try:
        from core.printing import print_manager, TemplateType
        
        # بيانات تجريبية
        test_student = {
            'id': 1,
            'name': 'اختبار الطباعة',
            'school_name': 'مدرسة الاختبار',
            'grade': 'الصف الأول',
            'section': 'أ',
            'gender': 'ذكر',
            'phone': '1234567890',
            'status': 'نشط',
            'total_fee': 100000,
            'start_date': '2024-01-01'
        }
        
        # اختبار تقديم القالب
        from core.printing import TemplateManager
        template_manager = TemplateManager()
        
        html_content = template_manager.render_template(
            TemplateType.STUDENT_REPORT,
            {'student': test_student}
        )
        
        if html_content and len(html_content) > 100:
            print("✅ نظام القوالب يعمل بشكل صحيح")
        else:
            print("❌ مشكلة في نظام القوالب")
            return False
        
        print("✅ جميع الاختبارات نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ فشل الاختبار: {e}")
        return False

def create_example_usage():
    """إنشاء ملف مثال للاستخدام"""
    
    example_code = '''#!/usr/bin/env python3
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
'''
    
    example_file = Path(__file__).parent / "printing_usage_example.py"
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(example_code)
    
    print(f"✅ تم إنشاء ملف المثال: {example_file}")

def main():
    """الدالة الرئيسية"""
    
    print("=" * 60)
    print("🖨️  إعداد نظام الطباعة الموحد للتطبيق  🖨️")
    print("=" * 60)
    
    # تهيئة النظام
    if setup_printing_system():
        # اختبار النظام
        if test_printing_system():
            # إنشاء ملف المثال
            create_example_usage()
            
            print("\n" + "=" * 60)
            print("✅ تم إعداد نظام الطباعة بنجاح!")
            print("=" * 60)
            print("\nالخطوات التالية:")
            print("1. راجع ملف PRINTING_SYSTEM_GUIDE.md للتوثيق الكامل")
            print("2. جرب الأمثلة في printing_usage_example.py")
            print("3. شغل python test_printing_system.py لاختبار شامل")
            print("4. أضف الطباعة لصفحاتك باستخدام الأمثلة")
            
        else:
            print("\n❌ فشل في اختبار النظام")
            return False
    else:
        print("\n❌ فشل في تهيئة النظام")
        return False
    
    return True

if __name__ == "__main__":
    main()
