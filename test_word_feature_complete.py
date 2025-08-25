# -*- coding: utf-8 -*-
"""
اختبار شامل للميزة الجديدة - طباعة Word
"""

import sys
import os

# إضافة المسار الجذر للمشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """اختبار استيراد جميع المكونات المطلوبة"""
    print("=" * 50)
    print("اختبار الاستيرادات...")
    print("=" * 50)
    
    try:
        # اختبار مكتبة python-docx
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        print("✓ مكتبة python-docx متوفرة")
        
        # اختبار word_manager
        from core.printing.word_manager import WordManager, create_students_word_document
        print("✓ word_manager متوفر")
        
        
        # اختبار print_manager المحدث
        from core.printing.print_manager import print_students_list
        print("✓ print_manager محدث")
        
        print("\n✅ جميع الاستيرادات نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاستيرادات: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_word_creation():
    """اختبار إنشاء ملف Word مع بيانات فعلية"""
    print("\n" + "=" * 50)
    print("اختبار إنشاء ملف Word...")
    print("=" * 50)
    
    try:
        from core.printing.word_manager import create_students_word_document
        
        # بيانات تجريبية شاملة
        test_students = [
            {
                'id': 1,
                'name': 'أحمد محمد علي الزهراني',
                'school_name': 'مدرسة النور الأهلية للبنين',
                'grade': 'الرابع الابتدائي',
                'section': 'أ',
                'gender': 'ذكر',
                'phone': '07901234567',
                'status': 'نشط',
                'total_fee': '1500000 د.ع',
                'total_paid': '1200000 د.ع',
                'remaining': '300000 د.ع'
            },
            {
                'id': 2,
                'name': 'فاطمة حسين كريم الموسوي',
                'school_name': 'مدرسة النور الأهلية للبنات',
                'grade': 'الثالث الابتدائي',
                'section': 'ب',
                'gender': 'أنثى',
                'phone': '07801234567',
                'status': 'نشط',
                'total_fee': '1400000 د.ع',
                'total_paid': '1400000 د.ع',
                'remaining': '0 د.ع'
            },
            {
                'id': 3,
                'name': 'سارة عبد الله جاسم الطائي',
                'school_name': 'مدرسة المستقبل الأهلية',
                'grade': 'الخامس الابتدائي',
                'section': 'أ',
                'gender': 'أنثى',
                'phone': '07701234567',
                'status': 'نشط',
                'total_fee': '1600000 د.ع',
                'total_paid': '800000 د.ع',
                'remaining': '800000 د.ع'
            },
            {
                'id': 4,
                'name': 'محمد عبد الرحمن الكاظمي',
                'school_name': 'مدرسة النور الأهلية للبنين',
                'grade': 'السادس الابتدائي',
                'section': 'ج',
                'gender': 'ذكر',
                'phone': '07601234567',
                'status': 'نشط',
                'total_fee': '1700000 د.ع',
                'total_paid': '1000000 د.ع',
                'remaining': '700000 د.ع'
            },
            {
                'id': 5,
                'name': 'زينب أحمد هاشم البغدادي',
                'school_name': 'مدرسة المستقبل الأهلية',
                'grade': 'الأول المتوسط',
                'section': 'أ',
                'gender': 'أنثى',
                'phone': '07501234567',
                'status': 'نشط',
                'total_fee': '1800000 د.ع',
                'total_paid': '1800000 د.ع',
                'remaining': '0 د.ع'
            }
        ]
        
        # جميع الأعمدة المحتملة
        selected_columns = {
            'id': 'المعرف',
            'name': 'الاسم الكامل',
            'school_name': 'المدرسة',
            'grade': 'الصف الدراسي',
            'section': 'الشعبة',
            'gender': 'الجنس',
            'phone': 'رقم الهاتف',
            'status': 'حالة الطالب',
            'total_fee': 'إجمالي الرسوم',
            'total_paid': 'المبلغ المدفوع',
            'remaining': 'المبلغ المتبقي'
        }
        
        # معلومات فلتر تفصيلية
        filter_info = "المدرسة: جميع المدارس - الصف: جميع الصفوف - الشعبة: جميع الشعب - الحالة: نشط - الجنس: جميع الطلاب - حالة الدفع: الجميع - مرتب حسب: الاسم الكامل (تصاعدي)"
        
        print(f"إنشاء ملف Word لـ {len(test_students)} طلاب...")
        print(f"عدد الأعمدة: {len(selected_columns)}")
        
        filepath = create_students_word_document(test_students, selected_columns, filter_info)
        
        if filepath and os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024  # بالكيلوبايت
            print(f"✅ تم إنشاء ملف Word بنجاح!")
            print(f"   المسار: {filepath}")
            print(f"   حجم الملف: {file_size:.1f} KB")
            return True
        else:
            print("❌ فشل في إنشاء ملف Word")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف Word: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("🧪 بدء الاختبارات الشاملة للميزة الجديدة")
    print("📝 ميزة: طباعة قائمة الطلاب في Word")
    print("📅 التاريخ:", "25 أغسطس 2025")
    
    results = {}
    
    # تشغيل الاختبارات
    results['imports'] = test_imports()
    results['word_creation'] = test_word_creation()
    
    # تقرير النتائج
    print("\n" + "=" * 50)
    print("📊 ملخص نتائج الاختبارات")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{test_name}: {status}")
    
    print(f"\nالنتيجة النهائية: {passed_tests}/{total_tests} اختبارات نجحت")
    
    if passed_tests == total_tests:
        print("🎉 جميع الاختبارات نجحت! الميزة جاهزة للاستخدام.")
    else:
        print("⚠️  بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    run_all_tests()
