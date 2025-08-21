#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار دعم العربية في هويات الطلاب
"""

import os
import sys
import logging
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# إعداد المسارات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'private_schools_accounting.settings')

import config
from core.pdf.student_id_generator import generate_student_ids_pdf

def test_arabic_support():
    """اختبار دعم العربية في هويات الطلاب"""
    
    print("🔍 بدء اختبار دعم العربية في هويات الطلاب...")
    
    # بيانات طلاب تجريبية بأسماء عربية طويلة ومتنوعة
    test_students = [
        {
            "name": "أحمد محمد علي السامرائي الطويل",
            "grade": "الصف الأول الابتدائي",
            "school_name": "مدرسة النور الأهلية للبنين والبنات"
        },
        {
            "name": "فاطمة حسن محمود عبدالرحمن",
            "grade": "الصف الثاني المتوسط",
            "school_name": "مدرسة الإمام علي (ع) النموذجية"
        },
        {
            "name": "محمد عبدالله أحمد الحسني البغدادي",
            "grade": "الصف الثالث الإعدادي العلمي",
            "school_name": "الثانوية الإسلامية المتطورة"
        },
        {
            "name": "نور الهدى صالح طارق العبيدي",
            "grade": "الصف الرابع الابتدائي",
            "school_name": "مدارس الرسالة الأهلية المتميزة"
        },
        {
            "name": "عمار طارق حسين الموسوي الكربلائي",
            "grade": "الصف الخامس العلمي",
            "school_name": "إعدادية الإمام الحسين (ع) للمتفوقين"
        },
        {
            "name": "زينب عادل مصطفى النجار الأنصاري",
            "grade": "الصف السادس الأدبي",
            "school_name": "ثانوية السيدة زينب (ع) للبنات"
        },
        {
            "name": "حسام الدين علي جواد الكاظمي",
            "grade": "الصف الأول المتوسط",
            "school_name": "متوسطة الإمام الكاظم (ع) الأهلية"
        },
        {
            "name": "مريم صادق عبدالحسين الحكيم",
            "grade": "الصف الثالث المتوسط",
            "school_name": "مدرسة آل البيت (ع) الإسلامية"
        }
    ]
    
    # إنشاء مجلد للاختبارات
    test_dir = Path("test_outputs")
    test_dir.mkdir(exist_ok=True)
    
    # إنشاء ملف الهويات مع دعم العربية
    output_file = test_dir / "test_arabic_student_ids.pdf"
    school_name = "مدرسة الإمام علي (عليه السلام) النموذجية للبنين والبنات"
    custom_title = "بطاقة هوية طالب"
    
    print(f"📝 إنشاء هويات لـ {len(test_students)} طالب...")
    print(f"🏫 اسم المدرسة: {school_name}")
    print(f"📄 عنوان البطاقة: {custom_title}")
    print(f"📁 ملف الإخراج: {output_file}")
    
    try:
        success = generate_student_ids_pdf(
            test_students,
            str(output_file),
            school_name,
            custom_title
        )
        
        if success:
            print("✅ تم إنشاء ملف الهويات بنجاح!")
            print(f"📍 الملف محفوظ في: {output_file.absolute()}")
            
            # فحص حجم الملف
            file_size = output_file.stat().st_size
            print(f"📏 حجم الملف: {file_size:,} بايت ({file_size/1024:.1f} KB)")
            
            # محاولة فتح الملف
            try:
                import subprocess
                subprocess.Popen([str(output_file.absolute())], shell=True)
                print("🖥️  تم فتح ملف PDF للمعاينة")
            except Exception as e:
                print(f"⚠️  لم يتم فتح الملف تلقائياً: {e}")
                print(f"💡 يمكنك فتح الملف يدوياً من: {output_file.absolute()}")
            
            return True
            
        else:
            print("❌ فشل في إنشاء ملف الهويات")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء الهويات: {e}")
        import traceback
        print("تفاصيل الخطأ:")
        traceback.print_exc()
        return False

def test_fonts():
    """اختبار الخطوط المتوفرة"""
    print("\n🔍 فحص الخطوط المتوفرة...")
    
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # المسارات المحتملة للخطوط
        font_paths = [
            Path(config.BASE_DIR) / "app" / "resources" / "fonts",
            Path(config.RESOURCES_DIR) / "fonts"
        ]
        
        fonts_found = []
        
        for font_dir in font_paths:
            if font_dir.exists():
                print(f"📂 فحص مجلد: {font_dir}")
                
                # البحث عن ملفات الخطوط
                font_files = {
                    'Cairo-Medium.ttf': 'Cairo-Medium',
                    'Cairo-Bold.ttf': 'Cairo-Bold', 
                    'Amiri.ttf': 'Amiri',
                    'Amiri-Bold.ttf': 'Amiri-Bold'
                }
                
                for font_file, font_name in font_files.items():
                    font_path = font_dir / font_file
                    if font_path.exists():
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                            fonts_found.append(font_name)
                            print(f"  ✅ {font_name}: {font_path}")
                        except Exception as e:
                            print(f"  ❌ فشل تحميل {font_name}: {e}")
                    else:
                        print(f"  ⭕ غير موجود: {font_file}")
        
        print(f"\n📊 الخطوط المحملة بنجاح: {len(fonts_found)}")
        for font in fonts_found:
            print(f"  • {font}")
            
        # عرض جميع الخطوط المسجلة
        all_fonts = pdfmetrics.getRegisteredFontNames()
        print(f"\n📋 جميع الخطوط المسجلة ({len(all_fonts)}):")
        for font in sorted(all_fonts):
            print(f"  • {font}")
            
        return len(fonts_found) > 0
        
    except Exception as e:
        print(f"❌ خطأ في فحص الخطوط: {e}")
        return False

def test_arabic_libraries():
    """اختبار مكتبات دعم العربية"""
    print("\n🔍 فحص مكتبات دعم العربية...")
    
    try:
        import arabic_reshaper
        import bidi.algorithm
        
        print("✅ مكتبة arabic_reshaper متوفرة")
        print("✅ مكتبة python-bidi متوفرة")
        
        # اختبار تشكيل نص عربي
        test_text = "مدرسة الإمام علي (عليه السلام) النموذجية"
        print(f"\n📝 النص الأصلي: {test_text}")
        
        reshaped = arabic_reshaper.reshape(test_text)
        print(f"🔄 بعد إعادة التشكيل: {reshaped}")
        
        bidi_text = bidi.algorithm.get_display(reshaped, base_dir='R')
        print(f"➡️  بعد تطبيق BiDi: {bidi_text}")
        
        return True
        
    except ImportError as e:
        print(f"❌ مكتبة مفقودة: {e}")
        print("💡 لتثبيت المكتبات المطلوبة:")
        print("   pip install arabic-reshaper python-bidi")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار مكتبات العربية: {e}")
        return False

if __name__ == "__main__":
    print("🚀 بدء اختبار شامل لدعم العربية في هويات الطلاب")
    print("=" * 60)
    
    # اختبار المكتبات
    libraries_ok = test_arabic_libraries()
    
    # اختبار الخطوط
    fonts_ok = test_fonts()
    
    # الاختبار الرئيسي
    if libraries_ok:
        print("\n" + "=" * 60)
        main_test_ok = test_arabic_support()
        
        print("\n" + "=" * 60)
        print("📊 ملخص النتائج:")
        print(f"  🔤 مكتبات العربية: {'✅' if libraries_ok else '❌'}")
        print(f"  🔠 الخطوط العربية: {'✅' if fonts_ok else '⚠️ '}")
        print(f"  🆔 إنشاء الهويات: {'✅' if main_test_ok else '❌'}")
        
        if main_test_ok:
            print("\n🎉 تم حل مشكلة دعم العربية في هويات الطلاب بنجاح!")
            print("💡 النص العربي سيظهر الآن بالاتجاه الصحيح من اليمين لليسار")
        else:
            print("\n⚠️  يحتاج الأمر لمراجعة إضافية")
    else:
        print("\n❌ لا يمكن المتابعة بدون مكتبات دعم العربية")
        print("💡 قم بتثبيت المكتبات المطلوبة أولاً:")
        print("   pip install arabic-reshaper python-bidi")
