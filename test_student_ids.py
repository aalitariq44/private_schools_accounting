#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام إنشاء هويات الطلاب
"""

import sys
import os
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# تهيئة المسارات
import config

from core.pdf.student_id_generator import generate_student_ids_pdf

def test_student_ids():
    """اختبار إنشاء هويات الطلاب"""
    
    print("🧪 اختبار نظام إنشاء هويات الطلاب...")
    
    # بيانات طلاب تجريبية
    test_students = [
        {
            "name": "أحمد محمد علي السامرائي",
            "grade": "الصف الأول الابتدائي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "فاطمة حسن محمود الجبوري", 
            "grade": "الصف الثاني الابتدائي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "محمد عبدالله أحمد",
            "grade": "الصف الثالث الابتدائي", 
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "نور الهدى صالح محمد",
            "grade": "الصف الرابع الابتدائي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "عمار طارق حسين علي",
            "grade": "الصف الخامس الابتدائي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "رنا عادل صالح",
            "grade": "الصف السادس الابتدائي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "حسام الدين محمد عبدالرحمن",
            "grade": "الصف الأول متوسط",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "زينب علي حسن",
            "grade": "الصف الثاني متوسط",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "يوسف إبراهيم محمد",
            "grade": "الصف الثالث متوسط",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "مريم عبدالله صالح",
            "grade": "الصف الأول ثانوي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "حيدر عمار طارق",
            "grade": "الصف الثاني ثانوي",
            "school_name": "مدرسة النور الأهلية"
        },
        {
            "name": "سارة محمود علي",
            "grade": "الصف الثالث ثانوي",
            "school_name": "مدرسة النور الأهلية"
        }
    ]
    
    # تحديد مسار الإخراج
    output_path = project_root / "test_student_ids_output.pdf"
    
    print(f"📝 إنشاء هويات لـ {len(test_students)} طالب...")
    
    # إنشاء الهويات
    success = generate_student_ids_pdf(
        test_students,
        str(output_path),
        "مدرسة النور الأهلية", 
        "هوية طالب"
    )
    
    if success:
        print(f"✅ تم إنشاء الهويات بنجاح!")
        print(f"📄 الملف: {output_path}")
        
        # فتح الملف إذا كان موجوداً
        if output_path.exists():
            print(f"📊 حجم الملف: {output_path.stat().st_size / 1024:.1f} KB")
            
            # محاولة فتح الملف
            try:
                import subprocess
                subprocess.Popen([str(output_path)], shell=True)
                print("🖥️ تم فتح الملف...")
            except Exception as e:
                print(f"⚠️ لم يتم فتح الملف تلقائياً: {e}")
        else:
            print("❌ الملف غير موجود!")
            return False
            
    else:
        print("❌ فشل في إنشاء الهويات!")
        return False
    
    return True

def test_template_functions():
    """اختبار وظائف القالب"""
    
    print("\n🧪 اختبار وظائف القالب...")
    
    try:
        from templates.id_template import save_template_as_json, load_template_from_json, ensure_default_template
        
        # إنشاء القالب الافتراضي
        ensure_default_template()
        print("✅ تم إنشاء القالب الافتراضي")
        
        # حفظ القالب كـ JSON
        template_file = project_root / "test_template.json"
        save_template_as_json(template_file)
        print(f"✅ تم حفظ القالب: {template_file}")
        
        # تحميل القالب
        if template_file.exists():
            success = load_template_from_json(template_file)
            if success:
                print("✅ تم تحميل القالب بنجاح")
            else:
                print("❌ فشل في تحميل القالب")
                
            # حذف الملف التجريبي
            template_file.unlink()
            print("🗑️ تم حذف الملف التجريبي")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار وظائف القالب: {e}")
        return False

if __name__ == "__main__":
    print("🚀 بدء اختبار نظام إنشاء هويات الطلاب\n")
    
    # اختبار وظائف القالب
    template_success = test_template_functions()
    
    # اختبار إنشاء الهويات
    ids_success = test_student_ids()
    
    print(f"\n📊 نتائج الاختبار:")
    print(f"   🔧 وظائف القالب: {'✅ نجح' if template_success else '❌ فشل'}")
    print(f"   📄 إنشاء الهويات: {'✅ نجح' if ids_success else '❌ فشل'}")
    
    if template_success and ids_success:
        print("\n🎉 جميع الاختبارات نجحت! نظام الهويات جاهز للاستخدام.")
    else:
        print("\n⚠️ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء.")
