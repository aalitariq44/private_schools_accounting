#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح تخطيط هويات الطلاب
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع إلى sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pdf.student_id_generator import generate_student_ids_pdf
from templates.id_template import verify_layout_fits, get_optimized_layout

def test_layout_verification():
    """اختبار التحقق من التخطيط"""
    print("=== اختبار التحقق من التخطيط ===")
    
    layout_check = verify_layout_fits()
    
    print(f"هل العرض مناسب: {layout_check['width_fits']}")
    print(f"هل الارتفاع مناسب: {layout_check['height_fits']}")
    print(f"العرض المطلوب: {layout_check['total_width']:.2f} نقطة")
    print(f"العرض المتاح: {layout_check['a4_width']:.2f} نقطة")
    print(f"هامش العرض: {layout_check['width_margin']:.2f} نقطة")
    print(f"الارتفاع المطلوب: {layout_check['total_height']:.2f} نقطة")
    print(f"الارتفاع المتاح: {layout_check['a4_height']:.2f} نقطة")
    print(f"هامش الارتفاع: {layout_check['height_margin']:.2f} نقطة")
    
    if not layout_check['width_fits'] or not layout_check['height_fits']:
        print("\n=== محاولة الحصول على تخطيط محسن ===")
        optimized = get_optimized_layout()
        if optimized:
            print(f"هامش الصفحة X: {optimized['page_margin_x']:.2f}")
            print(f"هامش الصفحة Y: {optimized['page_margin_y']:.2f}")
            print(f"المسافة بين البطاقات X: {optimized['card_spacing_x']:.2f}")
            print(f"المسافة بين البطاقات Y: {optimized['card_spacing_y']:.2f}")
        else:
            print("لا يمكن إيجاد تخطيط محسن")
    else:
        print("\nالتخطيط الحالي مناسب!")

def test_student_ids_generation():
    """اختبار إنشاء هويات الطلاب مع التخطيط الجديد"""
    print("\n=== اختبار إنشاء هويات الطلاب ===")
    
    # بيانات طلاب للاختبار (15 طالب - أكثر من صفحة واحدة)
    test_students = []
    
    for i in range(1, 16):
        student = {
            "name": f"الطالب رقم {i}",
            "grade": f"الصف {(i % 6) + 1}",
            "id": f"STD{i:03d}"
        }
        test_students.append(student)
    
    output_file = project_root / "test_layout_fixed.pdf"
    
    print(f"إنشاء ملف PDF لـ {len(test_students)} طالب...")
    
    result = generate_student_ids_pdf(
        test_students,
        str(output_file),
        "مدرسة الاختبار الأهلية",
        "هوية طالب"
    )
    
    if result:
        print(f"✅ تم إنشاء الملف بنجاح: {output_file}")
        print(f"📁 حجم الملف: {output_file.stat().st_size / 1024:.2f} KB")
        
        # فتح الملف للمعاينة
        try:
            os.startfile(str(output_file))
            print("📖 تم فتح الملف للمعاينة")
        except:
            print("يمكنك فتح الملف يدوياً للمعاينة")
            
    else:
        print("❌ فشل في إنشاء الملف")

def main():
    """الدالة الرئيسية"""
    print("اختبار إصلاح تخطيط هويات الطلاب")
    print("=" * 40)
    
    test_layout_verification()
    test_student_ids_generation()
    
    print("\n" + "=" * 40)
    print("انتهاء الاختبار")

if __name__ == "__main__":
    main()
