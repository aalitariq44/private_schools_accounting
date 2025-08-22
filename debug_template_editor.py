#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح وتصحيح محرر القالب
"""

import sys
import logging
from pathlib import Path

# إعداد السجلات
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_imports():
    """فحص جميع الاستيرادات المطلوبة"""
    
    print("🔍 فحص الاستيرادات...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5.QtWidgets")
    except ImportError as e:
        print(f"❌ PyQt5.QtWidgets: {e}")
        return False
    
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        print("✅ QWebEngineView")
    except ImportError as e:
        print(f"❌ QWebEngineView: {e}")
        return False
    
    try:
        from core.pdf.student_id_generator import StudentIDGenerator
        print("✅ StudentIDGenerator")
    except ImportError as e:
        print(f"❌ StudentIDGenerator: {e}")
        return False
    
    try:
        from templates.id_template import TEMPLATE_ELEMENTS
        print("✅ TEMPLATE_ELEMENTS")
    except ImportError as e:
        print(f"❌ TEMPLATE_ELEMENTS: {e}")
        return False
    
    return True

def check_template_elements():
    """فحص عناصر القالب"""
    
    print("\n🔍 فحص عناصر القالب...")
    
    try:
        from templates.id_template import TEMPLATE_ELEMENTS
        
        print(f"عدد العناصر: {len(TEMPLATE_ELEMENTS)}")
        
        for element_name, element_data in TEMPLATE_ELEMENTS.items():
            print(f"  📝 {element_name}: {type(element_data)}")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في فحص القالب: {e}")
        return False

def test_pdf_generator():
    """اختبار مولد PDF"""
    
    print("\n🔍 اختبار مولد PDF...")
    
    try:
        from core.pdf.student_id_generator import StudentIDGenerator
        
        # بيانات تجريبية
        test_data = {
            'student_name': 'اختبار PDF',
            'class_name': 'الصف الأول',
            'student_id': '001',
            'school_name': 'مدرسة الاختبار'
        }
        
        # مسار ملف اختبار
        import tempfile
        test_path = Path(tempfile.gettempdir()) / "test_pdf.pdf"
        
        # إنشاء المولد
        generator = StudentIDGenerator()
        
        print("📄 إنشاء PDF تجريبي...")
        success = generator.generate_student_ids(
            students_data=[test_data],
            output_path=str(test_path),
            school_name="مدرسة الاختبار",
            custom_title="اختبار PDF"
        )
        
        if success and test_path.exists():
            print(f"✅ تم إنشاء PDF بنجاح: {test_path}")
            print(f"📏 حجم الملف: {test_path.stat().st_size} بايت")
            return True
        else:
            print("❌ فشل في إنشاء PDF")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار PDF: {e}")
        return False

def test_template_editor_simple():
    """اختبار بسيط لمحرر القالب"""
    
    print("\n🔍 اختبار محرر القالب...")
    
    try:
        # لا ننشئ التطبيق، فقط نتحقق من إنشاء الكلاس
        from ui.dialogs.template_editor import TemplateEditor, LivePDFGenerator
        
        print("✅ تم استيراد TemplateEditor")
        print("✅ تم استيراد LivePDFGenerator")
        
        # اختبار إنشاء مولد PDF
        generator = LivePDFGenerator()
        print("✅ تم إنشاء LivePDFGenerator")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار المحرر: {e}")
        logging.exception("تفاصيل الخطأ:")
        return False

def main():
    """الدالة الرئيسية للفحص"""
    
    print("🔧 فحص وتصحيح محرر القالب مع معاينة PDF\n")
    
    # تغيير المجلد للمشروع
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    tests = [
        ("فحص الاستيرادات", check_imports),
        ("فحص عناصر القالب", check_template_elements),
        ("اختبار مولد PDF", test_pdf_generator),
        ("اختبار محرر القالب", test_template_editor_simple),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: نجح")
            else:
                print(f"❌ {test_name}: فشل")
                
        except Exception as e:
            print(f"💥 {test_name}: خطأ غير متوقع - {e}")
            results.append((test_name, False))
    
    # النتائج النهائية
    print(f"\n{'='*50}")
    print("📊 ملخص النتائج")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 النتيجة النهائية: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! المحرر جاهز للاستخدام.")
        return 0
    else:
        print("⚠️ هناك مشاكل تحتاج إلى إصلاح.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
