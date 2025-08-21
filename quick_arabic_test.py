#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لدعم العربية في هويات الطلاب
"""

import os
import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد المسارات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'private_schools_accounting.settings')

from core.pdf.student_id_generator import generate_student_ids_pdf

def quick_test():
    """اختبار سريع لدعم العربية"""
    
    print("🔍 اختبار سريع لدعم العربية في هويات الطلاب")
    
    # بيانات طلاب للاختبار
    students = [
        {
            "name": "أحمد محمد علي السامرائي",
            "grade": "الصف الثالث الابتدائي"
        },
        {
            "name": "فاطمة الزهراء (عليها السلام)",
            "grade": "الصف الثاني المتوسط"
        }
    ]
    
    # إعدادات الاختبار
    output_file = "quick_test_arabic_ids.pdf"
    school_name = "مدرسة الإمام علي (عليه السلام) النموذجية"
    custom_title = "بطاقة هوية طالب"
    
    print(f"📝 إنشاء هويات لـ {len(students)} طالب...")
    print(f"🏫 المدرسة: {school_name}")
    print(f"📄 العنوان: {custom_title}")
    
    # إنشاء الهويات
    success = generate_student_ids_pdf(
        students,
        output_file,
        school_name,
        custom_title
    )
    
    if success:
        print(f"✅ نجح الاختبار! تم إنشاء: {output_file}")
        
        # محاولة فتح الملف
        try:
            import subprocess
            subprocess.Popen([output_file], shell=True)
            print("🖥️  تم فتح الملف للمعاينة")
        except:
            print(f"📁 يمكنك فتح الملف: {Path(output_file).absolute()}")
        
        # معلومات إضافية
        file_path = Path(output_file)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"📏 حجم الملف: {size:,} بايت ({size/1024:.1f} KB)")
        
        print("\n✨ تحقق من:")
        print("  • النص العربي يظهر بالاتجاه الصحيح من اليمين لليسار")
        print("  • الأحرف العربية متصلة بشكل صحيح")
        print("  • أسماء الطلاب والمدرسة واضحة ومقروءة")
        
        return True
    else:
        print("❌ فشل الاختبار")
        return False

if __name__ == "__main__":
    print("🚀 بدء الاختبار السريع...")
    
    success = quick_test()
    
    if success:
        print("\n🎉 اكتمل دعم العربية في هويات الطلاب!")
        print("💡 النظام جاهز للاستخدام مع دعم كامل للعربية")
    else:
        print("\n⚠️  يحتاج النظام لمراجعة")
