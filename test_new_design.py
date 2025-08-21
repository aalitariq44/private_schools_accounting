#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التصميم الجديد المحسّن لهويات الطلاب
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع إلى sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pdf.student_id_generator import generate_student_ids_pdf
from datetime import datetime

def test_new_design():
    """اختبار التصميم الجديد لهويات الطلاب"""
    print("=== اختبار التصميم الجديد المحسّن لهويات الطلاب ===")
    
    # بيانات طلاب للاختبار مع أسماء مدارس مختلفة
    test_students = [
        {
            "id": 1001,
            "name": "أحمد محمد علي الخطيب",
            "grade": "الأول الابتدائي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "id": 1002,
            "name": "فاطمة حسن محمود السعدي",
            "grade": "الثاني الابتدائي",
            "school_name": "مدرسة الأمل الأهلية"
        },
        {
            "id": 1003,
            "name": "محمد عبدالله أحمد الزهراني",
            "grade": "الثالث الابتدائي",
            "school_name": "مدرسة الشروق الأهلية"
        },
        {
            "id": 1004,
            "name": "نور الهدى صالح العتيبي",
            "grade": "الرابع الابتدائي",
            "school_name": "مدرسة النجاح الأهلية"
        },
        {
            "id": 1005,
            "name": "عمار طارق حسين المحمدي",
            "grade": "الخامس الابتدائي",
            "school_name": "مدرسة الرشيد الأهلية"
        },
        {
            "id": 1006,
            "name": "زينب علي حسام الدين",
            "grade": "السادس الابتدائي",
            "school_name": "مدرسة المجد الأهلية"
        },
        {
            "id": 1007,
            "name": "يوسف إبراهيم محمد العلي",
            "grade": "الأول المتوسط",
            "school_name": "مدرسة الفجر الأهلية"
        },
        {
            "id": 1008,
            "name": "مريم عادل صالح البكري",
            "grade": "الثاني المتوسط",
            "school_name": "مدرسة الهداية الأهلية"
        }
    ]
    
    # إنشاء اسم ملف فريد
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / f"student_ids_new_design_{timestamp}.pdf"
    
    print(f"📄 إنشاء ملف: {output_file.name}")
    print(f"📊 عدد الطلاب: {len(test_students)}")
    
    # إنشاء PDF مع التصميم الجديد
    # سنستخدم اسم مدرسة عامة في البداية
    result = generate_student_ids_pdf(
        test_students,
        str(output_file),
        "مدرسة عامة",  # هذا سيتم تجاهله لأن كل طالب له مدرسته
        "هوية طالب"
    )
    
    if result:
        print(f"✅ تم إنشاء الملف بنجاح!")
        print(f"📁 حجم الملف: {output_file.stat().st_size / 1024:.2f} KB")
        print(f"📄 عدد الصفحات المتوقع: {(len(test_students) + 7) // 8}")
        
        # عرض قائمة بالطلاب والمدارس
        print("\n📋 الطلاب والمدارس المُضمنة:")
        for i, student in enumerate(test_students, 1):
            print(f"  {i:2d}. {student['name']}")
            print(f"      📚 {student['grade']} - 🏫 {student['school_name']}")
            print(f"      🆔 رقم الهوية: {student['id']}")
            print()
        
        print("\n🎨 المميزات الجديدة في التصميم:")
        print("   ✨ عنوان 'هوية طالب' ثابت ومُبرز في الأعلى")
        print("   🏫 اسم مدرسة الطالب الخاصة (وليس المؤسسة الرئيسية)")
        print("   📏 خطوط أكبر وأوضح للعناوين الرئيسية")
        print("   🎯 ترتيب محسّن مع تسميات واضحة")
        print("   🌈 ألوان أنيقة ومتناسقة")
        print("   📐 خطوط فاصلة لتحسين التنظيم")
        print("   📦 إطارات محسّنة للصورة ورمز QR")
        
        # محاولة فتح الملف
        try:
            os.startfile(str(output_file))
            print(f"\n📖 تم فتح الملف للمعاينة")
        except Exception as e:
            print(f"\n📖 يمكنك فتح الملف يدوياً: {output_file}")
            
        return True
    else:
        print("❌ فشل في إنشاء الملف")
        return False

def test_single_school_cards():
    """اختبار هويات لمدرسة واحدة فقط"""
    print("\n=== اختبار هويات مدرسة واحدة ===")
    
    # بيانات طلاب لمدرسة واحدة
    single_school_students = [
        {
            "id": 2001,
            "name": "خالد أحمد الراشد",
            "grade": "الأول الثانوي",
            "school_name": "مدرسة الحكمة الأهلية"
        },
        {
            "id": 2002,
            "name": "عائشة محمد الزهراني",
            "grade": "الثاني الثانوي",
            "school_name": "مدرسة الحكمة الأهلية"
        },
        {
            "id": 2003,
            "name": "عبدالرحمن سعد المطيري",
            "grade": "الثالث الثانوي",
            "school_name": "مدرسة الحكمة الأهلية"
        }
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / f"single_school_ids_{timestamp}.pdf"
    
    result = generate_student_ids_pdf(
        single_school_students,
        str(output_file),
        "مدرسة الحكمة الأهلية",
        "هوية طالب"
    )
    
    if result:
        print(f"✅ تم إنشاء ملف المدرسة الواحدة: {output_file.name}")
        try:
            os.startfile(str(output_file))
        except:
            pass
        return True
    else:
        print("❌ فشل في إنشاء ملف المدرسة الواحدة")
        return False

def main():
    """الدالة الرئيسية"""
    print("🎨 اختبار التصميم الجديد المحسّن لهويات الطلاب")
    print("=" * 60)
    
    success1 = test_new_design()
    success2 = test_single_school_cards()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 تم تطبيق التصميم الجديد بنجاح!")
        print("📋 المطلوب للمراجعة:")
        print("   🔍 تحقق من وضوح النصوص وحجم الخطوط")
        print("   🎨 تأكد من جمال التصميم والترتيب")
        print("   📏 تحقق من أن حجم الهوية مازال بحجم ماستر كارد")
        print("   🏫 تأكد من ظهور اسم مدرسة الطالب الصحيحة")
    else:
        print("❌ هناك مشكلة تحتاج إلى حل")

if __name__ == "__main__":
    main()
