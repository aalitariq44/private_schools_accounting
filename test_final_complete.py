#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي شامل للتصميم الجديد
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pdf.student_id_generator import generate_student_ids_pdf
from datetime import datetime

def test_full_page():
    """اختبار صفحة كاملة بـ 8 طلاب"""
    print("=== اختبار صفحة كاملة من الهويات الجديدة ===")
    
    # 8 طلاب لملء صفحة كاملة
    students = [
        {"id": 101, "name": "أحمد محمد الأحمد", "grade": "الأول الابتدائي", "school_name": "مدرسة النور الأهلية"},
        {"id": 102, "name": "فاطمة علي السعدي", "grade": "الثاني الابتدائي", "school_name": "مدرسة الأمل الأهلية"},
        {"id": 103, "name": "محمد حسن الخطيب", "grade": "الثالث الابتدائي", "school_name": "مدرسة الشروق الأهلية"},
        {"id": 104, "name": "زينب أحمد المحمدي", "grade": "الرابع الابتدائي", "school_name": "مدرسة النجاح الأهلية"},
        {"id": 105, "name": "عبدالله سعد الراشد", "grade": "الخامس الابتدائي", "school_name": "مدرسة الرشيد الأهلية"},
        {"id": 106, "name": "مريم عادل البكري", "grade": "السادس الابتدائي", "school_name": "مدرسة المجد الأهلية"},
        {"id": 107, "name": "يوسف إبراهيم العلي", "grade": "الأول المتوسط", "school_name": "مدرسة الفجر الأهلية"},
        {"id": 108, "name": "نور الهدى صالح", "grade": "الثاني المتوسط", "school_name": "مدرسة الهداية الأهلية"}
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / f"final_design_test_{timestamp}.pdf"
    
    print(f"📄 إنشاء: {output_file.name}")
    print(f"👥 عدد الطلاب: {len(students)} (صفحة كاملة)")
    
    result = generate_student_ids_pdf(
        students,
        str(output_file),
        "مدرسة عامة",
        "هوية طالب"
    )
    
    if result:
        print("✅ تم إنشاء الملف بنجاح!")
        print(f"📊 حجم الملف: {output_file.stat().st_size / 1024:.2f} KB")
        
        print("\n📋 الطلاب في الصفحة:")
        for i, student in enumerate(students, 1):
            print(f"  {i}. {student['name']}")
            print(f"     🏫 {student['school_name']}")
            print(f"     📚 {student['grade']} | 🆔 {student['id']}")
        
        try:
            os.startfile(str(output_file))
            print(f"\n📖 تم فتح الملف للمراجعة النهائية")
        except:
            print(f"\nيمكنك فتح الملف: {output_file}")
        
        return True
    else:
        print("❌ فشل في إنشاء الملف")
        return False

def test_multiple_pages():
    """اختبار عدة صفحات"""
    print("\n=== اختبار عدة صفحات ===")
    
    # 15 طالب لاختبار صفحتين
    students = []
    schools = [
        "مدرسة النور الأهلية", "مدرسة الأمل الأهلية", "مدرسة الشروق الأهلية",
        "مدرسة النجاح الأهلية", "مدرسة الرشيد الأهلية"
    ]
    grades = [
        "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
        "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي"
    ]
    
    for i in range(15):
        student = {
            "id": 200 + i,
            "name": f"الطالب رقم {i + 1}",
            "grade": grades[i % len(grades)],
            "school_name": schools[i % len(schools)]
        }
        students.append(student)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / f"multi_page_test_{timestamp}.pdf"
    
    result = generate_student_ids_pdf(
        students,
        str(output_file),
        "مدرسة عامة",
        "هوية طالب"
    )
    
    if result:
        pages = (len(students) + 7) // 8
        print(f"✅ تم إنشاء ملف {pages} صفحات بنجاح!")
        try:
            os.startfile(str(output_file))
        except:
            pass
        return True
    else:
        print("❌ فشل في إنشاء الملف متعدد الصفحات")
        return False

def main():
    """الاختبار النهائي الشامل"""
    print("🎨 الاختبار النهائي الشامل للتصميم الجديد")
    print("=" * 55)
    
    success1 = test_full_page()
    success2 = test_multiple_pages()
    
    print("\n" + "=" * 55)
    if success1 and success2:
        print("🎉 اكتمل تطوير التصميم الجديد بنجاح!")
        print()
        print("📋 ملخص التحسينات:")
        print("  ✨ عنوان 'هوية طالب' ثابت ومُبرز في الأعلى")
        print("  🏫 اسم مدرسة كل طالب ظاهر بوضوح")
        print("  📏 خطوط أكبر وأوضح للعناوين (حجم 14 و 12)")
        print("  🎯 ترتيب احترافي مع تسميات واضحة")
        print("  🌈 ألوان أنيقة ومتناسقة")
        print("  📐 خطوط فاصلة للتنظيم")
        print("  📦 إطارات محسّنة مع ألوان جميلة")
        print("  🎯 حفظ حجم ماستر كارد (85.60 × 53.98 مم)")
        print()
        print("📁 الملفات جاهزة للاستخدام!")
    else:
        print("❌ هناك مشكلة تحتاج مراجعة")

if __name__ == "__main__":
    main()
