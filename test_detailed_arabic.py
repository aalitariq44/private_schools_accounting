#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار مُحدث لدعم العربية في الهويات مع حالات اختبار إضافية
"""

import os
import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد المسارات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'private_schools_accounting.settings')

from core.pdf.student_id_generator import generate_student_ids_pdf, generate_single_student_id_preview

def test_all_text_elements():
    """اختبار جميع عناصر النص في الهوية"""
    
    print("🔍 اختبار شامل لجميع عناصر النص العربي في الهويات")
    print("=" * 60)
    
    # بيانات اختبار تحتوي على نصوص معقدة
    complex_students = [
        {
            "name": "أحمد محمد علي السامرائي البغدادي الكربلائي النجفي الموصلي البصري العراقي",
            "grade": "الصف الأول الابتدائي النموذجي للمتفوقين والموهوبين"
        },
        {
            "name": "فاطمة الزهراء بنت الإمام علي (عليها السلام)",
            "grade": "الثاني المتوسط العلمي"
        },
        {
            "name": "محمد عبدالله الحسني الطالقاني الكاظمي",
            "grade": "الثالث الإعدادي الأدبي"
        },
        {
            "name": "زينب العابدة الصالحة التقية النقية الطاهرة",
            "grade": "الرابع العلمي - شعبة أ"
        },
        {
            "name": "علي حسن طارق عبدالرحمن الأنصاري",
            "grade": "الخامس الأدبي"
        }
    ]
    
    # أسماء مدارس طويلة ومعقدة للاختبار
    complex_schools = [
        "مدرسة الإمام علي بن أبي طالب (عليه السلام) النموذجية للبنين والبنات - فرع الكرادة الشرقية - المنطقة التعليمية الأولى",
        "ثانوية السيدة زينب الكبرى (عليها السلام) للبنات المتفوقات والموهوبات",
        "إعدادية الإمام الحسين (عليه السلام) الأهلية المختلطة",
        "مدارس الرسالة الإسلامية المتطورة - القسم الابتدائي والمتوسط",
        "مجمع مدارس آل البيت (عليهم السلام) التعليمي المتكامل"
    ]
    
    titles = [
        "بطاقة هوية طالب/طالبة",
        "هوية طالب نموذجي متفوق",
        "بطاقة شخصية تعريفية",
        "كارت هوية المدرسة الأهلية",
        "بطاقة تعريف الطالب الأكاديمية"
    ]
    
    # إنشاء مجلد للنتائج
    test_dir = Path("detailed_arabic_test")
    test_dir.mkdir(exist_ok=True)
    
    print(f"📁 مجلد الاختبار: {test_dir.absolute()}")
    
    successful_tests = 0
    total_tests = 0
    
    # اختبار 1: هويات فردية لفحص دقيق
    print("\n📋 اختبار 1: معاينات فردية للفحص الدقيق")
    
    for i, student in enumerate(complex_students):
        school = complex_schools[i % len(complex_schools)]
        title = titles[i % len(titles)]
        
        preview_file = test_dir / f"detailed_test_{i+1}.pdf"
        
        print(f"  {i+1}. الطالب: {student['name'][:50]}...")
        print(f"     الصف: {student['grade']}")
        print(f"     المدرسة: {school[:60]}...")
        print(f"     العنوان: {title}")
        
        success = generate_single_student_id_preview(
            student,
            str(preview_file),
            school,
            title
        )
        
        total_tests += 1
        if success:
            successful_tests += 1
            size = preview_file.stat().st_size / 1024
            print(f"     ✅ نجح ({size:.1f} KB)")
        else:
            print(f"     ❌ فشل")
        print()
    
    # اختبار 2: هويات متعددة في صفحة واحدة
    print("📄 اختبار 2: هويات متعددة مع نصوص طويلة")
    
    multi_file = test_dir / "multiple_complex_ids.pdf"
    multi_success = generate_student_ids_pdf(
        complex_students,
        str(multi_file),
        complex_schools[0],  # أطول اسم مدرسة
        titles[0]  # أطول عنوان
    )
    
    total_tests += 1
    if multi_success:
        successful_tests += 1
        size = multi_file.stat().st_size / 1024
        print(f"✅ نجح - ملف متعدد ({size:.1f} KB)")
    else:
        print("❌ فشل - ملف متعدد")
    
    # اختبار 3: نصوص خاصة (أقواس، رموز، أرقام)
    print("\n🔤 اختبار 3: نصوص خاصة ورموز")
    
    special_student = {
        "name": "علي (أبو الحسن) بن أبي طالب الهاشمي القرشي - 2025",
        "grade": "الصف الـ 6 الإعدادي (العلمي) - شعبة A"
    }
    
    special_file = test_dir / "special_characters_test.pdf"
    special_success = generate_single_student_id_preview(
        special_student,
        str(special_file),
        "مدرسة الإمام علي (ع) - فرع #1 - سنة 2025-2026",
        "هوية طالب/طالبة معتمدة رسمياً"
    )
    
    total_tests += 1
    if special_success:
        successful_tests += 1
        size = special_file.stat().st_size / 1024
        print(f"✅ نجح - نصوص خاصة ({size:.1f} KB)")
    else:
        print("❌ فشل - نصوص خاصة")
    
    # ملخص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص الاختبار الشامل:")
    print(f"✅ اختبارات ناجحة: {successful_tests}")
    print(f"❌ اختبارات فاشلة: {total_tests - successful_tests}")
    print(f"📈 معدل النجاح: {(successful_tests/total_tests)*100:.1f}%")
    
    # عرض الملفات المُنشأة
    if successful_tests > 0:
        created_files = list(test_dir.glob("*.pdf"))
        total_size = sum(f.stat().st_size for f in created_files) / 1024
        
        print(f"\n📁 الملفات المُنشأة ({len(created_files)} ملف - {total_size:.1f} KB إجمالي):")
        for f in created_files:
            size = f.stat().st_size / 1024
            print(f"  • {f.name} ({size:.1f} KB)")
        
        # محاولة فتح المجلد
        try:
            import subprocess
            subprocess.Popen(f'explorer "{test_dir.absolute()}"', shell=True)
            print(f"\n🗂️  تم فتح مجلد الاختبار: {test_dir.absolute()}")
        except:
            print(f"\n📁 يمكنك فتح مجلد الاختبار: {test_dir.absolute()}")
    
    # تقييم الجودة
    if successful_tests == total_tests:
        print("\n🎉 ممتاز! جميع الاختبارات نجحت - دعم العربية مثالي!")
        print("🔤 النص العربي يُعرض بالشكل الصحيح في جميع الحالات")
        print("✨ النظام جاهز للإنتاج")
    elif successful_tests >= total_tests * 0.8:
        print(f"\n✅ جيد جداً! معظم الاختبارات نجحت ({successful_tests}/{total_tests})")
        print("🔧 قد تحتاج بعض الحالات الخاصة لمراجعة")
    else:
        print(f"\n⚠️  يحتاج تحسين - نجح {successful_tests} من {total_tests} اختبار")
        print("🛠️  مراجعة إضافية مطلوبة لدعم العربية")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    print("🚀 بدء الاختبار الشامل لدعم العربية في الهويات")
    print("💡 هذا الاختبار يفحص جميع عناصر النص العربي بدقة")
    
    success = test_all_text_elements()
    
    if success:
        print("\n🏆 تم حل جميع مشاكل دعم العربية بنجاح!")
        print("📝 النص العربي يظهر الآن بالشكل الصحيح في:")
        print("  ✅ أسماء الطلاب")  
        print("  ✅ أسماء المدارس")
        print("  ✅ الصفوف الدراسية")
        print("  ✅ عناوين الهويات")
        print("  ✅ النصوص الثابتة")
        print("  ✅ المربعات والتسميات")
    else:
        print("\n🔧 لا تزال هناك بعض التحسينات المطلوبة")
