#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مقارنة دعم العربية في هويات الطلاب - قبل وبعد التحسين
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد المسارات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'private_schools_accounting.settings')

import config
from core.pdf.student_id_generator import generate_student_ids_pdf, generate_single_student_id_preview

def create_comparison_test():
    """إنشاء اختبار مقارنة لدعم العربية"""
    
    print("🔍 اختبار مقارنة دعم العربية في هويات الطلاب")
    print("=" * 60)
    
    # بيانات اختبار تحتوي على نصوص عربية متنوعة
    test_cases = [
        {
            "name": "أحمد محمد علي السامرائي البغدادي الطويل جداً",
            "grade": "الصف الأول الابتدائي النموذجي",
            "description": "نص طويل جداً يختبر قطع النص"
        },
        {
            "name": "فاطمة الزهراء (عليها السلام)",
            "grade": "الثاني المتوسط",
            "description": "نص يحتوي على أقواس ورموز"
        },
        {
            "name": "محمد عبدالله الحسني",
            "grade": "الثالث الإعدادي العلمي",
            "description": "نص متوسط الطول"
        },
        {
            "name": "نور",
            "grade": "الرابع",
            "description": "نص قصير"
        },
        {
            "name": "عبدالرحمن عبدالرحيم عبدالكريم عبدالعظيم الكربلائي النجفي البصري الموصلي",
            "grade": "الخامس الإعدادي الأدبي للمتفوقين والموهوبين",
            "description": "نص طويل جداً للاختبار القاسي"
        }
    ]
    
    # إعدادات اختبار مختلفة
    test_schools = [
        "مدرسة الإمام علي (عليه السلام) النموذجية",
        "ثانوية السيدة زينب (عليها السلام) للبنات المتفوقات",
        "إعدادية الإمام الحسين (ع) الأهلية للبنين والبنات - فرع الكرادة الشرقية",
        "مدرسة"  # نص قصير
    ]
    
    custom_titles = [
        "بطاقة هوية طالب",
        "هوية طالب/طالبة",
        "بطاقة شخصية",
        "هوية"
    ]
    
    # إنشاء مجلد النتائج
    results_dir = Path("arabic_comparison_results")
    results_dir.mkdir(exist_ok=True)
    
    print(f"📁 مجلد النتائج: {results_dir.absolute()}")
    
    # اختبار 1: هويات متعددة مع تحديات مختلفة
    print("\n📋 اختبار 1: هويات متعددة مع نصوص متنوعة")
    multi_output = results_dir / "test_multiple_ids_arabic.pdf"
    
    success = generate_student_ids_pdf(
        test_cases,
        str(multi_output),
        test_schools[0],  # اسم مدرسة طويل
        custom_titles[0]
    )
    
    if success:
        print(f"✅ نجح: {multi_output.name}")
        file_size = multi_output.stat().st_size
        print(f"📏 حجم الملف: {file_size:,} بايت")
    else:
        print(f"❌ فشل: {multi_output.name}")
    
    # اختبار 2: معاينات فردية لكل حالة اختبار
    print("\n🔍 اختبار 2: معاينات فردية لحالات مختلفة")
    
    for i, test_case in enumerate(test_cases):
        preview_file = results_dir / f"preview_{i+1}_{test_case['name'][:20].replace(' ', '_')}.pdf"
        school = test_schools[i % len(test_schools)]
        title = custom_titles[i % len(custom_titles)]
        
        print(f"  {i+1}. {test_case['description']}")
        print(f"     الطالب: {test_case['name']}")
        print(f"     المدرسة: {school}")
        print(f"     العنوان: {title}")
        
        success = generate_single_student_id_preview(
            test_case,
            str(preview_file),
            school,
            title
        )
        
        if success:
            print(f"     ✅ {preview_file.name}")
        else:
            print(f"     ❌ فشل في {preview_file.name}")
        print()
    
    # اختبار 3: اختبار الخطوط المختلفة
    print("🔤 اختبار 3: اختبار الخطوط العربية المختلفة")
    
    font_test_data = {
        "name": "اختبار الخطوط العربية والإنجليزية Mixed Text",
        "grade": "جميع الصفوف - All Grades",
        "description": "اختبار مزج النصوص"
    }
    
    font_test_file = results_dir / "font_test_arabic_english.pdf" 
    font_success = generate_single_student_id_preview(
        font_test_data,
        str(font_test_file),
        "مدرسة Test School العربية الإنجليزية",
        "بطاقة Student ID العربية"
    )
    
    if font_success:
        print(f"✅ اختبار الخطوط: {font_test_file.name}")
    else:
        print(f"❌ فشل اختبار الخطوط: {font_test_file.name}")
    
    # ملخص الاختبار
    print("\n" + "=" * 60)
    print("📊 ملخص اختبار دعم العربية:")
    
    results_files = list(results_dir.glob("*.pdf"))
    successful_files = [f for f in results_files if f.stat().st_size > 1000]  # أكثر من 1KB
    
    print(f"📁 الملفات المُنشأة: {len(results_files)}")
    print(f"✅ الملفات الناجحة: {len(successful_files)}")
    print(f"❌ الملفات الفاشلة: {len(results_files) - len(successful_files)}")
    
    if successful_files:
        print(f"\n📋 الملفات الناجحة:")
        for f in successful_files:
            size_kb = f.stat().st_size / 1024
            print(f"  • {f.name} ({size_kb:.1f} KB)")
        
        # محاولة فتح المجلد
        try:
            import subprocess
            subprocess.Popen(f'explorer "{results_dir.absolute()}"', shell=True)
            print(f"\n🗂️  تم فتح مجلد النتائج: {results_dir.absolute()}")
        except Exception as e:
            print(f"\n📁 يمكنك فتح مجلد النتائج يدوياً: {results_dir.absolute()}")
    
    # اختبار النص العربي الخام
    print(f"\n🔤 اختبار تشكيل النص العربي:")
    test_arabic_processing()
    
    return len(successful_files) > 0

