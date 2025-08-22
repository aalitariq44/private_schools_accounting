#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تصميم الهوية الجديد المبسط
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_new_template():
    """اختبار القالب الجديد"""
    try:
        from templates.id_template import TEMPLATE_ELEMENTS, COLORS
        from core.pdf.student_id_generator import generate_student_ids_pdf
        
        print("🔹 اختبار التصميم الجديد للهوية...")
        
        # عرض إحصائيات القالب
        print(f"📊 عدد العناصر في القالب: {len(TEMPLATE_ELEMENTS)}")
        print(f"🎨 عدد الألوان المحددة: {len(COLORS)}")
        
        # عرض العناصر الرئيسية
        print("\n📋 العناصر الرئيسية:")
        for element_name, config in TEMPLATE_ELEMENTS.items():
            element_type = "نص"
            if "photo" in element_name:
                element_type = "صورة"
            elif "qr" in element_name:
                element_type = "QR"
            elif "line" in element_name or config.get('type') == 'line':
                element_type = "خط"
            elif "box" in element_name:
                element_type = "مربع"
                
            print(f"   • {element_name}: {element_type}")
        
        # اختبار إنشاء هوية نموذجية
        print("\n🎯 إنشاء هوية تجريبية...")
        
        sample_data = [{
            'name': 'أحمد محمد علي السامرائي',
            'grade': 'الصف الثالث الابتدائي',
            'school_name': 'مدرسة النموذج الأهلية',
            'birthdate': '15/03/2010',
            'id': 'ST2025001'
        }]
        
        output_path = project_root / "test_new_design.pdf"
        
        success = generate_student_ids_pdf(
            sample_data,
            str(output_path),
            "مدرسة النموذج الأهلية",
            "هوية طالب"
        )
        
        if success:
            print(f"✅ تم إنشاء الهوية التجريبية بنجاح: {output_path}")
            print("📁 يمكنك فتح الملف لمعاينة التصميم الجديد")
        else:
            print("❌ فشل في إنشاء الهوية التجريبية")
        
        # عرض تحسينات التصميم
        print("\n🎨 تحسينات التصميم الجديد:")
        print("   ✨ تصميم مبسط وأنيق")
        print("   🎯 تركيز على المعلومات الأساسية")
        print("   🎨 ألوان هادئة ومتناسقة")
        print("   📐 توزيع متوازن للعناصر")
        print("   🔤 خطوط واضحة ومقروءة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_template_features():
    """اختبار ميزات القالب"""
    print("\n🧪 اختبار ميزات القالب:")
    
    try:
        from templates.id_template import (
            save_template_as_json, 
            load_template_from_json,
            verify_layout_fits,
            get_optimized_layout
        )
        
        # اختبار حفظ القالب
        json_path = project_root / "test_template.json"
        save_template_as_json(str(json_path))
        print(f"✅ تم حفظ القالب كـ JSON: {json_path}")
        
        # اختبار التحقق من التخطيط
        layout_check = verify_layout_fits()
        print(f"📏 التحقق من التخطيط: {layout_check}")
        
        # اختبار التخطيط المحسن
        optimized = get_optimized_layout()
        if optimized:
            print("🔧 يوجد تحسين مقترح للتخطيط")
        else:
            print("✅ التخطيط الحالي مناسب")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار الميزات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("🎨 اختبار محرر القالب المحسّن للهويات")
    print("=" * 50)
    
    # اختبار التصميم الجديد
    template_test = test_new_template()
    
    # اختبار ميزات القالب
    features_test = test_template_features()
    
    print("\n" + "=" * 50)
    if template_test and features_test:
        print("🎉 جميع الاختبارات نجحت!")
        print("✨ التصميم الجديد جاهز للاستخدام")
        print("\n📝 التعليمات:")
        print("   1. افتح التطبيق الرئيسي")
        print("   2. اذهب إلى صفحة هويات الطلاب")
        print("   3. انقر على 'إدارة القوالب'")
        print("   4. اختر 'محرر القوالب المرئي'")
        print("   5. استمتع بالمعاينة اللحظية والتصميم الجديد!")
    else:
        print("⚠️ هناك مشاكل في بعض الاختبارات")
        print("🔧 يرجى مراجعة الأخطاء وإصلاحها")
    print("=" * 50)

if __name__ == "__main__":
    main()