def test_arabic_processing():
    """اختبار معالجة النص العربي"""
    
    try:
        import arabic_reshaper
        import bidi.algorithm
        
        test_texts = [
            "مدرسة الإمام علي (عليه السلام) النموذجية",
            "أحمد محمد علي السامرائي البغدادي",
            "الصف الثالث الإعدادي العلمي",
            "العام الدراسي 2025-2026",
            "بطاقة هوية طالب/طالبة"
        ]
        
        for text in test_texts:
            print(f"  النص الأصلي: {text}")
            
            # إعادة تشكيل
            reshaped = arabic_reshaper.reshape(text)
            print(f"  بعد التشكيل: {reshaped}")
            
            # تطبيق BiDi
            bidi_text = bidi.algorithm.get_display(reshaped, base_dir='R')
            print(f"  بعد BiDi: {bidi_text}")
            print()
    
    except ImportError:
        print("❌ مكتبات دعم العربية غير مثبتة")
    except Exception as e:
        print(f"❌ خطأ في اختبار النص العربي: {e}")

if __name__ == "__main__":
    print("🚀 بدء اختبار مقارنة دعم العربية في هويات الطلاب")
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = create_comparison_test()
    
    if success:
        print("\n🎉 تم اختبار دعم العربية بنجاح!")
        print("💡 تحقق من الملفات المُنشأة للتأكد من جودة دعم العربية")
        print("📝 النص العربي يجب أن يظهر بالاتجاه الصحيح من اليمين لليسار")
        print("🔤 الأحرف العربية يجب أن تكون متصلة بشكل صحيح")
    else:
        print("\n⚠️  يحتاج دعم العربية لمراجعة إضافية")
    
    print("\n📖 للمقارنة:")
    print("  • قبل التحسين: النص العربي قد يظهر مقطع أو بالاتجاه الخاطئ")
    print("  • بعد التحسين: النص العربي يظهر متصل وبالاتجاه الصحيح RTL")
